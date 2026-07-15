"""COMPANION A — 'The Cloth' — a Conway–Coxeter frieze woven as a flat band.

A random triangulation of an n-gon; its quiddity row (triangle counts at each
vertex) seeds a frieze: every 2x2 diamond obeys ad - bc = 1, and the
Conway–Coxeter theorem forces every entry to be a positive integer, closes
the cloth with a second row of 1s, and imposes glide symmetry with period n.
Interior entries equal 1 EXACTLY at the diagonals of the triangulation
(verified): the cyan lightning in the cloth IS the triangulation, woven.
One full period (n columns x n-1 rows — nearly square) fills the canvas;
the generating triangulated polygon glows as a seal in the corner.
"""
import sys, math, time
import numpy as np
from fractions import Fraction
sys.path.insert(0, '.')
from kit import *

t0 = time.time()
S   = int(sys.argv[1]) if len(sys.argv) > 1 else 1024
TAG = sys.argv[2] if len(sys.argv) > 2 else 'proto'
SS  = 2
R   = S * SS
RSCALE = R / 2048

N    = 56
SEED = 9

GOLD  = hex_rgb('ffd27a'); GOLD2 = hex_rgb('ffc457')
CYAN  = hex_rgb('7fd8e8')
WHITE = np.array([1.0, 0.96, 0.86], np.float32)
KNOT_PAL = [(0.00, hex_rgb('6b3418')), (0.35, hex_rgb('c96f2e')),
            (0.70, hex_rgb('f2bd6f')), (1.00, hex_rgb('fff3d0'))]

rng = np.random.default_rng(SEED)

# ------------------------------------------------------------- triangulation
def random_triangulation(n, rng):
    tris = []
    def rec(poly):
        if len(poly) == 3:
            tris.append(tuple(poly)); return
        if len(poly) < 3:
            return
        k = int(rng.integers(1, len(poly) - 1))
        tris.append((poly[0], poly[k], poly[-1]))
        rec(poly[:k + 1])
        rec(poly[k:])
    rec(list(range(n)))
    return tris

tris = random_triangulation(N, rng)
assert len(tris) == N - 2
quid = [0] * N
for t in tris:
    for v in t:
        quid[v] += 1

diagset = set()
for t in tris:
    for a, b in ((t[0], t[1]), (t[1], t[2]), (t[0], t[2])):
        a, b = min(a, b), max(a, b)
        if (b - a) % N not in (1, N - 1):
            diagset.add((a, b))

# ------------------------------------------------------------- frieze
W = N - 3
rows = [[Fraction(1)] * N, [Fraction(q) for q in quid]]
for r in range(1, W + 1):
    prev, cur = rows[r - 1], rows[r]
    rows.append([(cur[i] * cur[(i + 1) % N] - 1) / prev[(i + 1) % N] for i in range(N)])

assert all(v == 1 for v in rows[-1]), 'closure row of 1s'
assert all(v.denominator == 1 and v > 0 for row in rows for v in row), 'positive integers'
for r in range(1, len(rows) - 1):
    for i in range(N):
        assert rows[r][i] * rows[r][(i + 1) % N] - rows[r - 1][(i + 1) % N] * rows[r + 1][i] == 1, 'diamond'
ones = set()
for r in range(1, len(rows) - 1):
    for i in range(N):
        if rows[r][i] == 1:
            a = (i - 1) % N
            b = (i + r) % N
            ones.add((min(a, b), max(a, b)))
assert ones == diagset, '1-cells <-> diagonals bijection'
maxm = max(int(v) for row in rows for v in row)
print(f'frieze verified: n={N}, width={W}, max entry={maxm}, 1-cells==diagonals ({len(ones)})')

M = np.array([[float(v) for v in row] for row in rows])   # (NR, N)
NR = len(rows)

# ------------------------------------------------------------- flat band layout
MARG_X = 0.045 * R
MARG_Y = 0.075 * R
BW = R - 2 * MARG_X
BH = R - 2 * MARG_Y
cellw = BW / N
cellh = BH / (NR - 1)
PHASE = 0.0

def cell_xy(r, i):
    """diamond lattice: adjacent rows offset half a column; wraps mod N."""
    xcol = (i + 0.5 * (r - 1) + PHASE) % N
    return MARG_X + xcol * cellw, MARG_Y + r * cellh

logm = np.log2(M)
tval = np.clip(logm / max(np.log2(maxm), 1), 0, 1)

L_thr  = canvas_mono(R)
L_knot = canvas(R)
L_one  = canvas(R)

# ---- threads: two diagonal families, drawn as continuous strands (wrap-aware)
def draw_thread_seg(x1, y1, x2, y2, t1, t2, family):
    # skip wrap jumps
    if abs(x2 - x1) > 0.6 * BW:
        return
    Lpx = math.hypot(x2 - x1, y2 - y1)
    n = max(6, int(Lpx * 1.1))
    tt = np.linspace(0, 1, n)
    xs = x1 + (x2 - x1) * tt
    ys = y1 + (y2 - y1) * tt
    ws = 0.08 + 2.4 * (t1 + (t2 - t1) * tt) ** 1.35
    splat_points_mono(L_thr, R, xs, ys, ws * (Lpx / n) * 0.15)

for di in (0, -1):
    for i0 in range(N):
        i = i0
        prev = None
        for r in range(NR):
            cur = (*cell_xy(r, i), tval[r, i % N])
            if prev is not None:
                draw_thread_seg(prev[0], prev[1], cur[0], cur[1], prev[2], cur[2], di)
            prev = cur
            i += di

print(f'threads done t={time.time()-t0:.0f}s', flush=True)

# ---- knots: soft diamond glow per cell, brightness by log entry
th48 = np.linspace(0, 2 * math.pi, 48, endpoint=False)
ps = SS * RSCALE
for r in range(NR):
    for i in range(N):
        x, y = cell_xy(r, i)
        t = tval[r, i]
        col = lerp_palette(KNOT_PAL, np.array([t]))[0]
        base = (0.12 + 11.0 * t ** 1.55) * ps
        # soft rhombus: rings of points squashed into diamond orientation
        for frac, ww in ((0.0, 0.45), (0.45, 0.30), (0.9, 0.16), (1.5, 0.07)):
            rad = frac * 3.0 * ps
            dx = rad * np.cos(th48); dy = rad * np.sin(th48)
            # rotate 45 deg and squash -> diamond-ish footprint
            qx = (dx - dy) * 0.78
            qy = (dx + dy) * 0.5
            splat_points(L_knot, x + qx, y + qy, base * ww / 48, col)
        if 0 < r < NR - 1 and M[r, i] == 1:
            for rad, ww in ((0.0, 9.0), (1.7 * ps, 4.5), (3.6 * ps, 1.8), (5.6 * ps, 0.7)):
                splat_points(L_one, x + rad * np.cos(th48), y + rad * np.sin(th48),
                             ww * ps / 48, CYAN)

print(f'knots done t={time.time()-t0:.0f}s', flush=True)

# ---- the two rims of 1s: continuous silver-gold threads
for r in (0, NR - 1):
    y = MARG_Y + r * cellh
    xs = np.linspace(MARG_X - 0.01 * R, R - MARG_X + 0.01 * R, int(BW * 1.3))
    splat_points(L_one, xs, np.full_like(xs, y), 0.30, WHITE * 0.8)

# ------------------------------------------------------------- polygon seal
sealR = 0.128 * R
sx, sy = R - MARG_X - sealR * 1.28, R - MARG_Y - sealR * 1.30
ang = 2 * math.pi * np.arange(N) / N + 0.35
vx = sx + sealR * np.cos(ang)
vy = sy - sealR * np.sin(ang)

def draw_seg(L, x1, y1, x2, y2, mass_per_px, col):
    Lpx = math.hypot(x2 - x1, y2 - y1)
    n = max(4, int(Lpx * 1.4))
    tt = np.linspace(0, 1, n)
    splat_points(L, x1 + (x2 - x1) * tt, y1 + (y2 - y1) * tt, mass_per_px * Lpx / n, col)

for (a, b) in diagset:
    draw_seg(L_one, vx[a], vy[a], vx[b], vy[b], 0.55, CYAN * 0.6)
for i in range(N):
    j = (i + 1) % N
    draw_seg(L_one, vx[i], vy[i], vx[j], vy[j], 1.1, GOLD)
for i in range(N):
    b = (0.4 + 0.22 * quid[i]) * ps
    splat_points(L_one, vx[i] + b * 0.9 * np.cos(th48), vy[i] + b * 0.9 * np.sin(th48),
                 1.3 * ps / 48, GOLD2)

print(f'seal done t={time.time()-t0:.0f}s', flush=True)

# ------------------------------------------------------------- compose
from scipy.ndimage import gaussian_filter as _gf
def fatten(L, amt):
    sig = 0.85 * SS * max(1.0, RSCALE)
    return L + amt * _gf(L, (sig, sig, 0))
L_knot = fatten(L_knot, 0.55)
L_one  = fatten(L_one, 0.60)
def norm99(L):
    v = L.mean(2)
    p = np.percentile(v[v > 0], 99.2) if (v > 0).any() else 1.0
    return L / max(p, 1e-9)

def norm99m(Lm):
    v = Lm[Lm > 0]
    p = np.percentile(v, 99.2) if v.size else 1.0
    return (Lm / max(p, 1e-9)).reshape(R, R)

img = (0.52 * norm99m(L_thr)[..., None] * (GOLD[None, None, :] * 0.82)
       + 1.55 * norm99(L_knot)
       + 1.55 * norm99(L_one))

img = bloom_add(img, tight=max(2, 0.0015 * R), wide=0.030 * R, t_amt=0.45, w_amt=0.20, thresh=0.7)
u8 = tonemap(img, k=1.9 * (0.72 + 0.28 * max(1.0, RSCALE)), gamma=0.78, sat=1.12)
from PIL import Image
Image.fromarray(u8).resize((S, S), Image.LANCZOS).save(f'frieze_{TAG}.png')
print(f'saved frieze_{TAG}.png t={time.time()-t0:.0f}s')
