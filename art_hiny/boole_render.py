"""The Sky of Returns — Boole map x -> x - 1/x excursion ensemble.

Chart: time -> x-pixel, sign(x)*asinh(|x|) -> y. Each orbit is a thread;
each excursion (maximal run of one sign) is destiny-colored by its peak
height. The scramble near x=0 burns warm; the great arcs cool to ice.
"""
import sys
import numpy as np
from glow import splat_segments, filmic, bloom, save, lerp_palette

S        = int(sys.argv[1]) if len(sys.argv) > 1 else 1280
SS       = 2                     # supersample
M        = int(sys.argv[2]) if len(sys.argv) > 2 else 1500   # orbits
T        = int(sys.argv[3]) if len(sys.argv) > 3 else 6000   # steps shown
BURN     = 500
SEED     = int(sys.argv[4]) if len(sys.argv) > 4 else 11
GAIN     = float(sys.argv[5]) if len(sys.argv) > 5 else 1.0
OUT      = sys.argv[6] if len(sys.argv) > 6 else f"proto/boole_{S}_{M}_{T}_{SEED}.png"

W = H = S * SS
rng = np.random.default_rng(SEED)

# ---- simulate ---------------------------------------------------------------
x = rng.uniform(0.5, 2.0, M)
for _ in range(BURN):
    x = x - 1.0 / x
xs = np.empty((M, T + 1), np.float64)
xs[:, 0] = x
for t in range(T):
    x = x - 1.0 / x
    xs[:, t + 1] = x

# ---- chart ------------------------------------------------------------------
VMAX = np.abs(xs).max()
v = np.sign(xs) * np.arcsinh(np.abs(xs)) / np.arcsinh(VMAX)   # in [-1,1]
px = np.linspace(0, W - 1, T + 1)[None, :].repeat(M, 0)
py = H / 2 - v * (H / 2) * 0.94

# ---- destiny colors: per-excursion peak -------------------------------------
# palette: low peaks warm ember/gold -> high peaks pale ice blue
PAL = [(0.00, (1.00, 0.42, 0.10)),
       (0.30, (1.00, 0.70, 0.25)),
       (0.55, (0.85, 0.85, 0.70)),
       (0.78, (0.55, 0.75, 1.00)),
       (1.00, (0.80, 0.92, 1.00))]

sgn = xs > 0
col = np.empty((M, T + 1, 3), np.float32)
logmax = np.log10(VMAX)
for i in range(M):
    s = sgn[i]
    # excursion boundaries
    cuts = np.nonzero(s[1:] != s[:-1])[0] + 1
    bounds = np.concatenate([[0], cuts, [T + 1]])
    a = np.abs(xs[i])
    for b0, b1 in zip(bounds[:-1], bounds[1:]):
        peak = a[b0:b1].max()
        tt = np.log10(max(peak, 1.0)) / logmax
        col[i, b0:b1] = lerp_palette(tt, PAL)

# ---- splat ------------------------------------------------------------------
acc = np.zeros((H, W, 3), np.float32)
# per-segment: endpoints t, t+1
x0 = px[:, :-1].ravel(); x1 = px[:, 1:].ravel()
y0 = py[:, :-1].ravel(); y1 = py[:, 1:].ravel()
cseg = ((col[:, :-1] + col[:, 1:]) * 0.5).reshape(-1, 3)

# launch segments (huge |dy|) get reduced weight so fountains whisper
dy = np.abs(y1 - y0)
wseg = np.full(len(x0), 1.0)
steep = dy > H * 0.05
wseg[steep] = 0.25

BASE = 0.012 * GAIN * (1280 / S) ** 0.6   # fog law tuning
splat_segments(acc, x0, y0, x1, y1, wseg * BASE, cseg)

# ---- tone -------------------------------------------------------------------
img = filmic(acc, k=1.0, gamma=0.85)
img = bloom(img, mask_lo=0.55, sigma=6 * SS, gain=0.5)
img = np.clip(img, 0, 1)

import os
os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
from PIL import Image
im8 = (np.clip(img, 0, 1) * 255).astype(np.uint8)
Image.fromarray(im8).resize((S, S), Image.LANCZOS).save(OUT)
print("saved", OUT, " VMAX=", round(VMAX, 1))
