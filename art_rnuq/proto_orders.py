"""proto_orders.py — one closed polygon (n vectors of norm ≤ 1 summing to zero) told in several orders:
partial-sum paths for angle-sorted, block-interleaved, van der Corput, random, greedy-balanced.
Quick grey/colour look with PIL. Prints max |partial sum| per ordering (Banaszczyk: best ≤ √5/2 in the plane)."""
import numpy as np
from PIL import Image, ImageDraw
n = 600
rng = np.random.default_rng(7)
th = rng.uniform(0, 2 * np.pi, n)
V = np.stack([np.cos(th), np.sin(th)], -1)
V -= V.mean(0); V /= np.linalg.norm(V, axis=1).max()
ang = np.arctan2(V[:, 1], V[:, 0])
order_sorted = np.argsort(ang)

def vdc(k, base=2):
    out = np.zeros(len(k)); f = 1.0 / base; i = k.astype(int).copy()
    while i.max() > 0:
        out += f * (i % base); i //= base; f /= base
    return out

def greedy(V):
    rem = list(range(len(V))); S = np.zeros(2); order = []
    while rem:
        cand = np.array(rem); d = np.linalg.norm(S[None, :] + V[cand], axis=1)
        j = cand[np.argmin(d)]; order.append(j); S += V[j]; rem.remove(j)
    return np.array(order)

def improve(V, order, iters=20000, seed=1):
    """local search on max |partial sum| with 2-swaps"""
    r = np.random.default_rng(seed); order = order.copy()
    def score(o):
        return np.linalg.norm(np.cumsum(V[o], 0), axis=1).max()
    best = score(order)
    for _ in range(iters):
        i, j = r.integers(0, len(order), 2)
        o2 = order.copy(); o2[i], o2[j] = o2[j], o2[i]
        s = score(o2)
        if s <= best:
            best, order = s, o2
    return order, best

orders = {}
orders['sorted'] = order_sorted
for m in (2, 3, 5):
    idx = np.concatenate([order_sorted[j::m] for j in range(m)])
    orders['blocks%d' % m] = idx
orders['vdc'] = order_sorted[np.argsort(vdc(np.arange(n)))]
orders['random'] = rng.permutation(n)
g = greedy(V); orders['greedy'] = g
gi, best = improve(V, g); orders['greedy+ls'] = gi
paths = {}
for k, o in orders.items():
    S = np.concatenate([[[0, 0]], np.cumsum(V[o], 0)])
    paths[k] = S
    print('%-10s max|S| = %.3f' % (k, np.linalg.norm(S, axis=1).max()))
print('Banaszczyk bound sqrt(5)/2 = %.4f' % (5 ** 0.5 / 2))

W = 1200; im = Image.new('RGB', (W, W), (250, 248, 243)); dr = ImageDraw.Draw(im)
cols = dict(sorted=(120, 150, 230), blocks2=(140, 190, 230), blocks3=(150, 210, 200), blocks5=(190, 220, 150),
            vdc=(240, 170, 90), random=(230, 130, 150), greedy=(90, 90, 90), **{'greedy+ls': (220, 90, 80)})
scale = W * 0.42 / (n / (2 * np.pi)); ox, oy = W * 0.5, W * 0.88
for k, S in paths.items():
    pts = [(ox + scale * p[0], oy - scale * p[1]) for p in S]
    dr.line(pts, fill=cols[k], width=1)
r = 5 ** 0.5 / 2 * scale
dr.ellipse([ox - r, oy - r, ox + r, oy + r], outline=(230, 90, 80), width=2)
im.save('cache/proto_orders.png')
# zoom on the knot
Z = Image.new('RGB', (W, W), (250, 248, 243)); dz = ImageDraw.Draw(Z)
sc2 = W * 0.4 / 2.0; ox2 = oy2 = W / 2
for k in ('greedy+ls', 'vdc', 'random'):
    S = paths[k]; pts = [(ox2 + sc2 * p[0], oy2 - sc2 * p[1]) for p in S]
    dz.line(pts, fill=cols[k], width=1)
r = 5 ** 0.5 / 2 * sc2; dz.ellipse([ox2 - r, oy2 - r, ox2 + r, oy2 + r], outline=(230, 90, 80), width=2)
Z.save('cache/proto_orders_zoom.png')
print('saved')
