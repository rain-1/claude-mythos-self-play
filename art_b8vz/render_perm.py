"""render_perm.py — permutohedra of order 4 as sorbet glass (MO 515645, ordered partitions).

The faces of the permutohedron Π₃ = conv{permutations of (1,2,3,4)} are exactly the ordered set
partitions of {1,2,3,4}: 24 vertices (strict finishing orders), 36 edges (one tie), 14 facets
(two blocks), 1 solid (everyone ties) — 75 = the Fubini number.  Π₃ tiles space (the
bitruncated cubic honeycomb); here a central cell and its 14 face-neighbours, pulled apart a
little, each a convex glass body.  Every ray sums Beer–Lambert chord lengths through every
cell; facets carry a flat sheen and fresnel, edges a fine light line; a paper wall behind
catches the tinted shadows.  The 36 edges of the centre cell (the largest rank of the poset,
its maximum antichain) can be lit in coral.

usage: render_perm.py S out.png [key=val ...]
"""
import sys, numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

ARG = dict(a.split('=', 1) for a in sys.argv[3:] if '=' in a)
def P(k, d): return type(d)(ARG.get(k, d))

def normalize(v):
    return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-12)

# truncated octahedron in the bcc frame: |x|,|y|,|z| <= 2 (squares), |±x±y±z| <= 3 (hexagons)
NRM, OFF = [], []
for i in range(3):
    for s in (1, -1):
        n = np.zeros(3); n[i] = s; NRM.append(n); OFF.append(2.0)
for sx in (1, -1):
    for sy in (1, -1):
        for sz in (1, -1):
            n = np.array([sx, sy, sz]) / np.sqrt(3); NRM.append(n); OFF.append(3 / np.sqrt(3))
NRM = np.array(NRM, np.float64); OFF = np.array(OFF)
NEIGH = [n * 4 if k < 6 else n * np.sqrt(3) * 2 for k, n in enumerate(NRM)]   # face-neighbour centres

def absorb(t): return -np.log(np.array(t, np.float32))
SQ = [(1.00, 0.56, 0.66), (1.00, 0.72, 0.52), (1.00, 0.88, 0.48),
      (1.00, 0.62, 0.86), (1.00, 0.66, 0.60), (0.98, 0.80, 0.50)]          # warm: 2|2 ties
HX = [(0.56, 0.92, 0.74), (0.56, 0.82, 1.00), (0.66, 0.68, 1.00), (0.80, 0.64, 1.00),
      (0.62, 0.94, 0.86), (0.60, 0.76, 1.00), (0.74, 0.66, 1.00), (0.78, 0.94, 0.56)]  # cool: 1|3 ties
CENTRE = (0.97, 0.95, 0.99)


WHEEL = [(1.00, 0.52, 0.62), (1.00, 0.70, 0.52), (1.00, 0.88, 0.46), (0.78, 0.95, 0.50),
         (0.52, 0.93, 0.76), (0.52, 0.84, 1.00), (0.64, 0.68, 1.00), (0.80, 0.62, 1.00),
         (1.00, 0.60, 0.90)]

def wheel(h):
    n = len(WHEEL); x = (h % 1.0) * n; i = int(x) % n; t = x - int(x)
    a, b = np.array(WHEEL[i]), np.array(WHEEL[(i + 1) % n])
    return tuple(a ** (1 - t) * b ** t)


def cells(explode, right=None, upv=None, hue0=0.0):
    out = [(np.zeros(3), absorb(CENTRE) * P('cdens', 1.0), 0)]
    pts = NEIGH
    R = P('rad', 0.0)
    if R > 0:
        g = np.arange(-4, 5)
        L = np.array([(4 * i + o, 4 * j + o, 4 * k + o) for i in g for j in g for k in g for o in (0, 2)], float)
        nr = np.linalg.norm(L, axis=1)
        pts = list(L[(nr > 0) & (nr < R)])
    for k, c in enumerate(pts):
        if right is not None:   # hue by the cell's angle around the view axis
            tint = wheel(hue0 + np.arctan2(c @ upv, c @ right) / (2 * np.pi))
        else:
            tint = SQ[k % 6] if k < 6 else HX[k % 8]
        out.append((c * explode, absorb(tint), k + 1))
    return out


def poly_interval(o, d, C):
    """entry/exit t of the ray through the cell centred at C, plus entry/exit face index"""
    oc = o - C
    dn = d @ NRM.T                                   # (...,14)
    on = oc @ NRM.T
    t = (OFF - on) / np.where(np.abs(dn) > 1e-12, dn, 1e-12)
    tin = np.where(dn < 0, t, -np.inf); tout = np.where(dn > 0, t, np.inf)
    fi = np.argmax(tin, -1); fo = np.argmin(tout, -1)
    t0 = np.take_along_axis(tin, fi[..., None], -1)[..., 0]
    t1 = np.take_along_axis(tout, fo[..., None], -1)[..., 0]
    inside_all = np.all((dn != 0) | (on <= OFF), -1)
    ok = (t1 > t0) & inside_all
    return np.where(ok, t0, np.inf), np.where(ok, t1, -np.inf), fi, fo


def edge_dist(X, C, face):
    """distance from a point on face `face` to the nearest other face plane (≈ distance to an edge)"""
    m = OFF - (X - C) @ NRM.T                          # slack to every plane (>=0 inside)
    m = np.where(np.arange(len(OFF)) == face[..., None], np.inf, m)
    # slack along the face: divide by sin of dihedral-ish; good enough as a plane distance
    return np.min(m, -1)


def trace(o, d, CL, fadeL, dens, want=False, tstop=None):
    A = np.zeros(o.shape, np.float32)
    if want:
        sheen = np.zeros(o.shape[:-1], np.float32); edge = np.zeros(o.shape[:-1], np.float32)
        frost = np.zeros(o.shape, np.float32); fa = np.zeros(o.shape[:-1], np.float32)
        cedge = np.zeros(o.shape[:-1], np.float32)
    for C, ab, idx in CL:
        t0, t1, fi, fo = poly_interval(o, d, C)
        t0c = np.maximum(t0, 0)
        t1c = t1 if tstop is None else np.minimum(t1, tstop)
        L = np.clip(t1c - t0c, 0, None)
        fade = np.exp(-(np.dot(C, C)) / fadeL ** 2) if fadeL > 0 else 1.0
        A += (dens * L * fade)[..., None] * ab
        if want:
            hit = np.isfinite(t0) & (t0 > 0)
            Xe = o + d * np.where(hit, t0, 0)[..., None]
            Xx = o + d * np.where(hit, t1, 0)[..., None]
            ne = NRM[fi]; nx = NRM[fo]
            cs = np.clip(np.einsum('...i,...i', ne, HV), 0, 1)
            fr = (1 - np.clip(-np.einsum('...i,...i', ne, d), 0, 1)) ** 3
            lam = np.clip(np.einsum('...i,...i', ne, KEY), 0, 1)
            sheen += hit * fade * SHEEN * (0.50 * cs ** 70 + 0.10 * cs ** 6 + FRZ * fr)
            # flat faceting: each facet gets its own soft tone from the key light
            a = FROST * hit * fade
            tint = np.exp(-ab * 1.1)
            frost += a[..., None] * tint * (0.55 + 0.55 * lam[..., None])
            fa += a
            w = EDGEW
            de = edge_dist(Xe, C, fi); dx = edge_dist(Xx, C, fo)
            e = hit * fade * (np.exp(-(de / w) ** 2) + 0.45 * np.exp(-(dx / w) ** 2))
            if idx == 0:
                cedge += e
            else:
                edge += e
    if want:
        return A, sheen, edge, frost, np.clip(fa, 0, 0.9), cedge
    return A


def main():
    global KEY, HV, SHEEN, FROST, EDGEW, FRZ
    FRZ = P('frz', 0.28)
    S, out = int(sys.argv[1]), sys.argv[2]
    explode = P('explode', 1.12)
    cam = normalize(np.array([float(v) for v in P('cam', '1,0.62,0.48').split(',')]))
    dist, fov = P('dist', 30.0), P('fov', 0.30)
    dens, fadeL = P('dens', 0.16), P('fadeL', 0.0)
    SHEEN, FROST, EDGEW = P('sheen', 1.0), P('frost', 0.22), P('edgew', 0.055)
    BACK = P('back', 9.0)
    coral_on = P('coral', 1.0)
    eye = cam * dist; fwd = -cam
    up = np.array([0, 0, 1.0]); right = normalize(np.cross(fwd, up)); upv = np.cross(right, fwd)
    roll = P('roll', 0.0)
    if roll:
        c, s = np.cos(roll), np.sin(roll); right, upv = c * right + s * upv, -s * right + c * upv
    CL = cells(explode, right, upv, P('hue0', 0.0)) if P('screenhue', 1) else cells(explode)
    KEY = normalize(0.55 * upv - 0.40 * right + 0.70 * cam)
    HV = normalize(KEY + cam)
    key2 = normalize(KEY + np.array([float(v) for v in P('kl', '0.5,-0.4,0.3').split(',')]))
    paper = np.array([0.994, 0.988, 0.980], np.float32)
    SS = P('ss', 2)
    sx0 = P('sx', 0.0); sy0 = P('sy', 0.0)
    rng = np.random.default_rng(1)
    ya, yb = P('ya', 0), P('yb', S)
    img = np.zeros((S, S, 3), np.float32)
    B = 64
    rng = np.random.default_rng(1 + ya)
    for y0 in range(ya, yb, B):
        h = min(B, yb - y0)
        acc = np.zeros((h, S, 3), np.float32)
        for sy in range(SS):
            for sx in range(SS):
                yy, xx = np.meshgrid(np.arange(y0, y0 + h), np.arange(S), indexing='ij')
                u = (xx + (sx + rng.random(yy.shape)) / SS) / S * 2 - 1 + sx0
                v = 1 - (yy + (sy + rng.random(yy.shape)) / SS) / S * 2 + sy0
                d = normalize(fwd + fov * (u[..., None] * right + v[..., None] * upv))
                o = np.broadcast_to(eye, d.shape)
                # paper wall behind, perpendicular to the view, catching tinted shadows
                den = d @ cam
                tp = (-BACK - o @ cam) / np.where(np.abs(den) > 1e-9, den, -1e-9)
                Xp = o + d * tp[..., None]
                shp = np.zeros(d.shape, np.float32)
                ns = P('nsh', 3)
                for s_ in range(ns):
                    Ls = normalize(key2 + P('soft', 0.04) * rng.standard_normal(d.shape))
                    Ap = trace(Xp, Ls, CL, fadeL, dens * P('shdens', 1.5))
                    shp += np.exp(-Ap)
                shp /= ns
                # light focusing: glass slightly brightens the shadow core (a fake caustic)
                wall = paper * (P('wallamb', 0.60) + (1 - P('wallamb', 0.60)) * shp)
                A, sh, ed, fr, fa, ce = trace(o, d, CL, fadeL, dens, want=True)
                col = wall * np.exp(-A)
                col = col * (1 - fa[..., None]) + fr
                col = col + (1 - col) * np.clip(P('edgel', 0.55) * ed, 0, 1)[..., None]
                col = col + (1 - col) * np.clip(sh, 0, 1)[..., None]
                if coral_on:
                    coral = np.array([1.0, 0.45, 0.40], np.float32)
                    g = np.clip(coral_on * ce, 0, 1)[..., None]
                    col = col * (1 - 0.75 * g) + coral * 0.75 * g
                acc += col
        img[y0:y0 + h] = acc / (SS * SS)
        if y0 % 512 == 0:
            print('row', y0, flush=True)
    if P('strip', 0):
        np.save(out, img[ya:yb].astype(np.float32)); return
    lin = np.clip(img, 0, 1)
    srgb = np.where(lin <= 0.0031308, 12.92 * lin, 1.055 * lin ** (1 / 2.4) - 0.055)
    srgb = srgb * 255 + np.random.default_rng(9).uniform(-0.5, 0.5, srgb.shape)
    Image.fromarray(np.clip(srgb + 0.5, 0, 255).astype(np.uint8)).save(out)


if __name__ == '__main__':
    main()
