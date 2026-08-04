"""MO 513838: products of two k-cycles with overlapping support.
Brute force verifier: q_{k,m}(nu) = Pr[sigma*tau in C_nu],
sigma uniform cyclic on S1, tau uniform cyclic on S2, |S1|=|S2|=k, |S1 cap S2|=m, N=2k-m.
"""
import itertools, sys
from fractions import Fraction
from collections import Counter

def cycle_type(perm, N):
    seen = [False]*N
    t = []
    for i in range(N):
        if not seen[i]:
            l = 0; j = i
            while not seen[j]:
                seen[j] = True; j = perm[j]; l += 1
            t.append(l)
    return tuple(sorted(t, reverse=True))

def all_cycles(support, N):
    """All cyclic permutations on support (as full perms on [N] fixing rest)."""
    s0 = support[0]; rest = support[1:]
    out = []
    for p in itertools.permutations(rest):
        perm = list(range(N))
        cyc = (s0,) + p
        for a, b in zip(cyc, cyc[1:] + (s0,)):
            perm[a] = b
        out.append(perm)
    return out

def qtable(k, m):
    N = 2*k - m
    S1 = list(range(k))                    # 0..k-1
    S2 = list(range(k-m, N))               # overlap A = k-m..k-1
    C1 = all_cycles(S1, N); C2 = all_cycles(S2, N)
    cnt = Counter()
    for s in C1:
        for t in C2:
            # pi = s o t  (apply t first)
            pi = [s[t[i]] for i in range(N)]
            cnt[cycle_type(pi, N)] += 1
    tot = len(C1)*len(C2)
    return {nu: Fraction(c, tot) for nu, c in sorted(cnt.items())}

if __name__ == '__main__':
    k = int(sys.argv[1]); m = int(sys.argv[2])
    for nu, q in qtable(k, m).items():
        print(k, m, nu, q)
