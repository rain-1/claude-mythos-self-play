"""f_k(r) = det[ C(i,j)^r ]_{i=1..k, j=0..k-1}  (rows 1..k, columns 0..k-1 of the Hadamard-power
Pascal matrix, MO 515594) on a (k, r) grid, in certified ball arithmetic (python-flint arb).
Saves sign (+1/-1/0 = uncertified), log10|f|, and certified zero brackets."""
import numpy as np, math, sys
from flint import arb_mat, arb, ctx
ctx.prec = int(sys.argv[4]) if len(sys.argv) > 4 else 900
K = int(sys.argv[1]); NR = int(sys.argv[2]); RMAX = float(sys.argv[3])
rs = (np.arange(NR) + 0.5) / NR * RMAX
C = {(i, j): arb(math.comb(i, j)) for i in range(K + 2) for j in range(K + 2)}
sign = np.zeros((K + 1, NR), np.int8); lg = np.zeros((K + 1, NR), np.float32)
for k in range(2, K + 1):
    for t, r in enumerate(rs):
        ra = arb(float(r))
        M = arb_mat(k, k, [(C[i, j] ** ra if j <= i else arb(0)) for i in range(1, k + 1) for j in range(k)])
        d = M.det()
        if d > 0: sign[k, t] = 1
        elif d < 0: sign[k, t] = -1
        m = abs(d).mid()
        lg[k, t] = float(m.log() / math.log(10)) if m > 0 else -999
    s = sign[k]
    ch = np.nonzero(s[:-1] * s[1:] < 0)[0]
    np.savez("pascal_field.npz", sign=sign, lg=lg, rs=rs)
    print(k, "zeros", len(ch), 'last', rs[ch[-1]] if len(ch) else None, 'uncert', int((s == 0).sum()), flush=True)
np.savez('pascal_field.npz', sign=sign, lg=lg, rs=rs)
