"""THE ESTATE OF SHADOWS — for Hong Wang, Fields Medal 2026.

The four-corner Cantor set C = K x K (K = middle-half Cantor set) is the
canonical purely-unrectifiable 1-set: by the Besicovitch projection theorem
almost every orthogonal projection (shadow) of C has measure zero, and its
Favard length (mean shadow) tends to 0 with the generation.

Point-line duality: the grain (a,b) of C owns the line  u(t) = (a - 1/2) t + b.
The horizontal slice of the resulting line-field at height t is an affine copy
of the shadow of C in direction arctan(t).  So the union of all deeds -- the
ESTATE -- is a braided waterfall of every shadow at once: where the shadow
degenerates to measure zero the braid pinches into blazing filaments; at the
exceptional slopes t = +-1/2, +-2 the digit sets {0,3} + t{0,3} fill exactly
and the braid relaxes into a soft solid band; at t = -1 the digits collide
((a-b) has multiplicity 2^n on a Cantor set) and the braid burns hottest.

A set may own every direction and still own no area: Hong Wang and Joshua
Zahl proved (2025) that in R^3 such an estate is nevertheless forced to have
full Hausdorff dimension 3 -- the Kakeya set conjecture.

Render: exact per-row slice histograms (one giant bincount per row-chunk),
density + mean-slope moment buffers, filmic tone, bloom on true foci. 4096^2.
"""
import numpy as np
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import filmic, bloom, save_png, ramp, bilinear_splat
from scipy.ndimage import gaussian_filter

t0 = time.time()
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "estate_study.png")

# ----------------------------------------------------------------- geometry
G = 9                      # generations: K has 2^G points, C has 4^G grains
digs = np.array([0.0, 0.75])
K = np.zeros(1)
for g in range(G):
    K = (K[:, None] + digs[None, :] * 4.0 ** (-g)).ravel()   # 2^G points in [0,1)
K = K + 0.5 * 4.0 ** (-G)   # center of the generation-G interval
a = K.copy()                # slopes
b = K.copy()                # intercepts
A, B = np.meshgrid(a, b, indexing="ij")
A = A.ravel(); B = B.ravel()          # 4^G grains (a,b) of C
ap = A - 0.5                          # centered slope in [-1/2, 1/2]
N = len(A)
print(f"grains: {N}  ({time.time()-t0:.1f}s)")

# ----------------------------------------------------------------- canvas
SIZE = int(os.environ.get("SIZE", "4096"))
S = 2                       # supersample
H = SIZE * S; W = SIZE * S
T0, T1 = -1.62, 1.13        # vertical axis: slope t (direction tan)
U0, U1 = -0.72, 0.72        # horizontal axis: slice value u = (a-1/2) t + b
# palette position per grain: by slope a (who owns the thread)
pal_t = A.astype(np.float32)

dens = np.zeros((H, W), np.float64)
mom = np.zeros((H, W), np.float64)   # sum of pal_t (for mean slope color)

CHUNK = 48
rows = np.arange(H)
tvals = T0 + (rows + 0.5) / H * (T1 - T0)
for r0 in range(0, H, CHUNK):
    r1 = min(H, r0 + CHUNK)
    tb = tvals[r0:r1]                                # (R,)
    U = ap[None, :] * tb[:, None] + (B[None, :] - 0.5)       # (R, N)
    X = (U - U0) / (U1 - U0) * W - 0.5               # pixel col (float)
    ix = np.floor(X).astype(np.int64)
    fx = (X - ix)
    base = (np.arange(r0, r1)[:, None] - r0) * W
    for tap, wgt in ((ix, 1.0 - fx), (ix + 1, fx)):
        ok = (tap >= 0) & (tap < W)
        idx = (tap + base)[ok]
        wv = wgt[ok]
        dchunk = np.bincount(idx, weights=wv, minlength=(r1 - r0) * W)
        mchunk = np.bincount(idx, weights=wv * np.broadcast_to(pal_t, U.shape)[ok],
                             minlength=(r1 - r0) * W)
        dens[r0:r1] += dchunk.reshape(r1 - r0, W)
        mom[r0:r1] += mchunk.reshape(r1 - r0, W)
    if (r0 // CHUNK) % 40 == 0:
        print(f"row {r0}/{H}  ({time.time()-t0:.1f}s)", flush=True)

print(f"splat done ({time.time()-t0:.1f}s)")

# ------------------------------------------------------------- fold 2x2 -> 1x1
Hf, Wf = H // S, W // S
dens = dens.reshape(Hf, S, Wf, S).mean(axis=(1, 3))
mom = mom.reshape(Hf, S, Wf, S).mean(axis=(1, 3))
mean_a = np.where(dens > 0, mom / np.maximum(dens, 1e-12), 0.5)
mean_a = gaussian_filter(mean_a, 1.2)

# --------------------------------------------------------------- tone + color
d = gaussian_filter(dens, 0.55)
# per-row expected density if mass spread uniformly across the braid width
# (width at t is 1 + |t| in u-units); normalizing by it makes concentration,
# not raw mass, the light source.
tv = T0 + (np.arange(Hf) + 0.5) / Hf * (T1 - T0)
width_px = (1.0 + np.abs(tv)) / (U1 - U0) * Wf
flat = N / width_px          # per-pixel density if the slice were uniform
x = d / flat[:, None]        # concentration ratio (1 = boring uniform)

lum = filmic(x, k=0.62, gamma=0.80)

# color: cool verdigris for low-slope threads -> pale gold for high slopes,
# whites where density crushes everything
stops = [
    (0.00, (0.040, 0.130, 0.200)),   # deep teal
    (0.30, (0.075, 0.360, 0.400)),   # verdigris
    (0.50, (0.520, 0.600, 0.480)),   # sea glass silver
    (0.72, (0.950, 0.700, 0.290)),   # amber
    (1.00, (1.000, 0.870, 0.520)),   # pale gold
]
col = ramp(mean_a, stops)
rgb = col * lum[..., None]
# white-hot core where concentration is extreme
hot = filmic(x, k=0.075, gamma=1.0) ** 3.0
rgb += hot[..., None] * np.array([1.0, 0.97, 0.90]) * 0.85

rgb = bloom(rgb, mask_lo=0.70, sigma=5.5, strength=0.42, tint=(1.0, 0.9, 0.75))
rgb = bloom(rgb, mask_lo=0.35, sigma=28.0, strength=0.16, tint=(0.5, 0.75, 0.9))
save_png(rgb, OUT)
print(f"total {time.time()-t0:.1f}s")
