#!/usr/bin/env python3
"""HERO 4096^2: ONE UNIT OF LIGHT, FOLDED THIN -- MO 514628.

Main: champion sigma (n=512, annealed) as multiplicity-of-cover field:
brightness IS the photon count; total light = 1 in every cloth.
Right: the descent chart alpha_n. Bottom: five specimens, same total ink.
"""
import numpy as np, json, os
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter, zoom as ndzoom
from cloth_lib import sigma_id, sigma_rev, area_grid
from cloth_families2 import waist_sigma
from annot import fonts

rng = np.random.default_rng(4)
FINAL = 4096

def mult_field(sigma, R, C):
    """multiplicity-of-cover field (R rows x C cols), rows = y from 0 (bottom) to 1."""
    n = len(sigma)
    d = np.asarray(sigma, np.float64) + 1 - np.arange(1, n+1)
    base = np.arange(n, dtype=np.float64)
    y = (np.arange(R) + 0.5) / R
    L = (base[None, :] + y[:, None] * d[None, :]) / n          # (R, n) left edges in [0,1)
    Lpx = L * C
    Rpx = Lpx + C / n
    F = np.zeros((R, C + 2), np.float32)
    row_idx = np.repeat(np.arange(R), n)
    l = Lpx.ravel(); r = Rpx.ravel()
    li = np.floor(l).astype(np.int64); ri = np.floor(r).astype(np.int64)
    lf = 1.0 - (l - li); rf = r - ri
    li = np.clip(li, 0, C+1); ri = np.clip(ri, 0, C+1)
    flat = F.ravel()
    # full cells via diff trick: +1 at li+1 ... actually add fractional at boundary cells
    np.add.at(flat, row_idx*(C+2) + li, lf)
    np.add.at(flat, row_idx*(C+2) + np.clip(ri, 0, C+1), rf)
    # interior full coverage: +1 on cells (li+1 .. ri-1): diff array
    Dif = np.zeros((R, C + 3), np.float32)
    dflat = Dif.ravel()
    np.add.at(dflat, row_idx*(C+3) + np.clip(li+1, 0, C+2), 1.0)
    np.add.at(dflat, row_idx*(C+3) + np.clip(ri, 0, C+2), -1.0)
    F[:, :] += np.cumsum(Dif, axis=1)[:, :C+2]
    return F[:, :C]   # bottom row = y~0

# warm gold ramp by multiplicity
def colorize(F, mcap=None, gain=1.0):
    m = F.astype(np.float32)
    if mcap is None: mcap = max(np.percentile(m[m > 0.01], 99.9), 4)
    t = np.log1p(m) / np.log1p(mcap)
    t = np.clip(t, 0, 1)
    stops = np.array([[0.02,0.01,0.02],[0.30,0.07,0.03],[0.78,0.35,0.08],
                      [1.0,0.72,0.25],[1.0,0.95,0.72]])
    pos = np.array([0.0, 0.18, 0.5, 0.8, 1.0])
    img = np.zeros(m.shape + (3,), np.float32)
    for c in range(3):
        img[..., c] = np.interp(t, pos, stops[:, c])
    lum = (1 - np.exp(-gain * m))
    return img * lum[..., None]

def render_cloth(sigma, size, gain=0.9, ss=2):
    R = C = size * ss
    F = mult_field(sigma, R, C)
    img = colorize(F, gain=gain)
    img = gaussian_filter(img, (0.7*ss, 0.7*ss, 0))
    # flip so y=0 (bottom of the square) is at image bottom
    img = img[::-1]
    return img  # float 0..~1  (R, C, 3)

def to_pil(imgf, size):
    img8 = np.clip(imgf*255 + rng.uniform(-1, 1, imgf.shape), 0, 255).astype(np.uint8)
    return Image.fromarray(img8).resize((size, size), Image.LANCZOS)

if __name__ == "__main__":
    # ---- data ----
    champ_file = next(f for f in ("cloth_anneal_512c.json", "cloth_anneal_512b.json",
                 "cloth_anneal_512.json") if os.path.exists(f))
    champ = json.load(open(champ_file))
    s512 = np.array(champ["sigma"]); a512 = champ["area"]
    print("champion:", champ_file, a512)

    canvas = Image.new("RGB", (FINAL, FINAL), (5, 4, 7))

    # ---- main cloth ----
    MAIN = 3260
    main_f = render_cloth(s512, MAIN, gain=0.85, ss=2)
    # gentle bloom on the waist
    lum = main_f.sum(2)
    hi = np.clip(main_f - np.percentile(lum, 99.0)/3, 0, None)
    small = hi[::6, ::6]
    bl = gaussian_filter(small, (30/6, 30/6, 0))
    glow = np.clip(ndzoom(bl, (6, 6, 1), order=1)[:main_f.shape[0], :main_f.shape[1]], 0, None)
    main_f = main_f + 0.5*glow
    main_im = to_pil(np.clip(main_f, 0, 1.5)/1.0, MAIN)
    canvas.paste(main_im, (60, 100))

    # ---- specimens ----
    n = 512
    specs = [("identity — area 1.0000", sigma_id(n), None),
             ("random — area %.4f", rng.permutation(n), None),
             ("reversal — area %.4f", sigma_rev(n), None),
             ("waist design — area %.4f", waist_sigma(n, n//16, 0.4, 0.6, rng), None),
             ("annealed champion — area %.4f", s512, a512)]
    SP = 560
    x0 = 60; y0 = 3470
    F = fonts(1.0)
    d = ImageDraw.Draw(canvas)
    for k, (lab, sg, aval) in enumerate(specs):
        if aval is None: aval = area_grid(sg, 4096)
        f = render_cloth(sg, SP, gain=0.85, ss=2)
        # SAME total ink: normalize each by its own sum to equal budget
        tot = f.sum()
        f = f * (2.35e5 * (SP/560)**2 / max(tot, 1))
        im = to_pil(np.clip(f, 0, 1), SP)
        px = x0 + k*(SP + 235)
        canvas.paste(im, (px, y0))
        d.rectangle([px-1, y0-1, px+SP, y0+SP], outline=(60, 55, 70), width=1)
        txt = lab % aval if "%" in lab else lab
        d.text((px, y0 + SP + 10), txt, font=F["mono_s"], fill=(150, 140, 155))
    np.save("hero_stage.npy", np.zeros(1))
    canvas.save("hero_stage1.png")
    print("stage1 saved")
