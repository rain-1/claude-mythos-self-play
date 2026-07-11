"""The Families of Loss v4 — octave spiral with exact run-arc fog.

Odd losses drawn as maximal runs of consecutive odd losers -> spiral arcs
whose BREAKS are exactly the odd winners (primes, 3p/5p shifts, wild-fed).
The carpet of loss is woven with prime-shaped holes. No subsampling.
"""
import sys, os
import numpy as np
from glow import splat_points, splat_segments, filmic, bloom
from scipy.ndimage import gaussian_filter
from PIL import Image

S     = int(sys.argv[1])   if len(sys.argv) > 1 else 1280
GAIN  = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
OUT   = sys.argv[3]        if len(sys.argv) > 3 else "proto/game_d.png"
SS    = 2
W = H = S * SS
cx = cy = (W - 1) / 2
NMAX = 1 << 29
LG0, LG1 = 2.0, 29.0
R0, R1 = 0.050 * W, 0.475 * W
DR = (R1 - R0) / (LG1 - LG0)

bits = np.fromfile("cache/losing.bits", dtype=np.uint8)
L = np.unpackbits(bits, bitorder="little").astype(bool)
wild = np.loadtxt("cache/wild.txt", dtype=np.int64)[:, 0]
fam = np.load("cache/families.npz")
two_p, four_p = fam["two_p"], fam["four_p"]

def polar_xy(nvals):
    lg = np.log2(nvals.astype(np.float64))
    r = R0 + DR * (lg - LG0)
    th = 2 * np.pi * (lg % 1.0)
    return cx + r * np.cos(th), cy - r * np.sin(th)

def ring_area(k):
    return 2 * np.pi * (R0 + DR * (k + 0.5 - LG0)) * DR

acc = np.zeros((H, W, 3), np.float32)

# ---- odd-loss run arcs ---------------------------------------------------------
oddL = L[1::2]                       # index i -> n = 2i+1
d = np.diff(oddL.astype(np.int8))
starts = np.nonzero(d == 1)[0] + 1
ends = np.nonzero(d == -1)[0] + 1    # exclusive
if oddL[0]: starts = np.concatenate([[0], starts])
if oddL[-1]: ends = np.concatenate([ends, [len(oddL)]])
ns = 2 * starts + 1                  # first n of run
ne = 2 * (ends - 1) + 1              # last n of run
runlen = (ends - starts).astype(np.float64)
print("odd-loss runs:", len(ns), " total odd losses:", int(runlen.sum()))

k_run = np.floor(np.log2(ns.astype(np.float64))).astype(int)
k_run = np.clip(k_run, 0, 31)
cnt_per_oct = np.bincount(k_run, weights=runlen, minlength=32)
area = np.array([ring_area(kk) for kk in range(32)])
LVL_FOG = 0.34 * GAIN
mass_run = LVL_FOG * area[k_run] / np.maximum(cnt_per_oct[k_run], 1) * runlen
FOG_COL = np.array([0.52, 0.115, 0.125])

# split runs: long arcs (inner) need subdivision; chords fine when dtheta small
dlg = np.log2(ne.astype(np.float64) + 2) - np.log2(ns.astype(np.float64))
big = dlg > 0.004        # ~1.4 deg
# small runs as single chords
x0, y0 = polar_xy(ns[~big]); x1, y1 = polar_xy(ne[~big] + 0.999)
sl = np.hypot(x1 - x0, y1 - y0)
splat_segments(acc, x0, y0, x1, y1, mass_run[~big] / np.maximum(sl, 0.7), FOG_COL)
print("chord runs done:", (~big).sum())
# big runs subdivided along the true spiral
ib = np.nonzero(big)[0]
bx0 = []; by0 = []; bx1 = []; by1 = []; bw = []
for i in ib:
    npt = int(dlg[i] * 1200) + 2
    nn = np.exp2(np.linspace(np.log2(ns[i]), np.log2(ne[i] + 0.999), npt))
    xs, ys = polar_xy(nn)
    seg = np.hypot(np.diff(xs), np.diff(ys))
    bx0.append(xs[:-1]); by0.append(ys[:-1]); bx1.append(xs[1:]); by1.append(ys[1:])
    bw.append(np.full(npt - 1, mass_run[i] / max(seg.sum(), 0.7)))
if bx0:
    splat_segments(acc, np.concatenate(bx0), np.concatenate(by0),
                   np.concatenate(bx1), np.concatenate(by1),
                   np.concatenate(bw), FOG_COL)
print("long arc runs done:", len(ib))

# ---- families --------------------------------------------------------------------
def octave_calibrated_mass(nvals, level):
    k = np.floor(np.log2(nvals.astype(np.float64))).astype(int)
    cnt = np.bincount(k, minlength=32).astype(np.float64)
    return level * area[k] / np.maximum(cnt[k], 1)

xs, ys = polar_xy(two_p)
splat_points(acc, xs, ys, octave_calibrated_mass(two_p, 0.34 * GAIN), np.array([0.42, 0.78, 1.15]))
xs, ys = polar_xy(four_p)
splat_points(acc, xs, ys, octave_calibrated_mass(four_p, 0.22 * GAIN), np.array([0.80, 0.50, 1.15]))

# chains 2p -> 4p (radial steel hatch)
d4 = four_p; d2 = 2 * (four_p // 4)
x0, y0 = polar_xy(d2); x1, y1 = polar_xy(d4)
sl = np.hypot(x1 - x0, y1 - y0)
wch = octave_calibrated_mass(d4, 0.20 * GAIN) / np.maximum(sl, 1)
splat_segments(acc, x0, y0, x1, y1, wch, np.array([0.55, 0.65, 1.10]))
print("families+chains done")

# ---- golden spine -----------------------------------------------------------------
pk = np.array([1 << k for k in range(2, 29) if L[1 << k]], dtype=np.int64)
xs, ys = polar_xy(pk)
tmp = np.zeros((H, W), np.float32)
np.add.at(tmp, (np.clip(ys.astype(int), 0, H - 1), np.clip(xs.astype(int), 0, W - 1)), 1.0)
b1 = gaussian_filter(tmp, 1.1 * SS); b1 /= max(b1.max(), 1e-9)
b2 = gaussian_filter(tmp, 3.5 * SS); b2 /= max(b2.max(), 1e-9)
for c, v in enumerate((1.35, 1.05, 0.45)):
    acc[:, :, c] += b1 * v * 1.5 * GAIN
for c, v in enumerate((1.10, 0.75, 0.25)):
    acc[:, :, c] += b2 * v * 0.8 * GAIN

# ---- wild embers ---------------------------------------------------------------------
xs, ys = polar_xy(wild)
tmp = np.zeros((H, W), np.float32)
np.add.at(tmp, (np.clip(ys.astype(int), 0, H - 1), np.clip(xs.astype(int), 0, W - 1)), 1.0)
halo = gaussian_filter(tmp, 3.4 * SS); halo /= max(halo.max(), 1e-9)
core = gaussian_filter(tmp, 1.0 * SS); core /= max(core.max(), 1e-9)
for c, v in enumerate((1.35, 0.55, 0.22)):
    acc[:, :, c] += halo * v * 2.4 * GAIN
for c, v in enumerate((1.55, 1.20, 0.90)):
    acc[:, :, c] += core * v * 1.9 * GAIN

print("acc mean lum:", float(acc.mean()))
img = filmic(acc, k=1.0, gamma=0.88)
img = bloom(img, mask_lo=0.55, sigma=5 * SS, gain=0.5)
os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
im8 = (np.clip(img, 0, 1) * 255).astype(np.uint8)
Image.fromarray(im8).resize((S, S), Image.LANCZOS).save(OUT)
print("saved", OUT)
