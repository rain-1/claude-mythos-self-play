"""TWO HUNDRED SIXTY-ONE WAYS TO LIE DOWN — every unfolding of the tesseract, in sugared clay."""
import numpy as np, pickle, math, sys, time
from PIL import Image
from clay import render
from sorbet import PIG, text_mask, text_w
from nets import nets
from tess_proto import orient
S = int(sys.argv[1]); OUT = sys.argv[2]
ns, nao = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (10, 10)
res = pickle.load(open('tess261.pkl', 'rb'))
cube = nets(3)
def diam(es, n):
    adj = {i: [] for i in range(n)}
    for a, b in es: adj[a].append(b); adj[b].append(a)
    best = 0
    for s in range(n):
        dist = {s: 0}; q = [s]
        for x in q:
            for y in adj[x]:
                if y not in dist: dist[y] = dist[x] + 1; q.append(y)
        best = max(best, max(dist.values()))
    return best, sum(1 for i in adj if len(adj[i]) == 1)
for r in res:
    r['Q'] = orient(r['pos']); r['diam'], r['leaves'] = diam(r['edges'], 8)
    r['key'] = (r['diam'], -r['leaves'], int(np.prod(r['Q'].max(0) + 1)), r['Q'].max(0)[2], tuple(r['Q'].max(0)))
res.sort(key=lambda r: r['key'])
HUES = ['strawberry', 'butter', 'mint', 'periwinkle']
def colours(cells, Q):
    d = len(cells) // 2; axes = [c[0] for c in cells]
    mx = [np.mean([Q[i, 0] - 0.35 * Q[i, 1] + 0.2 * Q[i, 2] for i in range(len(cells)) if axes[i] == a]) for a in range(d)]
    hues = HUES if d == 4 else ['strawberry', 'butter', 'periwinkle']
    col = np.zeros((len(cells), 3))
    for rank, a in enumerate(np.argsort(mx)):
        base = np.array(PIG[hues[rank]])
        for i in range(len(cells)):
            if axes[i] == a: col[i] = base ** 1.05 if cells[i][1] > 0 else base ** 1.75
    return col
PAPER = np.array([0.988, 0.982, 0.972])
GT = {3: 'rose', 4: 'butter', 5: 'mint', 6: 'sky', 7: 'lilac', 0: 'peach'}
def gtint(g): return PAPER * np.array(PIG[GT[g]]) ** 0.30
COLS, ROWS = 17, 16
mx = int(S * 0.05); top = int(S * 0.05); cap = int(S * 0.125)
gap = max(2, S // 450)
ts = min((S - 2 * mx) // COLS, (S - top - cap) // ROWS)
x0 = (S - COLS * ts) // 2
az, el = math.radians(-58), math.radians(32)
L = np.array([-0.5, 0.42, 0.78]); L /= np.linalg.norm(L)
# camera basis for projected extents
dvec = -np.array([math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)])
rvec = np.array([-math.sin(az), math.cos(az), 0.0]); uvec = np.cross(rvec, dvec); uvec *= np.sign(uvec[2])
items = [('t', r) for r in res] + [('c', c) for c in cube]
boxes = []
for kind, r in items:
    if kind == 't':
        Q = r['Q']; B = np.column_stack([Q, np.ones((8, 3))]).astype(float); col = colours(r['cells'], Q); g = r['diam']
    else:
        Q = orient(np.column_stack([r['pos'], np.zeros(6, int)]))
        B = np.column_stack([Q, np.ones((6, 2)), 0.24 * np.ones(6)]).astype(float); col = colours(r['cells'], Q); g = 0
    corners = np.array([[B[k, 0] + a * B[k, 3], B[k, 1] + b * B[k, 4], B[k, 2] + c * B[k, 5]] for k in range(len(B)) for a in (0, 1) for b in (0, 1) for c in (0, 1)])
    px = corners @ rvec; py = corners @ uvec
    boxes.append((B, col, g, (px.min(), px.max(), py.min(), py.max())))
spans = np.array([max(e[1] - e[0], (e[3] - e[2]) * 1.0) for _, _, _, e in boxes]); print('span pct', np.percentile(spans, [50, 90, 99, 100])); span = 5.0
scale = (ts - 2 * gap) * 0.97 / span
print('ts', ts, 'span', span, 'scale', scale)
canvas = np.ones((S, S, 3)) * PAPER
t0 = time.time()
yy, xx = np.mgrid[0:ts, 0:ts]
rad = ts * 0.12
def rrect(w):
    dx = np.maximum(np.maximum(gap + rad - xx, xx - (ts - gap - rad)), 0); dy = np.maximum(np.maximum(gap + rad - yy, yy - (ts - gap - rad)), 0)
    d = np.hypot(dx, dy) - rad
    return np.clip(0.5 - d, 0, 1)
RR = rrect(ts)
for k, (B, col, g, e) in enumerate(boxes):
    i, j = divmod(k, COLS)
    # centre the projected bbox: solve for world point whose projection is the bbox centre
    pcx, pcy = (e[0] + e[1]) / 2, (e[2] + e[3]) / 2 + 0.06 * span
    # choose a world point on the axis: P = pcx*r + pcy*u (+ any multiple of d)
    P = pcx * rvec + pcy * uvec
    gt = gtint(g)
    sc = scale * min(1.0, span * 1.06 / max(e[1] - e[0], e[3] - e[2]))
    img, m = render(B, col, ts, ts, P[0], P[1], P[2], sc, az, el, L, ns, nao, gt)
    y0 = top + i * ts; xa = x0 + j * ts
    canvas[y0:y0 + ts, xa:xa + ts] = img * RR[..., None] + PAPER * (1 - RR[..., None])
    if k % 40 == 0: print(k, round(time.time() - t0), flush=True)
np.save(OUT + '.npy', canvas)
# caption
T = canvas
srgb = np.where(T <= 0.0031308, 12.92 * T, 1.055 * np.clip(T, 0, None) ** (1 / 2.4) - 0.055)
ink = np.array([0.36, 0.30, 0.40])
cy0 = top + ROWS * ts + int(S * 0.03)
items_t = [('Two Hundred Sixty-One Ways to Lie Down', S / 2, cy0, S * 0.026, 'serif_bold', 'mt'),
           ('every unfolding of the four-dimensional cube into our space, one per symmetry class: 82 944 spanning trees of its eight cells ÷ 384 symmetries', S / 2, cy0 + S * 0.037, S * 0.0145, 'italic', 'mt'),
           ('cubes facing each other across the fourth dimension share a hue, one light and one deep  ·  compartments tint by the longest chain of glued cubes, rose 3 → lilac 7', S / 2, cy0 + S * 0.060, S * 0.0115, 'italic', 'mt'),
           ('first: Dalí’s Corpus Hypercubus, the only one with a cube glued on all six sides  ·  last eleven, flat: the cube’s own nets, one dimension down', S / 2, cy0 + S * 0.078, S * 0.0115, 'italic', 'mt')]
tm = text_mask(S, S, items_t)
srgb = srgb * (1 - tm[..., None]) + tm[..., None] * np.array([0.40, 0.31, 0.44])
img = Image.fromarray((np.clip(srgb, 0, 1) * 255 + 0.5).astype(np.uint8))
img.save(OUT + '.png', optimize=True)
