# Parity of the number of unordered Hamiltonian decompositions of random 4-regular (multi)graphs.
import networkx as nx, random, sys
from collections import Counter
def ham_cycles_multi(n, edges):
    # edges: list of (a,b) with ids; returns list of frozensets of edge ids forming Ham cycles
    inc = {i: [] for i in range(n)}
    for k, (a, b) in enumerate(edges): inc[a].append((k, b)); inc[b].append((k, a))
    out = []; used_v = [False] * n; path_e = []
    used_v[0] = True
    def rec(u, depth):
        if depth == n - 1:
            for k, w in inc[u]:
                if w == 0 and k not in path_e:
                    cyc = frozenset(path_e + [k])
                    out.append(cyc)
            return
        for k, w in inc[u]:
            if not used_v[w]:
                used_v[w] = True; path_e.append(k); rec(w, depth + 1); path_e.pop(); used_v[w] = False
    rec(0, 0)
    return set(out)   # each cycle found twice (two directions) -> set dedups
def count_hd(n, edges):
    cyc = ham_cycles_multi(n, edges); allk = frozenset(range(len(edges)))
    return sum(1 for c in cyc if (allk - c) in cyc) // 2
random.seed(1); dist = Counter()
for t in range(int(sys.argv[2])):
    n = int(sys.argv[1])
    if len(sys.argv) > 3:   # multigraph: union of two random Ham cycles
        p = list(range(n)); q = list(range(n)); random.shuffle(q)
        edges = [(p[i], p[(i + 1) % n]) for i in range(n)] + [(q[i], q[(i + 1) % n]) for i in range(n)]
    else:
        G = nx.random_regular_graph(4, n, seed=random.randrange(10**9)); edges = list(G.edges())
    c = count_hd(n, edges)
    if c: dist[c] += 1
print(sys.argv[1:], sorted(dist.items()))
