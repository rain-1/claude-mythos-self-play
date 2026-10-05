# pick an instance (T1 = 0..n-1 cycle, P = Ham path disjoint from T1) and its re-decomposition
# (C, Q) maximising the number of edges that change hands; save as json for the renderer.
import random, json, sys
from collections import Counter
from ham_lp import ham_cycles, E
MODE = len(sys.argv) > 4
n = int(sys.argv[1]); random.seed(int(sys.argv[2]))
T1 = E(list(range(n)), True); T1s = set(T1)
def rand_path():
    while True:
        order = list(range(n)); random.shuffle(order)
        # randomized DFS for a Ham path in the complement
        path = [order[0]]; used = {order[0]}
        def rec():
            if len(path) == n: return True
            nb = [v for v in range(n) if v not in used and frozenset((path[-1], v)) not in T1s]
            random.shuffle(nb)
            for v in nb:
                path.append(v); used.add(v)
                if rec(): return True
                path.pop(); used.discard(v)
            return False
        if rec(): return path
best = None
for trial in range(int(sys.argv[3])):
    P = rand_path(); Pe = set(E(P, False)); allE = T1s | Pe; x, y = P[0], P[-1]
    adj = {i: [] for i in range(n)}
    for e in allE:
        a, b = tuple(e); adj[a].append(b); adj[b].append(a)
    alts = []
    for c in ham_cycles(n, adj):
        Ce = set(E(c, True))
        if Ce == T1s: continue
        rest = allE - Ce
        deg = Counter(v for e in rest for v in e)
        if len(rest) == n - 1 and deg[x] == 1 and deg[y] == 1 and all(deg[v] == 2 for v in range(n) if v not in (x, y)):
            seen = {x}; st = [x]
            while st:
                u = st.pop()
                for e in rest:
                    if u in e:
                        (w,) = tuple(e - {u})
                        if w not in seen: seen.add(w); st.append(w)
            if len(seen) == n: alts.append(c)
    if not alts: print('NO ALT', P); continue
    for c in alts:
        swapped = len(T1s - set(E(c, True)))
        key = (-len(alts), swapped) if MODE else (swapped, -len(alts))
        if best is None or key > best[0]: best = (key, P, c, len(alts))
print('best swapped', best[0], 'alts', best[3])
json.dump(dict(n=n, P=best[1], C=best[2], nalts=best[3]), open(f'ham_inst_{n}{"_min" if MODE else ""}.json', 'w'))
