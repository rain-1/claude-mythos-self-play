"""search.py — Koopman's optimal search allocation.

An object is somewhere, with prior density p(x).  Sensor: spending effort phi(x)
on x detects it with probability 1 - exp(-alpha*phi(x)) if it is there.  Spend a
total budget Phi to maximise the chance of finding it.

    maximise  int p (1 - e^{-alpha phi})   s.t.  int phi = Phi,  phi >= 0

Lagrange:  alpha p e^{-alpha phi} = lambda  on {phi > 0}, so

    phi(x) = (1/alpha) log( alpha p(x) / lambda )_+        [water-filling]
    posterior (given NO detection)  is proportional to  min( p(x), lambda/alpha )

i.e. the belief you are left with is your prior with every peak shaved to one
height, and the set you actually searched is the super-level set {p > lambda/alpha}.
"""
import numpy as np


def make_prior(H, W, seed=4):
    """a scattered belief: a drifting plume of lumps plus a few lonely hopes"""
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:H, 0:W]
    X = xx / W
    Y = yy / H
    p = np.zeros((H, W), np.float64)
    lumps = []
    # the plume: eight lumps along a drifting curve, shrinking and weakening
    for i, t in enumerate(np.linspace(0.10, 0.90, 8)):
        cx = 0.14 + 0.74 * t
        cy = 0.60 + 0.26 * np.sin(3.1 * t + 0.4) - 0.22 * t
        s0 = 0.030 + 0.030 * (1 - t)
        lumps.append((cx, cy, s0 * (0.8 + 0.5 * rng.uniform()),
                      s0 * (0.7 + 0.7 * rng.uniform()),
                      1.7 * np.sin(2.2 * t), 1.00 - 0.55 * t + 0.25 * rng.uniform()))
    # lonely hopes: small, far, weak
    for (cx, cy, s0, w) in [(0.20, 0.21, 0.036, 0.52), (0.82, 0.82, 0.030, 0.44),
                            (0.46, 0.14, 0.026, 0.37), (0.13, 0.78, 0.027, 0.40),
                            (0.70, 0.36, 0.022, 0.33), (0.36, 0.88, 0.023, 0.30)]:
        lumps.append((cx, cy, s0, s0 * (0.8 + 0.4 * rng.uniform()), rng.uniform(0, 3), w))
    for (cx, cy, sx, sy, th, w) in lumps:
        a = ((X - cx) * np.cos(th) + (Y - cy) * np.sin(th)) / sx
        b = (-(X - cx) * np.sin(th) + (Y - cy) * np.cos(th)) / sy
        p += w * np.exp(-0.5 * (a * a + b * b))
    p += 0.010 + 0.035 * np.exp(-0.5 * (((X - 0.5) / 0.55) ** 2 + ((Y - 0.5) / 0.55) ** 2))
    p /= p.sum()
    return p


def water_level(p, alpha, budget, iters=90):
    """find lambda/alpha = c with  int (1/alpha) log(p/c)_+ = budget"""
    lo, hi = p.min() * 0.5, p.max()
    for _ in range(iters):
        c = 0.5 * (lo + hi)
        eff = np.maximum(np.log(p / c), 0.0).sum() / alpha
        if eff > budget:
            lo = c
        else:
            hi = c
    return 0.5 * (lo + hi)


def solve(p, alpha, budget):
    c = water_level(p, alpha, budget)
    phi = np.maximum(np.log(p / c), 0.0) / alpha
    post = np.minimum(p, c)
    pdetect = 1.0 - post.sum()
    return dict(c=c, phi=phi, post=post / post.sum(), pdetect=pdetect,
                searched_fraction=float((p > c).mean()), effort=float(phi.sum()))


def uniform_compare(p, alpha, budget):
    phi = np.full(p.shape, budget / p.size)
    return float((p * (1 - np.exp(-alpha * phi))).sum())


def proportional_compare(p, alpha, budget):
    phi = budget * p / p.sum()
    return float((p * (1 - np.exp(-alpha * phi))).sum())


if __name__ == '__main__':
    import json
    H = W = 600
    p = make_prior(H, W)
    alpha = 1.0 / p.max() * 0.04
    out = {}
    for frac, name in [(3.0, 'small'), (12.0, 'medium'), (40.0, 'large')]:
        budget = frac / alpha
        s = solve(p, alpha, budget)
        out[name] = dict(budget=budget, P_detect_optimal=s['pdetect'],
                         P_detect_uniform=uniform_compare(p, alpha, budget),
                         P_detect_proportional=proportional_compare(p, alpha, budget),
                         searched_fraction=s['searched_fraction'])
        print(name, json.dumps({k: round(v, 5) for k, v in out[name].items()}))
