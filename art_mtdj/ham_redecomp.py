# For every (T1 = cycle 0..n-1, P = Ham path in complement), test whether T1 ∪ P has another
# decomposition into a Ham cycle C and an x–y Ham path Q (same endpoints) with C ∪ Q = T1 ∪ P.
# If yes: w(C)+w(Q) = w(T1)+w(P), so one of them is no worse -> uniqueness fails -> no counterexample.
import sys
from ham_lp import ham_cycles, ham_paths, E
from collections import Counter
n = int(sys.argv[1]); T1 = E(list(range(n)), True); T1s = set(T1)
cadj = {i: [j for j in range(n) if j != i and frozenset((i, j)) not in T1s] for i in range(n)}
def all_paths():
    for s in range(n):
        path = [s]; used = [False] * n; used[s] = True
        def rec():
            if len(path) == n:
                if path[0] < path[-1]: yield list(path)
                return
            for v in cadj[path[-1]]:
                if not used[v]:
                    used[v] = True; path.append(v); yield from rec(); path.pop(); used[v] = False
        yield from rec()
tot = ok = 0; stubborn = []
for P in all_paths():
    tot += 1; Pe = set(E(P, False)); allE = T1s | Pe
    adj = {i: [] for i in range(n)}
    for e in allE:
        a, b = tuple(e); adj[a].append(b); adj[b].append(a)
    x, y = P[0], P[-1]
    found = False
    for c in ham_cycles(n, adj):
        Ce = set(E(c, True))
        if Ce == T1s: continue
        rest = allE - Ce
        # rest must be an x-y Ham path (n-1 edges, connected, degrees right)
        if len(rest) != n - 1: continue
        deg = Counter(v for e in rest for v in e)
        if deg[x] == 1 and deg[y] == 1 and all(deg[v] == 2 for v in range(n) if v not in (x, y)):
            # connectivity
            seen = {x}; st = [x]
            while st:
                u = st.pop()
                for e in rest:
                    if u in e:
                        (w,) = tuple(e - {u})
                        if w not in seen: seen.add(w); st.append(w)
            if len(seen) == n: found = True; break
    ok += found
    if not found and len(stubborn) < 5: stubborn.append(P)
print('n', n, 'pairs', tot, 're-decomposable', ok, 'stubborn examples', stubborn)
