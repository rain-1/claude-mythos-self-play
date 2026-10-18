"""Restricted search: connected posets whose Hasse diagram is a tree (ANY
orientation, any height).  Every orientation of a tree is a Hasse diagram.
Iso classes are deduped by a canonical string of the oriented tree rooted at
its centre (the centre is fixed by automorphisms; for a bicentral tree the
central edge's direction distinguishes the two centres, so Aut = Aut(A)Aut(B)).
Usage: oriented_trees.py K   -> raw/otrees_K.json (top 60 by e/aut)."""
import sys, json, math
import numpy as np
import networkx as nx
from trees import linext

def rooted(T, D, v, p):
    subs = []
    for w in T[v]:
        if w == p: continue
        s, a = rooted(T, D, w, v)
        d = 'u' if (v, w) in D else 'd'      # w above v ('u') or below
        subs.append((d + s, a))
    subs.sort()
    aut = 1; i = 0
    while i < len(subs):
        j = i
        while j < len(subs) and subs[j][0] == subs[i][0]: j += 1
        aut *= math.factorial(j - i) * subs[i][1] ** (j - i)
        i = j
    return '(' + ''.join(s for s, _ in subs) + ')', aut

def main():
    k = int(sys.argv[1])
    seen = {}
    for T in nx.nonisomorphic_trees(k):
        edges = list(T.edges())
        c = nx.center(T)
        for mask in range(1 << len(edges)):
            D = set()
            for i, (u, v) in enumerate(edges):
                D.add((u, v) if mask >> i & 1 else (v, u))    # (lo, hi)
            if len(c) == 1:
                s, a = rooted(T, D, c[0], None)
            else:
                x, y = c
                if (y, x) in D: x, y = y, x                    # x < y
                T2 = T.copy(); T2.remove_edge(x, y)
                sx, ax = rooted(T2, D, x, None); sy, ay = rooted(T2, D, y, None)
                s, a = sx + '<' + sy, ax * ay
            if s in seen: continue
            pred = np.zeros(k, dtype=np.int64)
            for lo, hi in D: pred[hi] |= 1 << lo
            seen[s] = (int(linext(k, pred)), a, sorted([list(e) for e in D]))
    res = sorted(seen.values(), key=lambda r: -r[0] / r[1])
    json.dump(res[:60], open('raw/otrees_%d.json' % k, 'w'))
    print(k, len(seen), 'oriented-tree posets; top e/aut:', [(r[0], r[1]) for r in res[:4]])

if __name__ == '__main__':
    main()
