"""Thin-slice limit: K fans (apex, centre dir, half-width) on a plate of radius 1-eps.
Maximise total area (= sum of half-widths) with squared-penetration penalties; strict re-check."""
import numpy as np, sys, json, time
from scipy.optimize import minimize
from pizza import strict_check, check

def pts(X, n):
    ax, ay, th, w = X[:, 0:1], X[:, 1:2], X[:, 2:3], X[:, 3:4]
    t = np.linspace(0, 1, n)[None, :]
    s = np.linspace(-1, 1, n)[None, :]
    a = th + s * w
    xs = [ax + np.cos(th - w) * t, ax + np.cos(th + w) * t, ax + np.cos(a)]
    ys = [ay + np.sin(th - w) * t, ay + np.sin(th + w) * t, ay + np.sin(a)]
    for rr in (0.3, 0.6, 0.9):
        xs.append(ax + rr * np.cos(a)); ys.append(ay + rr * np.sin(a))
    return np.concatenate(xs, 1), np.concatenate(ys, 1)

def obj(x, K, r, lam, n):
    X = x.reshape(K, 4).copy()
    X[:, 3] = np.abs(X[:, 3])
    xs, ys = pts(X, n)
    pen = 10 * np.sum(np.maximum(np.hypot(xs, ys) - r, 0) ** 2)
    ax, ay, th, w = X[:, 0], X[:, 1], X[:, 2], X[:, 3]
    u = xs[:, None, :] - ax[None, :, None]; v = ys[:, None, :] - ay[None, :, None]
    c, s = np.cos(th)[None, :, None], np.sin(th)[None, :, None]
    lx = u * c + v * s; ly = -u * s + v * c
    sw, cw = np.sin(w)[None, :, None], np.cos(w)[None, :, None]
    dep = np.minimum(np.minimum(1 - np.hypot(lx, ly), lx * sw - ly * cw), lx * sw + ly * cw)
    dep[np.arange(K), np.arange(K), :] = 0
    pen += np.sum(np.maximum(dep, 0) ** 2)
    return -np.sum(np.minimum(X[:, 3], np.pi / 2)) + lam * pen

if __name__ == "__main__":
    K = int(sys.argv[1]); trials = int(sys.argv[2]); seed = int(sys.argv[3]); eps = float(sys.argv[4])
    r = 1 - eps; rng = np.random.default_rng(seed); best = 0
    for t in range(trials):
        a = rng.uniform(0, 0.6, K) ** 1.5; g = rng.uniform(0, 2 * np.pi, K)
        x = np.stack([a * np.cos(g), a * np.sin(g), g + np.pi + rng.normal(0, 0.6, K), rng.uniform(0.2, 0.9, K)], 1).ravel()
        for lam, n in ((30, 10), (300, 16), (3e3, 24), (3e4, 36), (3e5, 48), (3e6, 64)):
            x = minimize(obj, x, args=(K, r, lam, n), method='L-BFGS-B', options={'maxiter': 4000}).x
        X = x.reshape(K, 4); X[:, 3] = np.abs(X[:, 3])
        # shrink every fan a hair until strictly valid
        for shrink in (0, 1e-5, 1e-4, 3e-4, 1e-3, 3e-3, 1e-2):
            S = [(q[0], q[1], q[2], max(q[3] - shrink, 1e-6)) for q in X]
            out, dep = strict_check(S, r, 2000)
            if out <= 0 and dep <= 1e-9 and check(S, r)[0]: break
        else:
            print(f"trial {t}: invalid", flush=True); continue
        frac = sum(s[3] for s in S) / np.pi
        print(f"trial {t}: frac={frac:.4f}", flush=True)
        if frac > best:
            best = frac; json.dump({'K': K, 'eps': eps, 'frac': frac, 'fans': S}, open(f'limit_K{K}_s{seed}.json', 'w'))
            print("  BEST", np.round(np.array(S), 4).tolist(), flush=True)
