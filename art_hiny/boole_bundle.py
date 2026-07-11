"""The Sky of Returns v2 — a single orbit-bundle of the Boole map.

K starts separated by eps ride the same arcs as one blazing thread; every
passage through Nothing (x ~ 0, where T'(x) = 1 + 1/x^2 stretches) splits the
bundle. Branching tree of comet arcs = measure conserved, memory not.
"""
import sys, os
import numpy as np
from glow import splat_segments, filmic, bloom, lerp_palette
from PIL import Image

S    = int(sys.argv[1])   if len(sys.argv) > 1 else 1280
K    = int(sys.argv[2])   if len(sys.argv) > 2 else 240
T    = int(sys.argv[3])   if len(sys.argv) > 3 else 90_000
X0   = float(sys.argv[4]) if len(sys.argv) > 4 else 1.54217
EPS  = float(sys.argv[5]) if len(sys.argv) > 5 else 1e-12
GAIN = float(sys.argv[6]) if len(sys.argv) > 6 else 1.0
OUT  = sys.argv[7]        if len(sys.argv) > 7 else f"proto/bundle_{S}_{K}_{X0}_{EPS:g}.png"
SS   = 2
W = H = S * SS

# ---- simulate bundle --------------------------------------------------------
x = X0 + EPS * np.arange(K)
xs = np.empty((K, T + 1), np.float32)
xs[:, 0] = x
xw = x.astype(np.float64)
for t in range(T):
    xw = xw - 1.0 / xw
    xs[:, t + 1] = xw

VMAX = float(np.abs(xs).max())
den = np.arcsinh(VMAX)
logmax = np.log10(max(VMAX, 10.0))

PAL = [(0.00, (1.00, 0.40, 0.09)),
       (0.28, (1.00, 0.72, 0.26)),
       (0.52, (0.92, 0.90, 0.72)),
       (0.75, (0.58, 0.78, 1.00)),
       (1.00, (0.85, 0.94, 1.00))]

acc = np.zeros((H, W, 3), np.float32)
pxt = np.linspace(0, W - 1, T + 1)
BASE = GAIN * 0.55 * (2560 / W) ** 0.6 / (K / 240)

for i in range(K):
    xi = xs[i].astype(np.float64)
    v = np.sign(xi) * np.arcsinh(np.abs(xi)) / den
    py = H / 2 - v * (H / 2) * 0.94
    # destiny colors per excursion
    s = xi > 0
    cuts = np.nonzero(s[1:] != s[:-1])[0] + 1
    bounds = np.concatenate([[0], cuts, [T + 1]])
    col = np.empty((T + 1, 3), np.float32)
    a = np.abs(xi)
    for b0, b1 in zip(bounds[:-1], bounds[1:]):
        peak = a[b0:b1].max()
        tt = np.log10(max(peak, 1.0)) / logmax
        col[b0:b1] = lerp_palette(tt, PAL)
    cseg = (col[:-1] + col[1:]) * 0.5
    dy = np.abs(np.diff(py))
    wseg = np.where(dy > H * 0.05, 0.3, 1.0) * BASE
    splat_segments(acc, pxt[:-1], py[:-1], pxt[1:], py[1:], wseg, cseg)

img = filmic(acc, k=1.0, gamma=0.85)
img = bloom(img, mask_lo=0.5, sigma=5 * SS, gain=0.55)
os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
im8 = (np.clip(img, 0, 1) * 255).astype(np.uint8)
Image.fromarray(im8).resize((S, S), Image.LANCZOS).save(OUT)
print("saved", OUT, "VMAX=", round(VMAX, 1))
