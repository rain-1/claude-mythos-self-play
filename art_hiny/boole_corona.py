"""The Sun of Nothing — Boole map orbit as a polar corona.

One long orbit. angle = time, radius = r0 ± asinh(|x|)-scaled height
(positive excursions flare outward, negative fold inward). The scramble at
x~0 is the burning ring; excursions are flame tongues, destiny-colored by
their peak. Flares beyond VCAP exit the frame (gone toward Infinity for
longer than this window can see).
"""
import sys, os
import numpy as np
from glow import splat_segments, filmic, bloom, lerp_palette
from PIL import Image

S     = int(sys.argv[1])   if len(sys.argv) > 1 else 1280
T     = int(sys.argv[2])   if len(sys.argv) > 2 else 3_000_000
X0    = float(sys.argv[3]) if len(sys.argv) > 3 else 1.54217
VCAP  = float(sys.argv[4]) if len(sys.argv) > 4 else 300.0
GAIN  = float(sys.argv[5]) if len(sys.argv) > 5 else 1.0
OUT   = sys.argv[6]        if len(sys.argv) > 6 else "proto/corona_a.png"
SS    = 2
W = H = S * SS
R0    = 0.40   # zero-ring radius (fraction of half-frame)
ROUT  = 0.97
RIN   = 0.04

# ---- simulate ----------------------------------------------------------------
x = X0
xs = np.empty(T + 1, np.float32)
xs[0] = x
for t in range(T):
    x = x - 1.0 / x
    xs[t + 1] = x
xs64 = xs.astype(np.float64)

den = np.arcsinh(VCAP)
a = np.arcsinh(np.abs(xs64)) / den            # 0.. beyond 1
pos = xs64 > 0
r = np.where(pos, R0 + a * (ROUT - R0), R0 - a * (R0 - RIN))
theta = np.linspace(-np.pi / 2, 3 * np.pi / 2, T + 1)  # start at top, one turn
half = min(W, H) / 2
cx = cy = (W - 1) / 2
pxx = cx + r * half * np.cos(theta)
pyy = cy + r * half * np.sin(theta)

# ---- destiny colors ----------------------------------------------------------
PAL = [(0.00, (1.00, 0.38, 0.08)),
       (0.30, (1.00, 0.70, 0.22)),
       (0.55, (0.95, 0.90, 0.65)),
       (0.78, (0.55, 0.78, 1.00)),
       (1.00, (0.88, 0.95, 1.00))]
logden = np.log10(VCAP) * 1.15   # peaks above VCAP saturate the ice end
s = pos
cuts = np.nonzero(s[1:] != s[:-1])[0] + 1
bounds = np.concatenate([[0], cuts, [T + 1]])
col = np.empty((T + 1, 3), np.float32)
aa = np.abs(xs64)
for b0, b1 in zip(bounds[:-1], bounds[1:]):
    peak = aa[b0:b1].max()
    tt = min(np.log10(max(peak, 1.0)) / logden, 1.0)
    col[b0:b1] = lerp_palette(tt, PAL)
cseg = (col[:-1] + col[1:]) * 0.5

# ---- splat -------------------------------------------------------------------
acc = np.zeros((H, W, 3), np.float32)
dr = np.abs(np.diff(r))
wseg = np.where(dr > 0.05, 0.3, 1.0) * GAIN * 0.35 * (2560 / W) ** 0.6
splat_segments(acc, pxx[:-1], pyy[:-1], pxx[1:], pyy[1:], wseg, cseg)

img = filmic(acc, k=1.0, gamma=0.85)
img = bloom(img, mask_lo=0.5, sigma=5 * SS, gain=0.55)
os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
im8 = (np.clip(img, 0, 1) * 255).astype(np.uint8)
Image.fromarray(im8).resize((S, S), Image.LANCZOS).save(OUT)
n_exit = int(np.count_nonzero(np.array([aa[b0:b1].max() for b0, b1 in zip(bounds[:-1], bounds[1:])]) > VCAP))
print("saved", OUT, "| excursions:", len(bounds) - 1, "| flares beyond rim:", n_exit, "| max |x|:", round(float(aa.max()), 1))
