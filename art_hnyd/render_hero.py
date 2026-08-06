"""HERO 4096x4096: 'The Last to Settle' — one random binary matrix alternately
row/column sorted into double lexicographic order (MO 513971). Pixel-native:
1 cell = 1 pixel. Each cell lit by the pass at which it last changed."""
import numpy as np
from scipy.ndimage import gaussian_filter
from artlib import save, bake_text, star
import sys

S = 4096
z = np.load("hero_trace.npz")
Af = z['A_final'].astype(np.float32)
lc = z['last_change']
cc = z['change_count']
perm_kinds = z['perm_kinds']
perm_arrays = z['perm_arrays']
T = int(z['T'])

# ---------------- layers ----------------
buf = np.zeros((S, S, 3), np.float32)

# ground: settled matrix duotone (very dark; the doubly-sorted shores show)
g0 = np.array([0.012, 0.015, 0.034], np.float32)
g1 = np.array([0.046, 0.054, 0.096], np.float32)
buf += g0[None, None, :] + Af[:, :, None] * (g1 - g0)[None, None, :]

# strata palette (cold -> blazing), per-stratum ink budget ~ count^-0.8
cols = {
    1: (0.09, 0.11, 0.30),
    2: (0.15, 0.13, 0.46),
    3: (0.30, 0.15, 0.44),
    4: (0.62, 0.20, 0.26),
    5: (0.98, 0.44, 0.10),
    6: (1.00, 0.84, 0.38),
}
counts = {t: int((lc == t).sum()) for t in range(1, T + 1)}
ref = counts[6] ** 0.65
AMP6 = float(sys.argv[1]) if len(sys.argv) > 1 else 1.10
hot = np.zeros((S, S, 3), np.float32)
restw = (0.45 + 0.55 * cc.astype(np.float32) / T)   # restlessness modulation
for t in range(1, T + 1):
    amp = AMP6 * ref / counts[t] ** 0.65
    if t == 5:
        amp *= 1.7
    if t == 4:
        amp *= 1.3
    m = (lc == t).astype(np.float32) * restw
    c = np.asarray(cols[t], np.float32) * amp
    target = hot if t >= 5 else buf
    for ch in range(3):
        target[..., ch] += m * c[ch]
del m, restw

# restless cells (changed at every pass): white-gold stars
ys, xs = np.nonzero(cc == T)
print(f"restless cells: {len(xs)}")
starbuf = np.zeros((S, S, 3), np.float32)
for x, y in zip(xs, ys):
    star(starbuf, x, y, (1.0, 0.95, 0.80), amp=0.9, rad=2.2)

# final act: pass-6 is 22 adjacent-pair column swaps -> gold stitch knots at top
p6 = perm_arrays[5]
moved = np.nonzero(p6 != np.arange(S))[0]
print(f"pass-6 moved columns: {len(moved)}, max |move| = {int(np.abs(p6[moved]-moved).max())}")
arcbuf = np.zeros((S, S, 3), np.float32)
from artlib import polyline
pairs = [int(j) for j in moved if p6[j] == j + 1]      # left member of each swap
print(f"adjacent swaps: {len(pairs)}")
for j in pairs:
    xc = j + 0.5
    # stitch knot: a small loop (like thread tied off) at the top of the pair
    th = np.linspace(0, 2 * np.pi, 60)
    xs_a = xc + 11 * np.sin(th)
    ys_a = 46 - 30 * np.cos(th) - 8 * np.sin(2 * th)
    polyline(arcbuf, np.stack([xs_a, ys_a], 1), (1.0, 0.86, 0.44), amp=1.5)
    star(arcbuf, xc, 46, (1.0, 0.92, 0.60), amp=0.9, rad=2.2)

# pass-5 rows: same knots on the left edge (adjacent-pair swaps dominate)
p5 = perm_arrays[4]
mv5 = np.nonzero(p5 != np.arange(S))[0]
pairs5 = [int(i) for i in mv5 if p5[i] == i + 1]
print(f"pass-5 adjacent swaps: {len(pairs5)} of {len(mv5)} moved rows")
for i in pairs5[:]:
    yc = i + 0.5
    polyline(arcbuf, np.array([[16.0, yc], [40.0, yc]]), (0.97, 0.52, 0.18), amp=0.38)

# honest macro field: local density of late activity (passes >= 4), sigma 64
late = ((lc >= 4).astype(np.float32))
ls_small = gaussian_filter(late[::8, ::8], 8.0)
ls = np.kron(ls_small, np.ones((8, 8), np.float32))
ls /= max(ls.max(), 1e-9)
mod = (0.80 + 0.55 * ls)[:, :, None].astype(np.float32)
buf *= mod
del late, ls_small, ls, mod

# ---------------- compose + bloom ----------------
# hot layer: tight glow + wide soft glow (downsampled path to save RAM)
hb = np.empty_like(hot)
for ch in range(3):
    hb[..., ch] = gaussian_filter(hot[..., ch], 1.4)
buf += hot + 0.9 * hb
for ch in range(3):
    small = hot[::4, ::4, ch]
    wide = gaussian_filter(small, 3.0)
    buf[..., ch] += 0.35 * np.kron(wide, np.ones((4, 4), np.float32))
del hot, hb

sb = np.empty_like(starbuf)
for ch in range(3):
    sb[..., ch] = gaussian_filter(starbuf[..., ch], 3.0)
buf += starbuf + 1.1 * sb
del starbuf, sb

ab = np.empty_like(arcbuf)
for ch in range(3):
    ab[..., ch] = gaussian_filter(arcbuf[..., ch], 2.0)
buf += arcbuf + 0.8 * ab
del arcbuf, ab

# filmic tone map
img = 1.0 - np.exp(-1.70 * np.clip(buf, 0, None))
img = np.clip(img, 0, 1) ** 0.90
del buf

# ---------------- caption ----------------
texts = [
    (110, S - 300, "THE  LAST  TO  SETTLE", 74, (0.92, 0.88, 0.78), True, "ls"),
    (110, S - 210, "one 4096 x 4096 random binary matrix, rows and columns alternately sorted into double lexicographic order  (MO 513971)", 40, (0.62, 0.60, 0.58), False, "ls"),
    (110, S - 150, "settled after T = 6 sorts   -   each pixel lit by the pass in which it last changed   -   the final sort is 22 adjacent swaps of near-identical columns (gold stitches)", 40, (0.62, 0.60, 0.58), False, "ls"),
    (110, S - 90, "129 restless cells changed in every pass (white stars)   -   exact:  E[T](5) = 36573599 / 2^25,  worst case 2n-3 verified n <= 5", 40, (0.50, 0.48, 0.46), False, "ls"),
]
img = bake_text(img, texts, S)
save(img, "settle_4096.png", dither=True)
print("saved settle_4096.png")
