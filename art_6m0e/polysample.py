"""Sinai grand-canonical sampler for uniform convex lattice arcs (0,0)->(N,N).

Model: every primitive vector v=(a,b), a,b>=0, gcd(a,b)=1, is used 0 or 1
times, independently, with P(use v) = z^(a+b) / (1 + z^(a+b)),  z = e^{-t}.
Sorting the chosen vectors by slope gives a strictly convex lattice arc.
Conditioned on the endpoint being exactly (N,N), the arc is UNIFORM over all
strictly convex lattice arcs from (0,0) to (N,N) with edge directions in the
closed first quadrant (every such arc has the same weight z^(2N)).
"""
import numpy as np
from math import gcd

def primitive_vectors(smax):
    """All primitive (a,b), a,b>=0, gcd=1, 1 <= a+b <= smax. Includes (1,0),(0,1)."""
    vs = []
    for a in range(smax + 1):
        for b in range(smax + 1 - a):
            if a == 0 and b == 0:
                continue
            if gcd(a, b) == 1:
                vs.append((a, b))
    return np.array(vs, dtype=np.int64)

def mean_endpoint(t, V):
    s = V.sum(axis=1)
    p = 1.0 / (1.0 + np.exp(t * s))
    return (V[:, 0] * p).sum()  # symmetric: X mean == Y mean

def tune_t(N, smax):
    V = primitive_vectors(smax)
    lo, hi = 1e-4, 5.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if mean_endpoint(mid, V) > N:
            lo, hi = mid, hi
        else:
            hi = mid
        lo, hi = (mid, hi) if mean_endpoint(mid, V) > N else (lo, mid)
    return 0.5 * (lo + hi), V

def limit_path(t, V, npts=512):
    """Exact grand-canonical mean path, ordered by slope: the finite-N limit curve."""
    s = V.sum(axis=1)
    p = 1.0 / (1.0 + np.exp(t * s))
    ang = np.arctan2(V[:, 1], V[:, 0])
    o = np.argsort(ang, kind="stable")
    steps = V[o].astype(np.float64) * p[o, None]
    path = np.vstack([[0.0, 0.0], np.cumsum(steps, axis=0)])
    return path  # (K+1, 2)

def sample_arcs(N, t, V, n_target, batch=8192, window=0, rng=None, verbose=True):
    """Rejection-sample arcs hitting (N,N) exactly (window=0) or within window
    (then repaired EXACTLY by adjusting the counts of (1,0)/(0,1) axis steps,
    which keeps a valid weakly-convex lattice arc; repairs are <= window steps).
    Returns list of arcs; each arc is an int64 array (k,2) of vectors sorted by slope,
    plus stats dict."""
    if rng is None:
        rng = np.random.default_rng(20260712)
    s = V.sum(axis=1)
    p = (1.0 / (1.0 + np.exp(t * s))).astype(np.float64)
    ang = np.arctan2(V[:, 1], V[:, 0])
    order = np.argsort(ang, kind="stable")
    Vo = V[order]
    po = p[order]
    ax_h = int(np.where((Vo[:, 0] == 1) & (Vo[:, 1] == 0))[0][0])
    ax_v = int(np.where((Vo[:, 0] == 0) & (Vo[:, 1] == 1))[0][0])
    nV = len(Vo)
    arcs, tries, repaired = [], 0, 0
    a_col = Vo[:, 0].astype(np.float64)
    b_col = Vo[:, 1].astype(np.float64)
    while len(arcs) < n_target:
        tries += batch
        U = rng.random((batch, nV))
        B = U < po  # bool (batch, nV)
        X = B @ a_col
        Y = B @ b_col
        ok = (np.abs(X - N) <= window) & (np.abs(Y - N) <= window)
        idx = np.where(ok)[0]
        for i in idx:
            row = B[i].copy()
            dx, dy = int(N - X[i]), int(N - Y[i])
            # exact repair via axis multiplicities (multi[ax] = 1 + d)
            mh, mv = 1 + dx if row[ax_h] else dx, 1 + dy if row[ax_v] else dy
            if not row[ax_h]:
                mh = dx
            if not row[ax_v]:
                mv = dy
            if mh < 0 or mv < 0:
                continue
            if dx != 0 or dy != 0:
                repaired += 1
            ks = np.where(row)[0]
            mult = np.ones(len(ks), dtype=np.int64)
            # fold axis multiplicity adjustments
            arc_vs = Vo[ks]
            m = mult.copy()
            if row[ax_h]:
                m[np.where(ks == ax_h)[0][0]] = mh
            elif mh > 0:
                arc_vs = np.vstack([[1, 0], arc_vs]); m = np.concatenate([[mh], m])
            if row[ax_v]:
                m[np.where(ks == ax_v)[0][0]] = mv
            elif mv > 0:
                arc_vs = np.vstack([arc_vs, [0, 1]]); m = np.concatenate([m, [mv]])
            keep = m > 0
            arcs.append((arc_vs[keep], m[keep]))
            if len(arcs) >= n_target:
                break
    stats = dict(tries=tries, accepted=len(arcs), rate=len(arcs) / tries, repaired=repaired)
    if verbose:
        print(f"N={N} t={t:.5f} nV={nV} rate={stats['rate']:.2e} repaired={repaired}/{len(arcs)}")
    return arcs, stats

def arc_points(arc):
    """(vectors, mult) -> vertex array (k+1, 2) from (0,0)."""
    vs, m = arc
    steps = np.repeat(vs, m, axis=0)
    return np.vstack([[0, 0], np.cumsum(steps, axis=0)])

if __name__ == "__main__":
    import sys, time
    for N in [32, 64, 128]:
        smax = max(12, int(6 * N ** (1 / 3) * 2))
        t0 = time.time()
        t, V = tune_t(N, smax)
        s = V.sum(axis=1)
        p = 1 / (1 + np.exp(t * s))
        print(f"N={N}: t={t:.5f} smax={smax} nV={len(V)} E[edges]={p.sum():.1f} "
              f"meanX={ (V[:,0]*p).sum():.2f} tune={time.time()-t0:.1f}s")
        t0 = time.time()
        arcs, st = sample_arcs(N, t, V, 200, window=0)
        print(f"  exact-hit rate {st['rate']:.2e}  ({time.time()-t0:.1f}s for 200 arcs)")
