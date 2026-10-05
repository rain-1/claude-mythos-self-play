# MO 499431: K piles, N rocks; each round a uniformly random NON-EMPTY pile loses a rock; stop when one
# non-empty pile remains.  E(state) = expected size of the last pile.  Conjecture: a balanced start minimises it.
import sys
from functools import lru_cache
sys.setrecursionlimit(100000)
@lru_cache(maxsize=None)
def E(s):                      # s: sorted tuple of positive pile sizes
    if len(s) == 1: return float(s[0])
    m = len(s); tot = 0.0
    for i in range(m):
        if i and s[i] == s[i - 1]: tot += last; continue
        t = list(s); t[i] -= 1
        t = tuple(sorted(x for x in t if x > 0))
        last = E(t); tot += last
    return tot / m
def comps(N, K, lo=1):         # partitions of N into exactly K positive parts (sorted)
    if K == 1:
        if N >= lo: yield (N,)
        return
    for a in range(lo, N // K + 1):
        for r in comps(N - a, K - 1, a): yield (a,) + r
K, Nmax = int(sys.argv[1]), int(sys.argv[2])
bad = 0
for N in range(K, Nmax + 1):
    vals = sorted((E(c), c) for c in comps(N, K))
    q, r = divmod(N, K); bal = tuple(sorted([q] * (K - r) + [q + 1] * r))
    eb = E(bal); best = vals[0]
    if best[0] < eb - 1e-12:
        bad += 1; print('COUNTER?', N, best, 'balanced', eb)
    if N % 10 == 0: print(N, 'balanced E=%.6f' % eb, 'runner-up', vals[1][1] if len(vals) > 1 else '-', flush=True)
print('K', K, 'N<=', Nmax, 'violations', bad)
