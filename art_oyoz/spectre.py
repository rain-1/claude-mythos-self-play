"""spectre.py — the Spectre aperiodic monotile (Smith–Myers–Kaplan–Goodman-Strauss 2023),
ported from Craig Kaplan's public spectre.js substitution rules.

Produces a flat list of tiles: (path_of_labels, 2x3 affine, is_gamma2) where the path
records the label of the tile's ancestor at every substitution level (level 0 = the
tile's own label inside its level-1 supertile).  The whole hierarchy is thus carried
by every leaf — that is what the hero piece paints.

Verification functions at the bottom: chirality (every tile is a PROPER rigid motion
of one polygon — the monotile is chiral), non-overlap by rasterization, and the
substitution matrix / Perron eigenvalue.
"""
import numpy as np

SQ3 = np.sqrt(3.0)
SPECTRE = np.array([
    (0, 0), (1.0, 0.0), (1.5, -0.8660254037844386),
    (2.366025403784439, -0.36602540378443865), (2.366025403784439, 0.6339745962155614),
    (3.366025403784439, 0.6339745962155614), (3.866025403784439, 1.5), (3.0, 2.0),
    (2.133974596215561, 1.5), (1.6339745962155614, 2.3660254037844393),
    (0.6339745962155614, 2.3660254037844393), (-0.3660254037844386, 2.3660254037844393),
    (-0.866025403784439, 1.5), (0.0, 1.0)], float)
KEY_IDX = [3, 5, 7, 11]
LABELS = ['Gamma', 'Delta', 'Theta', 'Lambda', 'Xi', 'Pi', 'Sigma', 'Phi', 'Psi']
SUPER_RULES = {
    'Gamma':  ['Pi', 'Delta', None, 'Theta', 'Sigma', 'Xi', 'Phi', 'Gamma'],
    'Delta':  ['Xi', 'Delta', 'Xi', 'Phi', 'Sigma', 'Pi', 'Phi', 'Gamma'],
    'Theta':  ['Psi', 'Delta', 'Pi', 'Phi', 'Sigma', 'Pi', 'Phi', 'Gamma'],
    'Lambda': ['Psi', 'Delta', 'Xi', 'Phi', 'Sigma', 'Pi', 'Phi', 'Gamma'],
    'Xi':     ['Psi', 'Delta', 'Pi', 'Phi', 'Sigma', 'Psi', 'Phi', 'Gamma'],
    'Pi':     ['Psi', 'Delta', 'Xi', 'Phi', 'Sigma', 'Psi', 'Phi', 'Gamma'],
    'Sigma':  ['Xi', 'Delta', 'Xi', 'Phi', 'Sigma', 'Pi', 'Lambda', 'Gamma'],
    'Phi':    ['Psi', 'Delta', 'Psi', 'Phi', 'Sigma', 'Pi', 'Phi', 'Gamma'],
    'Psi':    ['Psi', 'Delta', 'Psi', 'Phi', 'Sigma', 'Psi', 'Phi', 'Gamma']}
T_RULES = [(60, 3, 1), (0, 2, 0), (60, 3, 1), (60, 3, 1), (0, 2, 0), (60, 3, 1), (-120, 3, 3)]

# ---- affine helpers: M = [[a,b,c],[d,e,f]]
def ident():
    return np.array([[1., 0., 0.], [0., 1., 0.]])

def mul(A, B):
    A3 = np.vstack([A, [0, 0, 1]]); B3 = np.vstack([B, [0, 0, 1]])
    return (A3 @ B3)[:2]

def trot(ang):
    c, s = np.cos(ang), np.sin(ang)
    return np.array([[c, -s, 0.], [s, c, 0.]])

def ttrans(tx, ty):
    return np.array([[1., 0., tx], [0., 1., ty]])

def apply(M, P):
    P = np.atleast_2d(P)
    return P @ M[:, :2].T + M[:, 2]

REFL = np.array([[-1., 0., 0.], [0., 1., 0.]])

# ---- system: dict label -> node; node = ('shape', label) | ('meta', [(child, T), ...]); each has .quad
class Node:
    def __init__(self, kind, label=None, children=None, quad=None):
        self.kind, self.label, self.children, self.quad = kind, label, children, quad

def build_base():
    keys = SPECTRE[KEY_IDX]
    sys = {}
    for lab in LABELS[1:]:
        sys[lab] = Node('shape', lab, quad=keys)
    g1 = Node('shape', 'Gamma1', quad=keys)
    g2 = Node('shape', 'Gamma2', quad=keys)
    T2 = mul(ttrans(*SPECTRE[8]), trot(np.pi / 6))
    sys['Gamma'] = Node('meta', 'Gamma', children=[(g1, ident()), (g2, T2)], quad=keys)
    return sys

def build_supertiles(sys):
    quad = np.array(sys['Delta'].quad)
    Ts = [ident()]
    total = 0.0
    rot = ident()
    tquad = quad.copy()
    for ang, frm, to in T_RULES:
        total += ang
        if ang != 0:
            rot = trot(np.radians(total))
            tquad = apply(rot, quad)
        src = apply(Ts[-1], quad[frm])[0]
        ttt = ttrans(src[0] - tquad[to][0], src[1] - tquad[to][1])
        Ts.append(mul(ttt, rot))
    Ts = [mul(REFL, T) for T in Ts]
    super_quad = np.array([apply(Ts[6], quad[2])[0], apply(Ts[5], quad[1])[0],
                           apply(Ts[3], quad[2])[0], apply(Ts[0], quad[1])[0]])
    ret = {}
    for lab, subs in SUPER_RULES.items():
        ch = [(sys[s], Ts[i]) for i, s in enumerate(subs) if s is not None]
        ret[lab] = Node('meta', lab, children=ch, quad=super_quad)
    return ret

def build(levels):
    sys = build_base()
    for _ in range(levels):
        sys = build_supertiles(sys)
    return sys

def flatten(node, T=None, path=(), ipath=()):
    """Yield (path, ipath, T) for every leaf shape.
    path  = (leaf_label, parent_label, grandparent, ...)
    ipath = (index of leaf in parent, index of parent in grandparent, ...) — identifies nodes uniquely."""
    if T is None:
        T = ident()
    if node.kind == 'shape':
        yield (node.label,) + path, ipath, T
    else:
        for ci, (child, CT) in enumerate(node.children):
            yield from flatten(child, mul(T, CT), (node.label,) + path, (ci,) + ipath)

def tiles(levels, root='Delta'):
    sys = build(levels)
    out = list(flatten(sys[root]))
    return out

# ---- verification
def tile_polys(tl):
    return np.stack([apply(T, SPECTRE) for _, _, T in tl])

def shoelace(P):
    x, y = P[..., 0], P[..., 1]
    return 0.5 * (np.sum(x * np.roll(y, -1, axis=-1), axis=-1) - np.sum(y * np.roll(x, -1, axis=-1), axis=-1))

def verify(levels=4, res=2400):
    tl = tiles(levels)
    dets = np.array([np.linalg.det(T[:, :2]) for _, _, T in tl])
    polys = tile_polys(tl)
    signed = shoelace(polys)
    a0 = abs(shoelace(SPECTRE))
    print(f'level {levels}: {len(tl)} tiles; det range {dets.min():.6f}..{dets.max():.6f}; '
          f'signed-area sign uniform: {np.all(np.sign(signed) == np.sign(signed[0]))}; '
          f'area/tile rel err {np.max(np.abs(np.abs(signed) - a0)) / a0:.2e}')
    # rasterize for overlap check
    from PIL import Image, ImageDraw
    lo = polys.reshape(-1, 2).min(0); hi = polys.reshape(-1, 2).max(0)
    span = (hi - lo).max()
    s = (res - 4) / span
    cover = np.zeros((res, res), np.int32)
    for P in polys:
        im = Image.new('L', (res, res), 0)
        d = ImageDraw.Draw(im)
        pts = [(float((p[0] - lo[0]) * s + 2), float((p[1] - lo[1]) * s + 2)) for p in P]
        d.polygon(pts, fill=1)
        cover += np.array(im, np.int32)
    union_px = (cover > 0).sum(); overlap_px = (cover > 1).sum()
    print(f'  raster: union {union_px} px, overlap {overlap_px} px ({overlap_px / union_px * 100:.3f}% — '
          f'edge-pixel double counts only if tiny); sum-of-areas/union-area = {len(tl) * a0 * s * s / union_px:.5f}')
    # counts by label per level + substitution matrix
    M = np.zeros((9, 9), int)
    for i, lab in enumerate(LABELS):
        for s_ in SUPER_RULES[lab]:
            if s_ is not None:
                M[LABELS.index(s_), i] += 1
    w = np.linalg.eigvals(M.astype(float))
    lam = max(w.real)
    print(f'  substitution matrix Perron eigenvalue {lam:.10f}  (4+sqrt15 = {4 + np.sqrt(15):.10f})')
    from collections import Counter
    c = Counter(p[0] for p, _, _ in tl)
    g2 = c['Gamma2']; tot = len(tl)
    print(f'  leaf counts {dict(c)}; Gamma2 (the 30°-rotated Mystic partner) share {g2 / tot:.5f}')
    return tl

if __name__ == '__main__':
    import sys
    lv = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    verify(lv)
