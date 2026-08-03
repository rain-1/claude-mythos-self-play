"""render_kps.py — THE FIFTH ATOM (2560^2)

Below: THE COUNTRY OF MEASURES — a generic 2-plane slice through the
4-simplex of probability weights on five atoms, cut into stained-glass
chambers by the 121 comparison walls sum(A) = sum(B) (A,B disjoint).
Every chamber IS one additively-representable comparative probability
order; hue = how far the chamber's order defies cardinality (inversions
|A|<|B| with A > B), walls glow.

Above: THE SKY OF ORDERS — the flip graph of all 546 canonical comparative
probability orders on 5 atoms (nodes; edges = one adjacent transposition).
516 gold orders own a country below (sampled threads reach down); the 30
ice orders satisfy every de Finetti axiom yet own no measure at all
(Kraft-Pratt-Seidenberg 1959) — each carries an exact 4-comparison balanced
witness. At n <= 4 atoms the sky and the country are in bijection (2 and 14
orders, all landed): the fifth atom is where order first outruns weight.
"""
import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image, ImageDraw, ImageFont

SCR = "/tmp/claude-0/-home-user-claude-mythos-self-play/adf44c3e-737f-5218-82c7-9c74bc24d1b1/scratchpad"
SIZE = 2560
W = H = SIZE
rs = SIZE / 1024.0
rng = np.random.default_rng(20260803)

n = 5
NS = 32
orders = [tuple(map(int, l.split())) for l in open(f"{SCR}/orders5c.txt") if not l.startswith('#')]
nonrep_set = set()
for l in open(f"{SCR}/cp_results_n5.txt"):
    if l.startswith("ORDER"):
        nonrep_set.add(tuple(map(int, l.split()[1:])))
is_rep = [o not in nonrep_set for o in orders]
print(f"{len(orders)} orders, {sum(is_rep)} representable, {len(nonrep_set)} not")

# ---------- flip graph: a PERFECT MATCHING (verified) ----------
# every order has exactly one axiom-free adjacent swap: its central pair,
# always complementary {A, comp A} at ranks 15|16; and every landless
# order's twin is landed.
idx_of = {o: i for i, o in enumerate(orders)}
partner = {}
for i, o in enumerate(orders):
    lo = list(o)
    sw = lo[:15] + [lo[16], lo[15]] + lo[17:]
    j = idx_of.get(tuple(sw))
    assert j is not None and lo[15] ^ lo[16] == 31
    partner[i] = j
popc = np.array([bin(S).count('1') for S in range(NS)])
def inversions(o):
    rank = np.empty(NS, dtype=np.int64); rank[list(o)] = np.arange(NS)
    c = 0
    for A in range(1, NS):
        for B in range(1, NS):
            if popc[A] < popc[B] and rank[A] > rank[B]: c += 1
    return c
invs = np.array([inversions(o) for o in orders])

# binaries sorted by defiance -> band of twin stars
pairs_list = sorted({tuple(sorted((i, partner[i]))) for i in range(len(orders))})
pairdef = [0.5 * (invs[a] + invs[b]) for a, b in pairs_list]
order_pairs = np.argsort(np.array(pairdef) + rng.random(len(pairdef)) * 1e-3)
npos = np.zeros((len(orders), 2))
SKY_Y = H * 0.315
for rank_, pi in enumerate(order_pairs):
    a, b = pairs_list[pi]
    t = rank_ / (len(pairs_list) - 1)
    bx = W * (0.075 + 0.85 * t)
    by = SKY_Y + H * 0.075 * np.sin(t * np.pi * 2.6) + rng.normal(0, H * 0.052)
    ang = rng.random() * 2 * np.pi
    off = 6.5 * rs / 2.5
    npos[a] = (bx + off * np.cos(ang), by + off * np.sin(ang))
    npos[b] = (bx - off * np.cos(ang), by - off * np.sin(ang))

# ---------- the glass: 2-plane slice ----------
# subsets / masks
masks = np.arange(NS)
MAT = np.array([[(S >> i) & 1 for S in range(NS)] for i in range(n)], dtype=np.float64)  # 5 x 32
# canonical disjoint pair vectors (121)
pairvecs = []
for S in range(NS):
    for T in range(S + 1, NS):
        if S & T: continue
        v = np.array([(T >> i & 1) - (S >> i & 1) for i in range(n)], dtype=np.float64)
        pairvecs.append(v / np.linalg.norm(v))
pairvecs = np.array(pairvecs)

c0 = np.array([0.088, 0.135, 0.19, 0.26, 0.327])   # ordered interior point
def orth(vec, base):
    for b in base:
        vec = vec - vec @ b * b
    return vec / np.linalg.norm(vec)
ones = np.ones(5) / np.sqrt(5)
u = orth(rng.standard_normal(5), [ones]); v2 = orth(rng.standard_normal(5), [ones, u])

GL_CX, GL_CY = W * 0.50, H * 0.760
GL_R = H * 0.205
scale = 0.16 / GL_R          # weight-units per pixel
ys, xs_ = np.mgrid[int(GL_CY - GL_R):int(GL_CY + GL_R), int(GL_CX - GL_R * 1.7):int(GL_CX + GL_R * 1.7)]
aa = (xs_ - GL_CX) * scale
bb = (ys - GL_CY) * scale
Xw = c0[None, None, :] + aa[..., None] * u[None, None, :] + bb[..., None] * v2[None, None, :]
inside = (Xw > 0.004).all(-1)
r_ell = np.sqrt((aa / (1.62 * GL_R * scale)) ** 2 + (bb / (0.95 * GL_R * scale)) ** 2)
inside &= r_ell < 1.0
sums = np.einsum('hwn,ns->hws', Xw, MAT)          # subset sums
# inversion count: pairs with |A| < |B| but sum_A > sum_B
popc = np.array([bin(S).count('1') for S in range(NS)])
inv = np.zeros(aa.shape, dtype=np.int32)
for Sa in range(1, NS):
    for Sb in range(1, NS):
        if popc[Sa] < popc[Sb]:
            inv += (sums[..., Sa] > sums[..., Sb])
inv = np.where(inside, inv, 0)
# wall distance
wd = np.abs(np.einsum('hwn,pn->hwp', Xw, pairvecs)).min(-1)
wd = np.where(inside, wd, 1.0)

# stained glass color: hue from inversion count (defiance of size)
invmax = np.percentile(inv[inside], 99.0)
tt_ = np.clip(inv / max(invmax, 1), 0, 1) ** 0.85
# palette: deep teal -> violet -> ember (defiance rises)
def pal(t):
    c1 = np.array([0.05, 0.30, 0.42]); c2 = np.array([0.36, 0.22, 0.68])
    c3 = np.array([1.00, 0.48, 0.12])
    t = t[..., None]
    return np.where(t < 0.5, c1 * (1 - 2 * t) + c2 * 2 * t,
                    c2 * (2 - 2 * t) + c3 * (2 * t - 1))
# per-chamber hash jitter to separate panes
signs = (np.einsum('hwn,pn->hwp', Xw, pairvecs) > 0)
hv = (signs * rng.random(len(pairvecs))[None, None, :]).sum(-1)
hjit = (hv - np.floor(hv)) - 0.5
tt_ = np.clip(tt_ + hjit * 0.22, 0, 1)
glass_rgb = pal(tt_) * 0.40
wallglow = np.exp(-wd / 0.00062)
glass_rgb += wallglow[..., None] * np.array([0.95, 0.85, 0.65]) * 0.58
# simplex boundary: where an atom's weight dies -> ice rim
from scipy.ndimage import binary_erosion
rim = inside & ~binary_erosion(inside, iterations=max(1, int(1.6 * rs)))
glass_rgb += rim[..., None] * np.array([0.55, 0.8, 1.0]) * 0.55
glass_rgb *= inside[..., None]

img = np.zeros((H, W, 3))
img[int(GL_CY - GL_R):int(GL_CY + GL_R), int(GL_CX - GL_R * 1.7):int(GL_CX + GL_R * 1.7)] += glass_rgb

# ---------- threads: sample chambers -> owning gold node ----------
# sample pixels, identify order, draw thread to node if matched
thr = np.zeros((H, W))
matched = {}
Hh, Ww = aa.shape
for _ in range(4000):
    iy, ix = rng.integers(0, Hh), rng.integers(0, Ww)
    if not inside[iy, ix]: continue
    o = tuple(np.argsort(sums[iy, ix]))
    j = idx_of.get(o)
    if j is not None and j not in matched:
        matched[j] = (ix + int(GL_CX - GL_R * 1.7), iy + int(GL_CY - GL_R))
print(f"threads: {len(matched)} chambers matched to orders")
def bezier(p0, p1, p2, nseg=220):
    t = np.linspace(0, 1, nseg)[:, None]
    return ((1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t ** 2 * p2)
for j, (gx, gy) in list(matched.items())[:34]:
    nx, ny = npos[j]
    mid = np.array([(gx + nx) / 2 + rng.normal(0, 60 * rs / 2.5), (gy + ny) / 2])
    pts = bezier(np.array([nx, ny]), mid, np.array([gx, gy]))
    for (x_, y_) in pts:
        xi, yi = int(x_), int(y_)
        if 0 <= xi < W and 0 <= yi < H: thr[yi, xi] += 0.05
thr = gaussian_filter(thr, 1.1 * rs)
img += np.clip(thr, 0, 0.8)[..., None] * np.array([1.0, 0.85, 0.5]) * 0.85

# ---------- sky: twin bars ----------
sky = np.zeros((H, W))
for a, b in pairs_list:
    p0, p1 = npos[a], npos[b]
    nseg = 14
    t = np.linspace(0, 1, nseg)[:, None]
    pts = p0 * (1 - t) + p1 * t
    for (x_, y_) in pts:
        xi, yi = int(x_), int(y_)
        if 0 <= xi < W and 0 <= yi < H: sky[yi, xi] += 0.10
sky = gaussian_filter(sky, 1.0 * rs)
img += np.clip(sky, 0, 0.5)[..., None] * np.array([0.75, 0.72, 0.85])

yy, xx = np.ogrid[0:H, 0:W]
gold_nodes = np.zeros((H, W)); ice_nodes = np.zeros((H, W))
for j, (x_, y_) in enumerate(npos):
    r2 = (xx - x_) ** 2 + (yy - y_) ** 2
    if is_rep[j]:
        gold_nodes += np.exp(-r2 / (2 * (2.3 * rs) ** 2)) * 0.9
    else:
        ice_nodes += np.exp(-r2 / (2 * (2.8 * rs) ** 2)) * 1.05 \
            + np.exp(-np.sqrt(r2) / (11 * rs)) * 0.26
img += gold_nodes[..., None] * np.array([1.0, 0.78, 0.35])
img += ice_nodes[..., None] * np.array([0.50, 0.80, 1.0])

# ---------- tone map ----------
img = 1.0 - np.exp(-1.5 * img)
img = img ** (1 / 1.8)
img += (rng.random((H, W, 3)) - 0.5) / 255.0
img = np.clip(img, 0, 1)
out = Image.fromarray((img * 255).astype(np.uint8))

# ---------- annotations ----------
dr = ImageDraw.Draw(out)
def LF(p, s):
    try: return ImageFont.truetype(p, s)
    except OSError: return ImageFont.load_default()
F = LF("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 29)
Fs = LF("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
Fb = LF("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 46)
Fi = LF("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 26)
gold = (255, 210, 130); cyan = (160, 215, 255); grey = (170, 170, 188)
dr.text((70, 60), "THE FIFTH ATOM", font=Fb, fill=gold)
dr.text((70, 128), "rank every event by likelihood, obeying de Finetti's axioms:", font=F, fill=grey)
dr.text((70, 168), "on 3 atoms there are 2 such orders, on 4 atoms 14 — every one", font=F, fill=grey)
dr.text((70, 208), "is the ranking of some measure.  On five atoms there are 546,", font=F, fill=grey)
dr.text((70, 248), "and exactly 30 of them are landless (Kraft–Pratt–Seidenberg 1959).", font=F, fill=grey)
dr.text((W - 1120, 128), "the sky: 273 twin stars — every order has exactly ONE free swap,", font=Fs, fill=grey)
dr.text((W - 1120, 162), "its central pair {A, A\u0304}; twins sorted left-to-right by defiance.", font=Fs, fill=grey)
dr.text((W - 1120, 196), "gold owns a country below; ice owns nothing — yet every", font=Fs, fill=cyan)
dr.text((W - 1120, 230), "ice star's twin is landed: one central swap from a measure.", font=Fs, fill=cyan)
gy = int(H * 0.560)
dr.text((70, gy), "the country of measures: a plane through the simplex of weights,", font=Fs, fill=grey)
dr.text((70, gy + 34), "cut by all 121 walls  Σ_A x = Σ_B x ;  every pane is one order,", font=Fs, fill=grey)
dr.text((70, gy + 68), "hue = how far the pane's order defies mere size |A|", font=Fs, fill=grey)
wy = H - 300
dr.text((70, wy), "one landless order, its exact witness:", font=Fi, fill=cyan)
dr.text((70, wy + 40), "{1,2} < {3}     {2,3} < {1,4}", font=F, fill=cyan)
dr.text((70, wy + 84), "{5} < {1,2,3}   {1,3,4} < {2,5}", font=F, fill=cyan)
dr.text((70, wy + 130), "four confident judgements whose two sides weigh", font=Fi, fill=grey)
dr.text((70, wy + 168), "the same multiset — no measure can grant all four.", font=Fi, fill=grey)
out.save("art_aoy6/fifth_atom_2560.png")
print("saved art_aoy6/fifth_atom_2560.png")
