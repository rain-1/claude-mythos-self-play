"""fit_test.py — does a folded figure fit back into a congruent copy of itself?  (MO 7016)
For each convex figure F (a fine polygon) and many random pairs of parallel folds, take the vertex
set S of the folded layers and minimise over rigid motions g the largest distance of g(S) outside F.
The disc always gives 0 (certificate of the picture); the others do not.
"""
import numpy as np, json, time
from scipy.optimize import minimize
import fold

rng = np.random.default_rng(0)


def poly_edges(F):
    # drop repeated consecutive vertices (zero-length edges have no normal)
    keep = np.linalg.norm(np.roll(F, -1, 0) - F, axis=1) > 1e-9
    F = F[keep]
    m = len(F)
    E = np.roll(F, -1, 0) - F
    nrm = np.c_[E[:, 1], -E[:, 0]]           # outward normals for a CCW polygon
    nrm /= np.linalg.norm(nrm, axis=1)[:, None]
    off = (nrm * F).sum(1)
    return nrm, off


def outside_dist(S, nrm, off):
    """max over points of the largest signed half-plane excess (0 if inside a convex polygon)"""
    d = S @ nrm.T - off[None]
    return np.clip(d.max(1), 0, None).max()


def best_fit(S, F, starts=24):
    nrm, off = poly_edges(F)
    cF = F.mean(0); cS = S.mean(0)
    best = np.inf
    for k in range(starts):
        th0 = rng.uniform(0, 2 * np.pi)
        def cost(v):
            th, tx, ty = v
            R = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
            G = (S - cS) @ R.T + cF + np.array([tx, ty])
            return outside_dist(G, nrm, off)
        res = minimize(cost, [th0, rng.normal(0, 0.05), rng.normal(0, 0.05)], method='Nelder-Mead',
                       options=dict(xatol=1e-7, fatol=1e-9, maxiter=4000))
        best = min(best, res.fun)
    return best


def figures():
    t = np.linspace(0, 2 * np.pi, 720, endpoint=False)
    out = {'disc': np.c_[np.cos(t), np.sin(t)],
           'ellipse 0.97': np.c_[np.cos(t), 0.97 * np.sin(t)],
           'ellipse 0.85': np.c_[np.cos(t), 0.85 * np.sin(t)],
           'square': np.array([[1, 1], [-1, 1], [-1, -1], [1, -1]], float),
           'hexagon': np.c_[np.cos(np.linspace(0, 2 * np.pi, 6, endpoint=False)), np.sin(np.linspace(0, 2 * np.pi, 6, endpoint=False))],
           'stadium': None, 'reuleaux': None, 'lens 1.99': None}
    # stadium: rectangle 1x0.5 with semicircle caps
    a = np.linspace(-np.pi / 2, np.pi / 2, 200); b = np.linspace(np.pi / 2, 3 * np.pi / 2, 200)
    out['stadium'] = np.vstack([np.c_[0.5 + 0.5 * np.cos(a), 0.5 * np.sin(a)], np.c_[-0.5 + 0.5 * np.cos(b), 0.5 * np.sin(b)]])
    # Reuleaux triangle of width 1
    V = np.c_[np.cos(np.linspace(np.pi / 2, np.pi / 2 + 2 * np.pi, 3, endpoint=False)), np.sin(np.linspace(np.pi / 2, np.pi / 2 + 2 * np.pi, 3, endpoint=False))] / np.sqrt(3)
    pts = []
    for k in range(3):
        c = V[k]; p = V[(k + 1) % 3]; q = V[(k + 2) % 3]
        a0 = np.arctan2(*(p - c)[::-1]); a1 = np.arctan2(*(q - c)[::-1])
        d = (a1 - a0 + np.pi) % (2 * np.pi) - np.pi      # the short arc (60 degrees)
        ang = np.linspace(a0, a0 + d, 200)
        pts.append(c + np.c_[np.cos(ang), np.sin(ang)])
    R = np.vstack(pts)
    c = R.mean(0); o = np.argsort(np.arctan2(R[:, 1] - c[1], R[:, 0] - c[0]))
    out['reuleaux'] = R[o]
    # lens: unit disc ∩ disc radius 1.99 centred (0,1)
    D = np.c_[np.cos(t), np.sin(t)]
    keep = (D[:, 0] ** 2 + (D[:, 1] - 1) ** 2) <= 1.99 ** 2
    # walk the boundary: part of unit circle inside big disc + part of big circle inside unit disc
    ang = np.linspace(0, 2 * np.pi, 2000)
    big = np.c_[1.99 * np.cos(ang), 1 + 1.99 * np.sin(ang)]
    bk = (big ** 2).sum(1) <= 1
    arcs = np.vstack([D[keep], big[bk]])
    # order by angle around the centroid
    c = arcs.mean(0); o = np.argsort(np.arctan2(arcs[:, 1] - c[1], arcs[:, 0] - c[0]))
    out['lens 1.99'] = arcs[o]
    for k in out:
        P = out[k]
        if (P[1] - P[0])[0] * (P[2] - P[1])[1] - (P[1] - P[0])[1] * (P[2] - P[1])[0] < 0:
            out[k] = P[::-1]
    return out


def two_parallel_folds(F, rng):
    fig = fold.Folded(F)
    pts = F; c = pts.mean(0)
    th = rng.uniform(0, 2 * np.pi); n = np.array([np.cos(th), np.sin(th)])
    proj = (pts - c) @ n; lo, hi = proj.min(), proj.max()
    d1 = rng.uniform(lo + 0.05 * (hi - lo), lo + 0.45 * (hi - lo))
    fig.fold(c + d1 * n, -n)                 # flip the low side over
    pts2 = fig.hull_pts(); proj2 = (pts2 - c) @ n
    d2 = rng.uniform(proj2.max() - 0.45 * (proj2.max() - proj2.min()), proj2.max() - 0.05 * (proj2.max() - proj2.min()))
    fig.fold(c + d2 * n, n)                  # flip the high side over
    return fig


if __name__ == '__main__':
    t0 = time.time()
    res = {}
    figs = figures()
    for name, F in figs.items():
        worst = 0.0; worst_fit = None
        diam = np.linalg.norm(F[:, None] - F[None], axis=2).max()
        for trial in range(30):
            fig = two_parallel_folds(F, rng)
            S = fig.hull_pts()
            # subsample the vertex set for speed
            if len(S) > 400:
                S = S[rng.choice(len(S), 400, replace=False)]
            b = best_fit(S, F, starts=12)
            if b > worst:
                worst = b
        res[name] = dict(worst_misfit_over_diameter=float(worst / diam), trials=30)
        print(name, res[name], time.time() - t0, flush=True)
    json.dump(res, open('fit_test.json', 'w'), indent=1)
