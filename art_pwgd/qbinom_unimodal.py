"""Is D = LHS − RHS (MO 330620, after the q-shifts) palindromic and unimodal?"""
import sys, numpy as np
from qbinom_check import check
B = int(sys.argv[1]) if len(sys.argv) > 1 else 6
tot = 0; pal = 0; uni = 0; bad = []
for b in range(2, B + 1):
    for c in range(1, b):
        d = b - c
        if c > d: continue
        for k in range(2, B + 1):
            for j in range(1, k):
                if k % j == 0: continue
                _, L, R = check(c, d, j, k)
                D = [int(x) for x in (L - R)]
                while D and D[-1] == 0: D.pop()
                lo = 0
                while D[lo] == 0: lo += 1
                D = D[lo:]
                tot += 1
                p = D == D[::-1]; pal += p
                m = len(D) // 2
                u = all(D[i] <= D[i + 1] for i in range(m)) and all(D[i] >= D[i + 1] for i in range(m, len(D) - 1))
                uni += u
                if not u and len(bad) < 8:
                    i0 = next(i for i in range(m) if D[i] > D[i + 1]) if any(D[i] > D[i + 1] for i in range(m)) else None
                    bad.append(((c, d, j, k), i0, D[:12]))
print('cases', tot, 'palindromic', pal, 'unimodal', uni)
for x in bad: print(x)
