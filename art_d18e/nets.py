"""generic d-cube unfoldings: spanning trees of the facet graph modulo B_d, unfolded into R^(d-1)."""
import numpy as np, itertools
def nets(d):
    cells = [(a, s) for a in range(d) for s in (1, -1)]
    n = len(cells); idx = {c: i for i, c in enumerate(cells)}
    edges = [(i, j) for i in range(n) for j in range(i+1, n) if cells[i][0] != cells[j][0]]
    group = []
    for perm in itertools.permutations(range(d)):
        for signs in itertools.product((1, -1), repeat=d):
            group.append([idx[(perm[a], s*signs[a])] for (a, s) in cells])
    def is_tree(es):
        p = list(range(n))
        def f(x):
            while p[x] != x: x = p[x]
            return x
        for i, j in es:
            a, b = f(i), f(j)
            if a == b: return False
            p[a] = b
        return True
    seen = {}
    for es in itertools.combinations(edges, n - 1):
        if not is_tree(es): continue
        k = min(tuple(sorted(tuple(sorted((g[i], g[j]))) for i, j in es)) for g in group)
        seen[k] = seen.get(k, 0) + 1
    out = []
    for es in seen:
        adj = {i: [] for i in range(n)}
        for i, j in es: adj[i].append(j); adj[j].append(i)
        root = max(range(n), key=lambda i: len(adj[i]))
        a0 = cells[root][0]; keep = [k for k in range(d) if k != a0]
        maps = {root: (np.eye(d), np.zeros(d))}; order = [root]
        for P in order:
            for B in adj[P]:
                if B in maps: continue
                a, s = cells[P]; b, t = cells[B]
                Mf = np.eye(d); cf = np.zeros(d)
                Mf[a] = 0; cf[a] = s; Mf[b] = 0; Mf[b, a] = -t*s; cf[b] = 2*t
                MP, cP = maps[P]; maps[B] = (MP @ Mf, MP @ cf + cP); order.append(B)
        pos = []
        for i in range(n):
            c = np.zeros(d); c[cells[i][0]] = cells[i][1]
            M, cc = maps[i]; pos.append((M @ c + cc)[keep] / 2)
        out.append(dict(edges=es, cells=cells, pos=np.round(pos).astype(int), orbit=seen[es]))
    return out
if __name__ == '__main__':
    c = nets(3); print(len(c), sorted(x['orbit'] for x in c))
