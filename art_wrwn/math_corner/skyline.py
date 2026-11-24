"""skyline.py — rows of n unit squares side by side with heights h_i ('skylines'); exact-ish optimisation."""
import sys, numpy as np
from scipy.optimize import minimize
from corner import width, width_fast, profiles
def row(h):
    n = len(h); return np.c_[np.arange(n) - (n - 1) / 2, h, np.zeros(n)]
def w_of(h, N=14400): return width_fast(row(np.asarray(h, float)), N)
if __name__ == '__main__':
    for n in range(2, 9):
        best = None
        for trial in range(16):
            r = np.random.default_rng(trial)
            h0 = r.uniform(0, 1, n) if trial else np.minimum(np.arange(n), np.arange(n)[::-1]) * 0.4
            res = minimize(lambda h: w_of(h, 1440), h0, method='Nelder-Mead', options=dict(xatol=1e-9, fatol=1e-11, maxiter=4000 * n, adaptive=True))
            if best is None or res.fun < best.fun: best = res
        res = best
        for N in (5760, 46080):
            res = minimize(lambda h: w_of(h, N), res.x, method='Nelder-Mead', options=dict(xatol=1e-11, fatol=1e-13, maxiter=3000 * n, adaptive=True))
        h = res.x - res.x.min()
        print(n, 'w=%.9f area=%.9f' % (res.fun, n / res.fun ** 2), 'h=', np.round(h, 6), flush=True)
