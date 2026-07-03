"""Fast GUE via the Dumitriu-Edelman tridiagonal beta=2 Hermite ensemble
(exact GUE eigenvalue law, O(N^2) instead of O(N^3)). Empirical smooth
unfolding (absorbs any normalization). Verified against the sine kernel."""
import numpy as np
from scipy.linalg import eigvalsh_tridiagonal


def gue_tridiag_unfolded(n_matrices=8, N=20000, seed=5, bulk=0.6):
    rng = np.random.default_rng(seed)
    out = []
    for k in range(n_matrices):
        d = rng.normal(0, np.sqrt(2), N)
        e = np.sqrt(rng.chisquare(2 * np.arange(N - 1, 0, -1)))
        ev = eigvalsh_tridiagonal(d / np.sqrt(2), e / np.sqrt(2))
        ev.sort()
        # empirical unfolding: fit rank ~ P(lambda), degree-15 poly on mid 90%
        kk = np.arange(N, dtype=np.float64)
        lo, hi = int(0.05 * N), int(0.95 * N)
        # scale lambda to [-1,1] for conditioning
        lam = ev / np.abs(ev).max()
        cf = np.polynomial.chebyshev.chebfit(lam[lo:hi], kk[lo:hi], 24)
        x = np.polynomial.chebyshev.chebval(lam, cf)
        b0, b1 = int((0.5 - bulk / 2) * N), int((0.5 + bulk / 2) * N)
        xb = x[b0:b1]
        out.append(xb - xb[0] + k * 1e7)
    return np.concatenate(out)


def pair_r2(x, umax=4.0, nbins=400, maxsep=24):
    h = np.zeros(nbins)
    for k in range(1, maxsep):
        d = x[k:] - x[:-k]
        d = d[(d > 0) & (d < umax)]
        if d.size == 0:
            continue
        hh, _ = np.histogram(d, bins=nbins, range=(0, umax))
        h += hh
    du = umax / nbins
    return h / (len(x) * du)


if __name__ == "__main__":
    import time
    t0 = time.time()
    g = gue_tridiag_unfolded(n_matrices=2, N=20000)
    print(f"2 matrices in {time.time()-t0:.1f}s; {len(g)} levels")
    gaps = np.diff(g); gaps = gaps[gaps < 100]
    print("mean bulk gap:", gaps.mean().round(5))
    u = np.linspace(0.005, 4, 400)
    r2t = 1 - np.sinc(u) ** 2
    r2 = pair_r2(g)
    m = (u > 0.05) & (u < 3.8)
    print("median |R2_emp - R2_sine| =", np.median(np.abs(r2[m] - r2t[m])).round(4))
    print("median |R2_emp - 1|      =", np.median(np.abs(r2[m] - 1)).round(4))
