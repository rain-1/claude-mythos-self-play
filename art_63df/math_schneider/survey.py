"""Survey a_n = n*c(nM) for many finite M in Z^2; look at the drop a_n - a_{n+1}."""
import sys, json, random
import numpy as np
from fractions import Fraction
from schneider import sumset, cindex

seed = int(sys.argv[1]); count = int(sys.argv[2]); nmax = int(sys.argv[3]); out = sys.argv[4]
rng = random.Random(seed)

def boundary_lattice(poly):
    pts = set()
    k = len(poly)
    from math import gcd
    for i in range(k):
        (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % k]
        g = gcd(abs(x1 - x0), abs(y1 - y0))
        for t in range(g):
            pts.add((x0 + (x1 - x0) // g * t, y0 + (y1 - y0) // g * t))
    return pts

def random_M():
    kind = rng.random()
    w = rng.randint(2, 6)
    if kind < 0.5:
        k = rng.randint(3, 9)
        pts = {(rng.randint(0, w), rng.randint(0, w)) for _ in range(k)}
    else:
        # boundary-heavy: hull of random points, keep lattice points on the boundary, drop a few, add a few
        k = rng.randint(3, 7)
        P = np.array(list({(rng.randint(0, w), rng.randint(0, w)) for _ in range(k)}))
        if len(P) < 3: return None
        from scipy.spatial import ConvexHull
        try: hv = ConvexHull(P).vertices
        except Exception: return None
        pts = boundary_lattice([tuple(int(v) for v in P[i]) for i in hv])
        pts = set(pts)
        for p in list(pts):
            if rng.random() < 0.15: pts.discard(p)
        for _ in range(rng.randint(0, 2)):
            pts.add((rng.randint(0, w), rng.randint(0, w)))
    pts = sorted(pts)
    if len(pts) < 3: return None
    A = np.array(pts)
    if np.linalg.matrix_rank(A[1:] - A[0]) < 2: return None
    return pts

res = []
tries = 0
while len(res) < count:
    M = random_M()
    if M is None: continue
    a = []
    ok = True
    for n in range(1, nmax + 1):
        c, ex, u, s = cindex(sumset(M, n), res=260, ncand=6)
        if not ex: ok = False
        a.append(c * n)
        if c == 0: 
            a += [Fraction(0)] * (nmax - n); break
    res.append(dict(M=M, a=[str(x) for x in a], exact=bool(ok)))
    if len(res) % 20 == 0:
        json.dump(res, open(out, "w")); print(len(res), flush=True)
json.dump(res, open(out, "w"))
