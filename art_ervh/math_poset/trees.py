"""Restricted search: connected posets whose Hasse diagram is a tree of height<=2
(a free tree T, 2-coloured, one colour class = minimal elements).  For each
tree on k<=KMAX vertices compute e(P) (numba DP over down-sets) and #Aut(P)
(rooted-tree automorphisms at the centre; a bicentral tree's centre-swap flips
the colouring so it is an anti-automorphism, i.e. the poset is self-dual).
Writes raw/trees_k.json with the top TOPC per size: [e, aut, ndual_types, covers]."""
import sys, json, math
import numpy as np
import networkx as nx
from numba import njit

KMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 16
TOPC = 60

@njit(cache=True)
def linext(n, pred):
    N = 1 << n
    dp = np.zeros(N, dtype=np.int64)
    dp[0] = 1
    for m in range(N):
        v = dp[m]
        if v == 0:
            continue
        for j in range(n):
            if (m >> j) & 1 == 0 and (pred[j] & ~m) == 0:
                dp[m | (1 << j)] += v
    return dp[N - 1]

def rooted_aut(T, root):
    """returns (canonical string, aut count) of T rooted at root (excluding parent)."""
    def rec(v, p):
        subs = [rec(w, v) for w in T[v] if w != p]
        subs.sort()
        aut = 1
        i = 0
        while i < len(subs):
            j = i
            while j < len(subs) and subs[j][0] == subs[i][0]:
                j += 1
            aut *= math.factorial(j - i) * subs[i][1] ** (j - i)
            i = j
        return ('(' + ''.join(s[0] for s in subs) + ')', aut)
    return rec(root, None)

def tree_poset(T):
    c = nx.center(T)
    col = nx.bipartite.color(T)
    n = T.number_of_nodes()
    if len(c) == 1:
        aut = rooted_aut(T, c[0])[1]
        ntypes = 2                 # root-min and root-max orientations, non-isomorphic
        # (for k=1 there is just one; for k=2 chain, bicentral)
    else:
        a, b = c
        T2 = T.copy(); T2.remove_edge(a, b)
        sa, aa = rooted_aut(T2, a); sb, ab = rooted_aut(T2, b)
        aut = aa * ab
        ntypes = 1 if sa == sb else 2
    # orientation: colour 0 = minimal
    pred = np.zeros(n, dtype=np.int64)
    covers = []
    for u, v in T.edges():
        lo, hi = (u, v) if col[u] == 0 else (v, u)
        pred[hi] |= 1 << lo
        covers.append([lo, hi])
    if n == 1: ntypes = 1
    return int(linext(n, pred)), aut, ntypes, covers

def main():
    for k in range(1, KMAX + 1):
        res = []
        if k == 1:
            res = [[1, 1, 1, []]]
        else:
            for T in nx.nonisomorphic_trees(k):
                e, a, nt, cov = tree_poset(T)
                res.append([e, a, nt, cov])
        res.sort(key=lambda r: -r[0] / r[1])
        json.dump(res[:TOPC], open('raw/trees_%d.json' % k, 'w'))
        print(k, len(res), 'trees; best e/aut =', res[0][0], '/', res[0][1], flush=True)

if __name__ == '__main__':
    main()
