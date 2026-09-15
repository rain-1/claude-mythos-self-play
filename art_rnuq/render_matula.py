"""render_matula.py — THE MEANING OF A NUMBER IS A TREE.
Matula–Goebel: every natural number is a rooted tree (1 = a single node; n = p_{k1} p_{k2} ... has a root whose
children are the trees of k1, k2, ...). Every rooted tree appears exactly once.  The first N numbers planted
as a garden: branch ink by subtree size, foliage pigment by depth, coral stems for the bamboo numbers
1, 2, 3, 5, 11, 31, 127 (the primeth recurrence: a single stem — the only trees with one branch at every node).

usage: python3 render_matula.py FINAL N cols out_prefix [labels=1]
"""
import sys, json, time
import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image, ImageDraw
import pastel as P
from sympy import primefactors, factorint, primepi, isprime

FINAL = int(sys.argv[1]); N = int(sys.argv[2]); COLS = int(sys.argv[3]); OUT = sys.argv[4]
LABELS = int(sys.argv[5]) if len(sys.argv) > 5 else 1
SS = 2; W = H = FINAL * SS; rs = FINAL / 1024.0 * SS
t0 = time.time(); rng = np.random.default_rng(3)

memo = {}
def tree(n):
    """rooted tree of n as nested tuples of children (Matula–Goebel), children sorted by size"""
    if n in memo: return memo[n]
    if n == 1:
        t = ()
    else:
        ch = []
        for p, e in factorint(n).items():
            k = int(primepi(p))
            ch += [tree(k)] * e
        ch.sort(key=lambda c: size(c))
        t = tuple(ch)
    memo[n] = t
    return t

def size(t):
    return 1 + sum(size(c) for c in t)
def height(t):
    return 1 + max([height(c) for c in t], default=0)

BAMBOO = {1, 2, 3, 5, 11, 31, 127, 709}
DEPTH_PIG = ['lemon', 'pistachio', 'mint', 'aqua', 'cornflower', 'lavender', 'orchid', 'blush']

def layout(t, x, y, th, L, depth, out, seed):
    """recursive botanical layout: returns list of (x0,y0,x1,y1,xm,ym, width, depth, size, is_leaf) segments + foliage"""
    r = np.random.default_rng(seed)
    c = len(t)
    sz = size(t)
    if c == 0:
        out['leaves'].append((x, y, depth))
        return
    # fan of children, bigger subtrees toward the outside so the crown opens
    span = min(2.6, 0.75 * (c - 1) + 0.35) if c > 1 else 0.0
    # alternate the order so the sorted (small..big) children spread symmetrically
    order = list(range(c))
    sym = []
    for i, j in enumerate(reversed(order)):
        sym.insert(len(sym) // 2 if i % 2 else len(sym) - len(sym) // 2, j) if False else None
    # simple: interleave big ones to both ends
    idx = sorted(range(c), key=lambda i: -size(t[i]))
    arr = [None] * c; lo, hi = 0, c - 1
    for k, i in enumerate(idx):
        if k % 2 == 0: arr[lo] = i; lo += 1
        else: arr[hi] = i; hi -= 1
    for slot, i in enumerate(arr):
        ch = t[i]
        a = th + (span * (slot - (c - 1) / 2) / max(c - 1, 1)) + r.normal(0, 0.07)
        Lc = L * (0.62 + 0.10 * min(height(ch), 5)) * (0.92 + 0.16 * r.random())
        x1, y1 = x + Lc * np.cos(a), y - Lc * np.sin(a)
        # slight bend: control point off the chord
        bend = r.normal(0, 0.10) * Lc
        xm, ym = (x + x1) / 2 - bend * np.sin(a), (y + y1) / 2 - bend * np.cos(a)
        out['segs'].append((x, y, x1, y1, xm, ym, size(ch), depth))
        layout(ch, x1, y1, a, L * 0.78, depth + 1, out, seed * 7 + i + 1)

sheet = P.Sheet(W, H, seed=21)
rows = int(np.ceil(N / COLS))
x0, x1 = 0.05 * W, 0.95 * W
cw = (x1 - x0) / COLS
y_top, y_bot = 0.06 * H, 0.87 * H
rh = (y_bot - y_top) / rows
L0 = 0.30 * rh
ink = np.zeros((H, W), np.float32)
coral = np.zeros((H, W), np.float32)
fol = {d: np.zeros((H, W), np.float32) for d in range(len(DEPTH_PIG))}
im_ink = Image.new('F', (W, H), 0.0); dri = ImageDraw.Draw(im_ink)
im_cor = Image.new('F', (W, H), 0.0); drc = ImageDraw.Draw(im_cor)
im_fol = {d: Image.new('F', (W, H), 0.0) for d in range(len(DEPTH_PIG))}
drf = {d: ImageDraw.Draw(im_fol[d]) for d in im_fol}
labels = []
stats = []
for n in range(1, N + 1):
    t = tree(n)
    row, col = (n - 1) // COLS, (n - 1) % COLS
    bx = x0 + (col + 0.5) * cw; by = y_top + (row + 1) * rh - 0.10 * rh
    out = dict(segs=[], leaves=[])
    # trunk: the root sits on the ground, a short stem up to the root node
    trunk = 0.45 * L0
    rx, ry = bx, by - trunk
    layout(t, rx, ry, np.pi / 2, L0, 1, out, n)
    is_bamboo = n in BAMBOO
    dr_ = drc if is_bamboo else dri
    wt = 1.0
    dr_.line([(bx, by), (rx, ry)], fill=wt, width=int(max(1, round((1.2 + 0.9 * (size(t) + 1) ** 0.5) * rs))))
    for (ax, ay, cx_, cy_, mx, my, sz, dep) in out['segs']:
        wdt = (0.9 + 0.55 * sz ** 0.45) * rs
        # quadratic bezier as polyline
        ts = np.linspace(0, 1, 8)
        px = (1 - ts) ** 2 * ax + 2 * (1 - ts) * ts * mx + ts ** 2 * cx_
        py = (1 - ts) ** 2 * ay + 2 * (1 - ts) * ts * my + ts ** 2 * cy_
        w_par = (0.9 + 0.9 * (sz + 1) ** 0.5) * rs; w_ch = (0.9 + 0.9 * max(sz - 1, 0.6) ** 0.5) * rs * 0.8
        for q in range(len(ts) - 1):
            ww = w_par + (w_ch - w_par) * q / (len(ts) - 2)
            dr_.line([(px[q], py[q]), (px[q + 1], py[q + 1])], fill=wt, width=int(max(1, round(ww))))
        # foliage: soft disc at the child node, sized by subtree size, tinted by depth
        d = min(dep, len(DEPTH_PIG) - 1)
        rad = (3.0 + 2.2 * sz ** 0.5) * rs
        drf[d].ellipse([cx_ - rad, cy_ - rad, cx_ + rad, cy_ + rad], fill=0.40)
    for (lx, ly, dep) in out['leaves']:
        d = min(dep, len(DEPTH_PIG) - 1)
        rl = np.random.default_rng(n * 131 + int(lx) + int(ly))
        for _ in range(7):
            ox, oy = rl.normal(0, 3.2 * rs, 2)
            rad = (1.6 + 1.2 * rl.random()) * rs
            drf[d].ellipse([lx + ox - rad, ly + oy - rad, lx + ox + rad, ly + oy + rad], fill=1.0)
    if LABELS:
        labels.append((str(n), bx, by + 0.045 * rh, 7.5 * rs, 'italic', 'mt'))
    stats.append(dict(n=n, size=size(t), height=height(t), children=len(t)))
print('trees laid out [%.0fs]' % (time.time() - t0), flush=True)

# ground lines per row (faint ink)
gsegs = [(x0, y_top + (r + 1) * rh - 0.10 * rh, x1, y_top + (r + 1) * rh - 0.10 * rh) for r in range(rows)]
ground = P.draw_lines_density(W, H, gsegs, 0.8 * rs, sigma=0.5 * rs)
sheet.wash(ground * 0.35, 'ink')
grass = np.zeros((H, W), np.float32)
yy = np.arange(H, dtype=np.float32)
for r_ in range(rows):
    gy = y_top + (r_ + 1) * rh - 0.10 * rh
    band = np.exp(-np.clip(yy - gy, 0, None) / (0.05 * rh)) * (yy >= gy - 1.5 * rs)
    grass += band[:, None]
grass *= (1 + 0.5 * P.lowfreq(H, W, 40, 5))
sheet.wash(np.clip(grass, 0, 1) * 0.22, 'pistachio', granulate=0.4, seed=61)
# foliage washes (blurred), depth pigments
for d in range(len(DEPTH_PIG)):
    a = np.asarray(im_fol[d], np.float32)
    if a.max() == 0: continue
    a = gaussian_filter(a, 1.2 * rs)
    sheet.wash(np.clip(a, 0, 1.2) * 1.1, DEPTH_PIG[d], granulate=0.25, seed=40 + d)
inka = gaussian_filter(np.asarray(im_ink, np.float32), 0.45 * rs)
sheet.wash(np.clip(inka, 0, 1) * 1.05, 'ink')
cora = gaussian_filter(np.asarray(im_cor, np.float32), 0.45 * rs)
sheet.wash(np.clip(cora, 0, 1) * 1.5, 'coral')
if LABELS:
    sheet.wash(P.text_density(W, H, labels) * 0.75, 'ink')

title = 'The Meaning of a Number Is a Tree'
sub = 'Matula and Goebel: 1 is a leaf, and n = p_k · p_l · … is a root whose branches are the trees of k, l, …  Every rooted tree grows here exactly once. The coral stems are 1, 2, 3, 5, 11, 31, 127: the numbers that are one straight stalk.'
ts = 30 * rs; ss = 15 * rs
lines = P.wrap(sub, ss, 'italic', 0.86 * W)
items = [(title, W / 2, 0.915 * H, ts, 'serif_bold', 'mm')]
for i, l in enumerate(lines):
    items.append((l, W / 2, 0.952 * H + i * 1.35 * ss, ss, 'italic', 'mm'))
sheet.wash(P.text_density(W, H, items), 'ink')
img = sheet.develop()
P.finish(img, (FINAL, FINAL), OUT + '_%d.png' % FINAL)
json.dump(dict(N=N, cols=COLS, bamboo=sorted(BAMBOO & set(range(1, N + 1))), stats=stats), open(OUT + '_%d_cert.json' % FINAL, 'w'))
print('done [%.0fs]' % (time.time() - t0))
