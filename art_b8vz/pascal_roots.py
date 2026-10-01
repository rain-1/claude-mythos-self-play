"""certified zero census of D_k(r) on (0,1) in the variable v = -log(1-r) (resolves zeros near 1)."""
import sys, math, numpy as np
from flint import arb, ctx
K = int(sys.argv[1]); ctx.prec = int(sys.argv[2]); VMAX = float(sys.argv[3]); NV = int(sys.argv[4])
lfac = [arb(math.factorial(m)).log() for m in range(K + 1)]
def Dall(r):
    a = [(-r * lfac[m]).exp() for m in range(K + 1)]
    b = [arb(1)]
    for k in range(1, K + 1):
        s = arb(0)
        for m in range(1, k + 1): s += a[m] * b[k - m]
        b.append(-s)
    return [b[k] if k % 2 == 0 else -b[k] for k in range(K + 1)]
def sg(x): return 1 if x > 0 else (-1 if x < 0 else 0)
vs = np.concatenate([np.linspace(1e-4, 0.05, NV // 4), np.linspace(0.05, VMAX, NV)[1:]])
rows = []
for v in vs:
    r = 1 - (-arb(float(v))).exp()
    rows.append([sg(d) for d in Dall(r)])
S = np.array(rows)            # (nv, K+1)
unc = (S == 0).sum(0)
res = {}
for k in range(3, K + 1):
    s = S[:, k]; idx = np.nonzero(s[1:] * s[:-1] < 0)[0]
    # refine the last zero by bisection in v
    i = idx[-1]; lo, hi = vs[i], vs[i + 1]; slo = s[i]
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        d = Dall(1 - (-arb(mid)).exp())[k]
        if sg(d) == slo: lo = mid
        else: hi = mid
    res[k] = (len(idx), 0.5 * (lo + hi))
    print(k, 'zeros', len(idx), 'k-2 =', k - 2, ' last zero: 1-r = %.6e' % math.exp(-0.5 * (lo + hi)), ' v=%.6f' % (0.5*(lo+hi)), ' unc', unc[k], flush=True)
