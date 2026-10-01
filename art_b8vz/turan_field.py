"""τ_k(r) = D_k² − D_{k−1}D_{k+1}  ( = the minor rows 2..k+1 × cols 0..k−1 of [C(i,j)^r], up to a positive
factor; Jacobi–Trudi λ = (2^k) via the dual 2×2 form).  D_k = [z^k] 1/E_r(−z).  Certified signs.
usage: turan_field.py K NR RMAX out.npz"""
import sys, math, numpy as np
from flint import arb, ctx
K, NR, RMAX, out = int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
ctx.prec = int(sys.argv[5]) if len(sys.argv) > 5 else 600
lfac = [arb(math.factorial(m)).log() for m in range(K + 3)]
rs = (np.arange(NR) + 0.5) / NR * RMAX
sg = np.zeros((K + 1, NR), np.int8); val = np.zeros((K + 1, NR), np.float32)
for t, r in enumerate(rs):
    ra = arb(float(r)); a = [(-ra * lfac[m]).exp() for m in range(K + 3)]
    b = [arb(1)]
    for k in range(1, K + 2):
        s = arb(0)
        for m in range(1, k + 1): s += a[m] * b[k - m]
        b.append(-s)
    D = [b[k] if k % 2 == 0 else -b[k] for k in range(K + 2)]
    for k in range(1, K + 1):
        tau = D[k] * D[k] - D[k - 1] * D[k + 1]
        sg[k, t] = 1 if tau > 0 else (-1 if tau < 0 else 0)
        rel = tau / (D[k] * D[k]) if (D[k] != 0) else arb(0)
        try:
            val[k, t] = float(rel.mid())
        except Exception:
            val[k, t] = 0
np.savez(out, sign=sg, val=val, rs=rs)
for k in range(2, K + 1, 4):
    s = sg[k]; neg = rs[s < 0]
    print(k, 'neg fraction', round(float((s < 0).mean()), 3), 'uncert', int((s == 0).sum()),
          'neg r>1:', np.round(neg[neg > 1][:3], 3), '...')
