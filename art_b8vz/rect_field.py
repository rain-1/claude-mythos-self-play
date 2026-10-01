"""Rectangular minors  M_{s,k}(r) = det[C(i,j)^r]_{i = s..s+k−1, j = 0..k−1}  (MO 515594).
By the Toeplitz rescaling and dual Jacobi–Trudi, M_{s,k} ∝ s_{(s^k)} = det[D_{k−i+j}]_{i,j=1..s},
D_k = [z^k] 1/E_r(−z).  Certified signs for s = 1..SMAX, k = 1..K on an r grid.
usage: rect_field.py SMAX K NR RMAX out.npz [prec]"""
import sys, math, numpy as np
from flint import arb, arb_mat, ctx
SMAX, K, NR, RMAX, out = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
ctx.prec = int(sys.argv[6]) if len(sys.argv) > 6 else 500
lfac = [arb(math.factorial(m)).log() for m in range(K + SMAX + 3)]
rs = (np.arange(NR) + 0.5) / NR * RMAX
sg = np.zeros((SMAX + 1, K + 1, NR), np.int8)
for t, r in enumerate(rs):
    ra = arb(float(r)); a = [(-ra * lfac[m]).exp() for m in range(K + SMAX + 2)]
    b = [arb(1)]
    for k in range(1, K + SMAX + 1):
        s = arb(0)
        for m in range(1, k + 1): s += a[m] * b[k - m]
        b.append(-s)
    D = [b[k] if k % 2 == 0 else -b[k] for k in range(K + SMAX + 1)]
    Dx = lambda m: D[m] if m >= 0 else arb(0)
    for s in range(1, SMAX + 1):
        for k in range(1, K + 1):
            M = arb_mat(s, s, [Dx(k - i + j) for i in range(s) for j in range(s)])
            d = M.det()
            sg[s, k, t] = 1 if d > 0 else (-1 if d < 0 else 0)
    if t % 200 == 0: print('r', r, flush=True)
np.savez(out, sign=sg, rs=rs)
fail = (sg[1:] < 0).any(axis=(0, 1))
print('uncertified', int((sg[1:, 1:] == 0).sum()))
# r-intervals where some minor fails
edges = np.nonzero(np.diff(fail.astype(int)))[0]
print('fail fraction', fail.mean(), ' positive-everywhere r values:', np.round(rs[~fail], 3)[:60])
