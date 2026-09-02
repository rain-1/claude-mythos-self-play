"""render_spectre.py — WHICH LEVEL DECIDES (hero, pastel watercolor).

A window onto a level-5 Spectre supertile (the 2023 chiral aperiodic monotile):
every tile is the SAME shape, rotated only, never reflected.  The hierarchy that
the tiles force (and that forces the tiles) is painted from above:
  * base pigment      = the label of the tile's level-2 supertile (9 pastel pigments)
  * lightness rhythm  = its level-1 supertile (random per supertile) and a per-tile jitter
  * coral blossoms    = the 30°-turned partner tile of every 'Mystic' pair (share 1/(4+√15)... measured)
  * ink               = tile edges (fine graphite) < level-1 < level-2 < level-3 borders (ink + halo glaze)
Subtractive stack from pastel.py (Beer–Lambert glazes on paper).
"""
import sys, time, argparse
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import distance_transform_edt, gaussian_filter
sys.path.insert(0, '.')
import spectre as sp
from pastel import Watercolor, absorption, _blur, srgb_to_linear

t0 = time.time()
def log(*a):
    print(f'[{time.time() - t0:7.1f}s]', *a, flush=True)

ap = argparse.ArgumentParser()
ap.add_argument('--S', type=int, default=2048)        # render size (supersampled)
ap.add_argument('--final', type=int, default=1024)
ap.add_argument('--level', type=int, default=5)
ap.add_argument('--ntiles', type=float, default=3400)  # tiles per full frame
ap.add_argument('--bulge', type=float, default=0.5)
ap.add_argument('--seed', type=int, default=7)
ap.add_argument('--out', default='spectre_proto.png')
ap.add_argument('--cx', type=float, default=0.5)      # window centre as fraction of patch bbox
ap.add_argument('--cy', type=float, default=0.5)
args = ap.parse_args()
S = args.S; rs = S / 2048.0
rng = np.random.default_rng(args.seed)

# ------------------------------------------------------------------ pigments (a fresh, brighter box)
PIG = {
    'coral':      absorption('#f4917f'),
    'apricot':    absorption('#f7be7a'),
    'lemon':      absorption('#f3df8a'),
    'pistachio':  absorption('#c6df95'),
    'mint':       absorption('#9fdcc2'),
    'aqua':       absorption('#93d4e3'),
    'cornflower': absorption('#97b8ee'),
    'lavender':   absorption('#bcaaea'),
    'orchid':     absorption('#e6a9d9'),
    'blush':      absorption('#f5b6c4'),
    'graphite':   absorption('#8b93a3'),
    'ink':        absorption('#57505b'),
}
LABEL_PIG = {'Gamma': 'lemon', 'Delta': 'aqua', 'Theta': 'orchid', 'Lambda': 'coral',
             'Xi': 'pistachio', 'Pi': 'cornflower', 'Sigma': 'apricot', 'Phi': 'mint', 'Psi': 'lavender'}

# ------------------------------------------------------------------ tiles
log('building level', args.level)
tl = sp.tiles(args.level, root='Delta')
log(len(tl), 'tiles')
paths = [p for p, _, _ in tl]
ipaths = [ip for _, ip, _ in tl]
Ts = np.stack([T for _, _, T in tl])           # (n,2,3)
# curved outline in tile-local coords (Kaplan's CurvyShape, bulge param)
def curvy(pts, bulge, nseg=10):
    out = []
    prev = pts[-1]; sign = 1.0
    ts = np.linspace(0, 1, nseg, endpoint=False)[1:]
    for p in pts:
        v = p - prev; w = np.array([-v[1], v[0]])
        c1 = prev + 0.33 * v + sign * bulge * w
        c2 = prev + 0.67 * v + sign * bulge * w
        out.append(prev)
        for t in ts:
            b = (1 - t) ** 3 * prev + 3 * (1 - t) ** 2 * t * c1 + 3 * (1 - t) * t ** 2 * c2 + t ** 3 * p
            out.append(b)
        sign = -sign; prev = p
    return np.array(out)
local = curvy(sp.SPECTRE, args.bulge)
a0 = abs(sp.shoelace(sp.SPECTRE))
polys = np.einsum('nij,kj->nki', Ts[:, :, :2], local) + Ts[:, None, :, 2]   # (n,k,2)
cent = polys.mean(1)
lo = cent.min(0); hi = cent.max(0)
Wd = np.sqrt(args.ntiles * a0)   # world width of the frame
# deepest interior point of the patch (coarse occupancy grid of tile centroids -> EDT)
cell = np.sqrt(a0) * 0.9
G = np.ceil((hi - lo) / cell).astype(int) + 3
occ = np.zeros((G[1], G[0]), bool)
gi = ((cent - lo) / cell).astype(int) + 1
occ[gi[:, 1], gi[:, 0]] = True
from scipy.ndimage import binary_closing
occ = binary_closing(occ, iterations=2)
dpt = distance_transform_edt(occ)
if args.cx == 0.5 and args.cy == 0.5:
    j, i = np.unravel_index(np.argmax(dpt), dpt.shape)
    c = lo + (np.array([i, j]) - 1 + 0.5) * cell
    log(f'deepest interior point {c}, depth {dpt.max() * cell:.1f} world units; frame half-width {Wd / 2:.1f}')
else:
    c = lo + (hi - lo) * np.array([args.cx, args.cy])
scale = S / Wd
pix = (polys - (c - Wd / 2)) * scale        # world -> pixel
pix[..., 1] = S - pix[..., 1]               # y up
keep = np.nonzero((pix[..., 0].max(1) > -4) & (pix[..., 0].min(1) < S + 4) &
                  (pix[..., 1].max(1) > -4) & (pix[..., 1].min(1) < S + 4))[0]
log('tiles in frame:', len(keep), ' tile px width ~', np.sqrt(a0) * scale)
pix = pix[keep]; paths = [paths[i] for i in keep]; ipaths = [ipaths[i] for i in keep]
n = len(keep)

# ------------------------------------------------------------------ id map + ancestor ids
im = Image.new('I', (S, S), 0)
d = ImageDraw.Draw(im)
for i in range(n):
    d.polygon([tuple(map(float, q)) for q in pix[i]], fill=int(i + 1))
idmap = np.array(im, np.int32)
holes = (idmap == 0).sum()
log('idmap done; uncovered px:', holes)
if holes > 0:
    # fill hairline gaps with nearest id
    _, (iy, ix) = distance_transform_edt(idmap == 0, return_indices=True)
    idmap = idmap[iy, ix]
idmap -= 1

# the Gamma 'Mystic' is a PAIR of tiles one level below the others: normalise so that
# level k >= 1 means the level-k supertile for every tile (Gamma tiles carry one extra index)
gam = np.array([p[1] == 'Gamma' for p in paths])
def ancestor_ids(k):
    """id of the level-k ancestor of each tile (k=0: the tile itself)."""
    keyd = {}
    out = np.zeros(n, np.int32)
    for i, ip in enumerate(ipaths):
        key = ip if k == 0 else ip[k + int(gam[i]):]
        out[i] = keyd.setdefault(key, len(keyd))
    return out
anc = [ancestor_ids(k) for k in range(0, 4)]
leaf_label = np.array([p[0] for p in paths])
anc1_label = np.array([p[1 + int(g)] for p, g in zip(paths, gam)])
anc2_label = np.array([p[2 + int(g)] for p, g in zip(paths, gam)])
anc3_label = np.array([p[3 + int(g)] for p, g in zip(paths, gam)])
log('ancestors: level-1 patches', anc[1].max() + 1, 'level-2', anc[2].max() + 1, 'level-3', anc[3].max() + 1)

def boundary_dist(ids):
    """distance (px) from every pixel to the nearest boundary between different ids."""
    f = ids[idmap]
    b = np.zeros((S, S), bool)
    b[:, :-1] |= f[:, :-1] != f[:, 1:]
    b[:-1, :] |= f[:-1, :] != f[1:, :]
    dist = distance_transform_edt(~b).astype(np.float32)
    return dist
tile_px = np.sqrt(a0) * scale

# ------------------------------------------------------------------ paint
wc = Watercolor(S, S, seed=args.seed, warm=1.0)
# base wash by level-2 label, lightness by level-1 patch + per-tile jitter
l1_gain = rng.uniform(0.72, 1.18, anc[1].max() + 1).astype(np.float32)
l3_gain = rng.uniform(0.85, 1.12, anc[3].max() + 1).astype(np.float32)
tile_gain = rng.uniform(0.86, 1.14, n).astype(np.float32)
gain = (l1_gain[anc[1]] * tile_gain * l3_gain[anc[3]]).astype(np.float32)
d0 = boundary_dist(anc[0])
pool = np.exp(-d0 / (0.09 * tile_px)).astype(np.float32)          # pigment pooling at tile rims
interior = (1.0 - 0.35 * np.exp(-d0 / (0.28 * tile_px))).astype(np.float32)  # lighter centres
log('rim fields done')
labels9 = list(LABEL_PIG.keys())
for lab in labels9:
    sel = np.nonzero(anc2_label == lab)[0]
    if len(sel) == 0:
        continue
    m = np.zeros(n, np.float32); m[sel] = 1.0
    field = m[idmap] * gain[idmap] * (0.70 * interior + 0.30 * pool)
    wc.wash(field, PIG[LABEL_PIG[lab]], strength=0.9, granulate=0.22)
    del field
# a gentle unifying glaze: warm light falling from the upper left
yy, xx = np.mgrid[0:S, 0:S].astype(np.float32) / S
wc.wash((0.25 + 0.75 * (0.5 * xx + 0.5 * yy)).astype(np.float32), PIG['blush'], strength=0.16)
del xx, yy
log('base washes done')
# coral blossoms: the 30°-turned Mystic partners
m = np.zeros(n, np.float32); m[leaf_label == 'Gamma2'] = 1.0
field = m[idmap] * (0.6 * interior + 0.35 * pool)
wc.wash(field, PIG['coral'], strength=0.85, granulate=0.3)
share_g2 = float(np.mean(leaf_label == 'Gamma2'))
del field, m
log('blossoms done; Gamma2 share in frame', share_g2)
# ink hierarchy
def ink_line(dist, width, strength, pig):
    line = np.exp(-(dist / width) ** 2).astype(np.float32)
    wc.wash(line, PIG[pig], strength=strength)
    del line
ink_line(d0, 0.5 * rs, 0.2, 'graphite')
del d0
d1 = boundary_dist(anc[1]); ink_line(d1, 0.8 * rs, 0.38, 'graphite'); del d1
d2 = boundary_dist(anc[2]); ink_line(d2, 1.3 * rs, 0.75, 'ink')
halo = _blur(np.exp(-(d2 / (3 * rs)) ** 2).astype(np.float32), 6 * rs); wc.wash(halo * 0.9, PIG['ink'], strength=0.07); del d2, halo
d3 = boundary_dist(anc[3]); ink_line(d3, 2.2 * rs, 1.05, 'ink')
halo = _blur(np.exp(-(d3 / (5 * rs)) ** 2).astype(np.float32), 14 * rs); wc.wash(halo * 1.6, PIG['ink'], strength=0.12); del d3, halo
log('ink done')
yy, xx = np.mgrid[0:S, 0:S].astype(np.float32) / S
edge = np.minimum(np.minimum(xx, 1 - xx), np.minimum(yy, 1 - yy))          # distance to frame (0..0.5)
noise = _blur(rng.standard_normal((S // 8, S // 8)).astype(np.float32), 6 * rs)
from scipy.ndimage import zoom as _zoom
noise = _zoom(noise, 8, order=1)[:S, :S]; noise = 0.035 * noise / (noise.std() + 1e-9)
front = np.clip((edge + noise - 0.035) / 0.11, 0, 1); front = front * front * (3 - 2 * front)
wc.D *= (0.12 + 0.88 * front)[..., None]
del xx, yy, edge, noise, front
log('unfinished edge done')

# ------------------------------------------------------------------ caption (ink-density wash, before develop)
def text_mask(lines, sizes, y0, x0):
    mk = Image.new('L', (S, S), 0)
    dr = ImageDraw.Draw(mk)
    y = y0
    for txt, sz, face in zip(lines, sizes, ['/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf',
                                            '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf',
                                            '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf']):
        try:
            f = ImageFont.truetype(face, int(sz))
        except Exception as e:
            print('font fail', face, e); f = ImageFont.load_default()
        dr.text((x0, y), txt, fill=255, font=f)
        y += int(sz * 1.35)
    return np.array(mk, np.float32) / 255.0
pad = int(0.018 * S)
cap = text_mask(['WHICH LEVEL DECIDES',
                 f'the Spectre, one chiral tile · {n:,} tiles in frame, rotated only, never reflected · '
                 f'ink weight = supertile level · coral = the 30°-turned partner of every Mystic ({share_g2 * 100:.1f}%)'],
                [0.022 * S, 0.0105 * S], S - int(0.062 * S), pad)
# paper strip behind caption: lighten the density there so text sits on paper
strip = np.zeros((S, S), np.float32); strip[S - int(0.075 * S):, :] = 1.0
strip = _blur(strip, 6 * rs)
wc.D *= (1.0 - 0.82 * strip)[..., None]
wc.wash(cap, PIG['ink'], strength=1.6)
log('caption done')
wc.save(args.out, final_size=(args.final, args.final), dmax=2.4)
log('saved', args.out)
