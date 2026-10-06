"""Where is the q-inequality tightest?  min over i of D_i / L_i on the support of R, and its position."""
import sys
from qbinom_check import check
B = int(sys.argv[1]) if len(sys.argv) > 1 else 6
rows = []
for b in range(2, B + 1):
    for c in range(1, b):
        d = b - c
        if c > d: continue
        for k in range(2, B + 1):
            for j in range(1, k):
                if k % j == 0: continue
                _, L, R = check(c, d, j, k)
                sup = [i for i in range(len(R)) if R[i] > 0]
                n = len(L) - 1
                while L[n] == 0: n -= 1
                r = [(float(L[i] - R[i]) / float(L[i]), i) for i in sup]
                mn, at = min(r)
                rows.append(((c, d, j, k), mn, at / n, float(sum(R)) / float(sum(L))))
rows.sort(key=lambda t: t[1])
for x in rows[:12]: print(x)
print('position of tightest coefficient (fraction of degree): min %.3f max %.3f' % (min(r[2] for r in rows), max(r[2] for r in rows)))
