"""render_post.py — Post's lattice as a candy mobile (MO 515756).

Every Boolean clone is a five-gore beach ball.  Gore i is coloured iff the clone lies inside
Post's i-th maximal clone (T0 = keeps 0, T1 = keeps 1, M = monotone, D = self-dual, L = affine),
white otherwise.  So the whole lattice is a chart of promises: the projections at the bottom keep
all five (a full ball); BF at the top keeps none (a white pearl) — Post's completeness theorem is
the statement that only BF is all white.  Threads are cover relations, tinted by the promise
broken on the way up (plain plum where none is).  The eight infinite chains S_0^k ⊃ S_0^{k+1} ⊃ …
are strings of beads shrinking geometrically toward their limit clone.

usage: render_post.py W H out.png [key=val]
"""
import sys, json, functools, numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter
from scipy.optimize import minimize

ARG = dict(a.split('=', 1) for a in sys.argv[4:] if '=' in a)
def P(k, d): return type(d)(ARG.get(k, d))
W, H, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]

d = json.load(open('post_lattice.json'))
names = d['names']; cover = [tuple(e) for e in d['cover']]; code = d['code']
down = {k: [a for a, b in cover if b == k] for k in names}
@functools.lru_cache(None)
def rk(k): return 0 if not down[k] else 1 + max(rk(a) for a in down[k])

def dual(nm):
    tr = {'R0': 'R1', 'R1': 'R0', 'M0': 'M1', 'M1': 'M0', 'L0': 'L1', 'L1': 'L0', 'V': 'E', 'E': 'V',
          'V0': 'E1', 'E1': 'V0', 'V1': 'E0', 'E0': 'V1', 'V2': 'E2', 'E2': 'V2', 'I0': 'I1', 'I1': 'I0'}
    if nm in tr: return tr[nm]
    if nm.startswith('S0'): return 'S1' + nm[2:]
    if nm.startswith('S1'): return 'S0' + nm[2:]
    return nm

# ---------- y: rank, with hand nudges so self-dual nodes on the axis do not collide ----------
Y = {k: float(rk(k)) for k in names}
NUDGE = dict(BF=8.6, D=5.6, L=4.5, N=3.35, L3=2.5, D1=3.3, I=2.0, D2=1.15, L2=1.3, N2=1.6, M=7.2, R2=6.2, M2=5.0)
Y.update({k: v for k, v in NUDGE.items()})
# ---------- x: symmetric energy layout ----------
idx = {k: i for i, k in enumerate(names)}
pairs = [(idx[k], idx[dual(k)]) for k in names if dual(k) != k and idx[k] < idx[dual(k)]]
selfd = [idx[k] for k in names if dual(k) == k]
# initial guess: S1-chains far left, S0-chains far right
x0 = np.zeros(len(names))
for k in names:
    s = 0.0
    if k.startswith('S1'): s = -7
    if k.startswith('S0'): s = 7
    if k in ('R0', 'M0', 'L0', 'V0', 'E0', 'I0', 'V', 'V1', 'V2'): s = -3
    if k in ('R1', 'M1', 'L1', 'E1', 'V1', 'I1', 'E', 'E0', 'E2'): s = 3
    x0[idx[k]] = s + 0.1 * np.sin(idx[k])
# self-dual columns: M family centre, D family left of centre, L family right — a deliberate,
# visible asymmetry (D and L are both self-dual, so true mirror symmetry would stack them)
SELF_X = dict(BF=0, M=0, R2=0, M2=0, D=-2.2, D1=-1.6, D2=-0.0, L=2.2, L3=0.9, L2=0.0, N=2.6, N2=1.7, I=0.0, I2=0.0)
fixed = {idx[k]: v for k, v in SELF_X.items()}

def energy(x):
    e = 0.0
    for a, b in cover:
        dx = x[idx[a]] - x[idx[b]]; dy = Y[a] - Y[b]
        e += dx * dx / (dy * dy)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            dy = Y[names[i]] - Y[names[j]]
            if abs(dy) < 0.7:
                dx = x[i] - x[j]
                e += 3.0 * np.exp(-(dx * dx) / 1.2) * (1 - abs(dy) / 0.7)
    for a, b in pairs: e += 50 * (x[a] + x[b]) ** 2
    for i, v in fixed.items(): e += 200 * (x[i] - v) ** 2
    return e
res = minimize(energy, x0, method='L-BFGS-B')
X = {k: res.x[idx[k]] for k in names}
for a, b in pairs:                       # exact symmetry
    m = 0.5 * (X[names[a]] - X[names[b]]); X[names[a]], X[names[b]] = m, -m
for i, v in fixed.items(): X[names[i]] = v
print('layout energy', res.fun)
if P('layout', ''):
    LY = json.load(open(P('layout', '')))
    X = {k: v[0] for k, v in LY.items()}; Y = {k: v[1] for k, v in LY.items()}
    ymax = max(Y.values()); Y = {k: v / ymax * 8.6 for k, v in Y.items()}

# ---------- canvas ----------
SS = 2; WW, HH = W * SS, H * SS
xs = np.array(list(X.values())); xmin, xmax = xs.min(), xs.max()
mx, top, bot = 0.09 * WW, 0.08 * HH, 0.80 * HH
def to_px(k_or_xy):
    x, y = (X[k_or_xy], Y[k_or_xy]) if isinstance(k_or_xy, str) else k_or_xy
    return (mx + (x - xmin) / (xmax - xmin) * (WW - 2 * mx), top + (8.6 - y) / 8.6 * (bot - top))

PIG = dict(T0=(0.52, 0.80, 1.00), T1=(1.00, 0.55, 0.62), M=(1.00, 0.86, 0.42), D=(0.76, 0.60, 1.00), L=(0.52, 0.92, 0.72))
KEYS = ['T0', 'T1', 'M', 'D', 'L']
INK = np.array([0.36, 0.30, 0.42])
paper = np.ones((HH, WW, 3), np.float32) * np.array([0.993, 0.986, 0.976], np.float32)
g = gaussian_filter(np.random.default_rng(1).standard_normal((HH // 4, WW // 4)).astype(np.float32), 1.0)
paper *= (1 + 0.012 * np.kron(g, np.ones((4, 4)))[:HH, :WW] / (np.abs(g).max() + 1e-9))[..., None]
img = paper.copy()

def stroke_layer(segs, width):
    im = Image.new('F', (WW, HH), 0.0); dr = ImageDraw.Draw(im)
    for pts in segs:
        dr.line([tuple(map(float, p)) for p in pts], fill=1.0, width=int(width), joint='curve')
    return np.asarray(im, np.float32).copy()

def curve(a, b, n=40, sag=0.0):
    (x0_, y0_), (x1_, y1_) = to_px(a), to_px(b)
    t = np.linspace(0, 1, n)
    # gentle S-curve: vertical tangents at both ends (like threads hanging between beads)
    yy = y0_ + (y1_ - y0_) * t
    xx = x0_ + (x1_ - x0_) * (3 * t * t - 2 * t ** 3)
    return np.stack([xx, yy], 1)

# chains: insert phantom beads k = 4.. between S?^3-family and its limit
CH = []
fam = []
for side in '01':
    for suf in ('', '2', '1', '0'):
        fam.append((f'S{side}{suf}^3', f'S{side}{suf}'))
chain_beads = []   # (x, y, scale, code)
chain_edges = set()
for a3, lim in fam:
    (xa, ya), (xl, yl) = (X[a3], Y[a3]), (X[lim], Y[lim])
    pts = []
    for j, k in enumerate(range(4, 12)):
        f = 1 - 0.5 ** (j + 1)                     # geometric approach to the limit
        pts.append((xa + (xl - xa) * f, ya + (yl - ya) * f, 0.62 ** (j + 1)))
    chain_beads += [(p, code[a3]) for p in pts]
    chain_edges.add((lim, a3))

# ---------- threads ----------
bw = P('bw', 0.0052) * WW
for a, b in cover:
    lost = [KEYS[i] for i in range(5) if code[a][i] and not code[b][i]]
    tint = np.array(PIG[lost[0]]) if len(lost) == 1 else (np.array([0.62, 0.55, 0.70]) if not lost else np.array([0.62, 0.55, 0.70]))
    if (a, b) in chain_edges:
        # limit to the chain: dotted fading thread
        c = curve(a, b, 60)
        segs = [c[i:i + 2] for i in range(0, len(c) - 1, 3)]
        m = stroke_layer(segs, bw * 0.55)
        dens = 0.55
    else:
        m = stroke_layer([curve(a, b)], bw)
        dens = 0.85
    m = gaussian_filter(m, 0.8 * SS)
    A = -np.log(tint) * 1.3 + 0.10
    img *= np.exp(-dens * m[..., None] * A)
    # glossy core of the thread
    if (a, b) not in chain_edges:
        gl = 0.35 * gaussian_filter(stroke_layer([curve(a, b)], bw * 0.25), SS)[..., None]
        img = img * (1 - gl) + gl
# shadows + beads
R0 = P('br', 0.017) * WW
beads = [(to_px(k), 1.0, code[k], k) for k in names] + [(to_px((x, y)), s, c, None) for (x, y, s), c in chain_beads]
LEG = []
if P('legend', 1):
    lx0, ly = P('legx', 0.60) * WW, P('legy', 0.905) * HH
    for i in range(5):
        cc = [0] * 5; cc[i] = 1
        pos = (lx0 + i * P('legdx', 0.074) * WW, ly)
        beads.append((pos, 1.25, cc, 'LEG%d' % i)); LEG.append(pos)
sh = Image.new('F', (WW, HH), 0.0); ds = ImageDraw.Draw(sh)
for (px, py), s, c, k in beads:
    r = R0 * s * (1.25 if k == 'BF' else 1.0)
    ds.ellipse([px - r + 0.25 * r, py - r + 0.35 * r, px + r + 0.25 * r, py + r + 0.35 * r], fill=1.0)
sh = gaussian_filter(np.asarray(sh, np.float32), R0 * 0.35)
img *= np.exp(-0.30 * sh[..., None] * -np.log(np.array([0.70, 0.72, 0.95])))

yy, xx = np.mgrid[0:HH, 0:WW].astype(np.float32)
for (px, py), s, c, k in beads:
    r = R0 * s * (1.25 if k == 'BF' else 1.0)
    x0b, x1b, y0b, y1b = int(px - r - 3), int(px + r + 4), int(py - r - 3), int(py + r + 4)
    X_ = xx[y0b:y1b, x0b:x1b] - px; Y_ = yy[y0b:y1b, x0b:x1b] - py
    rr = np.sqrt(X_ ** 2 + Y_ ** 2) / r
    inside = np.clip((1 - rr) * r * 0.9, 0, 1)
    # beach-ball gores: on a sphere seen slightly from above, gore boundaries are meridians
    z = np.sqrt(np.clip(1 - rr ** 2, 0, 1))
    al = P('tilt', 0.55)                                   # pole tilted toward viewer-top
    pole_v = np.array([0.0, -np.sin(al), np.cos(al)]); e2 = np.array([0.0, np.cos(al), np.sin(al)])
    nX, nY, nZ = X_ / r, Y_ / r, z
    lon = np.arctan2(nX, nY * e2[1] + nZ * e2[2])
    grot = P('grot', 0.5) - (int(k[3:]) if (k or '').startswith('LEG') else 0)
    gi = np.floor(((lon / (2 * np.pi)) % 1.0) * 5 + grot).astype(int) % 5
    cap = (nY * pole_v[1] + nZ * pole_v[2]) > 0.975
    col = np.ones(X_.shape + (3,), np.float32)
    for i in range(5):
        if c[i]:
            col[gi == i] = PIG[KEYS[i]]
    # shading: lambert from upper-left + rim darkening + specular
    nx, ny, nz = X_ / r, Y_ / r, z
    lam = np.clip(0.55 + 0.45 * (-0.45 * nx - 0.55 * ny + 0.70 * nz), 0, 1)
    spec = np.exp(-((nx + 0.38) ** 2 + (ny + 0.42) ** 2) / 0.018)
    shade = col * (0.55 + 0.45 * lam[..., None]) + 0.55 * spec[..., None]
    rim = np.clip((rr - 0.86) / 0.14, 0, 1)[..., None]
    shade = shade * (1 - 0.25 * rim) + 0.25 * rim * INK * 1.4
    # pole cap (the little white button of a beach ball)
    shade[cap & (rr < 1)] = shade[cap & (rr < 1)] * 0.25 + 0.8
    a = inside[..., None]
    img[y0b:y1b, x0b:x1b] = img[y0b:y1b, x0b:x1b] * (1 - a) + a * np.clip(shade, 0, 1.2)

img = np.clip(img, 0, 1)
srgb = np.where(img <= 0.0031308, 12.92 * img, 1.055 * np.power(img, 1 / 2.4) - 0.055)
pim = Image.fromarray((np.clip(srgb, 0, 1) * 255 + 0.5).astype(np.uint8)).resize((W, H), Image.LANCZOS)

# ---------- labels ----------
dr = ImageDraw.Draw(pim)
FD = '/usr/share/fonts/truetype/liberation/'
lab = ImageFont.truetype(FD + 'LiberationSerif-Italic.ttf', int(P('ls', 0.0105) * W))
def pretty(k):
    return k.replace('^', '').replace('S0', 'S₀').replace('S1', 'S₁')
INKc = (92, 77, 102)
for k in names:
    px, py = to_px(k); px /= SS; py /= SS
    r = R0 / SS * (1.25 if k == 'BF' else 1.0)
    SUB = str.maketrans('0123456789', '₀₁₂₃₄₅₆₇₈₉'); SUP = {'2': '²', '3': '³'}
    base, _, kk = k.partition('^')
    txt = base[0] + base[1:].translate(SUB) + (SUP[kk] if kk else '')
    dr.text((px + r * 1.15, py + r * 0.55), txt, font=lab, fill=INKc, anchor='ls')
LEGTXT = ['keeps 0', 'keeps 1', 'monotone', 'self-dual', 'affine']
leg = ImageFont.truetype(FD + 'LiberationSerif-Italic.ttf', int(P('legs', 0.0115) * W))
for (px, py), t in zip(LEG, LEGTXT):
    dr.text((px / SS, py / SS + R0 / SS * 2.0), t, font=leg, fill=INKc, anchor='mt')
if P('title', ''):
    tb = ImageFont.truetype(FD + 'LiberationSerif-Bold.ttf', int(0.030 * W))
    ti = ImageFont.truetype(FD + 'LiberationSerif-Italic.ttf', int(0.0155 * W))
    tr_ = ImageFont.truetype(FD + 'LiberationSerif-Regular.ttf', int(0.0125 * W))
    x, y = 0.07 * W, P('ty', 0.862) * H
    dr.text((x, y), P('title', ''), font=tb, fill=INKc); y += int(0.030 * W * 1.35)
    for line_, f_ in ((P('l1', ''), ti), (P('l2', ''), tr_), (P('l3', ''), tr_)):
        if line_:
            dr.text((x, y), line_, font=f_, fill=INKc); y += int(f_.size * 1.4)
pim.save(out)
json.dump({k: to_px(k) for k in names}, open(out.replace('.png', '_pos.json'), 'w'))
print('saved', out)
