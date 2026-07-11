"""The Families of Loss v2 — octave spiral (the clock of doubling).

Chart: radius = log2(n) (one ring per octave), angle = 2*pi*frac(log2(n)).
Multiplication by 2 = step one ring outward at the SAME angle. Hence:
  - the 2^k losses line up on a single golden ray (the spine),
  - each prime p with L(2p) and L(4p) yields a radial dash 2p -> 4p,
  - wild losses are ember stars off the law-lines,
  - odd losses are the garnet fog that owns the field.
Full data to 2^29 (the MO poster's exact range), verified census.
"""
import sys, os
import numpy as np
from glow import splat_points, splat_segments, filmic, bloom
from scipy.ndimage import gaussian_filter
from PIL import Image

S     = int(sys.argv[1])   if len(sys.argv) > 1 else 1280
GAIN  = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
OUT   = sys.argv[3]        if len(sys.argv) > 3 else "proto/game_b.png"
FOGK  = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0
SS    = 2
W = H = S * SS
cx = cy = (W - 1) / 2
NMAX = 1 << 29
LG0, LG1 = 2.0, 29.0
R0, R1 = 0.045 * W, 0.475 * W

bits = np.fromfile("cache/losing.bits", dtype=np.uint8)
L = np.unpackbits(bits, bitorder="little").astype(bool)   # index by n
wild = np.loadtxt("cache/wild.txt", dtype=np.int64)[:, 0]

def polar(nvals):
    lg = np.log2(nvals.astype(np.float64))
    r = R0 + (R1 - R0) * (lg - LG0) / (LG1 - LG0)
    th = 2 * np.pi * (lg % 1.0)
    return cx + r * np.cos(th), cy - r * np.sin(th), r, th

acc = np.zeros((H, W, 3), np.float32)
AREA = (W / 2560) ** 2

# ---- odd-loss fog: constant mass per octave, subsampled ---------------------
rng = np.random.default_rng(5)
FOG_M = FOGK * 9.0 * AREA          # total fog mass per octave
FOG_COL = np.array([0.46, 0.11, 0.12])
CAP = 400_000
for k in range(int(LG0), 29):
    a, b = 1 << k, min((1 << (k + 1)), NMAX)
    idx = np.arange(a | 1, b, 2, dtype=np.int64)
    idx = idx[L[idx]]
    cnt = len(idx)
    if cnt == 0: continue
    if cnt > CAP:
        idx = idx[rng.integers(0, cnt, CAP)]
    xs, ys, _, _ = polar(idx)
    wpt = FOG_M / len(idx)
    splat_points(acc, xs, ys, np.full(len(idx), wpt), FOG_COL)

# ---- 2p / 4p families --------------------------------------------------------
half = NMAX // 2 + 2
isp = np.ones(half, bool); isp[:2] = False
for p in range(2, int(half ** 0.5) + 1):
    if isp[p]: isp[p * p::p] = False
print("prime sieve done")

# collect 2p losses
p_all = np.nonzero(isp)[0].astype(np.int64)          # primes up to 2^28
n2 = 2 * p_all
n2 = n2[n2 < NMAX]
m2 = L[n2]
two_p = n2[m2]                                        # 2p losses
p4 = p_all[p_all < NMAX // 4]
n4 = 4 * p4
m4 = L[n4]
four_p = n4[m4]
print("2p losses:", len(two_p), " 4p losses:", len(four_p))

# family mass: constant per octave => wpt ∝ 1/(count in its octave)
def octave_mass(nvals, total_per_oct):
    k = np.floor(np.log2(nvals.astype(np.float64))).astype(int)
    cnt = np.bincount(k, minlength=30)
    return total_per_oct / np.maximum(cnt[k], 1)

M2 = 30.0 * AREA * GAIN
xs, ys, _, _ = polar(two_p)
splat_points(acc, xs, ys, octave_mass(two_p, M2), np.array([0.55, 0.82, 1.05]))
xs, ys, _, _ = polar(four_p)
splat_points(acc, xs, ys, octave_mass(four_p, M2 * 0.8), np.array([0.78, 0.55, 1.05]))

# ---- radial dashes where BOTH 2p and 4p lose ---------------------------------
both = np.intersect1d(two_p, four_p // 2 * 0 + four_p)  # dummy to keep shape
p_both = np.intersect1d(two_p // 2, four_p // 4)
d2 = 2 * p_both; d4 = 4 * p_both
x0, y0, _, _ = polar(d2)
x1, y1, _, _ = polar(d4)
wd = octave_mass(d2, 12.0 * AREA * GAIN) * 0.05
splat_segments(acc, x0, y0, x1, y1, wd, np.array([0.62, 0.72, 1.0]))
print("2p&4p chains:", len(p_both))

# ---- golden spine: 2^k ---------------------------------------------------------
pk = np.array([1 << k for k in range(2, 29) if L[1 << k]], dtype=np.int64)
xs, ys, _, _ = polar(pk)
tmp = np.zeros((H, W), np.float32)
np.add.at(tmp, (np.clip(ys.astype(int), 0, H - 1), np.clip(xs.astype(int), 0, W - 1)), 1.0)
tmp = gaussian_filter(tmp, 2.0 * SS)
tmp /= max(tmp.max(), 1e-9)
for c, v in enumerate((1.15, 0.85, 0.30)):
    acc[:, :, c] += tmp * v * 2.6 * GAIN
# spine ray (very faint golden radius at angle 0)
rr = np.linspace(R0, R1, 400)
splat_segments(acc, cx + rr[:-1], np.full(399, cy), cx + rr[1:], np.full(399, cy),
               np.full(399, 0.05 * AREA * GAIN), np.array([1.0, 0.8, 0.35]))

# ---- wild embers ----------------------------------------------------------------
xs, ys, _, _ = polar(wild)
tmp = np.zeros((H, W), np.float32)
np.add.at(tmp, (np.clip(ys.astype(int), 0, H - 1), np.clip(xs.astype(int), 0, W - 1)), 1.0)
halo = gaussian_filter(tmp, 3.2 * SS); halo /= max(halo.max(), 1e-9)
core = gaussian_filter(tmp, 1.0 * SS); core /= max(core.max(), 1e-9)
for c, v in enumerate((1.30, 0.62, 0.28)):
    acc[:, :, c] += halo * v * 3.0 * GAIN
for c, v in enumerate((1.5, 1.15, 0.85)):
    acc[:, :, c] += core * v * 2.2 * GAIN

img = filmic(acc, k=1.0, gamma=0.88)
img = bloom(img, mask_lo=0.5, sigma=5 * SS, gain=0.55)
os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
im8 = (np.clip(img, 0, 1) * 255).astype(np.uint8)
Image.fromarray(im8).resize((S, S), Image.LANCZOS).save(OUT)
print("saved", OUT)
