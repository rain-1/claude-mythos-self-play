"""Hessenberg minors of [C(i,j)^r] via the Toeplitz trick (MO 515594).
C(i,j)^r = (i!)^r (j!)^-r a_{i-j},  a_m = 1/(m!)^r  =>  rows 1..k, cols 0..k-1 minor
f_k(r) = [prod_{i=1..k} i!^r / prod_{j<k} j!^r] * D_k(r),   D_k = (-1)^k b_k,  sum b_k z^k = 1/E_r(z),
E_r(z) = sum z^m/(m!)^r.  Recursion b_k = -sum_{m=1..k} a_m b_{k-m}.  Ball arithmetic certifies signs.
usage: pascal_fast.py K NR out.npz"""
import sys, math, numpy as np
from flint import arb, ctx
K, NR, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
ctx.prec = int(sys.argv[4]) if len(sys.argv) > 4 else 400
# r grid: dense near 1 from below, plus (1, 1.2]
u = np.linspace(0.0, 1.0, NR)[1:]
r_lo = 1 - np.exp(-u * float(sys.argv[5] if len(sys.argv) > 5 else 11.0))   # (0,1)
rs = np.concatenate([r_lo, np.linspace(1.0, 1.25, NR // 8)[1:]])
lf = [arb(math.lgamma(m + 1)) for m in range(K + 1)]
lfac = [arb(math.factorial(m)).log() for m in range(K + 1)]
sign = np.zeros((K + 1, len(rs)), np.int8); lgD = np.zeros((K + 1, len(rs)), np.float32)
for t, r in enumerate(rs):
    ra = arb(float(r))
    a = [(-ra * lfac[m]).exp() for m in range(K + 1)]
    b = [arb(1)]
    for k in range(1, K + 1):
        s = arb(0)
        for m in range(1, k + 1):
            s += a[m] * b[k - m]
        b.append(-s)
    for k in range(K + 1):
        D = b[k] if k % 2 == 0 else -b[k]
        sign[k, t] = 1 if D > 0 else (-1 if D < 0 else 0)
        m = abs(D).mid()
        lgD[k, t] = float(m.log()) if m > 0 else -1e4
np.savez(out, sign=sign, lgD=lgD, rs=rs)
for k in range(2, K + 1):
    s = sign[k][rs < 1]
    print(k, 'zeros in (0,1):', int(np.sum(s[1:] * s[:-1] < 0)), ' r>=1 all positive:', bool(np.all(sign[k][rs >= 1] > 0)), ' uncertified:', int(np.sum(sign[k] == 0)))
