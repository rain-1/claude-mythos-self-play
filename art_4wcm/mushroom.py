"""mushroom.py — Bunimovich's mushroom billiard: a half-disc cap (radius R, y >= 0) on a
rectangular stem (|x| <= r, -h <= y <= 0).  Vectorised specular propagation of many
particles at once; chord rasteriser (additive, sampled at ~1 px) for the pastel sheet.

The trap theorem (Bunimovich 2001): an orbit in the cap has an invariant caustic radius
rho = |p x v| (distance of its line from the cap's centre), preserved by reflections off
the arc AND off the flat wall (the wall reflection is the unfolding of the half-disc to
the disc).  Its chords meet the line y = 0 at |x| >= rho, so rho >= r means it can never
find the stem mouth: trapped forever, integrable, happy.  rho < r: the foot points of
its chords on y = 0 move by an irrational rotation of the unfolded disc, so it reaches
|x| < r and falls into the stem; it is free — and it can spend arbitrarily long imitating
a trapped orbit when rho is just below r (stickiness, survival ~ 1/t).
"""
import numpy as np

EPS = 1e-12


def propagate(P, V, nb, R=1.0, r=0.5, h=1.0):
    """P,V: (n,2). Returns segs (nb,n,4) x0,y0,x1,y1 and region (nb,n) True if the segment
    starts in the cap (y>0 start) — chords fully in the cap vs stem passages."""
    n = len(P)
    P = P.astype(np.float64).copy(); V = V.astype(np.float64).copy()
    V /= np.linalg.norm(V, axis=1, keepdims=True)
    segs = np.zeros((nb, n, 4)); incap = np.zeros((nb, n), bool)
    BIG = 1e18
    for k in range(nb):
        x, y = P[:, 0], P[:, 1]; vx, vy = V[:, 0], V[:, 1]
        # --- circle (cap arc), valid if hit y >= 0
        bq = x * vx + y * vy; cq = x * x + y * y - R * R
        disc = bq * bq - cq
        tc = np.where(disc >= 0, -bq + np.sqrt(np.maximum(disc, 0)), BIG)
        yc = y + tc * vy
        tc = np.where((tc > EPS) & (yc >= -1e-9), tc, BIG)
        # --- flat wall y=0, |x| >= r
        tw = np.where(np.abs(vy) > EPS, -y / np.where(np.abs(vy) > EPS, vy, 1), BIG)
        xw = x + tw * vx
        tw = np.where((tw > EPS) & (np.abs(xw) >= r), tw, BIG)
        # --- stem sides x = +-r, valid y in [-h, 0]
        ts = np.full(n, BIG)
        for sgn in (1, -1):
            t = np.where(np.abs(vx) > EPS, (sgn * r - x) / np.where(np.abs(vx) > EPS, vx, 1), BIG)
            ys = y + t * vy
            t = np.where((t > EPS) & (ys <= 1e-9) & (ys >= -h - 1e-9), t, BIG)
            ts = np.minimum(ts, t)
        # --- stem bottom y = -h, |x| <= r
        tb = np.where(np.abs(vy) > EPS, (-h - y) / np.where(np.abs(vy) > EPS, vy, 1), BIG)
        xb = x + tb * vx
        tb = np.where((tb > EPS) & (np.abs(xb) <= r + 1e-9), tb, BIG)
        T = np.stack([tc, tw, ts, tb], 1)
        j = np.argmin(T, 1); t = T[np.arange(n), j]
        bad = t >= BIG
        if bad.any():
            t = np.where(bad, 0.0, t)
        Q = P + t[:, None] * V
        segs[k, :, 0:2] = P; segs[k, :, 2:4] = Q
        incap[k] = (P[:, 1] + Q[:, 1]) > 1e-9
        # normals
        N = np.zeros((n, 2))
        m = j == 0; N[m] = -Q[m] / R                     # inward normal of the arc
        m = j == 1; N[m, 1] = 1.0                        # flat wall: normal up into the cap
        m = j == 2; N[m, 0] = -np.sign(Q[m, 0])          # stem sides
        m = j == 3; N[m, 1] = 1.0                        # stem bottom
        V = V - 2 * (V * N).sum(1, keepdims=True) * N
        V /= np.linalg.norm(V, axis=1, keepdims=True)
        P = Q
        # nudge off the wall along the new direction
        P = P + 1e-10 * V
    return segs, incap


def caustic_radius(P, V):
    V = V / np.linalg.norm(V, axis=1, keepdims=True)
    return np.abs(P[:, 0] * V[:, 1] - P[:, 1] * V[:, 0])


def raster(segs, weights, W, H, xform, acc=None, step=1.0):
    """segs (m,4) in model coords; xform(x,y)->(px,py). Additive bilinear sampling at ~step px
    (C kernel in librast.so; falls back to numpy if the library is missing)."""
    import ctypes, os
    if acc is None:
        acc = np.zeros(H * W, np.float32)
    x0, y0 = xform(segs[:, 0], segs[:, 1]); x1, y1 = xform(segs[:, 2], segs[:, 3])
    lib = ctypes.CDLL(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'librast.so'))
    dp = ctypes.POINTER(ctypes.c_double); fp = ctypes.POINTER(ctypes.c_float)
    a = [np.ascontiguousarray(v, np.float64) for v in (x0, y0, x1, y1, weights)]
    lib.raster_segs(*[v.ctypes.data_as(dp) for v in a], ctypes.c_int64(len(x0)), ctypes.c_int(W), ctypes.c_int(H),
                    ctypes.c_double(step), acc.ctypes.data_as(fp))
    return acc


def raster_np(segs, weights, W, H, xform, acc=None, step=1.0):
    """segs (m,4) in model coords; xform(x,y)->(px,py). Additive sampling at ~step px."""
    if acc is None:
        acc = np.zeros(H * W, np.float64)
    x0, y0 = xform(segs[:, 0], segs[:, 1]); x1, y1 = xform(segs[:, 2], segs[:, 3])
    L = np.hypot(x1 - x0, y1 - y0)
    ns = np.maximum(2, np.ceil(L / step).astype(np.int64))
    w_per = weights / ns
    # chunked expansion
    CH = 20_000_000
    tot = int(ns.sum()); start = 0
    idx = 0
    cum = np.cumsum(ns)
    while start < tot:
        end = min(tot, start + CH)
        # segments covering [start,end)
        i0 = np.searchsorted(cum, start, side='right'); i1 = np.searchsorted(cum, end - 1, side='right')
        sl = slice(i0, i1 + 1)
        nn = ns[sl]; rep = np.repeat(np.arange(i0, i1 + 1), nn)
        # local parameter along each segment
        base = np.concatenate([[0], np.cumsum(nn)[:-1]])
        k = np.arange(len(rep)) - np.repeat(base, nn)
        u = (k + 0.5) / nn[rep - i0]
        px = x0[rep] + u * (x1[rep] - x0[rep]); py = y0[rep] + u * (y1[rep] - y0[rep])
        # bilinear splat
        fx = np.floor(px); fy = np.floor(py)
        dx = px - fx; dy = py - fy
        ix = fx.astype(np.int64); iy = fy.astype(np.int64)
        ww = w_per[rep]
        for ox, oy, wt in ((0, 0, (1 - dx) * (1 - dy)), (1, 0, dx * (1 - dy)), (0, 1, (1 - dx) * dy), (1, 1, dx * dy)):
            xx = ix + ox; yy = iy + oy
            ok = (xx >= 0) & (xx < W) & (yy >= 0) & (yy < H)
            acc += np.bincount((yy[ok] * W + xx[ok]), weights=(ww * wt)[ok], minlength=H * W)
        # this chunk consumed exactly the segments i0..i1 (approximation: whole segments)
        start = int(cum[i1])
    return acc


def sojourn_lengths_fast(incap, seglen):
    """completed cap-sojourn lengths, vectorised (run-lengths of True along axis 0)"""
    nb, n = incap.shape
    pad = np.zeros((1, n), bool)
    a = np.concatenate([pad, incap, pad], 0)
    d = np.diff(a.astype(np.int8), axis=0)
    starts = np.argwhere(d == 1); ends = np.argwhere(d == -1)     # same order (column-major sorted by row)
    # sort both by (col, row)
    so = np.lexsort((starts[:, 0], starts[:, 1])); eo = np.lexsort((ends[:, 0], ends[:, 1]))
    starts = starts[so]; ends = ends[eo]
    cs = np.concatenate([np.zeros((1, n)), np.cumsum(seglen, 0)], 0)
    L = cs[ends[:, 0], ends[:, 1]] - cs[starts[:, 0], starts[:, 1]]
    completed = ends[:, 0] < nb
    return L[completed]


def sojourns(incap, seglen):
    """incap (nb,n) bool, seglen (nb,n). Returns for each (k,i) the total cap-sojourn length
    of the sojourn the segment belongs to (0 for stem segments), and the list of all
    completed sojourn lengths."""
    nb, n = incap.shape
    soj = np.zeros((nb, n)); lengths = []
    for i in range(n):
        col = incap[:, i]; L = seglen[:, i]
        # run-length over k
        k = 0
        while k < nb:
            if not col[k]:
                k += 1; continue
            j = k
            while j < nb and col[j]:
                j += 1
            s = L[k:j].sum()
            soj[k:j, i] = s
            if j < nb:           # completed (left the cap before the end)
                lengths.append(s)
            k = j
    return soj, np.array(lengths)


if __name__ == '__main__':
    import time
    rng = np.random.default_rng(1)
    n = 2000
    # free orbits launched from the stem
    P = np.stack([rng.uniform(-0.5, 0.5, n), rng.uniform(-1.0, 0.0, n)], 1)
    a = rng.uniform(0, 2 * np.pi, n); V = np.stack([np.cos(a), np.sin(a)], 1)
    t0 = time.time()
    segs, incap = propagate(P, V, 3000)
    print('propagate', time.time() - t0)
    L = np.hypot(segs[..., 2] - segs[..., 0], segs[..., 3] - segs[..., 1])
    rho = np.abs(segs[..., 0] * (segs[..., 3] - segs[..., 1]) - segs[..., 1] * (segs[..., 2] - segs[..., 0])) / L
    # caustic radius must be < r for every cap chord of a free orbit
    print('max rho of free cap chords', rho[incap].max())
    soj, lens = sojourns(incap, L)
    print('sojourns', len(lens), 'max', lens.max(), 'mean', lens.mean())
    # survival law
    lens.sort()
    for q in (1, 3, 10, 30, 100, 300):
        print(q, (lens > q).mean())
