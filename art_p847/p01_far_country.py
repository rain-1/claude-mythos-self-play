#!/usr/bin/env python3
"""
01 — The Far Country
Hyperbolic {p,q} kaleidoscope in the Poincare disk via per-pixel fold-into-
fundamental-domain. Each point is reflected across the three mirrors of a
Schwarz triangle (angles pi/p, pi/q, pi/2) until it lands in the fundamental
triangle; we record the reflection count (a Cayley-graph word-length mandala),
the parity (checker) and the final position (faceting).

The ideal boundary |z|=1 is a singularity: tiles shrink to zero there, so the
crowding is genuinely multiscale and rewards native 4096.

Third mirror geometry (derived): a circle orthogonal to the unit disk whose
centre lies on the x-axis (so it meets mirror-1 at right angle = order-2 vertex)
and meets the pi/p ray at angle pi/q (order-q vertex):
    d = cos(pi/q)/sqrt(cos(pi/p)**2 - sin(pi/q)**2),   r = sqrt(d*d - 1)
real exactly when 1/p + 1/q < 1/2 (the hyperbolic condition).

Memory-safe: folds a flat, shrinking set of still-active pixels, not the full
grid each iteration -> bounded RAM even at 8192x8192 internal.
"""
import sys, numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

P, Q = 7, 3                  # {7,3}: heptagons, three to a vertex
S  = int(sys.argv[1]) if len(sys.argv) > 1 else 512
OUT = sys.argv[2] if len(sys.argv) > 2 else "01_far_country.png"
SS = 2
MAXIT = 260
N  = S * SS

a = np.pi / P
two_a = 2.0 * a
d = np.cos(np.pi/Q) / np.sqrt(np.cos(np.pi/P)**2 - np.sin(np.pi/Q)**2)
r = np.sqrt(d*d - 1.0)
r2 = r*r
print(f"{{{P},{Q}}}  N={N}  mirror circle centre d={d:.5f} r={r:.5f}", flush=True)

lin = ((np.arange(N) + 0.5) / N * 2.0 - 1.0).astype(np.float32)
X, Y = np.meshgrid(lin, lin)
R2 = (X*X + Y*Y).astype(np.float32)
inside = R2 < np.float32(0.9985**2)
idx = np.flatnonzero(inside)                       # flat indices of disk pixels

ax = X.ravel()[idx].copy()
ay = Y.ravel()[idx].copy()
acount = np.zeros(idx.size, np.int32)
live = np.ones(idx.size, bool)
del X, Y

for it in range(MAXIT):
    li = np.flatnonzero(live)
    if li.size == 0:
        break
    xx = ax[li]; yy = ay[li]

    # fold angle into the wedge [0, a] with the two diameter mirrors
    ang = np.arctan2(yy, xx)
    rad = np.hypot(xx, yy)
    t = np.mod(ang, two_a)
    refl = t > a
    t = np.where(refl, two_a - t, t)
    k = np.floor(ang / two_a)
    nref = (2.0*np.abs(k)).astype(np.int32) + refl.astype(np.int32)
    nx = rad*np.cos(t); ny = rad*np.sin(t)
    changed_w = (np.abs(nx - xx) + np.abs(ny - yy)) > 1e-7
    xx = nx; yy = ny

    # invert across the mirror circle if on the wrong side
    dx = xx - d
    dist2 = dx*dx + yy*yy
    insidec = dist2 < (r2 - 1e-7)
    scale = np.where(insidec, r2/np.where(dist2 == 0, 1e-30, dist2), 1.0)
    xx = np.where(insidec, d + dx*scale, xx)
    yy = np.where(insidec, yy*scale, yy)

    acount[li] += nref + insidec.astype(np.int32)
    ax[li] = xx; ay[li] = yy
    converged = ~(changed_w | insidec)
    live[li[converged]] = False
    if it % 30 == 0:
        print(f"  it {it:3d}  live {li.size}", flush=True)

boundary_active = live.copy()                       # stuck against the boundary

# --- colour (all per active-pixel, then scatter) --------------------------
fang = np.clip(np.arctan2(np.abs(ay), ax) / a, 0, 1)
darc = np.hypot(ax - d, ay)
fv = np.clip((darc - r) / (d - r), 0, 1)

rpx = np.sqrt(np.clip(R2.ravel()[idx], 0, 1.0))
t = rpx**1.15
cstops = np.array([
    [255, 248, 224], [252, 216, 132], [244, 152, 66], [216, 82, 66],
    [160, 50, 98],   [92, 50, 130],   [46, 52, 132],  [30, 40, 104],
    [20, 28, 74],
], np.float32)
u = np.clip(t, 0, 1) * (len(cstops) - 1)
i0 = np.clip(np.floor(u).astype(int), 0, len(cstops)-2)
f = (u - i0)[:, None]
col = cstops[i0]*(1-f) + cstops[i0+1]*f

facet = 0.80 + 0.20*np.cos(2*np.pi*fang)
rimlight = 0.28*np.exp(-fv*5.0)
shade = np.clip(facet + rimlight, 0, 1.25)
col = col * shade[:, None]
checker = (acount % 2).astype(np.float32)
col *= (1.0 - 0.08*checker)[:, None]
edge = (fv < 0.016) | (fang < 0.011) | (fang > 0.989)
col = np.where(edge[:, None], col*0.30, col)

# scatter into the full image
img = np.zeros((N*N, 3), np.float32)
img[idx] = col
img = img.reshape(N, N, 3)

# bloom of the warm core
lum = img.mean(axis=2)
coremask = (lum > 150)[..., None] * img
halo = np.empty_like(img)
for c in range(3):
    halo[..., c] = gaussian_filter(coremask[..., c], sigma=N*0.012)
del coremask
img += 0.5*halo
del halo

# boundary singularity + ideal points -> deep ink
bnd_idx = idx[boundary_active]
img.reshape(N*N, 3)[bnd_idx] = np.array([6, 8, 20], np.float32)
flatR2 = R2.ravel()
rim = (flatR2 >= 0.9985**2) & (flatR2 < 1.02**2)
img.reshape(N*N, 3)[rim] = np.array([3, 4, 10], np.float32)
img.reshape(N*N, 3)[flatR2 >= 1.0] = np.array([2, 3, 8], np.float32)

k = 235.0
img = 255.0*(1.0 - np.exp(-img/k))
img = np.clip(img, 0, 255).astype(np.uint8)

im = Image.fromarray(img, "RGB")
if SS > 1:
    im = im.resize((S, S), Image.LANCZOS)
im.save(OUT)
print("saved", OUT, im.size, flush=True)
