"""render_lattice.py — the 75 ways four runners can finish, as an exploded permutohedron (MO 515645).

Every face of Π₃ = conv{orders of (1,2,3,4)} is an ordered set partition of the four runners.
Each face is pulled out from the centre along its own centroid and shrunk about it, so all 75
are visible at once as separate objects:
  24 pearls  (strict finishing orders, 4 blocks),
  36 glass rods (one two-way tie, 3 blocks) — the largest rank, the poset's widest antichain: coral glass,
  14 glass tiles (two blocks: 8 hexagons 1|3 or 3|1, 6 squares 2|2),
   1 glass core (one block: everyone ties).
Glass is Beer–Lambert chord absorbance; pearls are opaque with a soft key light; a paper wall
behind catches tinted shadows.
usage: render_lattice.py S out.png [key=val ...]
"""
import sys, itertools, numpy as np
from PIL import Image

ARG = dict(a.split('=', 1) for a in sys.argv[3:] if '=' in a)
def P(k, d): return type(d)(ARG.get(k, d))
def normalize(v): return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-12)
def absorb(t): return -np.log(np.array(t, np.float32))

# ---- geometry of Π₃ in 3-D ------------------------------------------------------------
B = np.linalg.qr(np.array([[1, -1, 0, 0], [0, 1, -1, 0], [0, 0, 1, -1]], float).T)[0]   # 4x3 basis of sum=0
def emb(x): return (np.asarray(x, float) - 2.5) @ B


def ordered_partitions(n):
    def rec(rest):
        if not rest:
            yield []
            return
        rest = list(rest)
        for k in range(1, len(rest) + 1):
            for blk in itertools.combinations(rest, k):
                for tail in rec([r for r in rest if r not in blk]):
                    yield [blk] + tail
    return list(rec(range(n)))


def face_vertices(op, n=4):
    """all rank vectors consistent with the ordered partition"""
    out = []
    starts = np.cumsum([0] + [len(b) for b in op])[:-1]
    for perms in itertools.product(*[itertools.permutations(b) for b in op]):
        x = np.zeros(n)
        for s, pb in zip(starts, perms):
            for i, r in enumerate(pb):
                x[r] = s + i + 1
        out.append(emb(x))
    return np.array(out)


def convex_hull_planes(V):
    from scipy.spatial import ConvexHull
    h = ConvexHull(V)
    eq = h.equations                          # n.x + d <= 0 inside
    N = eq[:, :3]; O = -eq[:, 3]
    # merge duplicate planes
    key = np.round(np.c_[N, O], 6)
    _, idx = np.unique(key, axis=0, return_index=True)
    return N[idx], O[idx]


def tile_planes(V, thick):
    """thin prism around the planar convex polygon V (k,3)"""
    c = V.mean(0)
    n = normalize(np.cross(V[1] - V[0], V[2] - V[0]))
    # order polygon vertices around c
    e1 = normalize(V[0] - c); e2 = np.cross(n, e1)
    ang = np.arctan2((V - c) @ e2, (V - c) @ e1)
    W = V[np.argsort(ang)]
    Ns, Os = [n, -n], [c @ n + thick / 2, -(c @ n) + thick / 2]
    for i in range(len(W)):
        a, b = W[i], W[(i + 1) % len(W)]
        m = normalize(np.cross(b - a, n))
        if (c - a) @ m > 0:
            m = -m
        Ns.append(m); Os.append(a @ m)
    return np.array(Ns), np.array(Os)


def poly_interval(o, d, N, O):
    dn = d @ N.T; on = o @ N.T
    t = (O - on) / np.where(np.abs(dn) > 1e-12, dn, 1e-12)
    tin = np.where(dn < 0, t, -np.inf); tout = np.where(dn > 0, t, np.inf)
    par_out = (np.abs(dn) <= 1e-12) & (on > O)
    fi = np.argmax(tin, -1)
    t0 = np.max(tin, -1); t1 = np.min(tout, -1)
    ok = (t1 > t0) & ~np.any(par_out, -1)
    return np.where(ok, t0, np.inf), np.where(ok, t1, -np.inf), fi


def cyl_interval(o, d, Pa, Pb, r):
    u = Pb - Pa; L = np.linalg.norm(u); u = u / L
    w = o - Pa
    du = d @ u; wu = w @ u
    a = np.maximum(1 - du * du, 1e-12)
    b = np.einsum('...i,...i', w, d) - wu * du
    c = np.einsum('...i,...i', w, w) - wu * wu - r * r
    disc = b * b - a * c
    sq = np.sqrt(np.maximum(disc, 0))
    t0 = (-b - sq) / a; t1 = (-b + sq) / a
    s0 = (0 - wu) / np.where(np.abs(du) > 1e-12, du, 1e-12); s1 = (L - wu) / np.where(np.abs(du) > 1e-12, du, 1e-12)
    lo = np.minimum(s0, s1); hi = np.maximum(s0, s1)
    T0 = np.maximum(t0, lo); T1 = np.minimum(t1, hi)
    ok = (disc > 0) & (T1 > T0)
    return np.where(ok, T0, np.inf), np.where(ok, T1, -np.inf), t0, t1


def sphere_t(o, d, C, r):
    w = o - C
    b = np.einsum('...i,...i', w, d); c = np.einsum('...i,...i', w, w) - r * r
    disc = b * b - c
    t = -b - np.sqrt(np.maximum(disc, 0))
    return np.where((disc > 0) & (t > 1e-4), t, np.inf)


WHEEL = [(1.00, 0.52, 0.62), (1.00, 0.70, 0.52), (1.00, 0.88, 0.46), (0.78, 0.95, 0.50),
         (0.52, 0.93, 0.76), (0.52, 0.84, 1.00), (0.64, 0.68, 1.00), (0.80, 0.62, 1.00),
         (1.00, 0.60, 0.90)]
def wheel(h):
    n = len(WHEEL); x = (h % 1.0) * n; i = int(x) % n; t = x - int(x)
    a, b = np.array(WHEEL[i]), np.array(WHEEL[(i + 1) % n])
    return tuple(a ** (1 - t) * b ** t)


def build(right, upv):
    ops = ordered_partitions(4)
    assert len(ops) == 75
    explode, shrink = P('explode', 0.55), P('shrink', 0.80)
    pearls, rods, tiles, core = [], [], [], []
    for op in ops:
        V = face_vertices(op)
        c = V.mean(0)
        k = len(op)
        off = c * explode
        if k == 4:
            pearls.append(c * (1 + explode))
        elif k == 3:
            a, b = V
            a2 = c + (a - c) * shrink + off; b2 = c + (b - c) * shrink + off
            rods.append((a2, b2))
        elif k == 2:
            W = c + (V - c) * P('tshrink', 0.78) + off
            h = P('hue0', 0.0) + np.arctan2(c @ upv, c @ right) / (2 * np.pi)
            tiles.append((tile_planes(W, P('thick', 0.07)), absorb(wheel(h)), c))
        else:
            core.append(convex_hull_planes(c + (V - c) * P('cshrink', 0.36)))
    return pearls, rods, tiles, core


def main():
    S, out = int(sys.argv[1]), sys.argv[2]
    cam = normalize(np.array([float(v) for v in P('cam', '1,0.62,0.48').split(',')]))
    dist, fov = P('dist', 14.0), P('fov', 0.30)
    eye = cam * dist; fwd = -cam
    up = np.array([0, 0, 1.0]); right = normalize(np.cross(fwd, up)); upv = np.cross(right, fwd)
    pearls, rods, tiles, core = build(right, upv)
    KEY = normalize(0.55 * upv - 0.40 * right + 0.70 * cam)
    HV = normalize(KEY + cam)
    key2 = normalize(KEY + np.array([float(v) for v in P('kl', '0.5,-0.4,0.3').split(',')]))
    rp, rr = P('rp', 0.16), P('rr', 0.075)
    dens = P('dens', 1.2)
    ROD = absorb(tuple(float(v) for v in P('rodc', '1.0,0.52,0.46').split(','))) * P('roddens', 1.6)
    CORE = absorb((0.92, 0.90, 0.98)) * 1.0
    paper = np.array([0.994, 0.988, 0.980], np.float32)
    BACK = P('back', 5.0)
    SS = P('ss', 2)
    sx0, sy0 = P('sx', 0.0), P('sy', 0.0)
    ya, yb = P('ya', 0), P('yb', S)

    def glass(o, d, tstop, want):
        A = np.zeros(o.shape, np.float32)
        sheen = np.zeros(o.shape[:-1], np.float32); edge = np.zeros(o.shape[:-1], np.float32)
        def facet(t0, nrm, fade=1.0):
            hit = np.isfinite(t0) & (t0 > 0) & (t0 < tstop)
            cs = np.clip(np.einsum('...i,...i', nrm, HV), 0, 1)
            fr = (1 - np.clip(np.abs(np.einsum('...i,...i', nrm, d)), 0, 1)) ** 3
            return hit * (0.45 * cs ** 60 + 0.08 * cs ** 6 + P('frz', 0.25) * fr)
        for (N, O), ab, c in tiles:
            t0, t1, fi = poly_interval(o, d, N, O)
            L = np.clip(np.minimum(t1, tstop) - np.maximum(t0, 0), 0, None)
            A += (dens * P('tdens', 2.5) * L)[..., None] * ab
            if want:
                sheen += facet(t0, N[fi])
                X = o + d * np.where(np.isfinite(t0), t0, 0)[..., None]
                m = O - X @ N.T
                m[..., :2] = np.inf                      # rim distance: only the side planes
                e = np.min(m, -1)
                edge += np.isfinite(t0) * (t0 > 0) * (t0 < tstop) * np.exp(-(e / P('edgew', 0.03)) ** 2)
        for (N, O) in core:
            t0, t1, fi = poly_interval(o, d, N, O)
            L = np.clip(np.minimum(t1, tstop) - np.maximum(t0, 0), 0, None)
            A += (dens * L)[..., None] * CORE
            if want:
                sheen += facet(t0, N[fi])
                X = o + d * np.where(np.isfinite(t0), t0, 0)[..., None]
                m = O - X @ N.T
                m = np.where(np.arange(len(O)) == fi[..., None], np.inf, m)
                edge += np.isfinite(t0) * (t0 > 0) * (t0 < tstop) * np.exp(-(np.min(m, -1) / P('edgew', 0.03)) ** 2)
        for a, b in rods:
            T0, T1, c0, c1 = cyl_interval(o, d, a, b, rr)
            L = np.clip(np.minimum(T1, tstop) - np.maximum(T0, 0), 0, None)
            A += (dens * L)[..., None] * ROD
            if want:
                full = np.where(np.isfinite(T0), np.clip(c1 - c0, 0, None), 0.0)
                hit = np.isfinite(T0) & (T0 > 0) & (T0 < tstop)
                # cylindrical sheen: normal at entry
                u = normalize(b - a)
                Xe = o + d * np.where(hit, T0, 0)[..., None] - a
                nrm = normalize(Xe - (Xe @ u)[..., None] * u)
                cs = np.clip(np.einsum('...i,...i', nrm, HV), 0, 1)
                sheen += hit * (0.55 * cs ** 50 + 0.10 * cs ** 5)
        return A, sheen, edge

    def pearl_hit(o, d):
        tb = np.full(o.shape[:-1], np.inf); idx = np.full(o.shape[:-1], -1)
        for i, C in enumerate(pearls):
            t = sphere_t(o, d, C, rp)
            m = t < tb; tb = np.where(m, t, tb); idx = np.where(m, i, idx)
        return tb, idx

    rng = np.random.default_rng(7 + ya)
    img = np.zeros((yb - ya, S, 3), np.float32)
    Bk = 48
    for y0 in range(ya, yb, Bk):
        h = min(Bk, yb - y0)
        acc = np.zeros((h, S, 3), np.float32)
        for sy in range(SS):
            for sx in range(SS):
                yy, xx = np.meshgrid(np.arange(y0, y0 + h), np.arange(S), indexing='ij')
                u = (xx + (sx + rng.random(yy.shape)) / SS) / S * 2 - 1 + sx0
                v = 1 - (yy + (sy + rng.random(yy.shape)) / SS) / S * 2 + sy0
                d = normalize(fwd + fov * (u[..., None] * right + v[..., None] * upv))
                o = np.broadcast_to(eye, d.shape)
                # wall
                den = d @ cam
                tp = (-BACK - o @ cam) / np.where(np.abs(den) > 1e-9, den, -1e-9)
                Xp = o + d * tp[..., None]
                shp = np.zeros(d.shape, np.float32)
                ns = P('nsh', 3)
                for _ in range(ns):
                    Ls = normalize(key2 + P('soft', 0.04) * rng.standard_normal(d.shape))
                    Ap, _, _ = glass(Xp, Ls, np.full(d.shape[:-1], np.inf), False)
                    tb, _ = pearl_hit(Xp, Ls)
                    shp += np.exp(-Ap * P('shdens', 1.3)) * np.where(np.isfinite(tb), 0.72, 1.0)[..., None]
                shp /= ns
                wall = paper * (P('wallamb', 0.62) + (1 - P('wallamb', 0.62)) * shp)
                # pearls
                tb, idx = pearl_hit(o, d)
                hitb = np.isfinite(tb)
                Cs = np.array(pearls)[np.clip(idx, 0, None)]
                X = o + d * np.where(hitb, tb, 0)[..., None]
                Nn = normalize(X - Cs)
                lam = np.clip(np.einsum('...i,...i', Nn, KEY), 0, 1)
                # pearl self-shadow from glass between pearl and light (one sample)
                As, _, _ = glass(X + Nn * 1e-3, np.broadcast_to(KEY, d.shape), np.full(d.shape[:-1], np.inf), False)
                lamc = lam[..., None] * np.exp(-As * 0.8)
                spec = np.clip(np.einsum('...i,...i', Nn, HV), 0, 1) ** 70
                pearlc = np.array([0.990, 0.972, 0.962], np.float32)
                ca = np.clip(np.einsum('...i,...i', Nn, -d), 0, 1)
                irid = 0.05 * np.stack([np.cos(7 * ca), np.cos(7 * ca + 2.1), np.cos(7 * ca + 4.2)], -1)
                skyamb = 0.55 + 0.12 * (Nn @ upv)[..., None]
                ballc = pearlc * (skyamb + 0.42 * lamc) + 0.35 * spec[..., None] + irid * (1 - ca)[..., None]
                behind = np.where(hitb[..., None], ballc, wall)
                A, sh, ed = glass(o, d, np.where(hitb, tb, np.inf), True)
                col = behind * np.exp(-A)
                col = col + (1 - col) * np.clip(P('edgel', 0.5) * ed, 0, 1)[..., None]
                col = col + (1 - col) * np.clip(sh, 0, 1)[..., None]
                acc += col
        img[y0 - ya:y0 - ya + h] = acc / (SS * SS)
    if P('strip', 0):
        np.save(out, img); return
    lin = np.clip(img, 0, 1)
    srgb = np.where(lin <= 0.0031308, 12.92 * lin, 1.055 * lin ** (1 / 2.4) - 0.055)
    srgb = srgb * 255 + np.random.default_rng(9).uniform(-0.5, 0.5, srgb.shape)
    Image.fromarray(np.clip(srgb + 0.5, 0, 255).astype(np.uint8)).save(out)


if __name__ == '__main__':
    main()
