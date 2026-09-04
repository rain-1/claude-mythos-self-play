"""pairsearch2.py — same search, but the covering f(T) u g(T) = T is EXACT by construction.

A = f(T) = [0, a]  (lift values of F in [0,a], both ends attained by construction),
B = g(T) = [b, 1+c] with 0 <= b <= a and 0 <= c  (so A u B = T exactly).
Parameters: a in (0.5,1), overlap fractions, breakpoints and free interior values for F, G.
Objective: D_n = max diam over words of length n.  If inf D_n -> 0 with exact covering, the
circle is a topological fractal with two maps (open per MO 488999); if the optimiser can only
approach 0 by opening a gap, that is evidence for an obstruction.
"""
import numpy as np, sys, json, time
from scipy.optimize import minimize
from pairsearch import image_of_arc_np, depth_max

def sigm(x):
    return 1 / (1 + np.exp(-x))

def build(p, m):
    """p: [a_raw, b_raw, c_raw, F-gaps(m+1), F-vals(m-1), G-gaps(m+1), G-vals(m-1)]
    F has m interior breakpoints; two of its interior values are pinned to 0 and a (min and max);
    the rest free in [0,a].  Same for G in [b, 1+c]."""
    a = 0.5 + 0.49 * sigm(p[0])
    b = a * sigm(p[1])                 # 0 <= b <= a
    c = 0.3 * sigm(p[2])               # 0 <= c
    i = 3
    def mk(lo, hi, q):
        gaps = np.exp(q[:m + 1]); gaps /= gaps.sum()
        xs = np.concatenate([[0.0], np.cumsum(gaps)]); xs[-1] = 1.0
        vals = lo + (hi - lo) * sigm(q[m + 1:2 * m])      # m-1 free interior values
        # interior breakpoints 1..m : first pinned to hi, second to lo, rest free; value at 0 (=1) free too
        ys = np.empty(m + 2)
        ys[1] = hi; ys[2] = lo
        ys[3:m + 1] = vals[1:]
        ys[0] = vals[0]; ys[-1] = ys[0]
        return xs, ys
    F = mk(0.0, a, p[i:i + 2 * m]); i += 2 * m
    G = mk(b, 1 + c, p[i:i + 2 * m])
    return F, G, (a, b, c)

def objective(p, m, n):
    F, G, _ = build(p, m)
    worst, _ = depth_max(F, G, n)
    return worst[-1]

if __name__ == '__main__':
    m = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 9
    trials = int(sys.argv[3]) if len(sys.argv) > 3 else 60
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    rng = np.random.default_rng(seed)
    npar = 3 + 4 * m
    best = (np.inf, None)
    t0 = time.time()
    for tr in range(trials):
        p0 = rng.normal(0, 1.0, npar)
        res = minimize(objective, p0, args=(m, n), method='Nelder-Mead',
                       options=dict(maxiter=6000, xatol=1e-7, fatol=1e-8, adaptive=True))
        # polish
        res = minimize(objective, res.x, args=(m, n), method='Nelder-Mead',
                       options=dict(maxiter=3000, xatol=1e-8, fatol=1e-9, adaptive=True))
        F, G, abc = build(res.x, m)
        worst, _ = depth_max(F, G, 18)
        print(f'trial {tr}: D_{n} = {res.fun:.5f}  (a,b,c)=({abc[0]:.3f},{abc[1]:.3f},{abc[2]:.3f})  D by depth: ' +
              ' '.join(f'{w:.4f}' for w in worst) + f'   ({time.time()-t0:.0f}s)')
        sys.stdout.flush()
        if res.fun < best[0]:
            best = (res.fun, res.x)
            json.dump(dict(m=m, n=n, obj=float(res.fun), params=[float(x) for x in res.x], abc=[float(x) for x in abc],
                           F=[list(map(float, F[0])), list(map(float, F[1]))], G=[list(map(float, G[0])), list(map(float, G[1]))],
                           worst18=[float(w) for w in worst]), open(f'pair2_best_m{m}_s{seed}.json', 'w'))
    print('done', best[0])
