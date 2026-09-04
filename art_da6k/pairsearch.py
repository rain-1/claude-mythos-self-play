"""pairsearch.py — is there ONE pair of circle maps whose long compositions all shrink?

Search over piecewise-linear degree-0 maps f, g: T -> T (lifts F, G on [0,1] with F(0)=F(1)),
with f(T) u g(T) = T, minimising  D_n = max over words of length n of diam(w(T)).
Also enforces the necessary condition found from the fold construction: no word may have a
fixed point with |slope| > 1 (else an arc maps onto a superset of itself) — checked a posteriori
by watching D_n decay across n.
"""
import numpy as np, sys, json, time
from scipy.optimize import minimize

def make_map(params, m):
    """params -> (xs, ys): m interior breakpoints; xs from softmax gaps, ys free; ys[-1]=ys[0]"""
    gaps = np.exp(params[:m + 1]); gaps /= gaps.sum()
    xs = np.concatenate([[0.0], np.cumsum(gaps)]); xs[-1] = 1.0
    ys = np.concatenate([params[m + 1:2 * m + 2], [params[m + 1]]])
    return xs, ys

def image_of_arc_np(xs, ys, lo, hi):
    if hi - lo >= 1 - 1e-12:
        return ys.min(), ys.max()
    a = lo % 1.0; b = a + (hi - lo)
    pts = [a, b if b <= 1 else b - 1]
    inner = xs[1:-1]
    sel = inner[((inner >= a) & (inner <= b)) | ((inner + 1 >= a) & (inner + 1 <= b))]
    vals = [np.interp(p, xs, ys) for p in pts] + list(np.interp(sel, xs, ys))
    if b > 1:
        vals.append(ys[0])
    return min(vals), max(vals)

def depth_max(F, G, n):
    """max diam over all words of length n (arcs as lifts).  F=(xs,ys), G=(xs,ys)."""
    arcs = [(0.0, 1.0)]
    worst = []
    for k in range(n):
        new = []
        for (lo, hi) in arcs:
            new.append(image_of_arc_np(*F, lo, hi))
            new.append(image_of_arc_np(*G, lo, hi))
        # prune: identical arcs
        arcs = list({(round(a, 12), round(b, 12)) for a, b in new})
        worst.append(max(b - a for a, b in arcs))
    return worst, arcs

def covers(F, G):
    a0, a1 = F[1].min(), F[1].max(); b0, b1 = G[1].min(), G[1].max()
    # arcs [a0,a1], [b0,b1] on the circle; union = T iff lengths cover with overlaps both ends
    la, lb = a1 - a0, b1 - b0
    if la >= 1 or lb >= 1:
        return 1.0, 0.0
    # uncovered measure by sampling
    x = np.linspace(0, 1, 2001, endpoint=False)
    inA = ((x - a0) % 1.0) <= la
    inB = ((x - b0) % 1.0) <= lb
    unc = 1 - (inA | inB).mean()
    return unc, min(la, lb)

def objective(p, m, n):
    F = make_map(p[:2 * m + 2], m); G = make_map(p[2 * m + 2:], m)
    unc, _ = covers(F, G)
    worst, _ = depth_max(F, G, n)
    return worst[-1] + 5 * unc + 0.02 * max(0, (F[1].max() - F[1].min()) - 1)

if __name__ == '__main__':
    m = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 9
    trials = int(sys.argv[3]) if len(sys.argv) > 3 else 60
    rng = np.random.default_rng(int(sys.argv[4]) if len(sys.argv) > 4 else 0)
    best = (np.inf, None)
    t0 = time.time()
    for tr in range(trials):
        p0 = np.concatenate([rng.normal(0, 0.7, m + 1), rng.uniform(0, 0.6, m + 1),
                             rng.normal(0, 0.7, m + 1), rng.uniform(0.4, 1.0, m + 1)])
        res = minimize(objective, p0, args=(m, n), method='Nelder-Mead',
                       options=dict(maxiter=4000, xatol=1e-6, fatol=1e-7, adaptive=True))
        if res.fun < best[0]:
            best = (res.fun, res.x)
            F = make_map(res.x[:2 * m + 2], m); G = make_map(res.x[2 * m + 2:], m)
            worst, _ = depth_max(F, G, 16)
            print(f'trial {tr}: obj {res.fun:.5f}  D_n by depth: ' + ' '.join(f'{w:.4f}' for w in worst) + f'   ({time.time()-t0:.0f}s)')
            sys.stdout.flush()
            json.dump(dict(m=m, n=n, obj=float(res.fun), params=[float(x) for x in res.x],
                           F=[list(map(float, F[0])), list(map(float, F[1]))], G=[list(map(float, G[0])), list(map(float, G[1]))],
                           worst16=[float(w) for w in worst]), open(f'pair_best_m{m}.json', 'w'))
    print('done', best[0])
