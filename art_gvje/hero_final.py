"""HERO 4096x4096: 'The Times Table of the Simplest Field'
Window: i,j < 1024 (one megacell of exact nim-products), 4x4 px per cell.
Hue+luminance: 0.45*log2-depth + 0.55*ECDF through a dusk ramp.
Origin-anchored warm light (the mex genesis radiates from 0),
Frobenius squaring diagonal as a gold thread, nim-inverse pairs as icy stars.
"""
import numpy as np, sys, time
from nim import nmul
from render_common import filmic, ramp, fast_bloom, save
from scipy.ndimage import gaussian_filter

W = 1024           # table window
UP = 4             # px per cell
S = W * UP         # canvas 4096
t0 = time.time()
i = np.arange(W, dtype=np.int32)
V = nmul(i[:, None], i[None, :])

t = np.log2(1.0 + V) / 16.0
order = np.argsort(V.ravel()).argsort().reshape(V.shape).astype(np.float64)
ecdf = order / order.size
m = 0.45 * t + 0.55 * ecdf

stops = [
    (0.000, (1.00, 0.99, 0.94)),
    (0.125, (1.00, 0.88, 0.55)),
    (0.250, (1.00, 0.72, 0.28)),
    (0.375, (0.92, 0.48, 0.16)),
    (0.500, (0.72, 0.26, 0.16)),
    (0.625, (0.50, 0.15, 0.24)),
    (0.700, (0.38, 0.13, 0.33)),
    (0.775, (0.26, 0.12, 0.38)),
    (0.850, (0.15, 0.13, 0.40)),
    (0.925, (0.08, 0.13, 0.30)),
    (1.000, (0.04, 0.08, 0.16)),
]
col = ramp(stops, m)
L = (1.0 - m) ** 1.2 * 1.15 + 0.26
base = col * L[..., None]                      # W x W x 3

# upscale data layer NEAREST (exact cells)
img = np.repeat(np.repeat(base, UP, axis=0), UP, axis=1)

# --- continuous layers at canvas res ---
y, x = np.meshgrid(np.arange(S, dtype=np.float64), np.arange(S, dtype=np.float64), indexing='ij')
r = np.sqrt(x*x + y*y) / (S * np.sqrt(2))
warm = np.exp(-(r / 0.34) ** 1.5)
light = (0.62 + 0.55 * warm)[..., None] * (np.array([1.0,1.0,1.0]) + warm[..., None]*np.array([0.08,-0.02,-0.16]))
img *= light
halo = np.exp(-(r / 0.06) ** 2) * 0.55
img += halo[..., None] * np.array([1.0, 0.88, 0.55])
del x, y

# Frobenius diagonal thread (soft, continuous)
d = np.abs(np.arange(S)[:, None] - np.arange(S)[None, :]).astype(np.float64)
diag_w = np.exp(-(d / 5.0) ** 2)
img *= (1.0 + 0.40 * diag_w)[..., None]
del d, diag_w

# icy-cyan inverse-pair stars at cell centers
star = np.zeros((S, S))
ys, xs = np.nonzero(V == 1)
star[ys*UP + UP//2, xs*UP + UP//2] = 1.0
starb = gaussian_filter(star, 5.0) * 260 + gaussian_filter(star, 1.8) * 55
img += starb[..., None] * np.array([0.55, 0.92, 1.0])
del star, starb

lum = img @ np.array([0.35, 0.5, 0.15])
hi = np.clip(lum - 0.85, 0, None)
img += fast_bloom(hi, 14)[..., None] * np.array([1.0, 0.85, 0.55]) * 0.4
del lum, hi
out = filmic(img, k=1.30, gamma=0.92)
save(out, 'hero_4096.png')
print('done', time.time() - t0)
