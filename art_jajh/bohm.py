"""bohm.py — exact Bohmian (de Broglie–Bohm) trajectories for a free superposition of Gaussian
packets in one dimension (ħ = m = 1).  The two-slit picture of Philippidis–Dewdney–Hiley is
this problem: psi(x, t) = sum_j w_j G(x - x_j, t), the transverse coordinate x across, time t up.

G(x, t) ∝ c(t)^{-1/2} exp(-x² / (4 σ² c(t))),  c(t) = 1 + i t / (2σ²)
v(x, t) = Im(∂x psi / psi)            (the guidance equation, dx/dt = v)

Equivariance theorem: if the initial positions are distributed as |psi(x,0)|², the positions at
time t are distributed as |psi(x,t)|² — the fringes appear in the crowd, never in one path.
No-crossing theorem: trajectories are integral curves of a smooth velocity field in the (x,t) plane,
so two trajectories never cross; by symmetry a path starting at x<0 stays at x<0 forever.
"""
import numpy as np


class TwoSlit:
    def __init__(self, centers=(-25.0, 25.0), weights=(1.0, 1.0), sigma=1.0, phases=(0.0, 0.0)):
        self.xj = np.asarray(centers, float)
        self.wj = np.asarray(weights, complex) * np.exp(1j * np.asarray(phases, float))
        self.s = float(sigma)

    def _terms(self, x, t):
        c = 1 + 1j * t / (2 * self.s ** 2)
        dx = x[..., None] - self.xj                        # (..., J)
        e = -(dx ** 2) / (4 * self.s ** 2 * c)             # complex exponents
        er = e.real
        m = er.max(axis=-1, keepdims=True)                 # log-sum-exp guard
        T = self.wj * np.exp(e - m)
        return T, dx, c

    def velocity(self, x, t):
        x = np.asarray(x, float)
        T, dx, c = self._terms(x, t)
        psi = T.sum(axis=-1)
        dpsi = (T * (-dx / (2 * self.s ** 2 * c))).sum(axis=-1)
        return np.imag(dpsi / psi)

    def density(self, x, t):
        """|psi|² up to the time-dependent normalisation (use for shape; normalise numerically)"""
        x = np.asarray(x, float)
        c = 1 + 1j * t / (2 * self.s ** 2)
        dx = x[..., None] - self.xj
        e = -(dx ** 2) / (4 * self.s ** 2 * c)
        psi = (self.wj * np.exp(e)).sum(axis=-1) / np.sqrt(c)
        return np.abs(psi) ** 2

    def quantum_potential(self, x, t, h=1e-3):
        """Q = -(1/2) R''/R with R = |psi|, by central differences"""
        x = np.asarray(x, float)
        R = np.sqrt(self.density(np.stack([x - h, x, x + h], -1), t))
        return -0.5 * (R[..., 0] - 2 * R[..., 1] + R[..., 2]) / (h * h) / R[..., 1]

    def sample_initial(self, n, kind='quantile', rng=None):
        """n starting points distributed as |psi(x,0)|² (no overlap at t=0 for well-separated slits):
        equal weight per slit, Gaussian of std sigma (|G|² has std sigma)."""
        J = len(self.xj)
        p = np.abs(self.wj) ** 2; p = p / p.sum()
        counts = np.round(p * n).astype(int)
        counts[-1] = n - counts[:-1].sum()
        xs = []
        for j in range(J):
            k = counts[j]
            if kind == 'quantile':
                from scipy.special import erfinv
                u = (np.arange(k) + 0.5) / k
                z = np.sqrt(2) * erfinv(2 * u - 1)
            else:
                z = (rng or np.random.default_rng(0)).standard_normal(k)
            xs.append(self.xj[j] + self.s * z)
        return np.concatenate(xs), np.repeat(np.arange(J), counts)

    def integrate(self, x0, T, nsteps, record_every=1):
        """RK4 in time for all trajectories at once.  Returns times, positions (n, m), speeds (n, m)."""
        x = np.asarray(x0, float).copy()
        dt = T / nsteps
        nrec = nsteps // record_every + 1
        X = np.empty((len(x), nrec)); V = np.empty_like(X); tt = np.empty(nrec)
        X[:, 0] = x; V[:, 0] = self.velocity(x, 0.0); tt[0] = 0.0
        r = 1
        for k in range(nsteps):
            t = k * dt
            k1 = self.velocity(x, t)
            k2 = self.velocity(x + 0.5 * dt * k1, t + 0.5 * dt)
            k3 = self.velocity(x + 0.5 * dt * k2, t + 0.5 * dt)
            k4 = self.velocity(x + dt * k3, t + dt)
            x = x + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
            if (k + 1) % record_every == 0:
                X[:, r] = x; V[:, r] = self.velocity(x, t + dt); tt[r] = t + dt; r += 1
        return tt[:r], X[:, :r], V[:, :r]


if __name__ == '__main__':
    import time
    S = TwoSlit()
    x0, slit = S.sample_initial(2000)
    t0 = time.time()
    tt, X, V = S.integrate(x0, 200.0, 4000, record_every=10)
    print('2000 paths, 4000 RK4 steps: %.1fs' % (time.time() - t0))
    # no-crossing certificate: order preserved
    order_ok = bool(np.all(np.diff(X, axis=0) > 0))
    print('order preserved along all times:', order_ok)
    # equivariance certificate at T: histogram vs |psi|²
    xf = X[:, -1]
    grid = np.linspace(xf.min() - 5, xf.max() + 5, 4001)
    rho = S.density(grid, 200.0); rho /= np.trapezoid(rho, grid)
    h, e = np.histogram(xf, bins=60, density=True)
    xc = 0.5 * (e[1:] + e[:-1])
    rc = np.interp(xc, grid, rho)
    print('equivariance: max |hist - rho| / max rho = %.3f' % (np.abs(h - rc).max() / rc.max()))
    print('final spread', xf.min(), xf.max(), 'fringe spacing pi*T/a =', np.pi * 200 / 25)


def quantile_paths(S, u, times, ngrid=60001, pad=6.0):
    """EXACT 1-D Bohmian trajectories via equivariance + no-crossing: the path with probability
    quantile u satisfies  F_t(x(t)) = u  where F_t is the CDF of |psi(·, t)|².  Returns X (len(u), len(times)).
    (Order-preserving by construction; velocity can be evaluated analytically afterwards.)"""
    u = np.asarray(u, float); X = np.empty((len(u), len(times)))
    for j, t in enumerate(times):
        s_t = S.s * np.sqrt(1 + (t / (2 * S.s ** 2)) ** 2)
        lo = S.xj.min() - pad * s_t; hi = S.xj.max() + pad * s_t
        g = np.linspace(lo, hi, ngrid)
        rho = S.density(g, t)
        cdf = np.concatenate([[0.0], np.cumsum(0.5 * (rho[1:] + rho[:-1]) * (g[1] - g[0]))])
        cdf /= cdf[-1]
        # strictly increasing for interp: drop flat stretches
        keep = np.concatenate([[True], np.diff(cdf) > 0])
        X[:, j] = np.interp(u, cdf[keep], g[keep])
    return X
