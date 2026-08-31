#!/usr/bin/env python3
"""THE ORBIT THAT WOULD NOT SETTLE — outer billiards on the golden kite (2560²).

Every orbit computed in exact (1/16)Z[sqrt5] arithmetic (the map is
subtraction only), so each fate is a certificate: gold web = seeds PROVABLY
periodic (state recurrence is exact integer equality; hue deepens with the
period, 3 up to tens of thousands); ice = seeds that never repeated a state
in 60,000 steps — the wanderers, one carried out to |P| = 239 and still
going (Schwartz: irrational kites have unbounded orbits — the Moser–Neumann
question answered); ember stubs = seeds that hit a singular ray exactly
(the map is undefined there; detected by a vanishing integer cross product).

Chart: asinh-compressed radius (center true-scale, the wanderers' far
country folded into the rim). The kite itself: gold, at center.
"""
import numpy as np, math, sys
import scipy.ndimage as ndi
from PIL import Image, ImageDraw, ImageFont

PROTO = len(sys.argv) > 1 and sys.argv[1] == "proto"
SIZE = 1024 if PROTO else 2560
SS = 2
S = SIZE * SS
rs = SIZE / 1024.0

D = np.load("outer_orbits.npz", allow_pickle=True)
VIS = D["vis"]            # (NSTEP, NS, 2)
fate = D["fate"]; periods = D["periods"]; exc = D["exc"]
NSTEP, NS, _ = VIS.shape
S5 = math.sqrt(5.0)
PHI1 = (S5 - 1) / 2

RSCALE = 9.0
AMAX = math.asinh(260.0 / RSCALE)
def warp(x, y):
    r = np.hypot(x, y)
    w = np.arcsinh(r / RSCALE) / AMAX
    f = np.where(r > 1e-9, w / np.maximum(r, 1e-9), 0.0)
    return x * f, y * f
CX, CY = 0.5 * S, 0.585 * S
RAD = 0.415 * S

img = np.zeros((S, S, 3), np.float32)

def splat_layer(pts_x, pts_y, wgt, sig, col_arr):
    H = np.zeros((S, S), np.float32)
    C = [np.zeros((S, S), np.float32) for _ in range(3)]
    wx, wy = warp(pts_x, pts_y)
    px = CX + wx * RAD
    py = CY - wy * RAD
    xi = np.clip(px.astype(int), 0, S - 1)
    yi = np.clip(py.astype(int), 0, S - 1)
    flat = yi * S + xi
    np.add.at(H.ravel(), flat, wgt)
    for ch in range(3):
        np.add.at(C[ch].ravel(), flat, wgt * col_arr[:, ch])
    H = ndi.gaussian_filter(H, sig)
    for ch in range(3):
        C[ch] = ndi.gaussian_filter(C[ch], sig)
    return H, C

# drop frozen repeats (retired seeds hold position)
move = np.ones((NSTEP, NS), bool)
move[1:] = np.any(VIS[1:] != VIS[:-1], axis=2)

# ---- periodic web (gold -> rose by log period)
per_m = (fate == 2)
if per_m.any():
    lp = np.log2(np.maximum(periods[per_m], 2)).astype(np.float32)
    lp = (lp - lp.min()) / max(lp.max() - lp.min(), 1e-9)
    cA = np.array([1.2, 0.95, 0.4], np.float32)
    cB = np.array([1.05, 0.35, 0.45], np.float32)
    colseed = cA[None, :] * (1 - lp[:, None]) + cB[None, :] * lp[:, None]
    sel = np.nonzero(per_m)[0]
    mv = move[:, sel]
    px = VIS[:, sel, 0][mv]; py = VIS[:, sel, 1][mv]
    cols = np.broadcast_to(colseed[None, :, :], (NSTEP, len(sel), 3))[mv]
    w = np.full(len(px), 1.0, np.float32)
    H, C = splat_layer(px, py, w, 1.1 * SS * rs, cols)
    Hn = H / max(np.percentile(H[H > 0], 99.0), 1e-9)
    tone = 1 - np.exp(-3.4 * np.power(Hn, 0.52))
    dsafe = np.maximum(H, 1e-9)
    for ch in range(3):
        img[..., ch] += tone * (C[ch] / dsafe)

# ---- wanderers (ice), brighter per point
wan_m = (fate == 0)
if wan_m.any():
    sel = np.nonzero(wan_m)[0]
    mv = move[:, sel]
    px = VIS[:, sel, 0][mv]; py = VIS[:, sel, 1][mv]
    cols = np.broadcast_to(np.array([0.45, 0.85, 1.15], np.float32)[None, None, :],
                           (NSTEP, len(sel), 3))[mv]
    H, C = splat_layer(px, py, np.full(len(px), 1.0, np.float32), 1.1 * SS * rs, cols)
    Hn = H / max(np.percentile(H[H > 0], 99.7), 1e-9)
    tone = 1 - np.exp(-1.1 * np.power(Hn, 0.8))
    dsafe = np.maximum(H, 1e-9)
    for ch in range(3):
        img[..., ch] += tone * (C[ch] / dsafe) * 0.55

# ---- singular stubs (ember, faint)
sg_m = (fate == 1)
if sg_m.any():
    sel = np.nonzero(sg_m)[0]
    mv = move[:, sel]
    px = VIS[:, sel, 0][mv]; py = VIS[:, sel, 1][mv]
    cols = np.broadcast_to(np.array([0.9, 0.35, 0.22], np.float32)[None, None, :],
                           (NSTEP, len(sel), 3))[mv]
    H, C = splat_layer(px, py, np.full(len(px), 1.0, np.float32), 1.2 * SS * rs, cols)
    Hn = H / max(np.percentile(H[H > 0], 99.0), 1e-9)
    tone = 1 - np.exp(-1.2 * np.power(Hn, 0.6))
    dsafe = np.maximum(H, 1e-9)
    for ch in range(3):
        img[..., ch] += tone * (C[ch] / dsafe) * 0.5

# ---- the kite (gold outline)
KV = [(-1.0, 0.0), (0.0, 1.0), (PHI1, 0.0), (0.0, -1.0), (-1.0, 0.0)]
for k in range(len(KV) - 1):
    t = np.linspace(0, 1, 400)
    x = KV[k][0] + (KV[k + 1][0] - KV[k][0]) * t
    y = KV[k][1] + (KV[k + 1][1] - KV[k][1]) * t
    wx, wy = warp(x, y)
    px = (CX + wx * RAD).astype(int); py = (CY - wy * RAD).astype(int)
    m = (px >= 2) & (px < S - 2) & (py >= 2) & (py < S - 2)
    for ch, v in enumerate((1.3, 1.05, 0.5)):
        img[py[m], px[m], ch] += v * 0.9
img[..., :] = np.maximum(img, 0)
img[:, :, :] = ndi.gaussian_filter(img, (0.7 * SS * rs, 0.7 * SS * rs, 0))

# faint asinh radius rings for scale (r = 10, 50, 239.1)
yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
for rv, amp in ((10, 0.05), (50, 0.05), (239.1, 0.10)):
    rw = math.asinh(rv / RSCALE) / AMAX * RAD
    dd = np.hypot(xx - CX, yy - CY)
    ring = np.exp(-((dd - rw) / (1.2 * SS * rs)) ** 2)
    for ch, v in enumerate((0.5, 0.7, 0.9)):
        img[..., ch] += ring * v * amp

# bloom
hot = np.clip(img.sum(2) - 2.7, 0, None)
ds = 4
bloom = ndi.zoom(ndi.gaussian_filter(hot[::ds, ::ds], 8 * rs), ds, order=1)[:S, :S]
if bloom.shape != (S, S):
    bloom = np.pad(bloom, ((0, S - bloom.shape[0]), (0, S - bloom.shape[1])), mode="edge")
img += bloom[..., None] * np.array([0.85, 0.8, 0.65])[None, None, :] * 0.18

img = 1 - np.exp(-1.35 * np.clip(img, 0, None))
img = np.power(np.clip(img, 0, 1), 1 / 2.1)
img = (img + np.random.uniform(-1 / 255, 1 / 255, img.shape)).clip(0, 1)
im = Image.fromarray((img * 255).astype(np.uint8)).resize((SIZE, SIZE), Image.LANCZOS)

def loadfont(p, sz):
    try: return ImageFont.truetype(p, sz)
    except Exception: return ImageFont.load_default()
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
d = ImageDraw.Draw(im)
npd = int((fate == 2).sum()); nw = int((fate == 0).sum()); nsg = int((fate == 1).sum())
pmax = int(periods[periods > 0].max()) if (periods > 0).any() else 0
mex = float(np.sqrt(exc[fate == 0].max())) if nw else 0.0
d.text((int(0.035 * SIZE), int(0.030 * SIZE)), "THE ORBIT THAT WOULD NOT SETTLE",
       font=loadfont(FB, int(28 * rs)), fill=(238, 216, 165))
y = int(0.075 * SIZE)
for line in [
    "outer billiards on the golden kite (-1,0)(0,1)((sqrt5-1)/2,0)(0,-1): reflect through the tangent corner, repeat",
    "every orbit in exact (1/16)Z[sqrt5] arithmetic — subtraction only, so each fate is a certificate",
    f"{npd} of 305 seeds PROVABLY periodic (exact recurrence; periods 3 to {pmax:,}) — the gold-to-rose web",
    f"{nw} wanderers never repeated a state in 60,000 steps; the farthest carried to |P| = {mex:.1f} — ice",
    f"{nsg} seeds struck a singular ray exactly (vanishing integer cross product) — ember stubs",
    "Schwartz 2007: irrational kites have unbounded orbits (Moser-Neumann); asinh radius chart",
]:
    d.text((int(0.035 * SIZE), y), line, font=loadfont(FR, int(14.5 * rs)), fill=(168, 173, 185))
    y += int(24.5 * rs)
OUT = "outer_proto.png" if PROTO else "outer_2560.png"
im.save(OUT)
print("wrote", OUT)
