"""Count perfect matchings (= permanent of M_n) of the Fibonacci-sum
bipartite graph Q_n: rows r_1..r_n, cols c_1..c_n, edge iff i+j Fibonacci.

Method: min-degree elimination order -> chordal completion -> clique tree
-> DP over the tree decomposition counting perfect matchings exactly
(python ints, no overflow).
"""
from detlib import fibs_upto


def build_graph(n):
    """Vertices 0..n-1 rows, n..2n-1 cols; adjacency sets."""
    F = fibs_upto(2 * n)
    adj = [set() for _ in range(2 * n)]
    for i in range(1, n + 1):
        for q in F:
            j = q - i
            if 1 <= j <= n:
                adj[i - 1].add(n + j - 1)
                adj[n + j - 1].add(i - 1)
    return adj


def elimination_order(adj):
    """Min-degree (with fill) order; returns order and chordal adjacency."""
    import heapq
    N = len(adj)
    A = [set(s) for s in adj]
    alive = [True] * N
    heap = [(len(A[v]), v) for v in range(N)]
    heapq.heapify(heap)
    order = []
    width = 0
    while heap:
        d, v = heapq.heappop(heap)
        if not alive[v] or len(A[v]) != d:
            if alive[v]:
                heapq.heappush(heap, (len(A[v]), v))
            continue
        alive[v] = False
        order.append(v)
        nb = [u for u in A[v] if alive[u]]
        width = max(width, len(nb))
        for a in nb:
            for b in nb:
                if a < b and b not in A[a]:
                    A[a].add(b)
                    A[b].add(a)
        for u in nb:
            A[u].discard(v)
            heapq.heappush(heap, (len(A[u]), u))
    return order, width


def count_pm(n):
    """Exact number of perfect matchings of Q_n (= permanent of M_n)."""
    if n == 0:
        return 1
    adj = build_graph(n)
    order, width = elimination_order(adj)
    pos = {v: k for k, v in enumerate(order)}
    # bags: when v eliminated, bag = {v} + later neighbors in chordal graph
    # recompute chordal fill with same order
    A = [set(s) for s in adj]
    bags = []
    for v in order:
        nb = [u for u in A[v] if pos[u] > pos[v]]
        bags.append((v, tuple(sorted(nb, key=lambda u: pos[u]))))
        for a in nb:
            for b in nb:
                if a != b:
                    A[a].add(b)
        for u in nb:
            A[u].discard(v)
    # DP along elimination: state = dict mapping frozenset(matched subset of
    # "active boundary" vertices) -> count. Active = not yet eliminated but
    # adjacent-in-chordal-graph to eliminated part. Process v in order:
    #   v must end matched: either already matched (in state), or match v to
    #   one of its later neighbors u (original edges only), marking u matched.
    # Elimination-forest DP. For vertex v with separator sep(v)=N_later(v)
    # (a clique, size <= treewidth), parent(v) = first-eliminated member of
    # sep(v). T_v[S] = #ways to match ALL vertices eliminated in v's subtree
    # (v and descendants) using edges of Q_n, where S subseteq sep(v) is the
    # set of separator vertices consumed by the subtree. Children tables are
    # merged with disjoint consumed-sets; then v is matched either by a child
    # or to an unconsumed u in sep(v) with an ORIGINAL edge.
    orig = adj
    sep = {v: nb for v, nb in bags}
    children = {v: [] for v, _ in bags}
    roots = []
    for v, nb in bags:
        if nb:
            par = nb[0]  # first-eliminated later neighbor
            children[par].append(v)
        else:
            roots.append(v)
    import sys
    sys.setrecursionlimit(300000)

    def solve(v):
        # iterative post-order to avoid recursion depth issues
        T = {frozenset(): 1}  # consumed subsets of {v} + sep(v), incl. v
        # merge children: child's sep(c) subseteq {v} + sep(v)? RIP gives
        # sep(c) - {c...}: child's separator is a clique containing v.
        for c in children[v]:
            Tc = TABLES.pop(c)
            merged = {}
            for S1, c1 in T.items():
                for S2, c2 in Tc.items():
                    if S1 & S2:
                        continue
                    S = S1 | S2
                    merged[S] = merged.get(S, 0) + c1 * c2
            T = merged
        # now ensure v matched
        out = {}
        sv = set(sep[v])
        for S, cnt in T.items():
            if v in S:
                S2 = frozenset(S - {v})
                out[S2] = out.get(S2, 0) + cnt
            else:
                for u in sep[v]:
                    if u in orig[v] and u not in S:
                        S2 = frozenset((S - {v}) | {u})
                        out[S2] = out.get(S2, 0) + cnt
        # all keys must lie within sep(v)
        out = {S: c for S, c in out.items() if S <= sv}
        return out

    TABLES = {}
    # process in elimination order (children are always eliminated before
    # their parent, since parent is a LATER neighbor)
    for v, nb in bags:
        TABLES[v] = solve(v)
    total = 1
    for r in roots:
        Tr = TABLES.pop(r)
        total *= Tr.get(frozenset(), 0)
    return total


if __name__ == "__main__":
    import sys
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 33
    adjw = build_graph(n)
    _, w = elimination_order(adjw)
    print("n:", n, "elim width:", w, "matchings:", count_pm(n))
