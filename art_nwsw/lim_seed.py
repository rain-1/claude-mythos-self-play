"""Seed the thin-slice fan optimiser with the verified M=6 packing (four 60-degree fans whose apexes
sit near the centre with different offsets) plus a few small random fans; grow, then strictly re-check."""
import numpy as np, json, sys
from scipy.optimize import minimize
from limit2 import obj
from pizza import strict_check, check

eps = 1e-4; r = 1 - eps
d = json.load(open('s2_M6.json')); S0 = [tuple(s) for s in d['slices']]
rng = np.random.default_rng(int(sys.argv[1]))
best = 0
for trial in range(int(sys.argv[2])):
    X = [[s[0], s[1], s[2], s[3]] for s in S0]
    for _ in range(int(sys.argv[3])):
        a = rng.uniform(0.3, 0.95); g = rng.uniform(0, 2 * np.pi)
        X.append([a * np.cos(g), a * np.sin(g), g + np.pi + rng.normal(0, 0.5), 0.05])
    x = np.array(X).ravel(); K = len(X)
    for lam, n in ((1e3, 16), (1e4, 24), (1e5, 36), (1e6, 48), (1e7, 64)):
        x = minimize(obj, x, args=(K, r, lam, n), method='L-BFGS-B', options={'maxiter': 6000}).x
    X = x.reshape(K, 4); X[:, 3] = np.abs(X[:, 3])
    S = [tuple(q) for q in X]
    out, dep = strict_check(S, r, 2000)
    frac = sum(s[3] for s in S) / np.pi
    print(trial, f"frac={frac:.4f} out={out:.2e} dep={dep:.2e}", flush=True)
    for shrink in (0, 1e-4, 1e-3, 3e-3, 1e-2):
        S2 = [(q[0], q[1], q[2], max(q[3] * (1 - shrink) - shrink, 1e-6)) for q in S]
        o2, d2 = strict_check(S2, r, 2000)
        if o2 <= 0 and d2 <= 1e-9 and check(S2, r)[0]:
            f2 = sum(s[3] for s in S2) / np.pi
            print("   valid", shrink, round(f2, 4), flush=True)
            if f2 > best:
                best = f2
                json.dump({'eps': eps, 'frac': f2, 'fans': S2}, open(f'limseed_{sys.argv[1]}.json', 'w'))
            break
