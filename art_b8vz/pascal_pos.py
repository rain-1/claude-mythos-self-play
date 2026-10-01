"""check D_k(r) > 0 (certified) for k <= K on a grid of r in [1, RMAX]"""
import sys, math, numpy as np
from flint import arb, ctx
K = int(sys.argv[1]); ctx.prec = 400
lfac = [arb(math.factorial(m)).log() for m in range(K + 1)]
bad = 0; n = 0
for r in np.concatenate([np.linspace(1, 1.01, 200), np.linspace(1.01, 6, 800)]):
    ra = arb(float(r)); a = [(-ra * lfac[m]).exp() for m in range(K + 1)]
    b = [arb(1)]
    for k in range(1, K + 1):
        s = arb(0)
        for m in range(1, k + 1): s += a[m] * b[k - m]
        b.append(-s)
    for k in range(1, K + 1):
        D = b[k] if k % 2 == 0 else -b[k]
        n += 1
        if not (D > 0): bad += 1; print('not certified positive', k, r)
print('checked', n, 'bad', bad)
