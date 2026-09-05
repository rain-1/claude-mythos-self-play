"""isospec.py — MO 514920 'When do two binary strings have the same characteristic polynomial?'

H_b = tridiagonal with b on the diagonal and 1's off it.  chi_b(x) = det(xI - H_b) = continuant
K(x-b_1, ..., x-b_n):   K_n = (x - b_n) K_{n-1} - K_{n-2},  K_0 = 1, K_{-1} = 0.

We build ALL 2^n polynomials at once (coefficient arrays, exact int64 — coefficients are bounded
by the n-th Fibonacci-like growth, < 2^62 for n <= 22), group equal rows, and report
  a_n = number of distinct polynomials,
  the classes that are NOT {b, reverse(b)},
  and a 'strong' equivalence: same chi AND same chi of the string minus its last letter
  (i.e. equal first row of the transfer product) — that one propagates under appending.
"""
import numpy as np, json, sys, time
from collections import defaultdict

NMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 18


def all_polys(n):
    """returns (K_n, K_{n-1}) coefficient arrays of shape (2^n, n+1) for all strings (bit i = b_{i+1});
    string index s has b_i = (s >> (i-1)) & 1."""
    Km1 = np.zeros((1, n + 2), np.int64)          # K_{-1} = 0
    K0 = np.zeros((1, n + 2), np.int64); K0[0, 0] = 1
    prev, cur = Km1, K0
    for i in range(n):
        # new letter b in {0,1}: K_new = (x - b) K_cur - K_prev ; strings doubled: b=0 block then b=1 block
        xK = np.zeros_like(cur); xK[:, 1:] = cur[:, :-1]
        new0 = xK - prev
        new1 = xK - cur - prev
        new = np.concatenate([new0, new1])
        prev = np.concatenate([cur, cur])
        cur = new
    return cur, prev


def bits(s, n):
    return ''.join(str((s >> i) & 1) for i in range(n))


def rev_index(s, n):
    return int(bits(s, n)[::-1], 2) if n else 0  # bits() is LSB-first so reversing the string = reading as int


def analyze(n):
    K, Kp = all_polys(n)
    N = 1 << n
    # group by polynomial
    _, inv, cnt = np.unique(K, axis=0, return_inverse=True, return_counts=True)
    a_n = len(cnt)
    classes = defaultdict(list)
    for s in range(N):
        classes[int(inv[s])].append(s)
    nontriv = []
    for c, mem in classes.items():
        if len(mem) <= 1:
            continue
        # is the class exactly {s, rev s}?
        S = set(mem)
        trivial = all(rev_index(s, n) in S for s in mem) and len(S) <= 2
        if not trivial:
            nontriv.append(sorted(bits(s, n) for s in mem))
    # strong classes: same (K, K')  where K' = chi of string minus last letter
    KK = np.concatenate([K, Kp], axis=1)
    _, inv2, cnt2 = np.unique(KK, axis=0, return_inverse=True, return_counts=True)
    strong = defaultdict(list)
    for s in range(N):
        strong[int(inv2[s])].append(s)
    strong_nontriv = [sorted(bits(s, n) for s in mem) for mem in strong.values() if len(mem) > 1]
    return a_n, nontriv, strong_nontriv, cnt


if __name__ == '__main__':
    out = {}
    for n in range(1, NMAX + 1):
        t = time.time()
        a_n, nontriv, strong, cnt = analyze(n)
        sizes = np.bincount(cnt)
        print(f'n={n:2d} a_n={a_n:8d}  2^n={1<<n:8d}  class-size histogram={ {int(i):int(v) for i,v in enumerate(sizes) if v} }'
              f'  nontrivial classes={len(nontriv)}  strong(prefix-propagating) classes={len(strong)}  {time.time()-t:.1f}s', flush=True)
        for cl in nontriv[:12]:
            print('     ', cl)
        if strong:
            print('   STRONG:', strong[:8])
        out[n] = dict(a_n=int(a_n), nontrivial=nontriv, strong=strong,
                      hist={int(i): int(v) for i, v in enumerate(sizes) if v})
        json.dump(out, open('isospec_census.json', 'w'))
    print('poster:', [2,3,6,10,20,36,72,134,270,526,1052,2072,4154,8231,16504])
    print('ours  :', [out[n]['a_n'] for n in range(1, NMAX + 1)])
