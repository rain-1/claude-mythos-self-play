"""mirage.py — an inferior mirage as a fold caustic.

Hot ground, cooler air above: the refractive index n(z) = 1 + ε(1 − e^{−z/h}) rises with height, so light bends
upward. Rays are traced with the Hamiltonian form of the eikonal equation, dr/ds = p, dp/ds = n∇n, |p| = n
(RK4 in the pseudo-arclength s). A ray from a point of the tower that dips toward the ground turns back up
before touching it and reaches the eye FROM BELOW, so the eye sees the tower a second time, inverted, beneath
the erect image; below the lowest turning ray it sees only the sky, and calls it water. The envelope of the
fan from one source point is a fold caustic: an eye inside the fold sees two images, outside it one.
"""
import numpy as np

EPS = 0.02      # index contrast (exaggerated ~50x for the picture; the geometry is the same)
HSC = 0.35      # scale height of the hot layer
L = 10.0        # tower -> eye distance


def n_of(z):
    return 1.0 + EPS * (1.0 - np.exp(-np.maximum(z, 0) / HSC))


def dn_dz(z):
    return (EPS / HSC) * np.exp(-np.maximum(z, 0) / HSC)


def trace(x0, z0, theta0, ds=0.01, smax=None):
    """trace rays from (x0, z0) (arrays or scalars broadcast) at launch angles theta0 (array).
    Returns X, Z (nray, nstep) with NaN after a ray leaves [0, L] or hits the ground."""
    theta0 = np.atleast_1d(theta0).astype(float)
    nr = len(theta0)
    x = np.full(nr, float(x0)) if np.isscalar(x0) else np.asarray(x0, float).copy()
    z = np.full(nr, float(z0)) if np.isscalar(z0) else np.asarray(z0, float).copy()
    n0 = n_of(z)
    px = n0 * np.cos(theta0); pz = n0 * np.sin(theta0)
    smax = smax or 1.3 * L
    nstep = int(smax / ds)
    X = np.full((nr, nstep + 1), np.nan); Z = np.full((nr, nstep + 1), np.nan)
    alive = np.ones(nr, bool)
    X[:, 0] = x; Z[:, 0] = z

    def f(x, z, px, pz):
        g = n_of(z) * dn_dz(z)
        return px, pz, np.zeros_like(px), g

    for k in range(1, nstep + 1):
        k1 = f(x, z, px, pz)
        k2 = f(x + 0.5 * ds * k1[0], z + 0.5 * ds * k1[1], px + 0.5 * ds * k1[2], pz + 0.5 * ds * k1[3])
        k3 = f(x + 0.5 * ds * k2[0], z + 0.5 * ds * k2[1], px + 0.5 * ds * k2[2], pz + 0.5 * ds * k2[3])
        k4 = f(x + ds * k3[0], z + ds * k3[1], px + ds * k3[2], pz + ds * k3[3])
        x = x + ds / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
        z = z + ds / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
        px = px + ds / 6 * (k1[2] + 2 * k2[2] + 2 * k3[2] + k4[2])
        pz = pz + ds / 6 * (k1[3] + 2 * k2[3] + 2 * k3[3] + k4[3])
        alive &= (z > 0) & (x <= L * 1.02)
        X[alive, k] = x[alive]; Z[alive, k] = z[alive]
    return X, Z


def resample(X, Z, xs):
    """z of every ray on a common x grid (NaN where the ray is absent)"""
    out = np.full((X.shape[0], len(xs)), np.nan)
    for i in range(X.shape[0]):
        m = ~np.isnan(X[i])
        if m.sum() < 2:
            continue
        xi, zi = X[i, m], Z[i, m]
        ok = (xs >= xi[0]) & (xs <= xi[-1])
        out[i, ok] = np.interp(xs[ok], xi, zi)
    return out


def caustic(Zg, xs):
    """fold points: where neighbouring rays (in launch angle) cross, i.e. z_{i+1} - z_i changes sign along i"""
    d = np.diff(Zg, axis=0)
    pts = []
    for j in range(len(xs)):
        col = d[:, j]
        ok = ~np.isnan(col)
        idx = np.where(ok[:-1] & ok[1:] & (np.sign(col[:-1]) != np.sign(col[1:])))[0]
        for i in idx:
            pts.append((xs[j], 0.5 * (Zg[i + 1, j] + Zg[i + 2, j]) if not np.isnan(Zg[i + 2, j]) else Zg[i + 1, j], i))
    return np.array(pts) if pts else np.zeros((0, 3))


def view(z_e, tower_z, nang=1200, th_range=(-0.35, 0.25)):
    """what an eye at (L, z_e) sees of tower points at heights tower_z: list of (z_t, arrival elevation)"""
    th = np.linspace(th_range[0], th_range[1], nang)
    seen = []
    for zt in tower_z:
        X, Z = trace(0.0, zt, th)
        # arrival height and direction at x = L
        zL = np.full(nang, np.nan); elev = np.full(nang, np.nan)
        for i in range(nang):
            m = ~np.isnan(X[i])
            xi = X[i, m]; zi = Z[i, m]
            if len(xi) < 3 or xi[-1] < L:
                continue
            k = np.searchsorted(xi, L)
            k = min(max(k, 1), len(xi) - 1)
            t = (L - xi[k - 1]) / (xi[k] - xi[k - 1] + 1e-15)
            zL[i] = zi[k - 1] + t * (zi[k] - zi[k - 1])
            elev[i] = np.arctan2(zi[k] - zi[k - 1], xi[k] - xi[k - 1])
        g = zL - z_e
        ok = ~np.isnan(g)
        for i in range(nang - 1):
            if ok[i] and ok[i + 1] and np.sign(g[i]) != np.sign(g[i + 1]):
                t = g[i] / (g[i] - g[i + 1])
                seen.append((zt, elev[i] + t * (elev[i + 1] - elev[i]), th[i] + t * (th[i + 1] - th[i])))
    return np.array(seen) if seen else np.zeros((0, 3))


if __name__ == '__main__':
    import json, time
    t0 = time.time()
    th = np.linspace(-0.30, 0.20, 400)
    X, Z = trace(0.0, 1.2, th)
    xs = np.linspace(0, L, 400)
    Zg = resample(X, Z, xs)
    c = caustic(Zg, xs)
    print('rays', len(th), 'caustic points', len(c), 'time', round(time.time() - t0, 1))
    if len(c):
        print('caustic z range', c[:, 1].min(), c[:, 1].max(), 'x range', c[:, 0].min(), c[:, 0].max())
    for ze in (0.3, 0.6, 1.0, 1.6):
        s = view(ze, np.linspace(0.3, 1.6, 8), nang=400)
        print('eye', ze, 'images per tower point:', np.bincount([int(np.sum(s[:, 0] == zt)) for zt in np.linspace(0.3, 1.6, 8)]) if len(s) else 0,
              'elev range', (s[:, 1].min(), s[:, 1].max()) if len(s) else None)
