"""Faster search for M congruent slices (angle 2pi/M) on a plate of radius 1-eps.
Smooth penalty: squared penetration depth of sampled boundary points of each slice into every
other slice + squared containment excess; L-BFGS from many random starts; strict re-check."""
import numpy as np, sys, json, time
from scipy.optimize import minimize
from pizza import strict_check, check, far_dist

def bpoints(X, ph, n):
    """boundary samples of k sectors: (k, 3n) x and y arrays."""
    ax, ay, th = X[:, 0:1], X[:, 1:2], X[:, 2:3]
    t = np.linspace(0, 1, n)[None, :]
    a = th + np.linspace(-ph, ph, n)[None, :]
    xs = np.concatenate([ax + np.cos(th - ph) * t, ax + np.cos(th + ph) * t, ax + np.cos(a)], 1)
    ys = np.concatenate([ay + np.sin(th - ph) * t, ay + np.sin(th + ph) * t, ay + np.sin(a)], 1)
    return xs, ys

def penalty(x, k, ph, r, n=24):
    X = x.reshape(k, 3)
    xs, ys = bpoints(X, ph, n)
    ax_, ay_, th_ = X[:, 0:1], X[:, 1:2], X[:, 2:3]
    cx = ax_ + 0.6 * np.cos(th_ + np.array([[-0.5, 0, 0.5]]) * ph); cy = ay_ + 0.6 * np.sin(th_ + np.array([[-0.5, 0, 0.5]]) * ph)
    xs = np.concatenate([xs, cx], 1); ys = np.concatenate([ys, cy], 1)
    # containment: all boundary points within r (arc max is sampled; fine for the penalty)
    rad = np.hypot(xs, ys) - r
    pen = np.sum(np.maximum(rad, 0) ** 2) * 10
    # penetration of points of i into sector j
    ax, ay, th = X[:, 0], X[:, 1], X[:, 2]
    u = xs[:, None, :] - ax[None, :, None]; v = ys[:, None, :] - ay[None, :, None]
    c, s = np.cos(th)[None, :, None], np.sin(th)[None, :, None]
    lx = u * c + v * s; ly = -u * s + v * c
    dep = np.minimum(np.minimum(1 - np.hypot(lx, ly), lx * np.sin(ph) - ly * np.cos(ph)),
                     lx * np.sin(ph) + ly * np.cos(ph))
    dep[np.arange(k), np.arange(k), :] = 0
    pen += np.sum(np.maximum(dep, 0) ** 2)
    return pen

def attempt(M, k, eps, rng, margin=2e-4):
    ph = np.pi / M; r = 1 - eps
    a = rng.uniform(0, 0.9, k) ** 0.7; g = rng.uniform(0, 2 * np.pi, k)
    x = np.stack([a * np.cos(g), a * np.sin(g), g + np.pi + rng.normal(0, 0.9, k)], 1).ravel()
    for n in (12, 24, 48):
        res = minimize(penalty, x, args=(k, ph, r - margin, n), method='L-BFGS-B',
                       options={'maxiter': 3000, 'ftol': 1e-16, 'gtol': 1e-12})
        x = res.x
    if res.fun > 1e-14: return None
    S = [(q[0], q[1], q[2], ph) for q in x.reshape(k, 3)]
    out, dep = strict_check(S, r, 3000)
    if out <= 0 and dep <= 1e-7 and check(S, r)[0]:
        return S
    return None

if __name__ == "__main__":
    M = int(sys.argv[1]); eps = float(sys.argv[2]); budget = float(sys.argv[3])
    rng = np.random.default_rng(M * 7 + 1)
    res = {}
    k = max(1, int(M * 0.45))
    while k <= M:
        t0 = time.time(); found = None; tries = 0
        while time.time() - t0 < budget:
            tries += 1
            found = attempt(M, k, eps, rng)
            if found: break
        print(f"M={M} k={k} {'FOUND' if found else 'no'} tries={tries} {time.time()-t0:.0f}s", flush=True)
        if not found: break
        res[k] = found
        json.dump({'M': M, 'eps': eps, 'best': max(res), 'slices': res[max(res)]}, open(f's2_M{M}.json', 'w'))
        k += 1
