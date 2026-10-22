# Does the trefoil's handedness equal the chirality chi = s12*s13*s23 of the three hull diagonals,
# s_ij = sign((u_i x u_j) . (p_j - p_i))  (independent of how each diagonal is oriented)?
import numpy as np
from scipy.spatial import ConvexHull
from knot import determinant, ham_cycles
def writhe(P, rot):
    Q = P @ rot.T; n = len(Q); w = 0
    for i in range(n):
        a, b = Q[i], Q[(i + 1) % n]
        for j in range(i + 2, n):
            if i == 0 and j == n - 1: continue
            c, d = Q[j], Q[(j + 1) % n]
            M = np.array([[b[0]-a[0], c[0]-d[0]], [b[1]-a[1], c[1]-d[1]]])
            if abs(np.linalg.det(M)) < 1e-12: continue
            s, t = np.linalg.solve(M, [c[0]-a[0], c[1]-a[1]])
            if 0 < s < 1 and 0 < t < 1:
                over_i = a[2] + s*(b[2]-a[2]) > c[2] + t*(d[2]-c[2])
                cr = (b-a)[0]*(d-c)[1] - (b-a)[1]*(d-c)[0]
                w += np.sign(cr) * (1 if over_i else -1)
    return w
rng = np.random.default_rng(3); cyc = ham_cycles(); agree = 0; tot = 0
rots = [np.linalg.qr(rng.standard_normal((3, 3)))[0] for _ in range(40)]
rots = [r if np.linalg.det(r) > 0 else -r for r in rots]
while tot < 200:
    P = rng.standard_normal((6, 3)); P /= np.linalg.norm(P, axis=1)[:, None]
    h = ConvexHull(P); E = set()
    for s in h.simplices:
        for a in range(3): E.add(frozenset((s[a], s[(a + 1) % 3])))
    deg = np.zeros(6, int)
    for e in E:
        for v in e: deg[v] += 1
    if not all(deg == 4): continue
    T = [c for c in cyc if determinant(P[list(c)], rots[0]) == 3][0]
    D = [(a, b) for a in range(6) for b in range(a + 1, 6) if frozenset((a, b)) not in E]
    s = 1
    for x in range(3):
        for y in range(x + 1, 3):
            (a, b), (c, d) = D[x], D[y]
            s *= np.sign(np.cross(P[b]-P[a], P[d]-P[c]) @ (P[c]-P[a]))
    hand = np.sign(np.mean([writhe(P[list(T)], r) for r in rots]))
    tot += 1; agree += (hand == s)
print('agree', agree, 'of', tot)
