"""polish.py n [rounds] — restart Nelder-Mead / Powell from best_n.json with small kicks; keeps improvements."""
import sys, json, numpy as np
from scipy.optimize import minimize
from corner import objective, width_fast, overlap
n = int(sys.argv[1]); R = int(sys.argv[2]) if len(sys.argv) > 2 else 12
d = json.load(open(f'best_{n}.json')); x = np.array(d['P']); r = np.random.default_rng(1)
def val(x):
    P = x.reshape(-1, 3); return n / (width_fast(P, 46080) + 2 * overlap(P)) ** 2
best = val(x); print('start', best)
for k in range(R):
    y = x + r.normal(0, 0.01 if k % 2 else 0.002, x.shape) * (k > 0)
    for N, lam in ((2880, 6.0), (11520, 10.0)):
        y = minimize(objective, y, args=(N, lam), method='Nelder-Mead', options=dict(maxiter=6000 * n, maxfev=6000 * n, xatol=1e-10, fatol=1e-12, adaptive=True)).x
        y = minimize(objective, y, args=(N, lam), method='Powell', options=dict(maxiter=4, xtol=1e-10, ftol=1e-13)).x
    v = val(y)
    if v > best and overlap(y.reshape(-1, 3)) < 1e-9:
        best = v; x = y; json.dump(dict(n=n, area=best, P=x.tolist()), open(f'best_{n}.json', 'w')); print(k, 'improved', best, flush=True)
P = x.reshape(-1, 3).copy(); P[:, 2] = np.degrees(P[:, 2]) % 90; print(np.round(P, 4)); print('final', best, 'overlap', overlap(x.reshape(-1, 3)))
