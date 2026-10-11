"""Seeded search: start from the best known packing (structured fans or earlier search) and try to
squeeze in one more slice: keep the known slices (slightly jittered), add a random one, L-BFGS."""
import numpy as np, sys, json, time, glob, os
from scipy.optimize import minimize
from search2 import penalty
from pizza import strict_check, check, five_sixths

def polish(x, k, ph, r, margin=2e-4):
    for n in (12, 24, 48):
        res = minimize(penalty, x, args=(k, ph, r - margin, n), method='L-BFGS-B',
                       options={'maxiter': 3000, 'ftol': 1e-16, 'gtol': 1e-12})
        x = res.x
    return x, res.fun

def verify(x, k, ph, r):
    S = [(q[0], q[1], q[2], ph) for q in x.reshape(k, 3)]
    out, dep = strict_check(S, r, 3000)
    return S if (out <= 0 and dep <= 1e-7 and check(S, r)[0]) else None

if __name__ == "__main__":
    M = int(sys.argv[1]); eps = float(sys.argv[2]); budget = float(sys.argv[3])
    ph = np.pi / M; r = 1 - eps
    rng = np.random.default_rng(M * 13 + 5)
    cands = [five_sixths(None, eps, grid=16, ph=ph)]
    for f in (f"s2_M{M}.json", f"s3_M{M}.json"):
        if os.path.exists(f): cands.append([tuple(s) for s in json.load(open(f))['slices']])
    best = max(cands, key=len)
    print(f"M={M} start k={len(best)}", flush=True)
    json.dump({'M': M, 'eps': eps, 'best': len(best), 'slices': best}, open(f's3_M{M}.json', 'w'))
    while True:
        k = len(best) + 1; t0 = time.time(); found = None; tries = 0
        while time.time() - t0 < budget and not found:
            tries += 1
            base = np.array([[s[0], s[1], s[2]] for s in best])
            base = base + rng.normal(0, [0.02, 0.02, 0.03], base.shape) * rng.uniform(0, 1)
            # drop 0-2 random slices and re-add that many + 1 random ones
            drop = rng.integers(0, 3)
            keep = rng.permutation(len(base))[:len(base) - drop]
            base = base[keep]
            add = k - len(base)
            a = rng.uniform(0, 0.9, add) ** 0.7; g = rng.uniform(0, 2 * np.pi, add)
            new = np.stack([a * np.cos(g), a * np.sin(g), g + np.pi + rng.normal(0, 0.9, add)], 1)
            x = np.concatenate([base, new]).ravel()
            x, f = polish(x, k, ph, r)
            if f < 1e-14:
                found = verify(x, k, ph, r)
        print(f"M={M} k={k} {'FOUND' if found else 'no'} tries={tries} {time.time()-t0:.0f}s", flush=True)
        if not found: break
        best = found
        json.dump({'M': M, 'eps': eps, 'best': len(best), 'slices': best}, open(f's3_M{M}.json', 'w'))
