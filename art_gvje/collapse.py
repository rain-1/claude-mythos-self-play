"""PANEL 3 (2560x2560): 'The Silence Before the Fourth Mountain'
MO 513363: for which n is the nim times-table M_n = [i(x)j] singular over Q?
x = log2(n).  Above the horizon: gold aurora = log|det M_n| / n (bits of memory per row),
with breaches where det = 0.  Below: cyan stalactite mountains = log2(1 + corank(n)),
independently recomputed for all n <= 1300 (two primes).  Far right: the conjectured
fourth range [q4+3, 2q4-4], peak corank q4/4-1 at 3q4/2-1 -- rendered as phantom mist.
Fermat towers n = 16, 256, 65536 as pillars of light.
"""
import numpy as np, time
from render_common import filmic, ramp, fast_bloom, save
from scipy.ndimage import gaussian_filter

S = 2560
corank = np.load('corank.npy')          # n = 1..1300
logdet = np.load('logdet.npy')
ext_n = np.load('ext_n.npy'); ext_ld = np.load('ext_ld.npy')

XL, XR = 3.0, 17.25
def xpix(n):
    return ((np.log2(n) - XL) / (XR - XL) * 0.94 + 0.03) * S
YH = 0.46 * S

ns = np.arange(1, 1301)
sing = corank > 0
ld_per = logdet / ns                     # nats per row
valid = np.isfinite(ld_per) & (ns >= 8)
lo, hi = np.nanmin(ld_per[valid]), np.nanmax(np.concatenate([ld_per[valid], ext_ld/ext_n]))
def ypix_a(ldp):                          # aurora height above horizon
    return YH - (0.05 + 0.30 * (ldp - lo) / (hi - lo)) * S
DMAX = np.log2(1 + 16383.0)
def dpix(c):                              # stalactite depth below horizon
    return (np.log2(1.0 + c) / DMAX) * 0.40 * S

img = np.zeros((S, S, 3))
yy = np.arange(S)[:, None].astype(np.float64)

# ---- Fermat pillars ----
xs_grid = np.arange(S)[None, :].astype(np.float64)
for q, amp in [(16, 0.10), (256, 0.12), (65536, 0.16)]:
    band = np.exp(-((xs_grid - xpix(q)) / (7.0)) ** 2) * amp
    vert = 0.55 + 0.45 * np.exp(-((yy - YH) / (0.5 * S)) ** 2)
    img += (band * vert)[..., None] * np.array([1.0, 0.92, 0.70])

# ---- aurora (nonsingular n) ----
aur = np.zeros((S, S))
pts = [(xpix(n), ypix_a(ld_per[n-1])) for n in range(8, 1301) if not sing[n-1] and np.isfinite(ld_per[n-1])]
px = np.array([p[0] for p in pts]); py = np.array([p[1] for p in pts])
# curve: splat with vertical gaussian thickness; fill: soft column from curve to horizon
colx = np.clip(px.astype(int), 0, S-1)
curve_y = np.full(S, np.nan)
for x_, y_ in zip(colx, py):
    curve_y[x_] = y_ if np.isnan(curve_y[x_]) else min(curve_y[x_], y_)
# extension samples
for n_, ld_ in zip(ext_n, ext_ld):
    x_ = int(np.clip(xpix(n_), 0, S-1)); curve_y[x_] = ypix_a(ld_ / n_)
have = ~np.isnan(curve_y)
xh = np.where(have)[0]
# dense-region interpolation only (avoid bridging the far silence): bridge gaps < 40 px
for a, b in zip(xh[:-1], xh[1:]):
    if b - a <= 40:
        t = np.arange(a, b+1)
        curve_y[t] = np.interp(t, [a, b], [curve_y[a], curve_y[b]])
havef = ~np.isnan(curve_y)
cy2 = curve_y.copy()
# draw
for x_ in np.where(havef)[0]:
    y0 = cy2[x_]
    aur[:, x_] += np.exp(-((np.arange(S) - y0) / 2.2) ** 2) * 2.6          # crisp curve
    below = (np.arange(S) > y0) & (np.arange(S) < YH + 2)
    depthfrac = np.clip((np.arange(S) - y0) / max(YH - y0, 1), 0, 1)
    aur[below, x_] += (0.28 * (1 - depthfrac[below]) ** 1.6)               # fill veil
img += aur[..., None] * np.array([1.0, 0.80, 0.38])
# extension + deep-silence beads (float log|det| samples)
bead = np.zeros((S, S))
bead_pts = list(zip(ext_n, ext_ld))
try:
    bd = np.load('bigdet.npy')
    bead_pts += [(int(r[0]), r[2]) for r in bd if np.isfinite(r[2])]
except FileNotFoundError:
    pass
for n_, ld_ in bead_pts:
    bx, by = int(xpix(n_)), int(ypix_a(ld_ / n_))
    bead[by, bx] += 1
img += (gaussian_filter(bead, 4.0) * 260 + gaussian_filter(bead, 1.5) * 60)[..., None] * np.array([1.0, 0.85, 0.5])
# faint trend thread through the beads
bp = sorted(bead_pts)
bx = np.array([xpix(n_) for n_, _ in bp]); by = np.array([ypix_a(ld_/n_) for n_, ld_ in bp])
thread = np.zeros((S, S))
for k in range(len(bp)-1):
    L = int(max(abs(bx[k+1]-bx[k]), abs(by[k+1]-by[k]), 2))
    ts = np.linspace(0, 1, L*2)
    xs = (bx[k] + (bx[k+1]-bx[k])*ts).astype(int); ys = (by[k] + (by[k+1]-by[k])*ts).astype(int)
    ok = (xs>=0)&(xs<S)&(ys>=0)&(ys<S)
    np.add.at(thread, (ys[ok], xs[ok]), 0.5/L)
img += gaussian_filter(thread, 1.5)[..., None] * np.array([1.0, 0.85, 0.5]) * 120

# ---- verified mountains ----
mnt = np.zeros((S, S)); rim = np.zeros((S, S))
depth_col = np.zeros(S)
for n in range(1, 1301):
    if sing[n-1]:
        x_ = int(np.clip(xpix(n), 0, S-1))
        x2 = int(np.clip(xpix(n+1), 0, S-1))
        for xc in range(x_, max(x_+1, x2)):
            depth_col[xc] = max(depth_col[xc], dpix(corank[n-1]))
for x_ in np.where(depth_col > 0)[0]:
    d = depth_col[x_]
    ybot = YH + d
    inside = (np.arange(S) >= YH) & (np.arange(S) <= ybot)
    frac = np.clip((np.arange(S) - YH) / max(d, 1), 0, 1)
    mnt[inside, x_] += (0.30 + 0.55 * frac[inside] ** 1.4)
    rim[:, x_] += np.exp(-((np.arange(S) - ybot) / 2.4) ** 2) * 2.6
img += mnt[..., None] * np.array([0.10, 0.38, 0.44])
img += rim[..., None] * np.array([0.45, 0.95, 1.0])
# crystal ticks: actual kernel free columns per singular n
try:
    fc = np.load('freecols.npz')
    crys = np.zeros((S, S))
    for key in fc.files:
        n = int(key)
        cols = fc[key].astype(float)
        onset = 19 if n <= 256 else 259
        x_ = int(np.clip(xpix(n), 0, S-1))
        d = dpix(corank[n-1])
        yy_t = YH + d * (cols - onset) / max(n - onset, 1)
        yy_t = np.clip(yy_t, YH, YH + d)
        np.add.at(crys, (yy_t.astype(int), np.full(len(cols), x_)), 1.0)
    crysb = gaussian_filter(crys, 1.0)
    img += np.clip(crysb, 0, 1.5)[..., None] * np.array([0.55, 0.95, 1.0]) * 0.9
except FileNotFoundError:
    pass

# ---- phantom fourth mountain (conjecture) ----
q4 = 65536
gx0, gxp, gx1 = xpix(q4 + 3), xpix(3 * q4 // 2 - 1), xpix(2 * q4 - 4)
gd = dpix(q4 // 4 - 1)
ghost = np.zeros((S, S))
for x_ in range(int(gx0), min(int(gx1) + 1, S)):
    t = (x_ - gx0) / (gxp - gx0) if x_ <= gxp else 1 - (x_ - gxp) / (gx1 - gxp)
    d = gd * np.clip(t, 0, 1) ** 0.7
    ybot = YH + d
    inside = (np.arange(S) >= YH) & (np.arange(S) <= ybot)
    frac = np.clip((np.arange(S) - YH) / max(d, 1), 0, 1)
    ghost[inside, x_] += (0.10 + 0.22 * frac[inside] ** 1.3)
    ghost[:, x_] += np.exp(-((np.arange(S) - ybot) / 5.0) ** 2) * 0.5
ghost = gaussian_filter(ghost, 6.0)
img += ghost[..., None] * np.array([0.42, 0.36, 0.62])

# ---- silence glow: horizon haze across the whole axis ----
img += (np.exp(-np.abs(yy - YH) / (0.045 * S)))[..., None] * np.array([0.45, 0.42, 0.55]) * 0.10 * np.ones((1, S, 1))

# ---- horizon line ----
img += np.exp(-((yy - YH) / 1.6) ** 2)[..., None] * np.array([1.0, 0.9, 0.7]) * 0.45 * np.ones((1, S, 1))

# ---- miniature system marker: soft glow around [19,55] teeth ----
lum = img @ np.array([0.35, 0.5, 0.15])
img += fast_bloom(np.clip(lum - 0.75, 0, None), 16)[..., None] * np.array([0.9, 0.9, 1.0]) * 0.5
save(filmic(img, k=1.35, gamma=0.9), 'collapse_2560.png')
print('done')
