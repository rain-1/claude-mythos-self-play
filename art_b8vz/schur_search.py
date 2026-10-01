"""search for a negative Jacobi–Trudi minor s_λ = det[h_{λ_i − i + j}] with h_m = 1/(m!)^r (MO 515594).
Every such determinant is a minor of the Toeplitz matrix [h_{i−j}], hence (after the positive diagonal
rescaling) a minor of [C(i,j)^r] lying on or below the diagonal."""
import sys, math
from flint import arb, arb_mat, ctx
ctx.prec = 300
r = float(sys.argv[1]); NMAX = int(sys.argv[2])
lf = [arb(math.factorial(m)).log() for m in range(NMAX + 2)]
h = [(-arb(r) * lf[m]).exp() for m in range(NMAX + 2)]
def H(m): return h[m] if m >= 0 else arb(0)
def parts(n, mx=None):
    if mx is None: mx = n
    if n == 0: yield (); return
    for k in range(min(n, mx), 0, -1):
        for p in parts(n - k, k): yield (k,) + p
worst = None; found = 0
for n in range(2, NMAX + 1):
    for lam in parts(n):
        L = len(lam)
        if L < 2: continue
        M = arb_mat(L, L, [H(lam[i] - i + j) for i in range(L) for j in range(L)])
        d = M.det()
        # normalise by the product of diagonal entries
        nd = d
        for i in range(L): nd = nd / H(lam[i])
        if nd < 0:
            found += 1
            if worst is None or float(nd.mid()) < worst[0]:
                worst = (float(nd.mid()), lam)
    print('n', n, 'negatives so far', found, 'worst', worst, flush=True)
    if found and n > 6 and '--first' in sys.argv: break
