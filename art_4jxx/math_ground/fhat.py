"""Enumerate vertices of F^ (2x2 tile frequency polytope cut out by row/column conservation laws)
and decide which are realised by periodic configurations (hence lie in K)."""
import itertools, json
import numpy as np
from gs import strip_opt, period_lattice, tile_freq

T = np.arange(16)
a, b, c, d = T & 1, (T >> 1) & 1, (T >> 2) & 1, (T >> 3) & 1
rows = []
for x in range(2):
    for y in range(2):
        rows.append(((a == x) & (b == y)).astype(float) - ((c == x) & (d == y)))  # top row = bottom row
        rows.append(((a == x) & (c == y)).astype(float) - ((b == x) & (d == y)))  # left col = right col
rows.append(np.ones(16))
A = np.array(rows)
rhs = np.zeros(len(rows)); rhs[-1] = 1
rk = np.linalg.matrix_rank(A)
verts = {}
for k in range(1, rk + 1):
    for S in itertools.combinations(range(16), k):
        AS = A[:, S]
        if np.linalg.matrix_rank(AS) < k:
            continue
        sol, *_ = np.linalg.lstsq(AS, rhs, rcond=None)
        if np.abs(AS @ sol - rhs).max() > 1e-9 or sol.min() < 1e-12:
            continue
        v = np.zeros(16); v[list(S)] = sol
        verts[tuple(np.round(v, 9))] = v
V = list(verts.values())
print("rank", rk, "vertices", len(V))
out = []
for v in V:
    S = np.nonzero(v > 1e-12)[0]
    J = np.ones(16); J[S] = 0.0  # exposes v (unique point of F^ supported in S)
    best = None
    for p in range(1, 13):
        e, g = strip_opt(J, p)
        if e < 1e-12:
            best = (p, g)
            break
    rec = dict(vertex=[float(t) for t in v], support=S.tolist())
    if best:
        area, pv, h, s, fd = period_lattice(best[1])
        fq = tile_freq(fd if s == 0 else best[1])
        rec.update(periodic=True, pv=pv, h=h, s=s, fd=fd.tolist(), freq_matches=bool(np.allclose(tile_freq(best[1]), v)))
    else:
        rec.update(periodic=False)
    out.append(rec)
    print(np.round(v, 3).tolist(), "support", S.tolist(), "periodic" if best else "NO periodic config (p<=12)",
          (rec.get("pv"), rec.get("h"), rec.get("s")) if best else "")
json.dump(out, open("data/fhat_vertices.json", "w"), indent=1)
