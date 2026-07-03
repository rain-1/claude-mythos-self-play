"""Unfolded spectra: Riemann zeta zeros (Odlyzko), GUE bulk, Poisson.
All unfolded to unit mean spacing. Verified against the sine-kernel R2."""
import numpy as np

ZEROS_PATH = "/tmp/claude-0/-home-user-claude-mythos-self-play/3b1c892d-85d8-5ccd-86d3-8c63e823ea19/scratchpad/zeros1"


def zeta_unfolded():
    g = np.loadtxt(ZEROS_PATH)
    # Riemann-von Mangoldt: N(T) = T/2pi log(T/2pi e) + 7/8 + S(T)
    x = g / (2 * np.pi) * np.log(g / (2 * np.pi * np.e)) + 7.0 / 8.0
    return x


def gue_unfolded(n_matrices=70, N=2000, seed=5):
    """Bulk eigenvalues of GUE matrices, unfolded by the semicircle CDF."""
    rng = np.random.default_rng(seed)
    out = []
    for k in range(n_matrices):
        A = rng.standard_normal((N, N)) + 1j * rng.standard_normal((N, N))
        H = (A + A.conj().T) / 2.0
        ev = np.linalg.eigvalsh(H) / np.sqrt(N)  # semicircle on [-2,2]
        # semicircle CDF: F(x) = 1/2 + (x sqrt(4-x^2)/4 + asin(x/2)) / (2 pi) *2
        x = np.clip(ev, -2, 2)
        F = 0.5 + (x * np.sqrt(4 - x * x) / 4 + np.arcsin(x / 2)) / np.pi
        u = N * F                       # unfolded, mean spacing 1
        # keep the bulk (middle 60%) where unfolding is accurate
        lo, hi = int(0.2 * N), int(0.8 * N)
        out.append(u[lo:hi] + k * 10 * N)  # separate matrices far apart
    return np.concatenate(out)


def poisson_unfolded(n=100_000, seed=9):
    rng = np.random.default_rng(seed)
    return np.cumsum(rng.exponential(1.0, n))


def pair_r2(x, umax=4.0, nbins=400, maxsep=64):
    """Empirical pair correlation R2(u) with unit mean spacing."""
    h = np.zeros(nbins)
    M = 0
    for k in range(1, maxsep):
        d = x[k:] - x[:-k]
        d = d[d < umax]
        if d.size == 0:
            break
        hh, _ = np.histogram(d, bins=nbins, range=(0, umax))
        h += hh
        M = max(M, 1)
    n = len(x)
    du = umax / nbins
    return h / (n * du)   # R2 estimate


if __name__ == "__main__":
    z = zeta_unfolded()
    print("zeta zeros:", len(z), "mean gap:", np.mean(np.diff(z)).round(4))
    g = gue_unfolded(n_matrices=6)   # quick check
    gaps = np.diff(g); gaps = gaps[gaps < 10]
    print("gue levels:", len(g), "mean bulk gap:", gaps.mean().round(4))
    u = np.linspace(0.005, 4, 400)
    sinc = np.sinc(u)  # sin(pi u)/(pi u)
    r2_theory = 1 - sinc ** 2
    for name, x in (("zeta", z), ("gue", g), ("poisson", poisson_unfolded())):
        r2 = pair_r2(x)
        # compare on u in [0.1, 3.5]
        m = (u > 0.1) & (u < 3.5)
        err_gue = np.median(np.abs(r2[m] - r2_theory[m]))
        err_poi = np.median(np.abs(r2[m] - 1.0))
        print(f"{name:8s} median|R2 - GUE|={err_gue:.4f}  median|R2 - 1|={err_poi:.4f}")
