"""Knot determinant of a closed polygon (|Delta(-1)|) from a generic projection; trefoil -> 3, unknot -> 1."""
import numpy as np, itertools

def crossings(P, rot):
    Q = P @ rot.T
    n = len(Q); out = []
    for i in range(n):
        a, b = Q[i], Q[(i + 1) % n]
        for j in range(i + 1, n):
            if j == i + 1 or (i == 0 and j == n - 1): continue
            c, d = Q[j], Q[(j + 1) % n]
            M = np.array([[b[0] - a[0], c[0] - d[0]], [b[1] - a[1], c[1] - d[1]]])
            det = np.linalg.det(M)
            if abs(det) < 1e-12: continue
            s, t = np.linalg.solve(M, [c[0] - a[0], c[1] - a[1]])
            if 0 < s < 1 and 0 < t < 1:
                zi = a[2] + s * (b[2] - a[2]); zj = c[2] + t * (d[2] - c[2])
                out.append((i + s, j + t, zi > zj))   # (param on strand i, param on strand j, i is over)
    return out

def determinant(P, rot=None):
    if rot is None:
        rot = np.linalg.qr(np.random.default_rng(1).standard_normal((3, 3)))[0]
    X = crossings(P, rot)
    if len(X) < 3: return 1
    n = len(P)
    # undercrossing parameters split the curve into arcs
    unders = sorted([(x[1] if x[2] else x[0]) for x in X])
    def arc_of(t):
        # arc k runs from unders[k-1] to unders[k]; arc index of a point at parameter t
        k = np.searchsorted(unders, t) % len(unders)
        return k
    m = len(X)
    A = np.zeros((m, m))
    for r, (ti, tj, iover) in enumerate(X):
        to, tu = (ti, tj) if iover else (tj, ti)
        o = arc_of(to)
        u_in = arc_of(tu - 1e-9); u_out = arc_of(tu + 1e-9)
        A[r, o] += 2; A[r, u_in] -= 1; A[r, u_out] -= 1
    return int(round(abs(np.linalg.det(A[1:, 1:]))))

def ham_cycles(k=6):
    """all (k-1)!/2 undirected cyclic orderings starting at 0"""
    seen = set(); out = []
    for p in itertools.permutations(range(1, k)):
        c = (0,) + p
        key = min(c[1:] , tuple(reversed(c[1:])))
        if p[0] > p[-1]: continue
        out.append(c)
    return out
