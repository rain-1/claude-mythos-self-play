"""siegel.py — the golden-mean Siegel disk of z -> z^2 + c.

theta = (sqrt5 - 1)/2, lambda = exp(2 pi i theta), c = lambda/2 - lambda^2/4: the fixed point
z0 = lambda/2 has multiplier lambda, so it is a Siegel point (Siegel 1942, theta Diophantine),
and by Douady–Ghys–Herman–Świątek the boundary of its Siegel disk is a quasicircle passing
through the critical point 0.  Inside: every orbit lies on a closed invariant curve.  Outside
the filled Julia set: Green's function G and external rays (Böttcher coordinate).
"""
import numpy as np, time, json


def params():
    th = (np.sqrt(5) - 1) / 2
    lam = np.exp(2j * np.pi * th)
    c = lam / 2 - lam ** 2 / 4
    z0 = lam / 2
    return th, lam, c, z0


def green(Z, c, nmax=400, R=1e4):
    """Green's function of K (0 inside), plus the iterate count."""
    z = Z.astype(np.complex128).copy()
    G = np.zeros(z.shape, np.float64)
    alive = np.ones(z.shape, bool)
    for n in range(nmax):
        z[alive] = z[alive] ** 2 + c
        a = np.abs(z)
        esc = alive & (a > R)
        G[esc] = np.log(a[esc]) / 2.0 ** (n + 1)
        alive &= ~esc
        if not alive.any():
            break
    return G


def orbit(z, c, n):
    """the orbit of a batch of points, shape (n, len(z))"""
    out = np.empty((n, len(z)), np.complex128)
    w = np.array(z, np.complex128)
    for k in range(n):
        out[k] = w
        w = w * w + c
    return out


def pullback(P, c, levels):
    """preimages of a point set P under f: level k gives 2^k copies (all branches)."""
    out = [P]
    cur = P
    for k in range(levels):
        r = np.sqrt(cur - c)
        cur = np.concatenate([r, -r])
        out.append(cur)
    return out


def rays(angles, c, R0=1e3, depth=44, sub=6):
    """external rays by Newton continuation along the Böttcher coordinate.
    Returns list of arrays (points along each ray), from far away toward the Julia set."""
    angles = np.asarray(angles, float)
    n_r = len(angles)
    # potential levels: |phi| = R0^(1/2^(n + s/sub)), n = 0..depth
    pts = [R0 * np.exp(2j * np.pi * angles)]
    z = pts[0].copy()
    for n in range(depth):
        for s in range(1, sub + 1):
            t = n + s / sub
            r = R0 ** (2.0 ** (-t))              # target |phi|
            # target w = f^{n+1}(z) should have phi(w) = r^(2^(n+1)) e^{2 pi i 2^(n+1) theta}; for |w| >> 1 phi(w) ~ w
            k = n + 1
            wt = (r ** (2.0 ** k)) * np.exp(2j * np.pi * np.mod(angles * 2.0 ** k, 1.0))
            # Newton on f^k(z) = wt, starting at the previous ray point
            for it in range(12):
                fz = z.copy(); dz = np.ones_like(z)
                for _ in range(k):
                    dz = 2 * fz * dz
                    fz = fz * fz + c
                step = (fz - wt) / dz
                z = z - step
                if np.abs(step).max() < 1e-13:
                    break
            pts.append(z.copy())
    return np.array(pts)   # (n_levels, n_rays)


if __name__ == '__main__':
    th, lam, c, z0 = params()
    print('c =', c, 'z0 =', z0, 'f(z0)-z0 =', z0 ** 2 + c - z0, "|f'(z0)| =", abs(2 * z0))
    t = time.time()
    O = orbit(np.array([0.0 + 0j]), c, 20000)[:, 0]
    print('critical orbit: max|z| =', np.abs(O).max(), 'min dist to z0 =', np.abs(O - z0).min(), f'{time.time()-t:.2f}s')
