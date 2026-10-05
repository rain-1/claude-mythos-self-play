# find (T1, P) on n vertices whose union has exactly K-1 re-decompositions; save all decompositions
import random, json, sys
from collections import Counter
from ham_lp import ham_cycles, E
n, K, seed = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]); random.seed(seed)
T1s = set(E(list(range(n)), True))
def rand_path():
    while True:
        path = [random.randrange(n)]; used = set(path)
        def rec():
            if len(path) == n: return True
            nb = [v for v in range(n) if v not in used and frozenset((path[-1], v)) not in T1s]; random.shuffle(nb)
            for v in nb:
                path.append(v); used.add(v)
                if rec(): return True
                path.pop(); used.discard(v)
            return False
        if rec(): return path
def decomps(P):
    Pe = set(E(P, False)); allE = T1s | Pe; x, y = P[0], P[-1]
    adj = {i: [] for i in range(n)}
    for e in allE:
        a, b = tuple(e); adj[a].append(b); adj[b].append(a)
    res = []
    for c in ham_cycles(n, adj):
        rest = allE - set(E(c, True)); deg = Counter(v for e in rest for v in e)
        if len(rest) == n - 1 and deg[x] == 1 and deg[y] == 1 and all(deg[v] == 2 for v in range(n) if v not in (x, y)):
            # order the path from x
            order = [x]; prev = None
            while len(order) < n:
                u = order[-1]
                nxt = [tuple(e - {u})[0] for e in rest if u in e and tuple(e - {u})[0] != prev]
                if not nxt: break
                prev = u; order.append(nxt[0])
            if len(order) == n: res.append((c, order))
    return res
for t in range(4000):
    P = rand_path(); D = decomps(P)
    if len(D) == K:
        # put the original first
        D.sort(key=lambda d: set(E(d[0], True)) != T1s)
        json.dump(dict(n=n, P=P, D=D), open(f'ham_sheet_{n}_{K}.json', 'w')); print('found at', t, 'x,y', P[0], P[-1]); break
else: print('none')
