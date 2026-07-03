"""Empirical 3-point correlation field R3(u,v) of a unit-spacing spectrum:
density of ordered triples (base, base+u, base+v). Sine-kernel determinant
gives the GUE/zeta theory. The field has canyons (repulsion) along u=0,
v=0, u=v — a six-armed star of absence."""
import numpy as np


def r3_hist(x, L=4.2, nbins=420, maxsep=14):
    """2-D histogram of (x[i+p]-x[i], x[i+q]-x[i]) over all p!=q in
    [-maxsep, maxsep]\\{0}. Levels x sorted, unit mean spacing; different
    matrices/blocks separated by huge offsets drop out via the L cut."""
    H = np.zeros((nbins, nbins), np.float64)
    n = len(x)
    offs = [o for o in range(-maxsep, maxsep + 1) if o != 0]
    for p in offs:
        for q in offs:
            if p == q:
                continue
            lo = max(0, -p, -q)
            hi = min(n, n - p, n - q)
            if hi <= lo:
                continue
            i = np.arange(lo, hi)
            u = x[i + p] - x[i]
            v = x[i + q] - x[i]
            m = (np.abs(u) < L) & (np.abs(v) < L)
            if m.any():
                hh, _, _ = np.histogram2d(u[m], v[m], bins=nbins,
                                          range=[[-L, L], [-L, L]])
                H += hh
    du = 2 * L / nbins
    return H / (n * du * du)      # R3 estimate


def r3_theory(L=4.2, nbins=420):
    c = (np.arange(nbins) + 0.5) / nbins * 2 * L - L
    U, V = np.meshgrid(c, c, indexing='ij')
    S = lambda t: np.sinc(t)
    a, b, cc = S(U), S(V), S(V - U)
    # det [[1,a,b],[a,1,cc],[b,cc,1]]
    return 1 + 2 * a * b * cc - a * a - b * b - cc * cc


if __name__ == "__main__":
    from spectra import zeta_unfolded
    z = zeta_unfolded()
    H = r3_hist(z)
    T = r3_theory()
    np.save("r3_zeta.npy", H)
    nb = H.shape[0]
    ring = (np.abs(np.hypot(*np.meshgrid(*(2*[np.linspace(-4.2, 4.2, nb)]),
            indexing='ij'))) > 3.0)
    print("far-field mean (should ~1):", H[ring].mean().round(4))
    m = np.ones_like(H, bool)
    err = np.median(np.abs(H - T))
    print("median |R3_emp - R3_theory| over field:", err.round(4))
    # against flat-1 baseline
    print("median |R3_emp - 1|:", np.median(np.abs(H - 1.0)).round(4))
    print("theory range:", T.min().round(3), T.max().round(3))
