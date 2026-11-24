"""opt.py n starts [seed]  — multistart Nelder-Mead on the 3n parameters; writes best_n.json"""
import sys, json, numpy as np
from multiprocessing import Pool
from scipy.optimize import minimize
from corner import objective, width, width_fast, overlap

def one(args):
    n, seed = args
    r = np.random.default_rng(seed)
    kind = seed % 5
    if kind == 0:   # loose random
        P = np.c_[r.uniform(-1, 1, n) * np.sqrt(n), r.uniform(-.8, .8, n) * np.sqrt(n) * .6, r.uniform(0, np.pi / 2, n)]
    elif kind == 1:  # row with jitter, parallel
        P = np.c_[np.arange(n) - (n - 1) / 2 + r.normal(0, .05, n), r.uniform(0, .6, n), r.normal(0, .05, n)]
    elif kind == 2:  # two rows
        k = (n + 1) // 2
        P = np.array([[i - (k - 1) / 2, 0, 0] for i in range(k)] + [[i - (n - k - 1) / 2 + r.uniform(-.5, .5), 1.05, 0] for i in range(n - k)], float)
        P += r.normal(0, .08, P.shape)
    elif kind == 4:  # skyline with jitter
        h = np.minimum(np.arange(n), np.arange(n)[::-1]) * r.uniform(.2, .7) + r.normal(0, .1, n)
        P = np.c_[np.arange(n) - (n - 1) / 2, h, np.zeros(n)] + r.normal(0, .02, (n, 3))
    else:           # arch: squares along an arc
        a = np.linspace(-1, 1, n) * r.uniform(.3, 1.2)
        R = r.uniform(1.0, 3.0)
        P = np.c_[R * np.sin(a) * n / 3, -R * (1 - np.cos(a)) + r.normal(0, .1, n), -a * r.uniform(0, 1) + r.normal(0, .1, n)]
    x = P.ravel()
    for N, lam, it in ((360, 2.0, 2500), (1440, 6.0, 2500)):
        res = minimize(objective, x, args=(N, lam), method="Nelder-Mead",
                       options=dict(maxiter=it * n, maxfev=it * n, xatol=1e-9, fatol=1e-11, adaptive=True))
        x = res.x
        res = minimize(objective, x, args=(N, lam), method="Powell", options=dict(maxiter=6, xtol=1e-9, ftol=1e-12))
        if res.fun < objective(x, N, lam): x = res.x
    P = x.reshape(-1, 3)
    w = width_fast(P, 28800); ov = overlap(P)
    return (n / (w + 2 * ov) ** 2, ov, x.tolist(), seed)

if __name__ == "__main__":
    n = int(sys.argv[1]); S = int(sys.argv[2]); s0 = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    with Pool(4) as p:
        out = p.map(one, [(n, s0 + i) for i in range(S)], chunksize=1)
    out.sort(key=lambda t: -t[0])
    for a, ov, x, seed in out[:8]:
        P = np.array(x).reshape(-1, 3)
        print(f"area {a:.6f} overlap {ov:.1e} seed {seed} angles", np.round(np.degrees(P[:, 2]) % 90, 2))
    import os
    old = json.load(open(f'best_{n}.json'))['area'] if os.path.exists(f'best_{n}.json') else 0
    if out[0][0] > old: json.dump(dict(n=n, area=out[0][0], P=out[0][2], all=[o[0] for o in out]), open(f"best_{n}.json", "w"))
