"""render_tower.py — a forgetful polygon as a spiral tower of glass plates (MO 515731).

A convex polygon is *forgetful* when deleting any one vertex leaves congruent polygons.
THEOREM (this run): forgetful <=> isogonal: regular, or a 2m-gon inscribed in a circle whose
arcs alternate a, b.  The tower shows why it matters: floor k is the polygon with vertex k
forgotten.  Every floor is the same plate, turned — the missing corner climbs a spiral, and a
coral bead floats where each forgotten vertex used to be.

Each plate is a convex prism (half-spaces), traced as sorbet glass on a paper table: Beer–Lambert
chord tint, flat facet sheen, edge light from plane slack, coloured soft shadows on the paper.

usage: render_tower.py S out.png [key=val ...]
"""
import sys, numpy as np
from PIL import Image

ARG = dict(a.split('=', 1) for a in sys.argv[3:] if '=' in a)
def P(k, d): return type(d)(ARG.get(k, d))
def normalize(v): return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-12)

WHEEL = [(1.00, 0.52, 0.62), (1.00, 0.70, 0.52), (1.00, 0.88, 0.46), (0.78, 0.95, 0.50),
         (0.52, 0.93, 0.76), (0.52, 0.84, 1.00), (0.64, 0.68, 1.00), (0.80, 0.62, 1.00),
         (1.00, 0.60, 0.90)]
def wheel(h):
    n = len(WHEEL); x = (h % 1.0) * n; i = int(x) % n; t = x - int(x)
    a, b = np.array(WHEEL[i]), np.array(WHEEL[(i + 1) % n])
    return a ** (1 - t) * b ** t


def isogonal(m, ratio, rot=0.0):
    """2m-gon on the unit circle, arcs alternating a, b with b = ratio*a (ratio=1: regular)."""
    a = 2 * np.pi / (m * (1 + ratio)); b = ratio * a
    ang = [rot]
    for i in range(2 * m - 1): ang.append(ang[-1] + (a if i % 2 == 0 else b))
    ang = np.array(ang)
    return np.stack([np.cos(ang), np.sin(ang)], 1), ang


def regular(n, rot=0.0):
    ang = rot + 2 * np.pi * np.arange(n) / n
    return np.stack([np.cos(ang), np.sin(ang)], 1), ang


def prism(poly, z0, z1, R):
    """half-spaces of the prism over convex CCW polygon (scaled by R) between heights z0, z1"""
    N, O = [], []
    k = len(poly)
    for i in range(k):
        p, q = poly[i] * R, poly[(i + 1) % k] * R
        e = q - p; n = np.array([e[1], -e[0]]); n /= np.linalg.norm(n)
        N.append([n[0], n[1], 0.0]); O.append(n @ p)
    N.append([0, 0, 1.0]); O.append(z1)
    N.append([0, 0, -1.0]); O.append(-z0)
    return np.array(N), np.array(O)


def build(spec):
    """list of bodies (NRM, OFF, absorb, kind) + list of beads (centre, radius)"""
    bodies, beads = [], []
    poly, ang = spec['poly'], spec['ang']
    n = len(poly); R = spec['R']; th = spec['th']; gap = spec['gap']; cx, cy = spec['at']
    order = spec.get('order', range(n))
    for f, k in enumerate(order):
        z0 = spec['z0'] + f * (th + gap)
        keep = [poly[j] for j in range(n) if j != k]
        N, O = prism(np.array(keep), z0, z0 + th, R)
        O = O + N[:, :2] @ np.array([cx, cy])        # translate
        tint = wheel(spec['hue0'] + (f + (ang[k] - ang[0]) / (2 * np.pi) * n - k) / n * spec.get('hspan', 1.0)) if 'order' in spec else wheel(spec['hue0'] + ang[k] / (2 * np.pi))
        cut = (k - 1) % (n - 1)
        bodies.append((N, O, -np.log(tint).astype(np.float32), cut))
        beads.append((np.array([cx + R * poly[k][0], cy + R * poly[k][1], z0 + th / 2]), spec['bead']))
    return bodies, beads


def interval(o, d, N, O):
    dn = d @ N.T; on = o @ N.T
    t = (O - on) / np.where(np.abs(dn) > 1e-12, dn, 1e-12)
    tin = np.where(dn < 0, t, -np.inf); tout = np.where(dn > 0, t, np.inf)
    tin = np.where((np.abs(dn) <= 1e-12) & (on > O), np.inf, tin)
    fi = np.argmax(tin, -1); fo = np.argmin(tout, -1)
    t0 = np.take_along_axis(tin, fi[..., None], -1)[..., 0]
    t1 = np.take_along_axis(tout, fo[..., None], -1)[..., 0]
    ok = t1 > t0
    return np.where(ok, t0, np.inf), np.where(ok, t1, -np.inf), fi, fo


def slack(X, N, O, face):
    m = O - X @ N.T
    m = np.where(np.arange(len(O)) == face[..., None], np.inf, m)
    return np.min(m, -1)


def sphere(o, d, c, r):
    oc = o - c; b = np.einsum('...i,...i', oc, d); cc = np.einsum('...i,...i', oc, oc) - r * r
    disc = b * b - cc
    t = -b - np.sqrt(np.maximum(disc, 0))
    return np.where((disc > 0) & (t > 0), t, np.inf)


def trace_shadow(o, d, bodies, beads, dens):
    A = np.zeros(o.shape, np.float32)
    occ = np.ones(o.shape[:-1], np.float32)
    for N, O, ab, f in bodies:
        t0, t1, _, _ = interval(o, d, N, O)
        L = np.clip(t1 - np.maximum(t0, 0), 0, None)
        A += (dens * L)[..., None] * ab
    for c, r in beads:
        occ *= np.where(np.isfinite(sphere(o, d, c, r)), P('beadocc', 0.6), 1.0)
    return np.exp(-A) * occ[..., None]


def main():
    S, out = int(sys.argv[1]), sys.argv[2]
    H = P('H', S)
    scene = P('scene', 'hero')
    specs = []
    if scene == 'hero':
        poly, ang = isogonal(P('m', 6), P('ratio', 0.42), P('rot', 0.3))
        if P('reg', 0): poly, ang = regular(P('reg', 0), P('rot', 0.3))
        n = len(poly); cyc = P('cyc', 2)
        specs.append(dict(poly=poly, ang=ang, R=P('R', 3.0), th=P('th', 0.30), gap=P('gap', 0.20),
                          at=(0.0, 0.0), z0=P('z0', 0.0), hue0=P('hue0', 0.0), bead=P('bead', 0.16),
                          order=[k % n for k in range(n * cyc)], hspan=1.0 / cyc))
    elif scene == 'trio':
        items = [(regular(4, 0.0) if P('rect', 0.0) == 0 else isogonal(2, P('rect', 0.0), 0.3), 4),
                 (regular(5, 0.3), 3), (isogonal(3, P('ratio', 0.45), 0.2), 3)]
        pos = [(float(v) for v in P(f'p{i}', d).split(',')) for i, d in enumerate(['3.5,-7.5', '0,0', '-3.5,7.5'])]
        for ((poly, ang), cyc), at in zip(items, pos):
            n = len(poly)
            specs.append(dict(poly=poly, ang=ang, R=P('R', 2.6), th=P('th', 0.12), gap=P('gap', 0.5),
                              at=tuple(at), z0=0.0, hue0=P('hue0', 0.0), bead=P('bead', 0.13),
                              order=[k % n for k in range(n * cyc)], hspan=1.0 / cyc))
    elif scene == 'shop':
        # a row of the forgetful family
        items = [regular(4, 0.2), isogonal(2, 0.45, 0.1), regular(5, 0.5), isogonal(3, 0.35, 0.4),
                 regular(7, 0.1), isogonal(4, 0.5, 0.2)]
        pos = [(-5.4, 2.6), (-1.8, 2.6), (1.8, 2.6), (5.4, 2.6), (-3.6, -1.6), (0.0, -1.6), (3.6, -1.6)]
        for (poly, ang), at in zip(items, pos):
            specs.append(dict(poly=poly, ang=ang, R=1.45, th=0.18, gap=0.13, at=at, z0=0.0,
                              hue0=P('hue0', 0.0), bead=0.08))
    bodies, beads = [], []
    for s in specs:
        b, e = build(s); bodies += b; beads += e
    zt = max(np.max(-O[-1:]) for _, O, _, _ in bodies)
    top = max(O[-2] for _, O, _, _ in bodies)

    elev, azim = P('elev', 0.62), P('azim', -0.35)
    cam = np.array([np.cos(elev) * np.cos(azim), np.cos(elev) * np.sin(azim), np.sin(elev)])
    look = np.array([P('lx', 0.0), P('ly', 0.0), P('lz', top * 0.45)])
    dist, fov = P('dist', 34.0), P('fov', 0.22)
    eye = look + cam * dist; fwd = -cam
    right = normalize(np.cross(fwd, np.array([0, 0, 1.0]))); upv = np.cross(right, fwd)
    KEY = normalize(np.array([float(v) for v in P('key', '-0.45,-0.75,1.0').split(',')]))
    HV = normalize(KEY + cam)
    dens = P('dens', 0.55)
    paper = np.array([0.993, 0.986, 0.978], np.float32)
    coral = np.array([1.0, 0.47, 0.42], np.float32)
    SS = P('ss', 3); ns = P('nsh', 4); soft = P('soft', 0.05)
    ya, yb = P('ya', 0), P('yb', H)
    rng = np.random.default_rng(7 + ya)
    img = np.zeros((yb - ya, S, 3), np.float32)
    B = 48
    for y0 in range(ya, yb, B):
        h = min(B, yb - y0)
        acc = np.zeros((h, S, 3), np.float32)
        for p in range(SS * SS):
            yy, xx = np.meshgrid(np.arange(y0, y0 + h), np.arange(S), indexing='ij')
            u = ((xx + rng.random(yy.shape)) / S * 2 - 1)
            v = (1 - (yy + rng.random(yy.shape)) / H * 2) * H / S + P('sy', 0.0)
            d = normalize(fwd + fov * (u[..., None] * right + v[..., None] * upv))
            o = np.broadcast_to(eye, d.shape).astype(np.float64)
            # paper table z=0
            tp = np.where(d[..., 2] < -1e-9, -o[..., 2] / np.minimum(d[..., 2], -1e-9), np.inf)
            Xp = o + d * np.where(np.isfinite(tp), tp, 0)[..., None]
            sh = np.zeros(d.shape, np.float32)
            for s_ in range(ns):
                Ls = normalize(KEY + soft * rng.standard_normal(d.shape))
                sh += trace_shadow(Xp + Ls * 1e-4, Ls, bodies, beads, dens * P('shd', 1.3))
            sh /= ns
            # gentle vignette on the table, fading to paper at the horizon
            r2 = (Xp[..., 0] ** 2 + Xp[..., 1] ** 2) / P('vig', 900.0)
            table = paper * (1 - P('vigk', 0.0) * np.clip(r2, 0, 1))[..., None]
            col = table * (P('amb', 0.55) + (1 - P('amb', 0.55)) * sh)
            col = np.where(np.isfinite(tp)[..., None], col, paper)
            tstop = np.where(np.isfinite(tp), tp, np.inf)
            # beads (opaque coral pearls) — nearest hit
            tb = np.full(d.shape[:-1], np.inf); nb = np.zeros(d.shape)
            for c, r in beads:
                t = sphere(o, d, c, r)
                closer = t < tb
                tb = np.where(closer, t, tb)
                X = o + d * np.where(np.isfinite(t), t, 0)[..., None]
                nb = np.where(closer[..., None], (X - c) / r, nb)
            hitb = np.isfinite(tb) & (tb < tstop)
            lam = np.clip(np.einsum('...i,...i', nb, KEY), 0, 1)
            spec = np.clip(np.einsum('...i,...i', nb, HV), 0, 1) ** 60
            beadc = coral * (0.62 + 0.42 * lam[..., None]) + 0.9 * spec[..., None]
            col = np.where(hitb[..., None], beadc, col)
            tstop = np.where(hitb, tb, tstop)
            # glass
            A = np.zeros(d.shape, np.float32); edge = np.zeros(d.shape[:-1], np.float32)
            sheen = np.zeros(d.shape[:-1], np.float32); frost = np.zeros(d.shape, np.float32)
            fa = np.zeros(d.shape[:-1], np.float32)
            cutl = np.zeros(d.shape[:-1], np.float32)
            for N, O, ab, cut in bodies:
                t0, t1, fi, fo = interval(o, d, N, O)
                hit = np.isfinite(t0) & (t0 < tstop)
                L = np.clip(np.minimum(t1, tstop) - np.maximum(t0, 0), 0, None)
                A += (dens * L)[..., None] * ab
                Xe = o + d * np.where(hit, t0, 0)[..., None]
                Xx = o + d * np.where(hit & (t1 < tstop), t1, 0)[..., None]
                ne = N[fi]
                cs = np.clip(np.einsum('...i,...i', ne, HV), 0, 1)
                fr = (1 - np.clip(-np.einsum('...i,...i', ne, d), 0, 1)) ** 3
                lm = np.clip(np.einsum('...i,...i', ne, KEY), 0, 1)
                sheen += hit * (0.45 * cs ** 80 + 0.08 * cs ** 8 + P('frz', 0.22) * fr)
                a = P('frost', 0.16) * hit
                frost += a[..., None] * np.exp(-ab * 1.1) * (0.55 + 0.5 * lm[..., None])
                fa += a
                w = P('edgew', 0.025)
                de = slack(Xe, N, O, fi); dx = slack(Xx, N, O, fo)
                edge += hit * (np.exp(-(de / w) ** 2) + 0.4 * (t1 < tstop) * np.exp(-(dx / w) ** 2))
                if P('cutc', 1.0) > 0:
                    sc_e = O[cut] - Xe @ N[cut]; sc_x = O[cut] - Xx @ N[cut]
                    wc = P('cutw', 0.035)
                    ce = np.where(fi == cut, 0.25, np.exp(-(sc_e / wc) ** 2))
                    cx_ = np.where(fo == cut, 0.0, np.exp(-(sc_x / wc) ** 2)) * (t1 < tstop)
                    cutl += hit * (ce + 0.5 * cx_)
            mean = frost / np.maximum(fa, 1e-6)[..., None]
            fe = 1 - np.exp(-fa)                         # = 1 - prod(1 - a_i) for small a
            col = col * np.exp(-A)
            col = col * (1 - fe[..., None]) + fe[..., None] * mean
            col = col + (1 - col) * np.clip(P('edgel', 0.6) * edge, 0, 1)[..., None]
            col = col + (1 - col) * np.clip(sheen, 0, 1)[..., None]
            g = np.clip(P('cutc', 1.0) * cutl, 0, 1)[..., None] * 0.85
            col = col * (1 - g) + coral * g
            acc += col
        img[y0 - ya:y0 - ya + h] = acc / (SS * SS)
        if (y0 - ya) % 480 == 0: print('row', y0, flush=True)
    if P('strip', 0):
        np.save(out, img); return
    save(img, out)


def save(img, out):
    lin = np.clip(img, 0, 1)
    srgb = np.where(lin <= 0.0031308, 12.92 * lin, 1.055 * lin ** (1 / 2.4) - 0.055)
    srgb = srgb * 255 + np.random.default_rng(9).uniform(-0.5, 0.5, srgb.shape)
    Image.fromarray(np.clip(srgb + 0.5, 0, 255).astype(np.uint8)).save(out)


if __name__ == '__main__':
    main()
