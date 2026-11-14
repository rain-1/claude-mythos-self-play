"""The 25-circle torus packing with d^2 = (13-6 sqrt3)/61 is a tiling by 24 triangles and 13 squares."""
import numpy as np, itertools, json
from torus import answer25, dists
P = answer25(); n = len(P); d = dists(P).min()
def delta(i, j):
    v = P[j] - P[i]; return v - np.round(v)
adj = {i: [] for i in range(n)}
for i in range(n):
    for j in range(n):
        if i != j and abs(np.hypot(*delta(i, j)) - d) < 1e-9: adj[i].append(j)
E = sum(len(v) for v in adj.values()) // 2
print("d =", d, "edges", E, "degrees", sorted(len(v) for v in adj.values()))
# faces: walk the rotation system
faces = []; seen = set()
ang = {i: sorted(adj[i], key=lambda j: np.arctan2(*delta(i, j)[::-1])) for i in range(n)}
for i in range(n):
    for j in adj[i]:
        if (i, j) in seen: continue
        f = []; a, b = i, j
        while (a, b) not in seen:
            seen.add((a, b)); f.append(a)
            nb = ang[b]; k = nb.index(a)
            a, b = b, nb[(k - 1) % len(nb)]
        faces.append(f)
sizes = sorted(len(f) for f in faces)
print("faces", len(faces), {k: sizes.count(k) for k in set(sizes)}, "Euler V-E+F =", n - E + len(faces))
out = []
for f in faces:
    pts = [P[f[0]]]
    for a, b in zip(f, f[1:]): pts.append(pts[-1] + delta(a, b))
    pts = np.array(pts)
    if len(f) == 4:
        e1 = pts[1] - pts[0]; e2 = pts[3] - pts[0]
        assert abs(e1 @ e2) < 1e-9, "not a square"
    out.append(dict(k=len(f), c=(pts.mean(0) % 1).tolist(), v=pts.tolist()))
print("all quadrilateral faces are squares; area check:", 24 * 3**.5 / 4 * d * d + 13 * d * d)
json.dump(dict(P=P.tolist(), d=d, faces=out, adj=adj), open("packing25.json", "w"))
