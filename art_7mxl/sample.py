"""Uniformly sample perfect matchings (Fibonacci permutations) of M_n via
sequential conditional counting, with permutation parity. Parallel over
workers; writes samples_<n>.pkl : list of (perm tuple, parity ±1).
"""
import pickle
import sys
import numpy as np
from multiprocessing import Pool
from detlib import fibs_upto
from permlib import elimination_order


def build_graph_sub(n, removed):
    F = fibs_upto(2 * n)
    adj = {}
    for i in range(1, n + 1):
        vi = i - 1
        if vi in removed:
            continue
        for q in F:
            j = q - i
            if 1 <= j <= n and (n + j - 1) not in removed:
                adj.setdefault(vi, set()).add(n + j - 1)
                adj.setdefault(n + j - 1, set()).add(vi)
    return adj


def count_sub(n, removed):
    """#perfect matchings of Q_n minus `removed` vertices."""
    adjd = build_graph_sub(n, removed)
    verts = sorted(set(range(2 * n)) - set(removed))
    if len(verts) % 2:
        return 0
    idx = {v: k for k, v in enumerate(verts)}
    adj = [set(idx[u] for u in adjd.get(v, ())) for v in verts]
    N = len(adj)
    if N == 0:
        return 1
    # elimination order + forest DP (same as permlib.count_pm)
    order, _ = elimination_order(adj)
    pos = {v: k for k, v in enumerate(order)}
    A = [set(s) for s in adj]
    bags = []
    for v in order:
        nb = sorted((u for u in A[v] if pos[u] > pos[v]), key=lambda u: pos[u])
        bags.append((v, tuple(nb)))
        for a in nb:
            for b in nb:
                if a != b:
                    A[a].add(b)
        for u in nb:
            A[u].discard(v)
    sepd = {v: nb for v, nb in bags}
    children = {v: [] for v, _ in bags}
    roots = []
    for v, nb in bags:
        (children[nb[0]].append(v) if nb else roots.append(v))
    TABLES = {}
    for v, nb in bags:
        T = {frozenset(): 1}
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
        out = {}
        sv = set(sepd[v])
        for S, cnt in T.items():
            if v in S:
                S2 = frozenset(S - {v})
                out[S2] = out.get(S2, 0) + cnt
            else:
                for u in sepd[v]:
                    if u in adj[v] and u not in S:
                        S2 = frozenset((S - {v}) | {u})
                        out[S2] = out.get(S2, 0) + cnt
        TABLES[v] = {S: c for S, c in out.items() if S <= sv}
    total = 1
    for r in roots:
        total *= TABLES.pop(r).get(frozenset(), 0)
    return total


def parity(perm):
    """perm as 0-indexed list; +1 even, -1 odd."""
    n = len(perm)
    seen = [False] * n
    sgn = 1
    for i in range(n):
        if seen[i]:
            continue
        l = 0
        j = i
        while not seen[j]:
            seen[j] = True
            j = perm[j]
            l += 1
        if l % 2 == 0:
            sgn = -sgn
    return sgn


def sample_one(args):
    n, seed = args
    rng = np.random.default_rng(seed)
    F = fibs_upto(2 * n)
    removed = set()
    perm = [None] * n
    for i in range(1, n + 1):
        vi = i - 1
        if vi in removed:
            raise RuntimeError
        opts = []
        for q in F:
            j = q - i
            if 1 <= j <= n and (n + j - 1) not in removed:
                opts.append(j)
        weights = []
        for j in opts:
            c = count_sub(n, removed | {vi, n + j - 1})
            weights.append(c)
        tot = sum(weights)
        assert tot > 0, (n, i, "no completion")
        r = rng.integers(0, tot)
        acc = 0
        for j, w in zip(opts, weights):
            acc += w
            if r < acc:
                perm[vi] = j - 1
                removed.add(vi)
                removed.add(n + j - 1)
                break
    # verify Fibonacci condition
    fset = set(F)
    for i in range(n):
        assert (i + 1) + (perm[i] + 1) in fset
    return tuple(perm), parity(perm)


if __name__ == "__main__":
    n = int(sys.argv[1])
    NS = int(sys.argv[2]) if len(sys.argv) > 2 else 2000
    with Pool(3) as p:
        res = p.map(sample_one, [(n, 1000 + s) for s in range(NS)],
                    chunksize=10)
    ev = sum(1 for _, s in res if s > 0)
    print(f"n={n}: {NS} samples, {ev} even, {NS-ev} odd")
    pickle.dump(res, open(f"samples_{n}.pkl", "wb"))
