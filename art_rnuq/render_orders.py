"""render_orders.py — THE ORDER YOU TELL IT IN (Steinitz / Banaszczyk).
One closed polygon: n vectors of norm ≤ 1 in the plane summing to zero. Told in angle order it is a circle of
radius n/2π; told in m interleaved angle-blocks it is a rose of m circles of radius n/(2πm) through the origin;
told at random it is a Brownian loop of size ~√n; told in the balanced order (greedy + local search) it never
leaves a disc of radius 1 — Banaszczyk (1987): some order keeps every partial sum within √5/2, and √5/2 is sharp.
Coral = the circle of radius √5/2 at the origin; the inset magnifies the balanced knot.

usage: python3 render_orders.py FINAL n out_prefix
"""
import sys, json, time
import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image, ImageDraw
import pastel as P

FINAL = int(sys.argv[1]); n = int(sys.argv[2]); OUT = sys.argv[3]
SS = 2; W = H = FINAL * SS; rs = FINAL / 1024.0 * SS
t0 = time.time(); rng = np.random.default_rng(7)

# the polygon: equidistributed angles with jitter, mean removed, max norm 1
th = 2 * np.pi * (np.arange(n) + 0.5) / n + rng.normal(0, 0.35 * 2 * np.pi / n, n)
V = np.stack([np.cos(th), np.sin(th)], -1) * (0.85 + 0.15 * rng.random(n))[:, None]
V -= V.mean(0); V /= np.linalg.norm(V, axis=1).max()
ang = np.arctan2(V[:, 1], V[:, 0])
# start the angle order so the m = 1 circle sits straight above the origin: first vector points left (angle π)
srt = np.argsort(ang % (2 * np.pi))   # first vector points right; the walk turns left, so the circle rises

def path(order):
    return np.concatenate([[[0, 0]], np.cumsum(V[order], 0)])

def greedy(V):
    rem = np.ones(len(V), bool); S = np.zeros(2); order = []
    for _ in range(len(V)):
        cand = np.flatnonzero(rem); d = np.linalg.norm(S[None, :] + V[cand], axis=1)
        j = cand[np.argmin(d)]; order.append(j); S += V[j]; rem[j] = False
    return np.array(order)

def improve(order, iters, seed=1):
    r = np.random.default_rng(seed); order = order.copy()
    def score(o): return np.linalg.norm(np.cumsum(V[o], 0), axis=1).max()
    best = score(order)
    for _ in range(iters):
        i, j = r.integers(0, len(order), 2)
        o2 = order.copy(); o2[i], o2[j] = o2[j], o2[i]
        s = score(o2)
        if s <= best: best, order = s, o2
    return order, best

MS = [1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48]
ROT = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0   # radians of extra turn per rose
orders = {}
for m in MS:
    # block j = every m-th vector in angle order, started 2πj/m further round so its circle is rotated by 2πj/m
    blocks = []
    rot = ROT * (MS.index(m)) / (2 * np.pi)      # each rose turned a little further: the flower opens
    for j in range(m):
        b = srt[j::m]; blocks.append(np.roll(b, -int(round((j / m + rot) * len(b))) % len(b)))
    orders['m%d' % m] = np.concatenate(blocks)
orders['random'] = rng.permutation(n)
g = greedy(V); gi, best = improve(g, 40000)
orders['balanced'] = gi
paths = {k: path(o) for k, o in orders.items()}
maxS = {k: float(np.linalg.norm(p, axis=1).max()) for k, p in paths.items()}
for k in paths: print('%-9s max|S| = %8.3f' % (k, maxS[k]))
print('Banaszczyk sqrt(5)/2 = %.4f' % (5 ** 0.5 / 2), '[%.0fs]' % (time.time() - t0), flush=True)
assert maxS['balanced'] <= 5 ** 0.5 / 2 + 1e-9

# ---- page: origin at the centre, the m = 1 circle (radius r1 = n/2π) reaching the top
r1 = n / (2 * np.pi)
cx, cy = W / 2, 0.47 * H
scale = 0.42 * H / (2 * r1)    # the m=1 circle spans 2 r1 : from the origin up to the top margin
def to_px(p):
    return cx + scale * p[:, 0], cy - scale * p[:, 1]

sheet = P.Sheet(W, H, seed=31)
PIGS = ['cornflower', 'aqua', 'mint', 'pistachio', 'lemon', 'apricot', 'blush', 'orchid', 'lavender', 'cornflower', 'aqua']
# rose family: each ordering a thread; width thins with m; the pigment cycles through the box
for i, m in enumerate(MS):
    X, Y = to_px(paths['m%d' % m])
    wdt = (3.0 - 1.8 * i / (len(MS) - 1)) * rs
    dens = P.polyline_density(W, H, list(zip(X, Y)), wdt, sigma=0.45 * rs)
    # the petals as one glaze: the union of the m discs, pigment pooling toward the rim of the union
    im = Image.new('F', (W, H), 0.0); d_ = ImageDraw.Draw(im)
    d_.polygon(list(zip(X, Y)), fill=1.0)
    for j in range(m):
        seg = np.arange(j * (n // m), min(n, (j + 1) * (n // m) + 1))
        d_.polygon(list(zip(X[seg], Y[seg])), fill=1.0)
    glaze = gaussian_filter(np.asarray(im, np.float32), 1.5 * rs)
    edge = gaussian_filter(dens, 5 * rs) * 3.0
    sheet.wash(np.clip(glaze * (0.14 + 0.12 * np.clip(edge, 0, 1)), 0, 0.45), PIGS[i], granulate=0.3, seed=70 + i)
    sheet.wash(np.clip(dens, 0, 1) * 1.15, PIGS[i])
# random order: a Brownian loop in ink, thin
X, Y = to_px(paths['random'])
dens = P.polyline_density(W, H, list(zip(X, Y)), 1.8 * rs, sigma=0.4 * rs)
sheet.wash(np.clip(dens, 0, 1) * 1.2, 'ink')
# balanced knot at the origin: a dense disc of chords, ink, plus coral circle
X, Y = to_px(paths['balanced'])
dens = P.polyline_density(W, H, list(zip(X, Y)), 0.9 * rs, sigma=0.4 * rs)
sheet.wash(np.clip(dens, 0, 1) * 0.9, 'ink')
rc = 5 ** 0.5 / 2 * scale
circ = P.polyline_density(W, H, [(cx + rc * np.cos(a), cy + rc * np.sin(a)) for a in np.linspace(0, 2 * np.pi, 400)], 1.6 * rs, sigma=0.5 * rs)
sheet.wash(np.clip(circ, 0, 1) * 1.2, 'coral')

# ---- inset: the knot magnified, bottom-left corner
ix0, iy0 = 0.70 * W, 0.615 * H; iw = 0.255 * W
sc2 = iw * 0.40 / 1.25; icx, icy = ix0 + iw / 2, iy0 + iw / 2
box = np.zeros((H, W), np.float32); box[int(iy0):int(iy0 + iw), int(ix0):int(ix0 + iw)] = 1
sheet.lighten(gaussian_filter(box, 2 * rs), 0.85)
frame = P.polyline_density(W, H, [(ix0, iy0), (ix0 + iw, iy0), (ix0 + iw, iy0 + iw), (ix0, iy0 + iw)], 1.0 * rs, sigma=0.4 * rs, closed=True)
sheet.wash(np.clip(frame, 0, 1) * 0.6, 'ink')
pb = paths['balanced']
X2, Y2 = icx + sc2 * pb[:, 0], icy - sc2 * pb[:, 1]
# chords tinted by time: warm early, cool late (history as palette) — thin ink underneath
segs = np.stack([X2[:-1], Y2[:-1], X2[1:], Y2[1:]], -1)
tt = np.linspace(0, 1, len(segs))
for j, pig in enumerate(['apricot', 'blush', 'lavender', 'aqua']):
    wj = np.clip(1 - np.abs(tt * 3 - j), 0, 1)
    d_ = P.draw_lines_density(W, H, segs, 1.0 * rs, weights=wj, sigma=0.35 * rs)
    sheet.wash(np.clip(d_, 0, 1) * 0.9, pig)
rc2 = 5 ** 0.5 / 2 * sc2
circ2 = P.polyline_density(W, H, [(icx + rc2 * np.cos(a), icy + rc2 * np.sin(a)) for a in np.linspace(0, 2 * np.pi, 400)], 1.8 * rs, sigma=0.5 * rs)
sheet.wash(np.clip(circ2, 0, 1) * 1.3, 'coral')
inset_items = [('the balanced order, ×%d' % round(sc2 / scale), icx, iy0 + iw + 9 * rs, 12 * rs, 'italic', 'mt'),
               ('every partial sum inside r = %.3f < √5/2' % maxS['balanced'], icx, iy0 + iw + 26 * rs, 12 * rs, 'italic', 'mt')]
sheet.wash(P.text_density(W, H, inset_items) * 0.85, 'ink')

# captions
title = 'The Order You Tell It In'
sub = 'The same %d steps, summing to nothing. Told by angle they make a circle; told in m interleaved blocks, a rose of m circles; told at random, a wandering loop; told in the balanced order they never leave the coral circle of radius √5/2 — and some order always keeps them inside it.' % n
ts = 30 * rs; ss = 15 * rs
sheet.caption_strip(0.905, 0.995, 0.5)
lines = P.wrap(sub, ss, 'italic', 0.86 * W)
items = [(title, W / 2, 0.925 * H, ts, 'serif_bold', 'mm')]
for i, l in enumerate(lines):
    items.append((l, W / 2, 0.958 * H + i * 1.35 * ss, ss, 'italic', 'mm'))
sheet.wash(P.text_density(W, H, items), 'ink')
img = sheet.develop()
P.finish(img, (FINAL, FINAL), OUT + '_%d.png' % FINAL)
json.dump(dict(n=n, max_partial_sum=maxS, banaszczyk=5 ** 0.5 / 2, radius_m1=r1, block_ms=MS), open(OUT + '_%d_cert.json' % FINAL, 'w'), indent=1)
print('done [%.0fs]' % (time.time() - t0))
