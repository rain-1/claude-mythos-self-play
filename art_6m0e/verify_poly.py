"""Verification battery for the convex-arc ensemble.

1. UNIFORMITY: at N=6, enumerate ALL strictly convex lattice arcs (0,0)->(6,6)
   (0/1 use of each primitive first-quadrant direction) by DP, then check the
   rejection sampler hits each arc with equal frequency (chi-square).
2. LIMIT SHAPE: empirical mean path -> parabola sqrt(y/N)+sqrt(1-x/N)=1 as N grows.
3. FLUCTUATIONS: transversal deviation scale vs N (report fitted exponent).
"""
import numpy as np
from itertools import combinations
from polysample import primitive_vectors, tune_t, sample_arcs, arc_points, limit_path

def enumerate_arcs(N):
    V = primitive_vectors(2 * N)
    V = V[(V.sum(axis=1) <= 2 * N)]
    ang = np.argsort(np.arctan2(V[:, 1], V[:, 0]), kind="stable")
    V = V[ang]
    sols = []
    nV = len(V)
    def rec(i, x, y, used):
        if x == N and y == N:
            sols.append(tuple(used))
        if i == nV or x > N or y > N:
            return
        # prune: remaining vectors can't reduce needed sum below...
        rec(i + 1, x + V[i, 0], y + V[i, 1], used + [i])
        rec(i + 1, x, y, used)
    rec(0, 0, 0, [])
    # dedupe (identical multisets impossible since 0/1 distinct directions)
    return V, sorted(set(sols))

if __name__ == "__main__":
    # --- 1. uniformity at N=6
    N = 6
    V6, sols = enumerate_arcs(N)
    print(f"N={N}: {len(sols)} strictly convex arcs total")
    t, V = tune_t(N, 2 * N)
    rng = np.random.default_rng(123)
    arcs, st = sample_arcs(N, t, V, 40000, window=0, rng=rng, verbose=False)
    # canonical key: sorted tuple of (a,b) edges
    def key(arc):
        pts = np.diff(arc_points(arc), axis=0)
        return tuple(map(tuple, pts))
    sol_keys = {}
    for s in sols:
        edges = tuple(map(tuple, V6[list(s)]))
        sol_keys[edges] = 0
    miss = 0
    for a in arcs:
        k = key(a)
        if k in sol_keys:
            sol_keys[k] += 1
        else:
            miss += 1
    counts = np.array(list(sol_keys.values()))
    M, K = counts.sum(), len(counts)
    chi2 = ((counts - M / K) ** 2 / (M / K)).sum()
    print(f"sampled {M} arcs into {K} classes (miss={miss}); "
          f"chi2={chi2:.1f} vs dof={K-1} (sqrt(2dof)={np.sqrt(2*(K-1)):.0f}) "
          f"=> {'UNIFORM OK' if abs(chi2-(K-1)) < 4*np.sqrt(2*(K-1)) else 'FAIL'}")
    print(f"min/max class count: {counts.min()}/{counts.max()} (expect ~{M//K})")

    # --- 2+3. limit shape + fluctuation scaling
    print("\nN    max|mean-parabola|/N   transversal std (lattice units)")
    devs = {}
    for N in [24, 48, 96, 192]:
        smax = max(16, int(14 * N ** (1 / 3)))
        t, V = tune_t(N, smax)
        rng = np.random.default_rng(N)
        arcs, st = sample_arcs(N, t, V, 400, window=(0 if N <= 96 else 1),
                               rng=rng, verbose=False)
        xg = np.linspace(0, N, 257)
        Ys = []
        for a in arcs:
            pts = arc_points(a).astype(float)
            # monotone in x except vertical runs: use unique x with max y
            Ys.append(np.interp(xg, pts[:, 0], pts[:, 1]))
        Ys = np.array(Ys)
        mean_y = Ys.mean(axis=0)
        parab = N * (1 - np.sqrt(np.maximum(1 - xg / N, 0))) ** 2
        maxdev = np.abs(mean_y - parab).max() / N
        std_mid = Ys.std(axis=0)[64:192].mean()
        devs[N] = std_mid
        print(f"{N:4d}   {maxdev:.4f}                 {std_mid:.2f}")
    Ns = np.array(sorted(devs))
    sds = np.array([devs[n] for n in Ns])
    slope = np.polyfit(np.log(Ns), np.log(sds), 1)[0]
    print(f"fluctuation exponent fit: std ~ N^{slope:.3f}  (theory: N^(2/3); "
          f"relative concentration ~ N^(-1/3))")
