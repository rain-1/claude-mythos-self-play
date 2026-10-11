"""N -> infinity: the plate is covered by 'fans' (sectors of radius 1 and any half-width).
Search K fans in the closed unit disc (eps -> 0) maximising total area without overlap."""
import numpy as np, sys, time
from scipy.optimize import minimize
from pizza import sector_poly, far_dist

def unpack(x, K):
    S = x.reshape(K, 4)
    return [(a, b, th, 0.5 * np.pi / (1 + np.exp(-w))) for a, b, th, w in S]   # ph in (0, pi/2)

def objective(x, K, r, lam):
    F = unpack(x, K)
    area = sum(ph for *_, ph in F)          # sector area = ph * 1^2
    pen = 0.0
    polys = []
    for (a, b, th, ph) in F:
        e = far_dist((a, b), th, ph) - r
        if e > 0: pen += e * 4 + 400 * e * e
        polys.append(sector_poly((a, b), th, ph, 40))
    for i in range(K):
        for j in range(i + 1, K):
            pi, pj = polys[i], polys[j]
            if pi.intersects(pj):
                pen += pi.intersection(pj).area
    return -area + lam * pen

if __name__ == "__main__":
    K = int(sys.argv[1]); trials = int(sys.argv[2]); seed = int(sys.argv[3])
    rng = np.random.default_rng(seed)
    r = 1 - 1e-4
    best = (0, None)
    for t in range(trials):
        x = []
        for _ in range(K):
            a = rng.uniform(0, 1); g = rng.uniform(0, 2 * np.pi)
            x += [a * np.cos(g), a * np.sin(g), g + np.pi + rng.normal(0, .5), rng.normal(-1, 1)]
        x = np.array(x)
        for lam in [3, 10, 30, 100, 300]:
            res = minimize(objective, x, args=(K, r, lam), method='Powell',
                           options={'maxiter': 20000, 'xtol': 1e-6, 'ftol': 1e-10})
            x = res.x
        F = unpack(x, K)
        pen = objective(x, K, r, 1.0) + sum(f[3] for f in F)
        area = sum(f[3] for f in F) / np.pi
        print(f"trial {t}: frac={area:.4f} pen={pen:.2e}", flush=True)
        if pen < 1e-9 and area > best[0]:
            best = (area, F)
            print("  BEST", [tuple(np.round(f, 4)) for f in F], flush=True)
    print("FINAL", best)
