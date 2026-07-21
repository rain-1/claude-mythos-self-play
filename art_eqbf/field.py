"""Field computations for the governing cubic P(T) = c T^3 - 2 T^2 + b T - 2a
of the Alpoge map.  Slice through the collision image q*=(-1/4,0,0):
    a = -1/4 + u,  b = (4/3) v,  c = v
so v=0 is the degeneration wall c=0, q* sits at (u,v)=(0,0), and the two real
cusps of the branch surface (triple roots) sit at (u,v)=(43/108, +-1)."""
import numpy as np

U_CUSP = 4 / 27 + 1 / 4   # 43/108


def slice_abc(u, v):
    return (-0.25 + u, (4.0 / 3.0) * v, v)


def disc(a, b, c):
    """Discriminant of cT^3 - 2T^2 + bT - 2a (up to the overall factor 4)."""
    return 18 * a * b * c - 16 * a + b * b - c * b ** 3 - 27 * a * a * c * c


def roots_grid(a, b, c, chunk=200_000):
    """Roots of the cubic per grid point via batched companion eigvals.
    a,b,c: same-shape arrays. Returns complex array shape (*a.shape, 3).
    Where |c| is tiny, solves the quadratic -2T^2+bT-2a and puts the third
    root at the escaping value 2/(c) (clipped) -- callers mask the wall."""
    sh = a.shape
    af, bf, cf = (np.ravel(np.asarray(w, np.float64)) for w in (a, b, c))
    n = af.size
    out = np.empty((n, 3), np.complex128)
    small = np.abs(cf) < 1e-9
    idx = np.where(~small)[0]
    for s in range(0, idx.size, chunk):
        ii = idx[s:s + chunk]
        m = ii.size
        C = np.zeros((m, 3, 3))
        # monic: T^3 - (2/c) T^2 + (b/c) T - 2a/c
        C[:, 0, 1] = 1.0
        C[:, 1, 2] = 1.0
        C[:, 2, 0] = 2 * af[ii] / cf[ii]
        C[:, 2, 1] = -bf[ii] / cf[ii]
        C[:, 2, 2] = 2 / cf[ii]
        out[ii] = np.linalg.eigvals(C)
    if small.any():
        ii = np.where(small)[0]
        disc2 = bf[ii] ** 2 - 16 * af[ii] + 0j
        r = np.sqrt(disc2)
        out[ii, 0] = (bf[ii] - r) / 4.0
        out[ii, 1] = (bf[ii] + r) / 4.0
        out[ii, 2] = np.inf
    return out.reshape(*sh, 3)


def pprime(t, a, b, c):
    return 3 * c[..., None] * t * t - 4 * t + b[..., None]


def x_of(t, a, b, c):
    """Source coordinate x = 2/P'(t) on each sheet."""
    return 2.0 / pprime(t, a, b, c)
