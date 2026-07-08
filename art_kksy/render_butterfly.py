#!/usr/bin/env python3
"""Render the labelled butterfly maps to a toned PNG.

Register: the spectrum (a Cantor set of bands) is the LIGHT SOURCE; each gap
is painted in its Chern colour, lit by proximity to the bands, so wide gaps
have dark bellies with glowing rims and the filigree blazes.
"""
import numpy as np, sys, time
from PIL import Image
from scipy.ndimage import gaussian_filter
from butterfly import compute_maps

def colorize(label, cov, dist, variant="A", sglow=None):
    H, W = label.shape
    if sglow is None:
        sglow = H / 160.0
    img = np.zeros((H, W, 3), np.float32)
    sentinel = label == -32768
    ingap = ~sentinel
    t = label.astype(np.float32)
    at = np.abs(t)

    # ---- gap colour by Chern number
    m = np.zeros_like(t)
    m[ingap] = np.minimum(at[ingap] - 1.0, 8.0) / 8.0   # 0 at |t|=1 -> 1 at |t|>=9
    if variant == "A":   # ember vs deep teal, tips brighten toward gold / violet
        base_pos = np.array([0.78, 0.16, 0.10]); tip_pos = np.array([1.00, 0.66, 0.18])
        base_neg = np.array([0.04, 0.44, 0.50]); tip_neg = np.array([0.42, 0.30, 0.85])
    else:                # B: crimson vs ice
        base_pos = np.array([0.62, 0.07, 0.14]); tip_pos = np.array([1.00, 0.48, 0.10])
        base_neg = np.array([0.04, 0.30, 0.44]); tip_neg = np.array([0.25, 0.75, 0.95])
    col = np.zeros((H, W, 3), np.float32)
    pos = ingap & (t > 0); neg = ingap & (t < 0)
    for mask, base, tip in ((pos, base_pos, tip_pos), (neg, base_neg, tip_neg)):
        mm = m[mask][:, None]
        col[mask] = (1 - mm) * base[None, :] + mm * tip[None, :]

    # ---- lighting: bands illuminate the gaps
    glow = np.zeros_like(dist)
    glow[ingap] = np.exp(-(dist[ingap] / sglow) ** 1.1)
    body = 0.13                                  # dim belly so wings still read
    lum = body + (1.0 - body) * glow
    # deep filigree (high |t|) recedes a touch: contrast for the brocade fans
    depthdim = 1.0 / (1.0 + 0.115 * np.minimum(at - 1.0, 8.0).clip(0))
    lum = lum * depthdim
    img[ingap] = col[ingap] * lum[ingap][:, None]

    # ---- spectrum filaments: white-gold
    band_col = np.array([1.0, 0.92, 0.70], np.float32)
    cv = cov.clip(0, 1)
    img = img * (1 - cv)[..., None] + (cv[..., None] * band_col[None, None, :]) * 1.35

    # ---- bloom only the true spectrum
    halo = gaussian_filter(cv, sglow * 0.7)
    img += halo[..., None] * band_col[None, None, :] * 0.30

    # ---- tone map
    img = 1.0 - np.exp(-2.3 * img)
    img = img ** (1 / 1.12)

    yy, xx = np.mgrid[0:H, 0:W]
    r2 = (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    img *= (1.0 - 0.10 * r2 ** 1.5)[..., None]
    return (img.clip(0, 1) * 255).astype(np.uint8)

if __name__ == "__main__":
    size = int(sys.argv[1]) if len(sys.argv) > 1 else 1024
    variants = sys.argv[2].split(",") if len(sys.argv) > 2 else ["A"]
    t0 = time.time()
    label, cov, dist, qs = compute_maps(size, size)
    for v in variants:
        rgb = colorize(label, cov, dist, v)
        Image.fromarray(rgb[::-1]).save(f"draft_butterfly_{size}_{v}.png")
        print("saved", v, f"({time.time()-t0:.1f}s)")
