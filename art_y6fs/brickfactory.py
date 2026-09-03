"""The Brick Factory — Zarankiewicz's drawing of K_{n,m} (MO 514851 / Turán's brick factory).
n vertices on the x-axis (half each side of the origin), m on the y-axis; every edge a segment.
The crossings are counted exactly and compared with Z(n,m) = floor(n/2)floor((n-1)/2)floor(m/2)floor((m-1)/2)
(Zarankiewicz's conjecture: cr(K_{n,m}) = Z(n,m); proved for min(n,m) <= 6 by Kleitman 1970).
Bonus: the exact minimum number of zeros R(n,m) of a (3,3)-even function for small n,m,
by enumerating the binary linear code ker(T_n (x) T_m).

usage: python3 brickfactory.py SIZE n m [out]
"""
import sys, math, itertools, time, json
import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image, ImageDraw
from pastel import *


def zar(n, m):
    return (n // 2) * ((n - 1) // 2) * (m // 2) * ((m - 1) // 2)


def layout(n, m, ax=1.0):
    """Zarankiewicz: x-points at +-1..+-ceil(n/2), y-points at +-1..; unequal halves for odd n"""
    xs = [i for i in range(1, n // 2 + 1)] + [-i for i in range(1, n - n // 2 + 1)]
    ys = [i for i in range(1, m // 2 + 1)] + [-i for i in range(1, m - m // 2 + 1)]
    X = [(float(x), 0.0) for x in xs]
    Y = [(0.0, float(y) * ax) for y in ys]
    return X, Y


def crossings(X, Y):
    """exact crossing count of the straight-line drawing (segments meet in interiors)"""
    E = [(i, j) for i in range(len(X)) for j in range(len(Y))]
    P = np.array([X[i] + Y[j] for i, j in E], float)   # x0,y0,x1,y1
    cnt = 0
    pts = []
    x0, y0, x1, y1 = P[:, 0], P[:, 1], P[:, 2], P[:, 3]
    for a in range(len(E)):
        i, j = E[a]
        # vectorised over b > a
        b = np.arange(a + 1, len(E))
        ib = np.array([E[k][0] for k in b]); jb = np.array([E[k][1] for k in b])
        share = (ib == i) | (jb == j)
        # orientation tests
        def orient(ax_, ay_, bx_, by_, cx_, cy_):
            return (bx_ - ax_) * (cy_ - ay_) - (by_ - ay_) * (cx_ - ax_)
        o1 = orient(x0[a], y0[a], x1[a], y1[a], x0[b], y0[b])
        o2 = orient(x0[a], y0[a], x1[a], y1[a], x1[b], y1[b])
        o3 = orient(x0[b], y0[b], x1[b], y1[b], x0[a], y0[a])
        o4 = orient(x0[b], y0[b], x1[b], y1[b], x1[a], y1[a])
        cross = (~share) & (o1 * o2 < 0) & (o3 * o4 < 0)
        cnt += int(cross.sum())
        for k in b[cross]:
            # intersection point
            d = (x1[a] - x0[a]) * (y1[k] - y0[k]) - (y1[a] - y0[a]) * (x1[k] - x0[k])
            t = ((x0[k] - x0[a]) * (y1[k] - y0[k]) - (y0[k] - y0[a]) * (x1[k] - x0[k])) / d
            pts.append((x0[a] + t * (x1[a] - x0[a]), y0[a] + t * (y1[a] - y0[a]), a, k))
    return cnt, pts, E, P


def R_exact(n, m):
    """min zeros of a (3,3)-even g: enumerate the code ker(M -> T_n M T_m^T) over GF(2)."""
    pairsA = list(itertools.combinations(range(n), 2)); pairsB = list(itertools.combinations(range(m), 2))
    ia = {p: k for k, p in enumerate(pairsA)}; ib = {p: k for k, p in enumerate(pairsB)}
    nv = len(pairsA) * len(pairsB)
    rows = []
    for A1 in itertools.combinations(range(n), 3):
        for B1 in itertools.combinations(range(m), 3):
            r = 0
            for e in itertools.combinations(A1, 2):
                for f in itertools.combinations(B1, 2):
                    r |= 1 << (ia[e] * len(pairsB) + ib[f])
            rows.append(r)
    # row reduce to find the kernel basis (variables = nv bits)
    # Gaussian elimination over GF(2) on constraint rows
    piv = {}
    for r in rows:
        for c in range(nv):
            if (r >> c) & 1:
                if c in piv:
                    r ^= piv[c]
                else:
                    piv[c] = r; break
    # reduced echelon
    cols = sorted(piv)
    for c in cols:
        for c2 in cols:
            if c2 != c and (piv[c2] >> c) & 1:
                piv[c2] ^= piv[c]
    free = [c for c in range(nv) if c not in piv]
    basis = []
    for fcol in free:
        v = 1 << fcol
        for c in cols:
            if (piv[c] >> fcol) & 1:
                v |= 1 << c
        basis.append(v)
    k = len(basis)
    assert k <= 28, k
    # enumerate all 2^k codewords by Gray code in numpy chunks
    basis = np.array(basis, dtype=np.uint64) if nv <= 64 else None
    best = 0
    lo_bits = min(k, 14); hi_bits = k - lo_bits
    lo = np.zeros(1 << lo_bits, np.uint64)
    for i in range(1, 1 << lo_bits):
        g = i ^ (i >> 1); gp = (i - 1) ^ ((i - 1) >> 1)
        lo[i] = lo[i - 1] ^ basis[int(math.log2(g ^ gp))]
    def popcount(a):
        a = a.astype(np.uint64)
        c = np.zeros(a.shape, np.int64)
        for s in range(0, nv, 8):
            c += np.array([bin(x).count('1') for x in range(256)], np.int64)[((a >> np.uint64(s)) & np.uint64(255)).astype(np.int64)]
        return c
    hi_val = np.uint64(0)
    for i in range(1 << hi_bits):
        if i > 0:
            g = i ^ (i >> 1); gp = (i - 1) ^ ((i - 1) >> 1)
            hi_val ^= basis[lo_bits + int(math.log2(g ^ gp))]
        w = popcount(lo ^ hi_val).max()
        best = max(best, int(w))
    return nv - best, k, nv


def render(SIZE, n, m, out):
    SS = 2
    W = H = SIZE * SS
    X, Y = layout(n, m)
    t0 = time.time()
    cnt, pts, E, P = crossings(X, Y)
    Z = zar(n, m)
    print('K_{%d,%d}: %d edges, crossings %d, Z(n,m) = %d, equal: %s (%.1fs)' % (n, m, len(E), cnt, Z, cnt == Z, time.time() - t0))
    # frame: the drawing spans [-n/2, n/2] x [-m/2, m/2]; leave paper around
    ext = max(n - n // 2, m - m // 2) + 0.5
    sc = 0.42 * W / ext
    cx, cy = W / 2, H / 2 - 0.02 * H
    tx = lambda x: cx + sc * x; ty = lambda y: cy - sc * y
    sheet = Sheet(W, H, seed=13)
    # edges by quadrant -> pigment; thin ink on top
    quad_pig = {(1, 1): 'apricot', (-1, 1): 'aqua', (-1, -1): 'lavender', (1, -1): 'pistachio'}
    for q, pig in quad_pig.items():
        segs = [(tx(P[a, 0]), ty(P[a, 1]), tx(P[a, 2]), ty(P[a, 3])) for a in range(len(E))
                if np.sign(P[a, 0] + P[a, 2]) == q[0] and np.sign(P[a, 1] + P[a, 3]) == q[1]]
        D = draw_lines_density(W, H, segs, 2.2 * SS, sigma=0.9 * SS)
        D = D / (D.max() + 1e-9)
        sheet.wash(D * 0.6, pig, granulate=0.2, seed=50 + len(pig))
    segs = [(tx(P[a, 0]), ty(P[a, 1]), tx(P[a, 2]), ty(P[a, 3])) for a in range(len(E))]
    D = draw_lines_density(W, H, segs, 0.7 * SS, sigma=0.4 * SS)
    sheet.wash(D / (D.max() + 1e-9) * 0.36, 'ink')
    # crossings: coral beads, size by local crossing density (how many crossings on the two edges)
    load = np.zeros(len(E), int)
    for (_, _, a, k) in pts:
        load[a] += 1; load[k] += 1
    bx = np.array([tx(p[0]) for p in pts]); by = np.array([ty(p[1]) for p in pts])
    bl = np.array([load[p[2]] + load[p[3]] for p in pts], float)
    br = (0.55 + 0.9 * (bl / bl.max())) * 0.0021 * W
    D = discs_density(W, H, bx, by, br, np.ones(len(pts)), sigma=0.6 * SS)
    sheet.wash(D / (D.max() + 1e-9) * 0.9, 'coral', granulate=0.15, seed=61)
    Dk = discs_density(W, H, bx, by, br * 0.30, np.ones(len(pts)), sigma=0.4 * SS)
    sheet.wash(Dk / (Dk.max() + 1e-9) * 0.6, 'ink')
    # the vertices: ink dots on the axes
    vx = [tx(x) for x, _ in X] + [tx(0) for _ in Y]; vy = [ty(0) for _ in X] + [ty(y) for _, y in Y]
    D = discs_density(W, H, vx, vy, [0.0065 * W] * len(vx), [1.0] * len(vx), sigma=0.8 * SS)
    sheet.wash(D / (D.max() + 1e-9) * 0.9, 'ink')
    sheet.caption_strip(0.905, 0.985)
    items = [("The Brick Factory", 0.05 * W, 0.935 * H, 0.030 * W, 'serif_bold', 'ls'),
             ("K(%d,%d) drawn Zarankiewicz's way: %d crossings = floor(n/2) floor((n−1)/2) floor(m/2) floor((m−1)/2) exactly; nobody has drawn it with fewer, and up to 6 nobody can" % (n, m, cnt),
              0.05 * W, 0.962 * H, 0.0135 * W, 'italic', 'ls')]
    T = text_density(W, H, items)
    sheet.wash(T * 0.85, 'ink')
    img = sheet.develop()
    finish(img, (SIZE, SIZE), out)
    return dict(n=n, m=m, edges=len(E), crossings=cnt, Z=Z)


if __name__ == '__main__':
    SIZE = int(sys.argv[1]); n = int(sys.argv[2]); m = int(sys.argv[3])
    out = sys.argv[4] if len(sys.argv) > 4 else 'brickfactory_%d.png' % SIZE
    res = render(SIZE, n, m, out)
    # exact R(n,m) for small cases
    table = {}
    for (a, b) in [(3, 3), (3, 4), (3, 5), (4, 4)]:
        t0 = time.time()
        R, k, nv = R_exact(a, b)
        bound = (a // 2) * ((a - 1) // 2) * (b // 2) * ((b - 1) // 2)
        lower24 = math.ceil(a * (a - 1) * b * (b - 1) / 24 / 1.0)
        table['%d,%d' % (a, b)] = dict(R=R, dim=k, F=nv, zar_upper=bound)
        print('R(%d,%d) = %d  (code dim %d, |F| = %d, Zarankiewicz-drawing upper bound %d)  %.1fs' % (a, b, R, k, nv, bound, time.time() - t0))
    res['R_table'] = table
    json.dump(res, open(out.replace('.png', '_cert.json'), 'w'), indent=1)
