"""adhesion.py — the cosmic web by the adhesion model (Zel'dovich + Burgers, zero viscosity).

Gurbatov–Saichev–Shandarin: dust with initial velocity u0 = -grad phi0 moves in straight lines
(x = q + t u0) until streams cross; then it STICKS (infinite-viscosity-limit of Burgers).  The exact
solution is a convex-hull construction (Hopf–Lax / Legendre):

    psi_t(q) = |q|^2 / (2t) - phi0(q);   x(q) = t * grad(conv psi_t)(q).

A Lagrangian point q that is a VERTEX of the lower convex hull of the lifted points (q, psi_t(q)) is
still free (it maps to x = q + t u0(q)); every point strictly above the hull has been swallowed.
Each lower-hull FACET (a triangle q1 q2 q3 with supporting plane of gradient g) is a lump of mass
(its Lagrangian area) sitting at the single Eulerian point x = t g: the nodes.  Chains of thin
facets are the filaments; the tiny facets of a still-convex region are the voids' thin mist.

This module builds the hull and returns per-facet (x, mass, epoch) so the renderer can paint it.
"""
import numpy as np, time, json
from scipy.spatial import ConvexHull


def gaussian_potential(N, seed, n_index=-1.0, k_cut=None, k_low=1.0, L=1.0, amp=1.0):
    """periodic Gaussian random density contrast delta with P(k) ~ k^n exp(-(k/k_cut)^2) (k in units 2pi/L),
    potential phi from  lap phi = delta  (so u0 = -grad phi is the Zel'dovich velocity up to a factor).
    Returns phi (N,N) with rms normalised to amp*L^2 (so that t is in units where t ~ 1 = first crossings)."""
    rng = np.random.default_rng(seed)
    kx = np.fft.fftfreq(N, d=L / N) * 2 * np.pi
    ky = np.fft.rfftfreq(N, d=L / N) * 2 * np.pi
    KX, KY = np.meshgrid(kx, ky, indexing='ij')
    k2 = KX ** 2 + KY ** 2
    k = np.sqrt(k2)
    k0 = 2 * np.pi / L
    with np.errstate(divide='ignore', invalid='ignore'):
        P = np.where(k > 0, (k / k0) ** n_index, 0.0)
    if k_cut is not None:
        P = P * np.exp(-(k / (k_cut * k0)) ** 2)
    if k_low > 0:
        P = P * (1 - np.exp(-(k / (k_low * k0)) ** 2))
    white = np.fft.rfft2(rng.standard_normal((N, N)))
    delta_k = white * np.sqrt(P)
    with np.errstate(divide='ignore', invalid='ignore'):
        phi_k = np.where(k2 > 0, -delta_k / k2, 0.0)
    phi = np.fft.irfft2(phi_k, s=(N, N))
    phi -= phi.mean()
    # normalise so that the rms of the initial velocity-gradient tensor eigenvalue ~ 1/L... simpler:
    # normalise rms(|grad phi|) to amp * L
    gy, gx = np.gradient(phi, L / N)
    s = np.sqrt((gx ** 2 + gy ** 2).mean())
    phi *= amp * L / s
    return phi


def tile_field(phi, margin, L=1.0):
    """periodic extension by `margin` cells on every side. Returns (q (M,2), psi_base (M,), inside mask)."""
    N = phi.shape[0]
    idx = np.arange(-margin, N + margin)
    P = phi[np.ix_(idx % N, idx % N)]
    qx = idx * (L / N)
    QX, QY = np.meshgrid(qx, qx, indexing='ij')
    inside = (QX >= 0) & (QX < L) & (QY >= 0) & (QY < L)
    return np.stack([QX.ravel(), QY.ravel()], 1), P.ravel(), inside.ravel()


def lower_hull(q, phi, t):
    """lower convex hull of (q, psi_t(q)). Returns dict with facet vertex indices, Eulerian x, mass, and the
    set of free (vertex) particles."""
    psi = (q[:, 0] ** 2 + q[:, 1] ** 2) / (2 * t) - phi
    pts = np.column_stack([q, psi])
    t0 = time.time()
    hull = ConvexHull(pts, qhull_options='Qt')   # triangulated output
    eq = hull.equations              # (F,4): n_x, n_y, n_z, d ; n.p + d = 0
    low = eq[:, 2] < 0
    simp = hull.simplices[low]
    nz = eq[low, 2]
    g = -eq[low, :2] / nz[:, None]   # gradient of z = -(n_x x + n_y y + d)/n_z
    x = t * g
    a, b, c = q[simp[:, 0]], q[simp[:, 1]], q[simp[:, 2]]
    area = 0.5 * np.abs((b[:, 0] - a[:, 0]) * (c[:, 1] - a[:, 1]) - (c[:, 0] - a[:, 0]) * (b[:, 1] - a[:, 1]))
    free = np.zeros(len(q), bool)
    free[np.unique(simp)] = True
    return dict(simplices=simp, x=x, mass=area, free=free, secs=time.time() - t0, nfacets=int(low.sum()))


if __name__ == '__main__':
    import sys
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 256
    phi = gaussian_potential(N, seed=1, n_index=-1.0, k_cut=N / 6, amp=0.08)
    q, P, inside = tile_field(phi, margin=N // 8)
    print('points', len(q))
    for t in [0.2, 0.5, 1.0, 2.0]:
        h = lower_hull(q, P, t)
        cell = (1.0 / N) ** 2
        m = h['mass'] / cell
        big = m > 3
        print(f"t={t}: hull {h['secs']:.1f}s facets {h['nfacets']} free {h['free'][inside].mean():.3f} "
              f"mass in facets>3 cells {m[big].sum() / m.sum():.3f}  max facet {m.max():.0f} cells  n(>3)={big.sum()}")
