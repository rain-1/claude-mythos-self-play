"""tess.py — the 261 unfoldings of the tesseract into R^3.
Cells: (axis a, sign s), x_a = s. Two cells adjacent iff axes differ. An unfolding = spanning tree
of the cell-adjacency graph K_{2,2,2,2}; classes = orbits of the hyperoctahedral group B4 (384)."""
import numpy as np, itertools, pickle
cells = [(a, s) for a in range(4) for s in (1, -1)]
idx = {c: i for i, c in enumerate(cells)}
edges = [(i, j) for i in range(8) for j in range(i+1, 8) if cells[i][0] != cells[j][0]]

def is_tree(es):
    p = list(range(8))
    def f(x):
        while p[x] != x: p[x] = p[p[x]]; x = p[x]
        return x
    for i, j in es:
        a, b = f(i), f(j)
        if a == b: return False
        p[a] = b
    return True

# B4: permutation of axes + sign flips -> action on cells
group = []
for perm in itertools.permutations(range(4)):
    for signs in itertools.product((1, -1), repeat=4):
        group.append([idx[(perm[a], s*signs[a])] for (a, s) in cells])
def canon(es):
    best = None
    for g in group:
        k = tuple(sorted(tuple(sorted((g[i], g[j]))) for i, j in es))
        if best is None or k < best: best = k
    return best

trees = [es for es in itertools.combinations(edges, 7) if is_tree(es)]
print('spanning trees', len(trees))
classes = {}
for es in trees:
    k = canon(es)
    classes.setdefault(k, 0); classes[k] += 1
print('classes', len(classes))

def unfold(es, root=None):
    """returns list of 8 (cell, 3-D centre in units where cube side=2, map) via fold maps"""
    adj = {i: [] for i in range(8)}
    for i, j in es: adj[i].append(j); adj[j].append(i)
    deg = [len(adj[i]) for i in range(8)]
    if root is None: root = max(range(8), key=lambda i: deg[i])
    a0, s0 = cells[root]
    keep = [k for k in range(4) if k != a0]
    # affine maps as functions R^4 -> R^4 (points stay in root hyperplane), composed
    maps = {root: (np.eye(4), np.zeros(4))}
    order = [root]; seen = {root}
    k = 0
    while k < len(order):
        P = order[k]; k += 1
        for B in adj[P]:
            if B in seen: continue
            seen.add(B); order.append(B)
            a, s = cells[P]; b, t = cells[B]
            # fold F: x_a := s ; x_b := t + t*(1 - s*x_a)
            Mf = np.eye(4); cf = np.zeros(4)
            Mf[a] = 0; cf[a] = s
            Mf[b] = 0; Mf[b, a] = -t*s; cf[b] = t + t
            MP, cP = maps[P]
            maps[B] = (MP @ Mf, MP @ cf + cP)
    out = []
    for i in range(8):
        a, s = cells[i]
        c = np.zeros(4); c[a] = s
        M, cc = maps[i]
        y = M @ c + cc
        out.append(y[keep] / 2.0)
    return np.array(out), [cells[i] for i in range(8)]

if __name__ == '__main__':
    res = []
    for k, n in classes.items():
        P, cl = unfold(k)
        P = np.round(P).astype(int)
        assert len(set(map(tuple, P))) == 8, 'overlap'
        res.append(dict(edges=k, orbit=n, pos=P, cells=cl))
    print('orbit sizes', sorted(set(r['orbit'] for r in res)), 'sum', sum(r['orbit'] for r in res))
    pickle.dump(res, open('tess261.pkl', 'wb'))
    # Dali cross check: a straight 4 + 4 arms
