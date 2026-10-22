# In a combinatorially regular octahedron (hull of 6 random sphere points), is the unique trefoil
# always one of the 8 hexagons that alternate 'diagonal' (non-hull-edge chord) and hull edge?
import numpy as np
from scipy.spatial import ConvexHull
from knot import determinant, ham_cycles
rng = np.random.default_rng(11); cyc = ham_cycles(); stats = {}
rot = np.linalg.qr(rng.standard_normal((3, 3)))[0]
done = 0
while done < 400:
    P = rng.standard_normal((6, 3)); P /= np.linalg.norm(P, axis=1)[:, None]
    h = ConvexHull(P); E = set()
    for s in h.simplices:
        for a in range(3): E.add(frozenset((s[a], s[(a + 1) % 3])))
    deg = np.zeros(6, int)
    for e in E:
        for v in e: deg[v] += 1
    if not all(deg == 4): continue
    done += 1
    T = [c for c in cyc if determinant(P[list(c)], rot) == 3]
    for c in T:
        k = sum(frozenset((c[i], c[(i + 1) % 6])) not in E for i in range(6))
        stats[k] = stats.get(k, 0) + 1
print('trefoil cycles by number of non-edge chords:', stats, 'over', done, 'regular octahedra')
