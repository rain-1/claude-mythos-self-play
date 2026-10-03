"""render_stalk.py — the Pythagorean beanstalk B_n from the side, as a botanical plate.
Height = the number itself.  Seeds 1..n lie in the soil; every grown z is a bean at height z,
fed by two vines from the members x, y with x^2 + y^2 = z^2.  Coral = the climb to a(n).
usage: render_stalk.py n S out.png [title sub legend]"""
import sys, pickle, numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image, ImageDraw
from sorbet import Sheet, PIG, absorb, wheel_tint, text_mask, lines

n, S, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
_, B, gen, der = pickle.load(open(f'bs_{n}.pkl', 'rb'))
top = max(B)
grown = sorted(z for z in B if z > n)
edges = []                         # (parent, child, primary?)
for z in grown:
    ds = sorted(der[z], key=lambda p: max(gen[p[0]], gen[p[1]]))
    for k, (a, b) in enumerate(ds):
        prim = k == 0
        edges += [(a, z, prim), (b, z, prim)]
seeds = sorted({p for p, c, _ in edges if p <= n})
nodes = seeds + grown
W, H = S, int(S * 1.25)
rng = np.random.default_rng(3)
# --- layout: heights fixed by value; x by barycentric relaxation + same-height repulsion ---
soil_top = 0.80 * H
ybot, ytop = soil_top - 0.02 * H, 0.07 * H
rows_ = 5
def Y(v):
    if v <= n:
        return soil_top + 0.035 * H + 0.11 * H * (rows_ - 1 - (v - 1) * rows_ // n) / (rows_ - 1)
    return ybot - (ybot - ytop) * ((v - n) / (top - n)) ** 0.85
X = {v: rng.uniform(0.15, 0.85) for v in nodes}
nbr = {v: [] for v in nodes}
for p, c, prim in edges:
    w = 1.0 if prim else 0.35
    nbr[p].append((c, w)); nbr[c].append((p, w))
for it in range(600):
    newX = {}
    for v in nodes:
        sw = sum(w for _, w in nbr[v]); m = sum(X[u] * w for u, w in nbr[v]) / sw
        newX[v] = 0.5 * X[v] + 0.5 * (0.88 * m + 0.12 * 0.5)
    X = newX
    # repulsion among nodes with close heights
    ys = {v: Y(v) / H for v in nodes}
    arr = np.array(nodes)
    for v in nodes:
        f = 0.0
        for u in nodes:
            if u == v: continue
            dy = abs(ys[u] - ys[v]); dx = X[v] - X[u]
            if dy < 0.03 and abs(dx) < 0.07:
                f += np.sign(dx + 1e-9) * (0.07 - abs(dx)) * (1 - dy / 0.03)
        X[v] = float(np.clip(X[v] + 0.25 * f, 0.06, 0.94))
gx = np.array([X[v] for v in grown]); lo, hi = np.percentile(gx, 2), np.percentile(gx, 98)
X = {v: float(np.clip(0.545 + (X[v] - (lo + hi) / 2) / (hi - lo) * 0.60, 0.04, 0.95)) for v in nodes}
# seeds: rows by value, x sorted then spread evenly in each row (no overlaps)
rows = 5
for r_ in range(rows):
    rs = [s_ for s_ in seeds if (s_ - 1) * rows // n == r_]
    rs.sort(key=lambda s_: X[s_])
    for q, s_ in enumerate(rs):
        X[s_] = 0.08 + 0.84 * (q + 0.5 + 0.5 * (r_ % 2)) / (len(rs) + 0.5)
xs = {v: (0.04 + 0.92 * X[v]) * W for v in nodes}
ys = {v: Y(v) for v in nodes}

sh = Sheet(W, H, seed=192)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
# sky wash: pale periwinkle at the top fading to paper, soil: peach-honey band
sky = np.clip(1 - yy / soil_top, 0, 1) ** 2.2
sh.wash(sky * 0.10, 'sky')
soil = np.clip((yy - soil_top) / (0.006 * H), 0, 1)
sh.wash(soil * (0.22 + 0.10 * np.clip((yy - soil_top) / (0.15 * H), 0, 1)), 'peach')
sh.wash(soil * 0.08, 'honey')

# ancestry of the top (primary derivations)
anc = set(); st = [top]
while st:
    z = st.pop()
    if z in anc: continue
    anc.add(z)
    if z > n:
        a, b = sorted(der[z], key=lambda p: max(gen[p[0]], gen[p[1]]))[0]
        st += [a, b]

def bez(p0, p1, bend, turns=1.5, amp=0.012, ph=0.0):
    (x0, y0), (x1, y1) = p0, p1
    t = np.linspace(0, 1, 120)[:, None]
    c0 = (x0 + bend, y0 - 0.45 * (y0 - y1)); c1 = (x1 - 0.3 * bend, y1 + 0.35 * (y0 - y1))
    pts = ((1 - t) ** 3) * np.array([x0, y0]) + 3 * (1 - t) ** 2 * t * np.array(c0) + 3 * (1 - t) * t ** 2 * np.array(c1) + t ** 3 * np.array([x1, y1])
    tt = t[:, 0]
    pts[:, 0] += amp * W * np.sin(2 * np.pi * turns * tt + ph) * np.sin(np.pi * tt)
    return pts
vine_lw = 0.0032 * W
groups = {'prim': [], 'alt': [], 'coral': []}
for p, c, prim in edges:
    bend = (xs[c] - xs[p]) * 0.35 + rng.normal(0, 0.01 * W)
    L = (ys[p] - ys[c]) / H
    pts = bez((xs[p], ys[p]), (xs[c], ys[c]), bend, turns=1 + 6 * L, amp=0.006 + 0.01 * L, ph=rng.uniform(0, 2 * np.pi))
    key = 'coral' if (prim and p in anc and c in anc) else ('prim' if prim else 'alt')
    groups[key].append(pts)
sh.wash(lines(W, H, groups['alt'], vine_lw * 0.6, sigma=0.8) * 0.6, 'mint')
v = lines(W, H, groups['prim'], vine_lw, sigma=0.9)
sh.wash(v * 1.1, 'lime'); sh.wash(v * 0.35, 'mint')
sh.wash(lines(W, H, groups['coral'], vine_lw * 1.4, sigma=0.9) * 1.3, 'coral')

# leaves: a heart-shaped bean leaf beside every grown bean, alternating sides
def leaf_poly(x, y, size, ang):
    """pointed bean leaf with its base at (x, y), pointing along ang"""
    w_ = np.linspace(0, 1, 30)
    half = 0.42 * size * np.sin(np.pi * w_) ** 0.75 * (1 - 0.35 * w_) + 0.06 * size * np.sin(np.pi * w_) * (w_ < 0.3)
    L = size * 1.25
    u = np.concatenate([w_ * L, w_[::-1] * L]); v = np.concatenate([half, -half[::-1]])
    ca, sa = np.cos(ang), np.sin(ang)
    return list(zip((x + u * ca - v * sa).tolist(), (y + u * sa + v * ca).tolist())), (x, y, x + L * ca, y + L * sa)
im = Image.new('F', (W, H), 0.0); dr = ImageDraw.Draw(im)
im2 = Image.new('F', (W, H), 0.0); dr2 = ImageDraw.Draw(im2)
k = 0
ribs = []
for key in ('prim', 'coral'):
    for pts in groups[key]:
        Lp = len(pts)
        for fr in (0.22, 0.45, 0.68):
            if rng.random() < 0.75 and pts[int(fr * len(pts))][1] < soil_top - 0.01 * H:
                q = pts[int(fr * Lp)]; q2 = pts[int(fr * Lp) + 3]
                tang = np.arctan2(q2[1] - q[1], q2[0] - q[0])
                side = 1 if (k % 2) else -1; k += 1
                ang = tang + side * (1.2 + 0.4 * rng.random()) - np.pi / 2
                ang = tang + side * (1.0 + 0.5 * rng.random())
                poly, rib = leaf_poly(q[0], q[1], 0.028 * W * (0.7 + 0.5 * rng.random()), ang)
                (dr2 if rng.random() < 0.5 else dr).polygon(poly, fill=1.0)
                ribs.append([rib[:2], rib[2:]])
for imx, tint in ((im, 'lime'), (im2, 'mint')):
    a = np.asarray(imx, np.float32).copy()
    sh.wash(gaussian_filter(a, 1.2) * 1.1, tint)
    sh.wash(np.clip(a - gaussian_filter(a, 6), 0, 1) * 0.5, 'lime')
    sh.lighten(np.clip(gaussian_filter(a, 0.006 * W) - 0.6, 0, 1) * 2, 0.25)   # body light
sh.lighten(np.clip(lines(W, H, ribs, max(1, 0.0012 * W), sigma=0.6), 0, 1), 0.45)

# beans: grown = glossy pastel beans by generation; seeds = small beans in the soil
def bean(xc, yc, r, tint, k=1.0, gloss=True, ring=None):
    d = np.clip((r - np.hypot((xx - xc) / 1.25, yy - yc)) / 1.5, 0, 1) if False else None
for z in nodes:
    pass
bx = np.array([xs[z] for z in grown]); by = np.array([ys[z] for z in grown])
from sorbet import discs
maxg = max(gen[z] for z in grown)
R0 = 0.0125 * W
sh.lighten(np.clip(discs(W, H, bx, by, np.full(len(bx), R0 * 1.25), sigma=2), 0, 1), 0.9)
for g in range(1, maxg + 1):
    m = np.array([gen[z] == g and z != top for z in grown])
    if m.any():
        sh.wash(discs(W, H, bx[m], by[m], np.full(m.sum(), R0), sigma=1.2) * 1.0,
                wheel_tint(0.62 + 0.42 * (g - 1) / max(1, maxg - 1)), 1.5)
sx = np.array([xs[s] for s in seeds]); sy_ = np.array([ys[s] for s in seeds])
sh.lighten(np.clip(discs(W, H, sx, sy_, np.full(len(sx), R0 * 1.0), sigma=2), 0, 1), 0.8)
sh.wash(discs(W, H, sx, sy_, np.full(len(sx), R0 * 0.8), sigma=1.2) * 1.4, 'honey')
tx, ty = xs[top], ys[top]
sh.lighten(np.clip(discs(W, H, [tx], [ty], [R0 * 1.9], sigma=2), 0, 1), 0.95)
sh.wash(discs(W, H, [tx], [ty], [R0 * 1.6], sigma=1.5) * 1.6, 'coral')
# gloss
allx = np.concatenate([bx, sx, [tx]]); ally = np.concatenate([by, sy_, [ty]])
sh.lighten(np.clip(discs(W, H, allx - 0.3 * R0, ally - 0.35 * R0, np.full(len(allx), 0.28 * R0), sigma=1.5), 0, 1), 0.5)
# labels
items = [(str(z), xs[z], ys[z], (0.0098 if z != top else 0.014) * W, 'serif', 'mm') for z in grown + seeds]
sh.wash(text_mask(W, H, items) * 2.4, 'ink')
if len(sys.argv) > 4:
    x_, y_ = 0.06 * W, 0.075 * H
    cap = []
    for ln in sys.argv[4].split('|'):
        cap.append((ln, x_, y_, 0.036 * W, 'serif_bold', 'ls')); y_ += 0.044 * W
    y_ += 0.004 * W
    for ln in sys.argv[5].split('|'):
        cap.append((ln, x_, y_, 0.0185 * W, 'italic', 'ls')); y_ += 0.027 * W
    y_ += 0.008 * W
    for ln in sys.argv[6].split('|'):
        cap.append((ln, x_, y_, 0.0135 * W, 'mono', 'ls')); y_ += 0.021 * W
    sh.wash(text_mask(W, H, cap) * 3.4, 'ink')
sh.develop(dmax=1.7, glow=0.10).save(out)
