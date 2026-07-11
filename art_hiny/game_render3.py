"""The Families of Loss v3 — octave spiral, calibrated luminance.

radius = log2(n), angle = 2*pi*frac(log2(n)); doubling = one ring out, same angle.
Layers: garnet odd-loss fog / cyan 2p / violet 4p / 2p->4p radial chains /
golden 2^k spine / wild embers. Per-octave mass is calibrated to ring area so
every octave reads at its intended luminance.
"""
import sys, os
import numpy as np
from glow import splat_points, splat_segments, filmic, bloom
from scipy.ndimage import gaussian_filter
from PIL import Image

S     = int(sys.argv[1])   if len(sys.argv) > 1 else 1280
GAIN  = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
OUT   = sys.argv[3]        if len(sys.argv) > 3 else "proto/game_c.png"
SS    = 2
W = H = S * SS
cx = cy = (W - 1) / 2
NMAX = 1 << 29
LG0, LG1 = 2.0, 29.0
R0, R1 = 0.050 * W, 0.475 * W
DR = (R1 - R0) / (LG1 - LG0)      # px per octave

bits = np.fromfile("cache/losing.bits", dtype=np.uint8)
L = np.unpackbits(bits, bitorder="little").astype(bool)
wild = np.loadtxt("cache/wild.txt", dtype=np.int64)[:, 0]
fam = np.load("cache/families.npz")
two_p, four_p = fam["two_p"], fam["four_p"]

def polar(nvals):
    lg = np.log2(nvals.astype(np.float64))
    r = R0 + DR * (lg - LG0)
    th = 2 * np.pi * (lg % 1.0)
    return cx + r * np.cos(th), cy - r * np.sin(th)

def ring_area(k):
    rmid = R0 + DR * (k + 0.5 - LG0)
    return 2 * np.pi * rmid * DR

def octave_calibrated_mass(nvals, level):
    """per-point weight so that Σ mass in octave k = level * ring_area(k)."""
    k = np.floor(np.log2(nvals.astype(np.float64))).astype(int)
    cnt = np.bincount(k, minlength=32).astype(np.float64)
    area = np.array([ring_area(kk) for kk in range(32)])
    return level * area[k] / np.maximum(cnt[k], 1)

acc = np.zeros((H, W, 3), np.float32)
rng = np.random.default_rng(5)

# ---- odd-loss fog --------------------------------------------------------------
FOG_COL = np.array([0.50, 0.115, 0.13])
CAP = 500_000
for k in range(2, 29):
    a, b = 1 << k, min(1 << (k + 1), NMAX)
    idx = np.arange(a | 1, b, 2, dtype=np.int64)
    idx = idx[L[idx]]
    if len(idx) == 0: continue
    keep = idx if len(idx) <= CAP else idx[rng.integers(0, len(idx), CAP)]
    xs, ys = polar(keep)
    wpt = 0.42 * GAIN * ring_area(k) / len(keep)
    splat_points(acc, xs, ys, np.full(len(keep), wpt), FOG_COL)
print("fog done")

# ---- families -------------------------------------------------------------------
xs, ys = polar(two_p)
splat_points(acc, xs, ys, octave_calibrated_mass(two_p, 0.60 * GAIN), np.array([0.50, 0.80, 1.10]))
xs, ys = polar(four_p)
splat_points(acc, xs, ys, octave_calibrated_mass(four_p, 0.45 * GAIN), np.array([0.80, 0.52, 1.10]))
print("families done")

# ---- 2p->4p chains (verified: every 4p loss has its 2p losing) -------------------
d2 = 2 * (four_p // 4); d4 = four_p
x0, y0 = polar(d2); x1, y1 = polar(d4)
# splat_segments spreads mass*length; normalize per octave via point-mass / length
seglen = np.hypot(x1 - x0, y1 - y0)
wch = octave_calibrated_mass(d4, 0.55 * GAIN) / np.maximum(seglen, 1)
splat_segments(acc, x0, y0, x1, y1, wch, np.array([0.60, 0.68, 1.05]))
print("chains done")

# ---- golden spine ----------------------------------------------------------------
pk = np.array([1 << k for k in range(2, 29) if L[1 << k]], dtype=np.int64)
xs, ys = polar(pk)
tmp = np.zeros((H, W), np.float32)
np.add.at(tmp, (np.clip(ys.astype(int), 0, H - 1), np.clip(xs.astype(int), 0, W - 1)), 1.0)
b1 = gaussian_filter(tmp, 1.1 * SS); b1 /= max(b1.max(), 1e-9)
b2 = gaussian_filter(tmp, 3.5 * SS); b2 /= max(b2.max(), 1e-9)
for c, v in enumerate((1.35, 1.05, 0.45)):
    acc[:, :, c] += b1 * v * 1.6 * GAIN
for c, v in enumerate((1.10, 0.75, 0.25)):
    acc[:, :, c] += b2 * v * 0.9 * GAIN

# ---- wild embers -------------------------------------------------------------------
xs, ys = polar(wild)
tmp = np.zeros((H, W), np.float32)
np.add.at(tmp, (np.clip(ys.astype(int), 0, H - 1), np.clip(xs.astype(int), 0, W - 1)), 1.0)
halo = gaussian_filter(tmp, 3.4 * SS); halo /= max(halo.max(), 1e-9)
core = gaussian_filter(tmp, 1.0 * SS); core /= max(core.max(), 1e-9)
for c, v in enumerate((1.35, 0.55, 0.22)):
    acc[:, :, c] += halo * v * 2.6 * GAIN
for c, v in enumerate((1.55, 1.20, 0.90)):
    acc[:, :, c] += core * v * 2.0 * GAIN

print("acc mean lum:", float(acc.mean()))
img = filmic(acc, k=1.0, gamma=0.88)
img = bloom(img, mask_lo=0.5, sigma=5 * SS, gain=0.55)
os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
im8 = (np.clip(img, 0, 1) * 255).astype(np.uint8)
Image.fromarray(im8).resize((S, S), Image.LANCZOS).save(OUT)
print("saved", OUT)
