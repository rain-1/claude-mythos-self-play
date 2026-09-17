"""render_names.py — THE NAMES THAT REACH US.
A Wright–Fisher population drawn as a planar forest of lineage fibres: every row a generation (past at the
top), every individual a point, a fibre from each child to its parent.  Rows are sorted by parent rank so
nothing crosses and every founder's family is a contiguous block.  Pigment = the founder's name (one of nine
pigments, dealt at random along the top row, with its own strength); as names die their blocks end.
Ink = the family tree of the present: only the fibres with living descendants, width by how many.
Coral: the founder whose name the present carries (the root, top) and the last forgetting.
    python3 render_names.py cache/wf_1000_3.npz FINAL AXIS(log|sqrt|lin|log2)
"""
import sys, json, numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image, ImageDraw
from pastel import *

path = sys.argv[1]; FINAL = int(sys.argv[2]); AXIS = sys.argv[3] if len(sys.argv) > 3 else 'log2'
SS = 2
W = H = FINAL * SS
rs = FINAL / 1024 * SS
d = np.load(path)
P, pos, nm, desc, alive = d['P'], d['pos'], d['nm'], d['desc'], d['alive']
G, N = P.shape
print('G', G, 'N', N)

mx, top, bot = 0.10, 0.075, 0.905
def ymap(t):
    t = np.asarray(t, np.float64)
    u = t / G
    if AXIS == 'log':
        v = np.log1p(t) / np.log1p(G)
    elif AXIS == 'sqrt':
        v = np.sqrt(u)
    elif AXIS.startswith('log2'):
        e2 = float(AXIS[4:]) if len(AXIS) > 4 else 1.0
        eps = 1.0 / G
        L = lambda x: np.log(x + eps) - np.log(1 - x + e2 * eps)
        v = (L(u) - L(0)) / (L(1) - L(0))
    else:
        v = u
    return (top + (bot - top) * v) * H
xs = (mx + (1 - 2 * mx) * (pos + 0.5) / N) * W
ys = ymap(np.arange(G + 1))

FAM = ['apricot', 'lemon', 'pistachio', 'mint', 'aqua', 'cornflower', 'lavender', 'orchid', 'blush']
rng = np.random.default_rng(5)
# deal pigments so neighbours differ: a random permutation of a repeated cycle, then swap collisions
founder_pig = np.tile(np.arange(len(FAM)), N // len(FAM) + 1)[:N]
rng.shuffle(founder_pig)
for _ in range(4):
    same = np.where(founder_pig[1:] == founder_pig[:-1])[0]
    for i in same:
        j = rng.integers(0, N)
        founder_pig[i + 1], founder_pig[j] = founder_pig[j], founder_pig[i + 1]
founder_str = 0.55 + 0.45 * rng.random(N)
pig = founder_pig[nm]                       # (G+1, N)
strength = founder_str[nm]
width = max(1.0, 1.4 * rs)
sheet = Sheet(W, H, seed=17)
par_x = np.take_along_axis(xs[:-1], P.astype(np.int64), axis=1)
child_x = xs[1:]
y0 = np.repeat(ys[:-1][:, None], N, axis=1); y1 = np.repeat(ys[1:][:, None], N, axis=1)
segs = np.stack([par_x, y0, child_x, y1], axis=-1).reshape(-1, 4)
cp = pig[1:].reshape(-1); cs = strength[1:].reshape(-1)
DENS = 0.95
for k, name in enumerate(FAM):
    im = Image.new('F', (W, H), 0.0); dr = ImageDraw.Draw(im)
    sel = np.where(cp == k)[0]
    for (x0, ya, x1, yb), wt in zip(segs[sel], cs[sel]):
        dr.line([(x0, ya), (x1, yb)], fill=float(wt * DENS), width=int(round(width)))
    a = gaussian_filter(np.asarray(im, np.float32), 0.6 * rs)
    sheet.wash(a, name, granulate=0.12, seed=k + 3)
    print(name, len(sel), 'segments', flush=True)
# ---- ink: the family tree of the present ----
dchild = desc[1:].reshape(-1)
live = np.where(dchild > 0)[0]
im = Image.new('F', (W, H), 0.0); dr = ImageDraw.Draw(im)
for i in live:
    x0, ya, x1, yb = segs[i]
    f = dchild[i] / N
    wd = (0.5 + 2.6 * np.sqrt(f)) * rs
    dr.line([(x0, ya), (x1, yb)], fill=float(0.2 + 0.45 * f ** 0.4), width=int(round(wd)))
tree = gaussian_filter(np.asarray(im, np.float32), 0.45 * rs)
sheet.wash(tree * 0.85, 'sepia')
print('tree fibres', len(live))
# ---- coral: root and last forgetting ----
winner = int(nm[G, 0])
tl = int(np.argmax(alive == 1)) - 1
loser = [v for v in np.unique(nm[tl]) if v != winner][0]
lx = xs[tl][nm[tl] == loser].mean(); ly = ys[tl]
pts = [(xs[0][winner], ys[0] - 5 * rs), (lx, ly + 3 * rs)]
cor = discs_density(W, H, [p[0] for p in pts], [p[1] for p in pts], [4.5 * rs] * 2, [1.0] * 2, sigma=0.8 * rs)
ring = np.zeros((H, W), np.float32)
for cx, cy in pts:
    im = Image.new('F', (W, H), 0.0); ImageDraw.Draw(im).ellipse([cx - 14 * rs, cy - 14 * rs, cx + 14 * rs, cy + 14 * rs], outline=1.0, width=int(round(1.4 * rs)))
    ring += np.asarray(im, np.float32)
sheet.wash(cor + gaussian_filter(ring, 0.5 * rs) * 0.9, 'coral')
# ---- ticks ----
ink = np.zeros((H, W), np.float32); items = []
ticks = [t for t in [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000] if t < G]
right = [G - t for t in [10, 20, 50, 100, 200, 500] if G - t > 0]
FS = 12 * rs
for t in ticks:
    y = ymap(t)
    im = Image.new('F', (W, H), 0.0); ImageDraw.Draw(im).line([(mx * W - 22 * rs, y), (mx * W - 8 * rs, y)], fill=1.0, width=int(round(1.2 * rs)))
    ink += np.asarray(im, np.float32)
    items.append((f'{t}', mx * W - 27 * rs, y, FS, 'italic', 'rm'))
    items.append((f'{alive[t]}', (1 - mx) * W + 10 * rs, y, FS, 'italic', 'lm'))
for t in right:
    y = ymap(t)
    im = Image.new('F', (W, H), 0.0); ImageDraw.Draw(im).line([(mx * W - 22 * rs, y), (mx * W - 8 * rs, y)], fill=1.0, width=int(round(1.2 * rs)))
    ink += np.asarray(im, np.float32)
    items.append((f'{G - t} ago', mx * W - 27 * rs, y, FS, 'italic', 'rm'))
items.append(('the present', W / 2, ymap(G) + 6 * rs, FS, 'italic', 'ma'))
items += [('generations', mx * W - 27 * rs, ymap(0) - 10 * rs, FS, 'italic', 'rd'),
          ('names left', (1 - mx) * W + 10 * rs, ymap(0) - 10 * rs, FS, 'italic', 'ld'),
          (f'{N} founders', W / 2, ymap(0) - 10 * rs, FS, 'italic', 'md')]
ink += text_density(W, H, items)
sheet.wash(ink * 0.85, 'ink')
sheet.caption_strip(0.915, 0.985, 0.5)
title = 'The Names That Reach Us'
sub = (f'A population of {N} that chooses its parents at random, every child drawn under its parent, so every name is one block; '
       f'the names die one by one until the present carries a single founder. Ink: the family tree of the present. Coral: its root, and the last name forgotten.')
lines = wrap(sub, 19 * rs, 'italic', 0.86 * W)
items = [(title, W / 2, 0.935 * H, 40 * rs, 'serif_bold', 'mm')] + [(ln, W / 2, (0.960 + 0.017 * i) * H, 19 * rs, 'italic', 'mm') for i, ln in enumerate(lines)]
sheet.wash(text_density(W, H, items), 'ink')
img = sheet.develop()
out = f'cache/names_{FINAL}_{AXIS}.png' if FINAL < 4096 else f'names_{FINAL}.png'
finish(img, (FINAL, FINAL), out)
json.dump(dict(N=int(N), G=int(G), winner=winner, one_name_from=tl + 1, axis=AXIS, seed_pigments=5), open(f'cache/names_meta_{AXIS}.json', 'w'))
