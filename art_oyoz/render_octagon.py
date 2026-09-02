"""render_octagon.py — THE LOOM OF THE OCTAGON (pastel ribbons).

Every periodic direction of the regular-octagon translation surface is a set of
cylinders; each cylinder is painted as a ribbon of its closed straight trajectories,
brightness sin(πu)^0.8 across the cylinder height, hue by direction, weight by
1/(shortest saddle length)^2.2 so the short directions lead and the long ones haze.
"""
import sys, json, time, argparse
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter
sys.path.insert(0, '.')
from pastel import Watercolor, absorption, _blur
import octagon as oc

t0 = time.time()
def log(*a): print(f'[{time.time() - t0:7.1f}s]', *a, flush=True)

ap = argparse.ArgumentParser()
ap.add_argument('--S', type=int, default=1600)
ap.add_argument('--final', type=int, default=800)
ap.add_argument('--data', default='octagon_test.json')
ap.add_argument('--out', default='octagon_proto.png')
ap.add_argument('--maxdirs', type=int, default=400)
ap.add_argument('--power', type=float, default=2.2)
ap.add_argument("--seed", type=int, default=3); ap.add_argument("--hunit", type=float, default=0.15)
args = ap.parse_args()
S = args.S; rs = S / 1600.0
rng = np.random.default_rng(args.seed)

PIGS = [absorption(h) for h in ['#f4917f', '#f7be7a', '#f3df8a', '#c6df95', '#9fdcc2', '#93d4e3', '#97b8ee', '#bcaaea', '#e6a9d9']]
INK = absorption('#57505b'); GRAPH = absorption('#8b93a3'); CORAL = absorption('#ef7d6a')

data = json.load(open(args.data))
data.sort(key=lambda x: (round(x['shortest'], 6), x['theta']))
data = data[:args.maxdirs]
lmin = data[0]['shortest']
log(len(data), 'directions; shortest', lmin, 'longest', data[-1]['shortest'])

# geometry -> pixels: octagon centred, circumradius = 0.40 S
cx = cy = S / 2; scale = 0.40 * S / oc.R
def topix(P):
    P = np.asarray(P, float)
    return np.stack([cx + P[..., 0] * scale, cy - P[..., 1] * scale], -1)

fields = [np.zeros((S, S), np.float32) for _ in PIGS]
def splat_segments(field, A, B, w):
    """additive bilinear splat of dense samples along segments A->B (N,2 px), per-segment weight w (N,)"""
    L = np.hypot(*(B - A).T)
    nper = np.maximum(2, np.ceil(L / 0.7)).astype(int)
    tot = int(nper.sum())
    idx = np.repeat(np.arange(len(A)), nper)
    # parametric t within each segment
    starts = np.cumsum(nper) - nper
    t = (np.arange(tot) - starts[idx] + 0.5) / nper[idx]   # open sampling: no double weight at chord junctions
    P = A[idx] + (B[idx] - A[idx]) * t[:, None]
    wt = np.repeat(w * 0.7, nper)   # weight per unit length
    x0 = np.floor(P[:, 0]).astype(int); y0 = np.floor(P[:, 1]).astype(int)
    fx = (P[:, 0] - x0).astype(np.float32); fy = (P[:, 1] - y0).astype(np.float32)
    H, W = field.shape
    for dx, wx in ((0, 1 - fx), (1, fx)):
        for dy, wy in ((0, 1 - fy), (1, fy)):
            xx = x0 + dx; yy = y0 + dy
            m = (xx >= 0) & (xx < W) & (yy >= 0) & (yy < H)
            field.ravel()[:] += np.bincount((yy[m] * W + xx[m]), weights=(wt * wx * wy)[m], minlength=H * W).astype(np.float32)

# ---- stripes: per cylinder, k ribbons spread across its height (a weave, not a fill)
CLASS_A = [absorption(h) for h in ['#f28b74', '#f6b673', '#e9a2d3', '#f2b3c0']]   # diagonal cusp (ratio 1): warm
CLASS_B = [absorption(h) for h in ['#88cfe0', '#8fb0ec', '#95d6b8', '#b7a6e6']]   # side cusp (ratio 2): cool
FAR = [absorption(h) for h in ['#c9dea3', '#a9b7c9', '#d9c7a6']]
fields = {}
def fld(key):
    if key not in fields: fields[key] = np.zeros((S, S), np.float32)
    return fields[key]
nseg_total = 0
classes = sorted(set(round(d['shortest'], 4) for d in data))
log('length classes:', classes)
for i, dd in enumerate(data):
    l = round(dd['shortest'], 4); ci = classes.index(l)
    amp = (lmin / dd['shortest']) ** args.power
    if ci == 0: pig = ('A', i % 4)
    elif ci == 1: pig = ('B', i % 4)
    elif ci <= 3: pig = ('F', ci % 3)
    else: continue
    A = []; B = []; Wt = []
    for cyl in dd['members']:
        us = np.array([m['u'] for m in cyl]); H = dd['H'][dd['members'].index(cyl)]
        k = int(max(2, round(H / args.hunit)))
        targets = (np.arange(k) + 0.5) / k
        for ut in targets:
            m = cyl[int(np.argmin(np.abs(us - ut)))]
            env = np.sin(np.pi * m['u']) ** 0.7
            loop = np.array(m['loop'])
            A.append(loop[:, 0]); B.append(loop[:, 1]); Wt.append(np.full(len(loop), amp * env))
    if not A: continue
    A = topix(np.concatenate(A)); B = topix(np.concatenate(B)); Wt = np.concatenate(Wt).astype(np.float32)
    nseg_total += len(A)
    splat_segments(fld(pig), A, B, Wt)
log('segments splatted:', nseg_total)
wc = Watercolor(S, S, seed=args.seed, warm=1.0)
# normalise: the strongest field sets the scale
blurred = {k: gaussian_filter(f, 2.6 * rs) for k, f in fields.items()}
peak = max(np.percentile(f[f > 0], 99.0) if (f > 0).any() else 1 for f in blurred.values())
for key, g in blurred.items():
    pg = {'A': CLASS_A, 'B': CLASS_B, 'F': FAR}[key[0]][key[1]]
    g = g / peak
    g = 1.0 - np.exp(-1.8 * g)          # soft knee in density
    wc.wash(g.astype(np.float32), pg, strength=1.05 if key[0] != 'F' else 0.7, granulate=0.15, edge=0.25, edge_sigma=2.0 * rs)
log('ribbons washed')

# octagon rim + saddle connections of the 4 shortest direction classes as fine ink; cone point beads
ink = np.zeros((S, S), np.float32)
im = Image.new('F', (S, S), 0.0); dr = ImageDraw.Draw(im)
poly = [tuple(p) for p in topix(oc.V)]
dr.polygon(poly + [poly[0]], outline=1.0, width=max(1, int(2.2 * rs)))
ink += np.array(im)
wc.wash(gaussian_filter(ink, 0.8 * rs), INK, strength=1.2)
sad = np.zeros((S, S), np.float32)
for dd in data:
    if round(dd['shortest'], 4) > classes[1] + 1e-6: continue
    for k, (chords, total, hit, q) in oc.shoot_from_cone(dd['theta'], 60.0):
        A = topix(np.array([a for a, b in chords])); B = topix(np.array([b for a, b in chords]))
        splat_segments(sad, A, B, np.full(len(A), 1.0, np.float32))
wc.wash(gaussian_filter(sad, 0.9 * rs) * 0.9, GRAPH, strength=0.9)
# beads at the 8 corners = ONE cone point
bead = np.zeros((S, S), np.float32)
yy, xx = np.mgrid[0:S, 0:S]
for p in topix(oc.V):
    r2 = (xx - p[0]) ** 2 + (yy - p[1]) ** 2
    bead += np.exp(-r2 / (2 * (4.5 * rs) ** 2))
wc.wash(bead, CORAL, strength=1.3)
log('rim + beads done')

# caption
def text_mask(lines, sizes, y0, x0, faces):
    mk = Image.new('L', (S, S), 0); dr = ImageDraw.Draw(mk); y = y0
    for txt, sz, face in zip(lines, sizes, faces):
        f = ImageFont.truetype(face, int(sz)); dr.text((x0, y), txt, fill=255, font=f); y += int(sz * 1.35)
    return np.array(mk, np.float32) / 255.0
r1 = sum(1 for d in data if abs(d['ratio'][-1] - 1) < 1e-3); r2 = sum(1 for d in data if abs(d['ratio'][-1] - 2) < 1e-3)
cap = text_mask(['THE LOOM OF THE OCTAGON',
                 f'regular-octagon translation surface · {len(data)} periodic directions verified, each exactly two cylinders · warm = diagonal cusp (moduli 1:1), cool = side cusp (moduli 1:2) · coral = the one cone point'],
                [0.026 * S, 0.0098 * S], S - int(0.075 * S), int(0.03 * S),
                ['/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'])
wc.wash(cap, INK, strength=1.6)
wc.save(args.out, final_size=(args.final, args.final), dmax=2.4)
log('saved', args.out)
