"""render_affine.py — ONE CUT, TWO OF THE SAME (specimen sheet, 2560²).

Nine convex polygons, each cut into two pieces by one polygonal cut (coral).  Where a two-piece
affine dissection exists, piece 2 is the exact affine image of piece 1: the rings drawn in piece 1
(concentric circles about its centroid) are carried by the same map into piece 2, where they become
concentric ellipses — the same drawing, affinely.  Where no dissection exists (generic pentagons,
a generic hexagon), the best cut the search found is shown with the image of piece 1 laid over piece 2
in ink: the sliver that does not fit is the theorem.

usage: python3 render_affine.py FINAL out.png
"""
import sys, json, time
import numpy as np
from scipy.ndimage import gaussian_filter, distance_transform_edt
from PIL import Image, ImageDraw
from shapely.geometry import Polygon, Point, LineString
from shapely.ops import unary_union
from pastel import Sheet, PIG, absorb, text_density, text_width, ink_from_distance, finish, wrap
import affine as af

FINAL = int(sys.argv[1]) if len(sys.argv) > 1 else 1024
out = sys.argv[2] if len(sys.argv) > 2 else f'cache/affine_{FINAL}.png'
SS = 2
W = H = FINAL * SS
rs = FINAL / 1024 * SS
t0 = time.time()
import glob
data = json.load(open('cache/affine_search_part1.json'))
for fn in glob.glob('cache/affine_*.json'):
    if 'part1' in fn or 'cert' in fn or 'search' in fn: continue
    data.update(json.load(open(fn)))

sh = Sheet(W, H, seed=33)


def _bbox(pts, pad):
    x0 = int(max(0, pts[:, 0].min() - pad)); x1 = int(min(W, pts[:, 0].max() + pad))
    y0 = int(max(0, pts[:, 1].min() - pad)); y1 = int(min(H, pts[:, 1].max() + pad))
    return x0, x1, y0, y1


def add_poly(pts, dens, tint, blur=0.8):
    """fill a polygon (screen px) into the sheet's absorbance within its bbox"""
    pts = np.asarray(pts, float)
    x0, x1, y0, y1 = _bbox(pts, 6)
    if x1 - x0 < 2 or y1 - y0 < 2:
        return
    im = Image.new('F', (x1 - x0, y1 - y0), 0.0)
    ImageDraw.Draw(im).polygon([(float(x - x0), float(y - y0)) for x, y in pts], fill=1.0)
    a = gaussian_filter(np.asarray(im, np.float32), blur) if blur else np.asarray(im, np.float32)
    sh.A[y0:y1, x0:x1] += (dens * a)[..., None] * absorb(PIG[tint])[None, None, :]


def add_line(pts, width, dens, tint, closed=False):
    pts = np.asarray(pts, float)
    if len(pts) < 2:
        return
    x0, x1, y0, y1 = _bbox(pts, int(width * 3 + 4))
    if x1 - x0 < 2 or y1 - y0 < 2:
        return
    im = Image.new('F', (x1 - x0, y1 - y0), 0.0)
    p = [(float(x - x0), float(y - y0)) for x, y in pts]
    if closed:
        p.append(p[0])
    ImageDraw.Draw(im).line(p, fill=1.0, width=int(max(1, round(width))), joint='curve')
    a = gaussian_filter(np.asarray(im, np.float32), 0.5)
    sh.A[y0:y1, x0:x1] += (dens * a)[..., None] * absorb(PIG[tint])[None, None, :]


# ---- the nine cells ----
order = [('triangle', 'a triangle: any cevian — two triangles are always affine twins'),
         ('random_quadrilateral', 'a generic quadrilateral: count 4 − n = 0, finitely many cuts'),
         ('regular_pentagon', 'the regular pentagon: its mirror axis, or any mirror-symmetric zigzag'),
         ('affine_regular_pentagon', 'an affinely regular pentagon: the axis went with the map'),
         ('affine_mirror_pentagon', 'a mirror-symmetric pentagon, squashed: still cut by its (affine) axis'),
         ('regular_hexagon', 'the regular hexagon: any zigzag through the centre, turned by a half-turn'),
         ('random_pentagon', 'a generic pentagon: the best of all two-piece cuts (m ≤ 4) misses — ink: the image of the warm piece'),
         ('random_pentagon_2', 'another generic pentagon: misses; the residual floor is a certified minimum, not a search failure'),
         ('random_hexagon', 'a generic hexagon: misses (count 4 − n = −2)')]

# a triangle case (not in the search: a cevian from vertex 0 to the midpoint of the opposite edge)
tri = np.array([[-0.9, -0.7], [1.0, -0.6], [0.15, 1.0]])
data['triangle'] = dict(Q=tri.tolist(), best_by_m={'0': dict(p_corner=True, i=2, q_corner=False, j=0, m=0,
                        residual=0.0, valid=True, p=tri[2].tolist(), q=((tri[0] + tri[1]) / 2 + 0.12 * (tri[1] - tri[0])).tolist(),
                        bps=[], nverts=3, P1=None, P2=None)})

# exact constructions for the symmetric cases (verified below by the same residual as the search)
def synth(name, Q, pc, i, qc, j, p, q, bps):
    Q = np.asarray(Q, float); p = np.asarray(p, float); q = np.asarray(q, float); bps = np.asarray(bps, float).reshape(-1, 2)
    P1, P2, _, _ = af.pieces(Q, p, i, q, j, bps, pc, qc)
    res, corr = af.best_correspondence(P1, P2)
    diam = max(np.linalg.norm(a - b) for a in Q for b in Q)
    print('synth', name, 'residual', res / diam ** 2)
    data[name] = dict(Q=Q.tolist(), best_by_m={str(len(bps)): dict(p_corner=pc, i=i, q_corner=qc, j=j, m=len(bps),
                      residual=res / diam ** 2, valid=True, p=p.tolist(), q=q.tolist(), bps=bps.tolist(), nverts=len(P1))})

_hex = af.regular(6)
_p = _hex[0] + 0.38 * (_hex[1] - _hex[0]); _b1 = np.array([0.30, 0.22])
synth('regular_hexagon', _hex, False, 0, False, 3, _p, -_p, [_b1, -_b1])
_quad = af.random_convex(4, np.random.default_rng(3))
synth('random_quadrilateral', _quad, True, 0, True, 2, _quad[0], _quad[2], [])
_v1 = np.array([0.55, 0.35]); _v2 = np.array([0.8, -0.6])
_sym = np.array([[0, 1.0], [-_v1[0], _v1[1]], [-_v2[0], _v2[1]], [_v2[0], _v2[1]], [_v1[0], _v1[1]]])
_S = np.array([[1.25, 0.6], [-0.35, 0.8]])
_amp = _sym @ _S.T
synth('affine_mirror_pentagon', _amp, True, 0, False, 2, _amp[0], 0.5 * (_amp[2] + _amp[3]), [])

cell = W / 3
pad = 0.13 * cell
for idx, (name, blurb) in enumerate(order):
    cx = (idx % 3 + 0.5) * cell
    cy = 0.06 * H + (idx // 3 + 0.5) * (0.80 * H / 3)
    if name not in data:
        print('missing', name); continue
    d = data[name]
    Q = np.array(d['Q'])
    # best dissection: smallest residual among valid m; prefer m=2 for the symmetric ones (prettier zigzag)
    bym = {int(k): v for k, v in d['best_by_m'].items()}
    exact = [m for m, v in bym.items() if v['residual'] < 1e-12 and v['valid']]
    if exact:
        m_pick = min(exact)   # the least cut that works (bent zigzags only exist for central symmetry, built exactly above)
    else:
        m_pick = min(bym, key=lambda m: bym[m]['residual'] if bym[m]['valid'] else 9)
    best = bym[m_pick]
    p = np.array(best['p']); q = np.array(best['q']); bps = np.array(best['bps']).reshape(-1, 2)
    n = len(Q)
    P1, P2, a1, a2 = af.pieces(Q, p, best['i'], q, best['j'], bps, best['p_corner'], best['q_corner'])
    res, corr = af.best_correspondence(P1, P2)
    rev, r, A_, b_ = corr
    A_ = np.array(A_); b_ = np.array(b_)
    # fit to the cell: centre the polygon's centroid, scale to 0.74 cell
    cen = Polygon(Q).centroid; cen = np.array([cen.x, cen.y])
    ext = max(np.abs(Q - cen).max(0)) * 2.0
    s = (cell - 2 * pad) / ext

    def T(pts):
        pts = np.asarray(pts, float)
        return np.stack([cx + s * (pts[:, 0] - cen[0]), cy - s * (pts[:, 1] - cen[1])], 1)

    # washes: piece 1 warm, piece 2 cool
    add_poly(T(P1), 0.38, 'apricot'); add_poly(T(P2), 0.38, 'aqua')
    # rings in piece 1 about its centroid, and their affine images in piece 2
    c1 = Polygon(P1).centroid; c1 = np.array([c1.x, c1.y])
    rmax = max(np.linalg.norm(P1 - c1, axis=1))
    poly1 = Polygon(P1); poly2 = Polygon(P2)
    ang = np.linspace(0, 2 * np.pi, 240)
    ring_abs = absorb(PIG['orchid'])
    for k in range(1, 8):
        rr = rmax * k / 7.5
        circ = np.stack([c1[0] + rr * np.cos(ang), c1[1] + rr * np.sin(ang)], 1)
        img = circ @ A_.T + b_
        for pts, poly in ((circ, poly1), (img, poly2)):
            # clip to the piece: draw runs of points inside
            inside = np.array([poly.contains(Point(x, y)) for x, y in pts])
            runs = []; st_ = None
            for i2, f in enumerate(inside):
                if f and st_ is None: st_ = i2
                if (not f) and st_ is not None: runs.append((st_, i2)); st_ = None
            if st_ is not None: runs.append((st_, len(inside)))
            for a, b in runs:
                if b - a > 1:
                    add_line(T(pts[a:b]), 1.5 * rs, 0.95, 'orchid')
    # for the misses: the image of piece 1 over piece 2 as ink, and the misfit as coral wash
    miss = res > 1e-10
    area_misfit = 0.0
    if miss:
        img1 = P1 @ A_.T + b_
        pim = Polygon(img1)
        if pim.is_valid and poly2.is_valid:
            diff = pim.symmetric_difference(poly2)
            area_misfit = diff.area / Polygon(Q).area
            polys = [diff] if diff.geom_type == 'Polygon' else list(getattr(diff, 'geoms', []))
            for g in polys:
                if g.geom_type == 'Polygon' and g.area > 1e-9:
                    add_poly(T(np.array(g.exterior.coords)), 0.75, 'coral')
        add_line(T(img1), 1.3 * rs, 0.8, 'ink', closed=True)
    # outlines: polygon in ink, cut in coral
    add_line(T(Q), 2.0 * rs, 0.95, 'ink', closed=True)
    cutpts = np.vstack([p[None], bps, q[None]])
    add_line(T(cutpts), 3.2 * rs, 1.1, 'coral')
    add_line(T(cutpts), 1.0 * rs, 0.5, 'ink')
    # label
    mism = np.sqrt(res)   # relative to the diameter (res already normalised by diam² in the search? no: raw)
    diam = max(np.linalg.norm(a - b) for a in Q for b in Q)
    mism = np.sqrt(res) / diam
    tag = ('exact' if not miss else f'misses: {100 * mism:.2f} % of diameter, {100 * area_misfit:.2f} % of area')
    lab = f'{blurb}'
    lines = wrap(lab, 10.5 * rs, 'italic', cell - 1.2 * pad)
    items = []
    y0 = cy + 0.5 * (cell - 2 * pad) * 0.92 + 6 * rs
    for i2, ln in enumerate(lines):
        items.append((ln, cx, y0 + i2 * 12.5 * rs, 10.5 * rs, 'italic', 'mm'))
    items.append((tag + (f'   (m = {m_pick}, {len(P1)}-gons)' if not miss else ''), cx, y0 + len(lines) * 12.5 * rs + 1 * rs, 9.5 * rs, 'mono', 'mm'))
    sh.wash(text_density(W, H, items) * 0.9, 'ink')
    print(name, 'm', m_pick, 'res', res, 'miss', mism, 'area_misfit', area_misfit, round(time.time() - t0, 1))

# ---- caption ----
sh.caption_strip(0.905, 0.985, 0.62)
title = 'One Cut, Two of the Same'
sub = ('Cut a convex polygon into two pieces that are affine images of each other (MO 515243). Rings drawn in one piece are carried '
       'by the map into the other. Counting cut parameters against vertex equations leaves 4 − n degrees of freedom: '
       'triangles and quadrilaterals always, symmetric polygons by their symmetry, and a generic pentagon or hexagon never.')
items = [(title, W * 0.5, H * 0.925, 30 * rs, 'serif_bold', 'mm')]
lines = wrap(sub, 14.5 * rs, 'italic', 0.84 * W)
for i, ln in enumerate(lines):
    items.append((ln, W * 0.5, H * (0.950 + 0.018 * i), 14.5 * rs, 'italic', 'mm'))
sh.wash(text_density(W, H, items) * 0.95, 'ink')
img = sh.develop()
finish(img, (FINAL, FINAL), out)
print('done', time.time() - t0)
