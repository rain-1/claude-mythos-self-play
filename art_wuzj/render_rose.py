"""render_rose.py — the Pythagorean beanstalk B_n seen from above.

Every element b of B_n is a circle of radius b about the origin.  The seeds 1..n fill a
disc; each grown element z is a ring outside it, and each derivation x^2+y^2=z^2 is a
bead at (±x, ±y), (±y, ±x) on that ring — a lattice point whose two coordinates are
already members.  Ring hue = generation; bead hue = its angle; coral = the ancestry of
the tallest element a(n).
usage: render_rose.py n S out.png
"""
import sys, pickle, numpy as np
from scipy.ndimage import gaussian_filter
from sorbet import Sheet, PIG, absorb, wheel_tint, discs, text_mask, finish, text_w

n, S, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
SS = 1  # draw at final size; strokes pinned as fractions of S
_, B, gen, der = pickle.load(open(f'bs_{n}.pkl', 'rb'))
top = max(B)
W = H = S
cx, cy = W / 2, H * 0.455
R = 0.405 * S                     # pixel radius of a(n)
k = R / top                       # px per unit
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
dx, dy = xx - cx, cy - yy
P = float(sys.argv[4]) if len(sys.argv) > 4 else 1.4
rho = np.hypot(dx, dy) / R                 # 0..1 at a(n)
r = top * rho ** (1 / P)                   # radius in integer units (warp: px ∝ r^P)
def to_px(u, v):
    q = np.hypot(u, v) / top
    f = R * q ** P / np.maximum(np.hypot(u, v), 1e-9)
    return cx + u * f, cy - v * f
th = np.arctan2(dy, dx)

sh = Sheet(W, H, seed=26)

# --- ancestry of the top (all derivations, recursively) ---
anc = set(); stack = [top]
while stack:
    z = stack.pop()
    if z in anc or z <= n: continue
    anc.add(z)
    for a, b in der.get(z, []):
        if max(gen[a], gen[b]) < gen[z]:
            stack += [a, b]

# --- a faint stained-glass glow inside the tallest ring: hue by angle, fading outward ---
GL = float(sys.argv[10]) if len(sys.argv) > 10 else 0.0
if GL > 0:
    hue = ((np.arctan2(dy, dx) / (2 * np.pi) + 0.25) % 1)
    lut = np.stack([absorb(wheel_tint(h)) for h in np.linspace(0, 1, 256)])
    Ag = lut[(hue * 255).astype(int)]
    fall = np.clip(1 - rho, 0, 1) ** 0.8 * np.clip((1.0 - rho) / 0.02, 0, 1)
    sh.wash_rgb(Ag * (GL * fall)[..., None])
# --- seed disc: soft cream-butter wash with a faint lilac rim (every circle 1..n present) ---
dr = (R * P / top) * (r / top) ** (P - 1)   # px per unit at radius r
seedf = np.clip((n - r) * dr / (0.004 * S), 0, 1)
sh.wash(seedf * (0.10 + 0.10 * (r / n) ** 3), 'butter')
sh.wash(seedf * 0.10 * (r / n) ** 6, 'peach')
rim = np.exp(-((r - n) * dr / (0.0018 * S)) ** 2)
sh.wash(rim * 0.55, 'lilac')

# --- grown rings: 1-D radial absorbance profiles, then lookup ---
NR = 200000
rg = np.linspace(0, top * 1.02, NR)
prof = np.zeros((NR, 3), np.float32)
drz = lambda z: (R * P / top) * (z / top) ** (P - 1)
maxg = max(gen[z] for z in B if z > n)
zs = np.array(sorted(z for z in B if z > n))
for z in sorted(B):
    if z <= n: continue
    g = gen[z]
    tint = wheel_tint(0.47 + 0.50 * (g - 1) / max(1, maxg - 1))   # mint → sky → periwinkle → lilac → bubblegum
    lw = 0.0005 * S / drz(z)
    near = np.sum(np.abs(zs - z) < 0.004 * S / drz(z))   # rings within ~2 ring-widths*4
    wgt = (0.6 + 0.2 * min(len(der[z]), 4)) * min(1.0, 3.0 / max(1, near) ** 0.7)
    if z == top:
        tint, wgt = PIG['coral'], 2.0

    i0, i1 = np.searchsorted(rg, [z - 6 * lw, z + 6 * lw])
    prof[i0:i1] += (wgt * np.exp(-((rg[i0:i1] - z) / lw) ** 2))[:, None] * absorb(tint)[None]
# halo: a soft pastel glow band around the grown zone so the rings sit in colour
for c in range(3):
    pass
A = np.stack([np.interp(r.ravel(), rg, prof[:, c]).reshape(H, W) for c in range(3)], -1)
A *= (r <= top * 1.01)[..., None]
sh.wash_rgb(A * 0.8)

# --- beads: every derivation point, 8-fold ---
from PIL import Image, ImageDraw
PET = float(sys.argv[5]) if len(sys.argv) > 5 else 1.0     # petal elongation (1 = round bead)
def petals(xs, ys, rs, ws=None, sigma=None, dx=0.0, dy=0.0):
    im = Image.new('F', (W, H), 0.0); dr = ImageDraw.Draw(im)
    t = np.linspace(0, 2 * np.pi, 20, endpoint=False)
    ws = np.ones(len(xs)) if ws is None else ws
    for x, y, rr, w in zip(xs, ys, rs, ws):
        a = np.arctan2(y - cy, x - cx)
        u, v = rr * PET * np.cos(t), rr / PET ** 0.5 * np.sin(t)
        px = x + dx + u * np.cos(a) - v * np.sin(a); py = y + dy + u * np.sin(a) + v * np.cos(a)
        dr.polygon(list(zip(px.tolist(), py.tolist())), fill=float(w))
    arr = np.asarray(im, np.float32).copy()
    return gaussian_filter(arr, sigma) if sigma else arr

def octo(pairs):
    xs, ys = [], []
    for (a, b) in pairs:
        for (u, v) in ((a, b), (b, a)):
            for sx in (1, -1):
                for sy in (1, -1):
                    px, py = to_px(sx * u, sy * v); xs.append(px); ys.append(py)
    return np.array(xs), np.array(ys)

def crowd(xs, ys, rad):
    """beads per bead-area around each bead -> soften crowds"""
    c = max(1, int(rad * 3))
    hist = np.zeros((H // c + 2, W // c + 2))
    np.add.at(hist, ((ys / c).astype(int), (xs / c).astype(int)), 1)
    hist = gaussian_filter(hist, 1.0)
    return hist[(ys / c).astype(int), (xs / c).astype(int)]

def beads(xs, ys, rad, strength, tint=None, soft=0.0, ws=None, nb=36):
    if tint is not None:
        sh.wash(petals(xs, ys, np.full(len(xs), rad), ws, sigma=soft or None) * strength, tint)
        return
    ang = np.arctan2(cy - ys, xs - cx)
    bins = ((ang / (2 * np.pi) + 0.25) % 1 * nb).astype(int)
    for bi in range(nb):
        m = bins == bi
        if not m.any(): continue
        d = petals(xs[m], ys[m], np.full(m.sum(), rad), None if ws is None else ws[m], sigma=soft or None)
        sh.wash(d * strength, wheel_tint((bi + 0.5) / nb))

inner = [p for z, v in der.items() if z <= n for p in v]
outer = [p for z, v in der.items() if z > n and z != top for p in v]
coralp = [p for p in der[top]]
BR = float(sys.argv[6]) if len(sys.argv) > 6 else 0.0030
ix, iy = octo(inner)
beads(ix, iy, 0.0012 * S, 1.3, soft=0.0004 * S, ws=1 / (1 + crowd(ix, iy, 0.0012 * S) / 20) ** 0.5)
ox, oy = octo(outer)
cw = 1 / (1 + crowd(ox, oy, BR * S) / 14.0) ** 0.5
# lift the paper under each pearl, then shadow, body, gloss
sh.lighten(np.clip(petals(ox, oy, np.full(len(ox), BR * S * 1.15), sigma=BR * S * 0.3), 0, 1), 0.8)
beads(ox + 0.25 * BR * S, oy + 0.35 * BR * S, BR * S, 0.22, tint='periwinkle', soft=0.6 * BR * S, ws=cw)
beads(ox, oy, BR * S, 1.7, ws=0.4 + 0.6 * cw)
sh.lighten(np.clip(petals(ox, oy, np.full(len(ox), BR * S * 0.38), sigma=BR * S * 0.25, dx=-0.3 * BR * S, dy=-0.3 * BR * S), 0, 1), 0.55)
kx, ky = octo(coralp)
sh.lighten(np.clip(petals(kx, ky, np.full(len(kx), BR * S * 1.6), sigma=BR * S * 0.3), 0, 1), 0.9)
beads(kx, ky, BR * S * 1.35, 1.7, tint='coral')
sh.lighten(np.clip(petals(kx, ky, np.full(len(kx), BR * S * 0.45), sigma=BR * S * 0.3, dx=-0.4 * BR * S, dy=-0.4 * BR * S), 0, 1), 0.6)

TITLE = sys.argv[7] if len(sys.argv) > 7 else ''
if TITLE:
    from sorbet import text_mask
    yb = H * 0.905
    items = [(TITLE, W / 2, yb, 0.026 * S, 'serif_bold', 'mm'),
             (sys.argv[8], W / 2, yb + 0.034 * S, 0.0155 * S, 'italic', 'mm'),
             (sys.argv[9], W / 2, yb + 0.060 * S, 0.0115 * S, 'mono', 'mm')]
    tm = text_mask(W, H, items)
    sh.lighten(gaussian_filter(tm, 0.004 * S), 0.0)
    sh.wash(tm * 2.6, 'ink')
img = sh.develop(dmax=1.7, glow=0.12)
img.save(out)
print('top', top, 'anc', sorted(anc))
