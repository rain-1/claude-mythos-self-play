"""lane.py SIZE out [n]  — cut-paper shadow box: a lane with a right-angled corner, seen from above the roofs
at night, and n crates nailed together going round it (the best assembly found for n squares).
Every pose is the true canonical motion (pressed to both outer walls), every length is to scale."""
import sys, numpy as np
from scipy import ndimage as ndi
from PIL import Image, ImageDraw
import papercut as pc
from papercut import rgb, mix
from geom import Motion, load

size = int(sys.argv[1]); out = sys.argv[2]; n = int(sys.argv[3]) if len(sys.argv) > 3 else 3
B = pc.Box(size, seed=11, base='#e7dcc3')
u = B.u; S = size
rng = np.random.default_rng(7)
M = Motion(load(n))
print('n', n, 'w', M.w, 'area', M.area)

# ---- plan (design units, 4096) ---------------------------------------------------------------------
W = 1010.0                    # lane width
OX, OY = 3560.0, 520.0        # outer corner
IX, IY = OX - W, OY + W       # inner corner
sc = W / M.w                  # px per assembly unit
def T(p):                     # corridor frame -> design px
    p = np.asarray(p, float)
    return np.stack([(IX + p[..., 0] * sc), (IY - p[..., 1] * sc)], -1)

xx, yy = B.grid(); xx = xx / u; yy = yy / u       # design coordinates per pixel

# ---- ground: moonlit flagstones --------------------------------------------------------------------
lane = ((yy > OY) & (yy < IY) & (xx < OX)) | ((xx > IX) & (xx < OX) & (yy > OY))
g = np.zeros((S, S), np.float32)
# flag joints: courses run along each arm, mitred at the corner on the diagonal
diag = (xx - IX) - (IY - yy)          # >0 : belongs to arm 2 (the vertical arm)
arm2 = diag > 0
across = np.where(arm2, xx - IX, IY - yy); along = np.where(arm2, yy, xx)
course = np.floor(across / 126.0)
j1 = np.abs((across / 126.0) % 1.0 - 0.5) > 0.5 - 2.2 / 126
off = (course % 2) * 95.0 + course * 37.0
j2 = np.abs(((along + off) / 190.0) % 1.0 - 0.5) > 0.5 - 2.2 / 190
j3 = np.abs(diag) < 2.4
g = ((j1 | j2 | j3) & lane).astype(np.float32)
g = ndi.gaussian_filter(g, 0.6 * max(1, u))
tone = pc._blur(rng.standard_normal((S, S)).astype(np.float32), 60 * u) * 30
floor = mix(rgb('#eadfc6'), rgb('#d9cdb4'), np.clip(0.5 + tone, 0, 1)[..., None])
stone = (np.floor(across / 126.0) * 7 + np.floor((along + off) / 190.0) * 13) % 5 / 4.0
floor = floor * (0.965 + 0.05 * stone)[..., None]
B.img[:] = floor * B.fibre(1.0, 0)[..., None]
B.ink(g, '#8d8672', 0.55)

# ---- the crates: poses fanned like a hand of cards, the corner moment on top -------------------------
K = 11
taus = np.array([-1.0, -0.52, -0.12, 0.14, 0.34, 0.5, 0.66, 0.86, 1.12, 1.52, 2.0])
order = sorted(range(K), key=lambda k: -abs(taus[k] - 0.5))      # far poses first (lowest)
FAR, NEAR = rgb('#3f5288'), rgb('#f6ecd2')
RED = rgb('#c8402f')
def crate_mask(F, idx=None, inset=0.0):
    im = Image.new('L', (S * 2, S * 2), 0); d = ImageDraw.Draw(im)
    for i, q in enumerate(F):
        if idx is not None and i not in idx: continue
        P = T(q) * u * 2
        if inset > 0:
            c = P.mean(0); L = np.hypot(*(P[1] - P[0])); P = c + (P - c) * (1 - 2 * inset * u * 2 / L)
        d.polygon([tuple(p) for p in P], fill=255)
    return np.asarray(im.resize((S, S), Image.LANCZOS), np.float32) / 255
def slat_mask(F, inset=0.085, k=5):
    im = Image.new('L', (S * 2, S * 2), 0); d = ImageDraw.Draw(im)
    for q in F:
        P = T(q) * u * 2; c = P.mean(0)
        Q = [c + (p - c) * (1 - 2 * inset) for p in P]
        d.line([tuple(p) for p in Q] + [tuple(Q[0])], fill=255, width=max(1, int(round(3.4 * u * 2))))
        for j in range(1, k):
            a = Q[0] + (Q[1] - Q[0]) * j / k; b = Q[3] + (Q[2] - Q[3]) * j / k
            d.line([tuple(a), tuple(b)], fill=210, width=max(1, int(round(2.4 * u * 2))))
        for a, b in ((Q[0], Q[2]),):
            d.line([tuple(a), tuple(b)], fill=150, width=max(1, int(round(2.0 * u * 2))))
    return np.asarray(im.resize((S, S), Image.LANCZOS), np.float32) / 255
# which square is the red one: the one nearest the inner corner at the corner moment
Fmid = M.pose(0.5); cen = Fmid.mean(1); red_i = int(np.argmin(np.hypot(cen[:, 0], cen[:, 1])))
for rank, k in enumerate(order):
    F = M.pose(float(taus[k]), slide=1.0)
    t = 1 - abs(taus[k] - 0.5) / 1.5
    col = mix(FAR, NEAR, np.clip(t, 0, 1) ** 1.3)
    z = 1.0 + 1.1 * rank
    top = (rank == K - 1)
    m = crate_mask(F)
    if top:
        colimg = np.broadcast_to(col, (S, S, 3)).copy()
        mr = crate_mask(F, idx={red_i}); colimg = colimg * (1 - mr[..., None]) + RED * mr[..., None]
        B.lay(m, colimg, z + 2, shadow=0.55, reach=7.0, soft=3.2, k=rank)
        B.ink(slat_mask(F) * m, '#3d3030', 0.40)
    else:
        # a ghost pose is a frame: the outline of each crate cut from a strip of paper
        fr = np.clip(m - crate_mask(F, inset=17.0 + 5.0 * t), 0, 1)
        B.lay(fr, col, z, shadow=0.46, reach=5.0, soft=2.4, k=rank, contact=0.3)

# ---- roofs ----------------------------------------------------------------------------------------
INKS = ['#27305a', '#303b6b', '#3a477c', '#465690', '#3b3a6e', '#2d4a6a', '#4b4580', '#34406f']
def house(x0, y0, x1, y1, z, ink, hip=1.0, sky=None, chim=None):
    """a hipped roof on the rectangle; contour lines = tile courses"""
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2; a, b = (x1 - x0) / 2, (y1 - y0) / 2
    X0, X1 = max(0, int(x0 * u) - 2), min(S, int(x1 * u) + 3); Y0, Y1 = max(0, int(y0 * u) - 2), min(S, int(y1 * u) + 3)
    if X1 <= X0 or Y1 <= Y0: return
    sx, sy = xx[Y0:Y1, X0:X1] - cx, yy[Y0:Y1, X0:X1] - cy
    dxe, dye = a - np.abs(sx), b - np.abs(sy)
    h = np.minimum(dxe * hip + (1 - hip) * 1e6 if a > b else dxe, dye * hip + (1 - hip) * 1e6 if b >= a else dye)
    facet_x = (dxe * (hip if a > b else 1) + ((1 - hip) * 1e6 if a > b else 0)) < (dye * (hip if b >= a else 1) + ((1 - hip) * 1e6 if b >= a else 0))
    nx = np.where(facet_x, np.sign(sx), 0.0); ny = np.where(facet_x, 0.0, np.sign(sy))
    lit = -(nx * B.light[0] + ny * B.light[1])            # >0 facing the moon... light = direction TO light
    lit = -lit
    base = rgb(ink)
    col = base[None, None, :] * (1.0 + 0.30 * lit)[..., None] + np.array([0.02, 0.025, 0.05], np.float32) * np.clip(lit, 0, 1)[..., None]
    # tile courses
    sp = 15.0
    line = np.abs((h / sp) % 1.0 - 0.5) > 0.5 - 1.3 / sp
    col = col * (1 - 0.16 * ndi.gaussian_filter(line.astype(np.float32), 0.5 * max(1, u)))[..., None]
    # ridge and hips: a pale cut line where facets meet
    full = np.zeros((S, S), np.float32)
    full[Y0:Y1, X0:X1] = np.clip(np.minimum(dxe, dye) * u + 0.5, 0, 1)
    colimg = np.zeros((S, S, 3), np.float32); colimg[Y0:Y1, X0:X1] = col
    B.lay(full, colimg, z, shadow=0.62, reach=4.2, soft=2.2, k=int(z) % 5, contact=0.3, tex=0.9)
    return (cx, cy, a, b)

houses = []
def row(x0, y0, x1, y1, along, depth_jit=0.0, zbase=34, wmin=330, wmax=560):
    """a terrace of houses filling the rectangle, party walls across `along`"""
    L = (x1 - x0) if along == 'x' else (y1 - y0); p = 0.0; cuts = [0.0]
    while L - p > wmax * 1.3:
        p += rng.uniform(wmin, wmax); cuts.append(p)
    cuts.append(L)
    for i in range(len(cuts) - 1):
        z = zbase + rng.integers(0, 4) * 5; ink = INKS[rng.integers(0, len(INKS))]
        if along == 'x': r = (x0 + cuts[i], y0, x0 + cuts[i + 1], y1)
        else: r = (x0, y0 + cuts[i], x1, y0 + cuts[i + 1])
        houses.append((r, z, ink))

# outer side: a terrace along the top and one down the right, a corner house between them
row(-40, -60, OX - 20, OY, 'x')
row(OX, OY + 20, 4160, 3700, 'y')
houses.append(((OX - 20, -60, 4160, OY + 20), 52, '#2d4a6a'))
# inner block: front terraces on both arms, a corner house, back rows, and a yard with a well
D = 520.0
row(-40, IY, IX - D, IY + D, 'x')
row(IX - D, IY + D, IX, 3700, 'y')
houses.append(((IX - D, IY, IX, IY + D), 56, '#465690'))
YX0, YY0, YX1, YY1 = 330.0, IY + D + 330, IX - D - 300, 3190.0      # the yard
row(-40, IY + D, YX0, 3700, 'y', wmin=420, wmax=640)
row(YX0, IY + D, IX - D, YY0, 'x', wmin=380, wmax=600)
row(YX1, YY0, IX - D, 3700, 'y', wmin=420, wmax=700)
row(YX0, YY1, YX1, 3700, 'x', wmin=420, wmax=700)

# the yard: packed earth, a round well with the moon in it, a tree
yard = B.rect(YX0 * u, YY0 * u, YX1 * u, YY1 * u)
B.img = B.img * (1 - yard[..., None]) + (rgb('#cfc3a6') * B.fibre(1.0, 2)[..., None]) * yard[..., None]
wx, wy, wr = (YX0 + YX1) / 2 - 150, (YY0 + YY1) / 2 + 40, 150.0
B.lay(B.disc(wx * u, wy * u, (wr + 34) * u), rgb('#8f8a80'), 3.0, shadow=0.5, reach=5, soft=3, k=1)       # kerb
B.lay(B.disc(wx * u, wy * u, wr * u), rgb('#151b3a'), 0.5, shadow=0.0, edge=0.6, k=2)                     # water
B.z[B.disc(wx * u, wy * u, wr * u) > 0.5] = -6
B.lay(B.disc((wx + 28) * u, (wy + 22) * u, 62 * u), rgb('#f6efd8'), -5.5, shadow=0.0, edge=0.3, tex=0.4, k=3)   # the moon, in the well
B.z[B.disc(wx * u, wy * u, wr * u) > 0.5] = 0.5
# ripples and three stars in the water; stepping stones from the houses to the well
rr = np.hypot(xx - wx, yy - wy)
rip = (np.abs(rr - 96) < 2.2) | (np.abs(rr - 126) < 1.6)
B.ink(ndi.gaussian_filter(rip.astype(np.float32), 0.7 * max(1, u)), '#5d6f98', 0.5)
for sx_, sy_, sr_ in ((-78, -60, 7), (-30, 92, 5), (70, -88, 6), (-104, 30, 4)):
    B.ink(B.disc((wx + sx_) * u, (wy + sy_) * u, sr_ * u), '#f6efd8', 0.9)
st = np.zeros((S, S), np.float32)
for i in range(7):
    a_ = i / 6.0; px_ = YX0 + 60 + (wx - wr - 110 - YX0 - 60) * a_; py_ = YY0 + 90 + (wy - YY0 - 90) * a_ ** 1.5 + 22 * np.sin(3.1 * i)
    t_ = np.linspace(0, 2 * np.pi, 9, endpoint=False) + i
    st = np.maximum(st, B.poly(np.c_[(px_ + (44 + 9 * np.sin(2 * t_ + i)) * np.cos(t_)) * u, (py_ + (36 + 7 * np.cos(3 * t_)) * np.sin(t_)) * u]))
B.lay(st, rgb('#b9b2a2'), 1.2, shadow=0.45, reach=4, soft=2.5, k=3)
# kerb shadow falling into the well
ring = B.disc(wx * u, wy * u, (wr + 34) * u) - B.disc(wx * u, wy * u, wr * u)

for r, z, ink in sorted(houses, key=lambda h: h[1]):
    house(*r, z, ink)

# tree in the yard: three tiers of leaves
tx, ty = wx + 420, wy - 150
for i, (rr, c, z) in enumerate([(235, '#24454d', 20), (170, '#2f5a5f', 26), (105, '#3f7273', 32)]):
    t = np.linspace(0, 2 * np.pi, 220, endpoint=False)
    rad = rr * (1 + 0.10 * np.sin(7 * t + i) + 0.06 * np.sin(13 * t + 2 * i))
    B.lay(B.poly(np.c_[(tx - 14 * i + rad * np.cos(t)) * u, (ty - 16 * i + rad * np.sin(t)) * u]), rgb(c), z, shadow=0.5, reach=5.0, soft=3.0, k=i)

t = np.linspace(0, 2 * np.pi, 160, endpoint=False)
for i, (rr_, c, z) in enumerate([(120, '#24454d', 14), (78, '#33626a', 19)]):
    rad = rr_ * (1 + 0.11 * np.sin(6 * t + 2 + i) + 0.05 * np.sin(11 * t))
    B.lay(B.poly(np.c_[(YX0 + 210 - 8 * i + rad * np.cos(t)) * u, (YY1 - 190 - 9 * i + rad * np.sin(t)) * u]), rgb(c), z, shadow=0.5, reach=5.0, soft=3.0, k=i + 2)

# chimneys and lit skylights (warm yellow), one per house or so
ch = np.zeros((S, S), np.float32); sk = np.zeros((S, S), np.float32)
for r, z, ink in houses:
    x0, y0, x1, y1 = r; cx, cy = (x0 + x1) / 2, (y0 + y1) / 2; a, b = (x1 - x0) / 2, (y1 - y0) / 2
    if a < 120 or b < 120: continue
    if a > b: px, py = cx + rng.uniform(-0.5, 0.5) * (a - b), cy
    else: px, py = cx, cy + rng.uniform(-0.5, 0.5) * (b - a)
    ch = np.maximum(ch, B.rect((px - 26) * u, (py - 20) * u, (px + 26) * u, (py + 20) * u))
    if rng.uniform() < 0.42:
        q = rng.uniform(0.35, 0.6) * (1 if rng.uniform() < 0.5 else -1)
        if a > b: lx, ly = cx + rng.uniform(-0.4, 0.4) * a, cy + q * b
        else: lx, ly = cx + q * a, cy + rng.uniform(-0.4, 0.4) * b
        sk = np.maximum(sk, B.rect((lx - 24) * u, (ly - 17) * u, (lx + 24) * u, (ly + 17) * u))
B.lay(sk, rgb('#f3cf7a'), 58, shadow=0.0, edge=0.5, tex=0.5, k=1)
glow = pc._blur(sk, 26 * u)[..., None]
B.img = np.clip(B.img + glow * np.array([0.30, 0.20, 0.05], np.float32) * (1 - sk[..., None]), 0, 1)
B.lay(ch, rgb('#6d6a86'), 78, shadow=0.6, reach=3.0, soft=2.0, k=2)

# a cat on the ridge of the corner house, looking down at the crates
def cat(cx, cy, s, ang):
    im = Image.new('L', (S * 2, S * 2), 0); d = ImageDraw.Draw(im)
    c, sn = np.cos(ang), np.sin(ang)
    def P(x, y): return ((cx + (x * c - y * sn) * s) * u * 2, (cy + (x * sn + y * c) * s) * u * 2)
    def ell(x, y, rx, ry, k=40):
        t = np.linspace(0, 2 * np.pi, k); d.polygon([P(x + rx * np.cos(a), y + ry * np.sin(a)) for a in t], fill=255)
    ell(0, 0, 1.0, 0.62); ell(1.05, 0, 0.42, 0.40)                       # body, head
    d.polygon([P(1.20, -0.36), P(1.48, -0.52), P(1.36, -0.16)], fill=255)   # ears
    d.polygon([P(1.20, 0.36), P(1.48, 0.52), P(1.36, 0.16)], fill=255)
    t = np.linspace(0, 1, 30); tail = [P(-0.9 - 1.1 * a, 0.25 + 0.75 * np.sin(2.6 * a)) for a in t]
    d.line(tail, fill=255, width=max(2, int(0.20 * s * u * 2)), joint='curve')
    return np.asarray(im.resize((S, S), Image.LANCZOS), np.float32) / 255
B.lay(cat(IX - 215, IY + 262, 74, -0.78), rgb('#11132a'), 80, shadow=0.55, reach=2.6, soft=1.8, k=3, edge=0.5)

# two small clouds, the highest sheets: their shadows drift over the roofs
def cloud(cx, cy, s, seed):
    r = np.random.default_rng(seed); m = np.zeros((S, S), np.float32)
    for i in range(14):
        t = r.uniform(-1, 1)
        m = np.maximum(m, B.disc((cx + t * 1.7 * s) * u, (cy - r.uniform(0.0, 0.42) * s * (1 - t * t)) * u, r.uniform(0.22, 0.46) * s * u * (1.15 - 0.5 * t * t)))
    m = np.maximum(m, B.rect((cx - 1.9 * s) * u, (cy - 0.08 * s) * u, (cx + 1.9 * s) * u, (cy + 0.26 * s) * u) * (1 - 0))
    m = np.maximum(m, B.disc((cx - 1.9 * s) * u, (cy + 0.09 * s) * u, 0.17 * s * u)); m = np.maximum(m, B.disc((cx + 1.9 * s) * u, (cy + 0.09 * s) * u, 0.17 * s * u))
    return m
B.lay(cloud(900, 3330, 230, 3), rgb('#c9c6d8'), 150, shadow=0.55, reach=1.25, soft=0.55, k=4, tex=0.7)
B.lay(cloud(1500, 330, 150, 5), rgb('#d6d2e0'), 150, shadow=0.5, reach=1.25, soft=0.55, k=1, tex=0.7)

# ---- mat and captions -----------------------------------------------------------------------------
mx0, my0, mx1, my1 = 170, 170, 3926, 3520
B.mat(mx0 * u, my0 * u, mx1 * u, my1 * u, colour='#f3eee2', z=190)
side = 1 / M.w
cap = [(S / 2, 3652 * u, {3: 'Three Crates and a Corner'}.get(n, f'{n} Crates and a Corner'), pc.SERIF, 92 * u, 'mm'),
       (S / 2, 3776 * u, CAP1 if (CAP1 := None) else '', pc.SERIF_I, 50 * u, 'mm')]
if n == 3:
    l1 = 'The lane is one pace wide. Three equal crates, nailed together, each 0.69 of a pace: the stair of them just turns the corner.'
    l2 = 'They carry (36 + 24√2)/49 = 1.4274 square paces.  Nobody has got more round in three squares, and nobody has shown that nobody can.'
else:
    l1 = f'The lane is one pace wide. {n} equal crates, nailed together, each {side:.3f} of a pace across, turning the corner pressed to the outer walls.'
    l2 = f'They carry {M.area:.4f} square paces — the most I could find for {n} squares.'
cap = [cap[0], (S / 2, 3776 * u, l1, pc.SERIF_I, 52 * u, 'mm'), (S / 2, 3852 * u, l2, pc.SERIF_I, 52 * u, 'mm'),
       (S / 2, 3946 * u, 'eleven moments of one carry, the corner moment on top  ·  the red crate is the one that grazes the inner corner  ·  the moon is in the well', pc.SERIF, 41 * u, 'mm')]
B.ink(B.text_mask(cap), '#3a3a48', 0.86)
B.save(out)
print('saved', out)
