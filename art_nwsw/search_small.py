"""Search: how many of M congruent slices (angle 2pi/M, radius 1) fit on a plate of radius 1-eps?
Penalty minimisation from random starts (overlap area + containment excess), then exact re-check."""
import numpy as np, sys, json, time
from scipy.optimize import minimize
from pizza import sector_poly, far_dist, check

def penalty(x, k, ph, r, n=20):
    S = x.reshape(k, 3)
    pen = 0.0
    polys = []
    for (ax, ay, th) in S:
        e = far_dist((ax, ay), th, ph) - r + 2e-4
        if e > 0: pen += 50 * e * e + e * 0.2
        polys.append(sector_poly((ax, ay), th, ph, n))
    for i in range(k):
        for j in range(i + 1, k):
            if polys[i].distance(polys[j]) <= 0:
                pen += polys[i].intersection(polys[j]).area
    return pen

def try_k(M, k, eps, trials, rng):
    ph = np.pi / M
    r = 1 - eps
    for t in range(trials):
        # random apexes, directions roughly inward
        x = []
        for _ in range(k):
            a = rng.uniform(0, r) ; g = rng.uniform(0, 2*np.pi)
            th = g + np.pi + rng.normal(0, 0.8)
            x += [a*np.cos(g), a*np.sin(g), th]
        x = np.array(x)
        for it in range(4):
            res = minimize(penalty, x, args=(k, ph, r), method='Powell',
                           options={'maxiter': 4000, 'xtol': 1e-7, 'ftol': 1e-12})
            x = res.x
            if res.fun < 1e-12: break
        if res.fun < 1e-12:
            S = [(s[0], s[1], s[2], ph) for s in x.reshape(k, 3)]
            ok, o, v = check(S, r, tol=1e-9)
            if ok:
                return S
    return None

if __name__ == "__main__":
    M = int(sys.argv[1]); eps = float(sys.argv[2]); trials = int(sys.argv[3])
    rng = np.random.default_rng(M)
    best = None
    k = 1
    while k <= M:
        t0 = time.time()
        S = try_k(M, k, eps, trials, rng)
        print(f"M={M} k={k} {'FOUND' if S else 'no'} ({time.time()-t0:.0f}s)", flush=True)
        if S is None: break
        best = S; k += 1
    json.dump({'M': M, 'eps': eps, 'k': len(best) if best else 0, 'slices': best}, open(f'small_M{M}.json', 'w'))
