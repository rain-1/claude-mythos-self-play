"""The Families of Loss — subtract-a-prime-divisor game on a Sacks spiral.

Every losing position n <= N drawn at (r,theta) = (sqrt(n), 2*pi*sqrt(n)).
Winning positions are the void. Families:
  odd losses     — deep garnet carpet (dense: most odd composites lose)
  n = 2p         — steel-cyan dust      (prime-driven, thinning like 1/log)
  n = 4p         — heather-violet dust
  n = 2^k        — gold beacons
  wild           — ember-white heroes with halos (114 below 2^29; the game's
                   only true irregularity — all have <= 2 distinct odd primes)
"""
import sys, os
import numpy as np
from glow import splat_points, filmic, bloom
from scipy.ndimage import gaussian_filter
from PIL import Image

S     = int(sys.argv[1])   if len(sys.argv) > 1 else 1280
GAIN  = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
NSHOW = int(float(sys.argv[3])) if len(sys.argv) > 3 else 14_000_000
OUT   = sys.argv[4]        if len(sys.argv) > 4 else "proto/game_a.png"
SS    = 2
W = H = S * SS
cx = cy = (W - 1) / 2
RMAX = 0.478 * W

bits = np.fromfile("cache/losing.bits", dtype=np.uint8)
L = np.unpackbits(bits, bitorder="little")[: NSHOW + 1].astype(bool)
wild = np.loadtxt("cache/wild.txt", dtype=np.int64)[:, 0]
wild = wild[wild <= NSHOW]

# primality sieve up to NSHOW/2 for family tests
half = NSHOW // 2 + 2
isp = np.ones(half, bool); isp[:2] = False
for p in range(2, int(half ** 0.5) + 1):
    if isp[p]:
        isp[p * p::p] = False

n = np.arange(NSHOW + 1, dtype=np.int64)
lose = L.copy(); lose[0] = False; lose[1] = True
odd = (n & 1).astype(bool)
oddL = lose & odd
evenL = lose & ~odd
is2p = np.zeros_like(lose); m = evenL & (n % 2 == 0)
h2 = n[m] // 2
is2p[n[m][isp[h2]]] = True
is4p = np.zeros_like(lose); m4 = evenL & (n % 4 == 0) & ~is2p
h4 = n[m4] // 4
is4p[n[m4][isp[h4]]] = True
pow2 = np.zeros_like(lose)
k = 2
while k <= NSHOW:
    if lose[k]: pow2[k] = True
    k *= 2
wildm = np.zeros_like(lose); wildm[wild] = True
rest = evenL & ~is2p & ~is4p & ~pow2 & ~wildm   # should be empty!
print("family counts: oddL", oddL.sum(), "| 2p", is2p.sum(), "| 4p", is4p.sum(),
      "| 2^k", pow2.sum(), "| wild", wildm.sum(), "| unclassified even:", rest.sum())

def coords(idx):
    rt = np.sqrt(idx.astype(np.float64))
    scale = RMAX / np.sqrt(NSHOW)
    r = rt * scale
    th = 2 * np.pi * rt
    return cx + r * np.cos(th), cy + r * np.sin(th)

acc = np.zeros((H, W, 3), np.float32)
A = (W / 2560) ** 2   # area scaling for per-point mass

def splat_class(mask, color, wpt, star=0.0):
    idx = np.nonzero(mask)[0]
    if len(idx) == 0: return
    xs, ys = coords(idx)
    if star <= 0:
        for c in range(3):
            pass
        splat_points(acc, xs, ys, np.full(len(xs), wpt * A), np.array(color))
    else:
        # gaussian star sprite via temp accumulation then blur — do direct small kernel
        tmp = np.zeros((H, W), np.float32)
        ii = np.clip(ys.astype(int), 0, H - 1); jj = np.clip(xs.astype(int), 0, W - 1)
        np.add.at(tmp, (ii, jj), wpt * A)
        tmp = gaussian_filter(tmp, star * SS)
        tmp *= (wpt * A * len(idx)) / max(tmp.sum(), 1e-12) * 1.0
        for c in range(3):
            acc[:, :, c] += tmp * color[c]

splat_class(oddL, (0.42, 0.10, 0.10), 0.10)          # garnet carpet
splat_class(is2p, (0.55, 0.80, 1.00), 0.85)          # steel-cyan
splat_class(is4p, (0.75, 0.55, 1.00), 1.10)          # violet
# beacons & heroes with real halos
splat_class(pow2, (1.15, 0.85, 0.30), 550.0, star=2.2)
splat_class(wildm, (1.30, 0.95, 0.72), 1300.0, star=3.0)
# hot cores for heroes
splat_class(wildm, (1.5, 1.2, 1.0), 40.0, star=0.9)
splat_class(pow2, (1.4, 1.1, 0.5), 18.0, star=0.8)

img = filmic(acc, k=1.0, gamma=0.88)
img = bloom(img, mask_lo=0.5, sigma=5 * SS, gain=0.5)
os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
im8 = (np.clip(img, 0, 1) * 255).astype(np.uint8)
Image.fromarray(im8).resize((S, S), Image.LANCZOS).save(OUT)
print("saved", OUT)
