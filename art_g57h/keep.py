"""keep.py — THE CHEAPEST WAY TO STAY: Brownian motion kept inside the unit disc by the L^2-cheapest force.

MO 511767 asks for the cheapest control K that keeps X = W + K in a ball up to time T.
For the quadratic cost E ∫ ½|u|² dt (u = dK/dt) the answer is classical (Hopf–Cole / Doob):
    u(t, x) = ∇ log φ(T − t, x),   φ(τ, x) = P_x( W stays in the disc for time τ ),
and the optimal cost from x0 is exactly −log φ(T, x0)  (Girsanov: the h-transform pays the
log of the probability it buys).  In the unit disc,
    φ(τ, r) = Σ_k a_k J0(j_k r) e^{−j_k² τ / 2},   a_k = 2 / (j_k J1(j_k)),  j_k = zeros of J0.
So the force is radial, grows like 1/(1−r) at the rim, and RELAXES as the deadline nears.

This module tabulates the log-gradient on a (τ, r) grid and integrates paths by Euler–Maruyama,
recording position, time and force along each path.  Certificate: mean sampled cost vs −log φ(T,0);
and occupation density vs the ground state J0(j_1 r)² for long horizons.
"""
import numpy as np
from scipy.special import jn_zeros, j0, j1


class DiscKeeper:
    def __init__(self, T, K=120, nr=4000, ntau=600, tau_min=2e-4):
        self.T = T
        j = jn_zeros(0, K)
        a = 2.0 / (j * j1(j))
        self.j, self.a = j, a
        self.r = np.linspace(0, 1 - 1e-6, nr)
        self.tau = np.geomspace(tau_min, T, ntau)
        J0 = j0(np.outer(j, self.r))            # (K, nr)
        J1 = j1(np.outer(j, self.r))
        E = np.exp(-np.outer(j ** 2 / 2, self.tau))  # (K, ntau)
        phi = (a[:, None, None] * J0[:, :, None] * E[:, None, :]).sum(0)         # (nr, ntau)
        dphi = (a[:, None, None] * (-j[:, None, None]) * J1[:, :, None] * E[:, None, :]).sum(0)
        phi = np.clip(phi, 1e-300, None)
        self.phi = phi
        self.g = dphi / phi                       # radial log-gradient (<= 0)
        # near the rim for tiny tau the series is not converged: patch with the half-line formula
        # phi ≈ erf((1-r)/sqrt(2 tau))  ->  g ≈ -sqrt(2/(pi tau)) exp(-(1-r)^2/(2tau)) / erf(...)
        from scipy.special import erf
        d = (1 - self.r)[:, None]; tt = self.tau[None, :]
        z = d / np.sqrt(2 * tt)
        g1 = -np.sqrt(2 / (np.pi * tt)) * np.exp(-z ** 2) / np.clip(erf(z), 1e-300, None)
        bad = (tt < 0.02) & (d < 6 * np.sqrt(tt))
        self.g = np.where(bad, g1, self.g)
        self.g = np.minimum(self.g, 0.0)
        self.logtau = np.log(self.tau)

    def force(self, tau, r):
        """bilinear lookup of the radial log-gradient (negative = inward)"""
        tau = np.clip(tau, self.tau[0], self.tau[-1])
        r = np.clip(r, 0, self.r[-1])
        ft = (np.log(tau) - self.logtau[0]) / (self.logtau[-1] - self.logtau[0]) * (len(self.tau) - 1)
        fr = r / self.r[-1] * (len(self.r) - 1)
        it = np.clip(np.floor(ft).astype(int), 0, len(self.tau) - 2); wt = ft - it
        ir = np.clip(np.floor(fr).astype(int), 0, len(self.r) - 2); wr = fr - ir
        g = self.g
        return ((1 - wt) * ((1 - wr) * g[ir, it] + wr * g[ir + 1, it]) +
                wt * ((1 - wr) * g[ir, it + 1] + wr * g[ir + 1, it + 1]))

    def survival(self, tau, r=0.0):
        return float((self.a * j0(self.j * r) * np.exp(-self.j ** 2 * tau / 2)).sum())

    def run(self, n, dt, seed=0, x0=(0.0, 0.0), record_every=10):
        """n paths from x0 up to T.  Returns pts (n, m, 2), times (m,), force magnitudes (n, m), costs (n,)"""
        rng = np.random.default_rng(seed)
        steps = int(round(self.T / dt))
        x = np.tile(np.asarray(x0, np.float64), (n, 1))
        m = steps // record_every + 2
        pts = np.zeros((n, m, 2), np.float32); fm = np.zeros((n, m), np.float32); tim = np.zeros(m, np.float32)
        cost = np.zeros(n); maxf = np.zeros(n); k = 0
        sq = np.sqrt(dt)
        for s in range(steps):
            t = s * dt; tau = self.T - t
            r = np.hypot(x[:, 0], x[:, 1])
            g = self.force(np.full(n, tau), r)          # radial, <= 0
            u = (g / np.clip(r, 1e-9, None))[:, None] * x    # vector force
            if s % record_every == 0:
                pts[:, k] = x; fm[:, k] = -g; tim[k] = t; k += 1
            cost += 0.5 * (g ** 2) * dt
            maxf = np.maximum(maxf, -g)
            x = x + u * dt + sq * rng.standard_normal((n, 2))
            rr = np.hypot(x[:, 0], x[:, 1])
            out = rr >= 1.0
            if out.any():  # discretisation leak: reflect (the continuous process never exits)
                x[out] *= ((2 - rr[out]) / rr[out])[:, None] * 0.999
        pts[:, k] = x; fm[:, k] = 0; tim[k] = self.T
        return pts[:, :k + 1], tim[:k + 1], fm[:, :k + 1], cost, maxf


if __name__ == '__main__':
    import sys, time
    T = float(sys.argv[1]) if len(sys.argv) > 1 else 3.0
    t0 = time.time()
    D = DiscKeeper(T)
    print('table', D.g.shape, 'in %.1fs' % (time.time() - t0))
    print('phi(T,0) =', D.survival(T), ' -log =', -np.log(D.survival(T)))
    pts, tim, fm, cost, maxf = D.run(200, 2e-4, seed=1)
    print('paths', pts.shape, 'mean cost', cost.mean(), '+-', cost.std() / np.sqrt(len(cost)),
          'max force median', np.median(maxf), 'in %.1fs' % (time.time() - t0))
    r = np.hypot(pts[..., 0], pts[..., 1]).ravel()
    h, e = np.histogram(r, bins=20, range=(0, 1))
    dens = h / (np.pi * (e[1:] ** 2 - e[:-1] ** 2)) / len(r)
    rc = 0.5 * (e[1:] + e[:-1]); gs = j0(D.j[0] * rc) ** 2; gs /= (gs * (e[1:] ** 2 - e[:-1] ** 2) * np.pi).sum()
    for a, b, c in zip(rc, dens, gs):
        print('r=%.3f occ=%.3f J0^2=%.3f' % (a, b, c))


class Keeper1D:
    """Brownian motion kept in [-1, 1] up to time T by the L^2-cheapest force u = d/dx log phi(T-t, x),
    phi(tau, x) = sum_k (4/((2k+1) pi)) (-1)^k cos((2k+1) pi x / 2) exp(-(2k+1)^2 pi^2 tau / 8)."""

    def __init__(self, T, K=400, nx=4001, ntau=800, tau_min=1e-4):
        self.T = T
        k = np.arange(K); lam = (2 * k + 1) * np.pi / 2
        a = 4 / ((2 * k + 1) * np.pi) * (-1.0) ** k
        self.xmax = 1 - 1e-4                      # the wall node itself (phi = 0, g = inf) is never tabulated
        self.x = np.linspace(-self.xmax, self.xmax, nx)
        self.tau = np.geomspace(tau_min, T, ntau)
        C = np.cos(np.outer(lam, self.x)); S = np.sin(np.outer(lam, self.x))
        E = np.exp(-np.outer(lam ** 2 / 2, self.tau))
        phi = (a[:, None, None] * C[:, :, None] * E[:, None, :]).sum(0)
        dphi = (a[:, None, None] * (-lam[:, None, None]) * S[:, :, None] * E[:, None, :]).sum(0)
        phi = np.clip(phi, 1e-300, None)
        g = dphi / phi
        # physical asymptote near a wall: phi ∝ (1 - |x|)  =>  |g| ≈ 1/(1-|x|); clamp the table there
        cap = 1.5 / (1 - np.abs(self.x) + 1e-9)
        self.g = np.sign(g) * np.minimum(np.abs(g), cap[:, None])
        self.phi = phi
        self.lam, self.a = lam, a
        self.logtau = np.log(self.tau)

    def force(self, tau, x):
        tau = np.clip(tau, self.tau[0], self.tau[-1]); x = np.clip(x, -self.xmax, self.xmax)
        ft = (np.log(tau) - self.logtau[0]) / (self.logtau[-1] - self.logtau[0]) * (len(self.tau) - 1)
        fx = (x + self.xmax) / (2 * self.xmax) * (len(self.x) - 1)
        it = np.clip(np.floor(ft).astype(int), 0, len(self.tau) - 2); wt = ft - it
        ix = np.clip(np.floor(fx).astype(int), 0, len(self.x) - 2); wx = fx - ix
        g = self.g
        return ((1 - wt) * ((1 - wx) * g[ix, it] + wx * g[ix + 1, it]) +
                wt * ((1 - wx) * g[ix, it + 1] + wx * g[ix + 1, it + 1]))

    def survival(self, tau, x=0.0):
        return float((self.a * np.cos(self.lam * x) * np.exp(-self.lam ** 2 * tau / 2)).sum())

    def run(self, n, dt, seed=0, x0=0.0, record_every=10):
        rng = np.random.default_rng(seed)
        steps = int(round(self.T / dt))
        x = np.full(n, float(x0))
        m = steps // record_every + 2
        xs = np.zeros((n, m), np.float32); fs = np.zeros((n, m), np.float32); tim = np.zeros(m, np.float32)
        cost = np.zeros(n); maxf = np.zeros(n); k = 0
        sq = np.sqrt(dt)
        SUB = 16; sqs = np.sqrt(dt / SUB)
        for s in range(steps):
            t = s * dt; tau = self.T - t
            u = self.force(np.full(n, tau), x)
            if s % record_every == 0:
                xs[:, k] = x; fs[:, k] = u; tim[k] = t; k += 1
            maxf = np.maximum(maxf, np.abs(u))
            near = np.abs(x) > 0.85
            far = ~near
            # far from the walls: one Euler step
            cost[far] += 0.5 * u[far] ** 2 * dt
            x[far] = x[far] + u[far] * dt + sq * rng.standard_normal(far.sum())
            # near a wall: SUB substeps with the force re-evaluated (the force is ~1/(1-|x|))
            if near.any():
                xn = x[near]; cn = np.zeros(xn.shape)
                for j in range(SUB):
                    un = self.force(np.full(len(xn), tau - j * dt / SUB), xn)
                    cn += 0.5 * un ** 2 * (dt / SUB)
                    xn = xn + un * (dt / SUB) + sqs * rng.standard_normal(len(xn))
                    out = np.abs(xn) >= 1.0
                    if out.any():
                        xn[out] = np.sign(xn[out]) * (2 - np.abs(xn[out])) * 0.999
                x[near] = xn; cost[near] += cn
        xs[:, k] = x; fs[:, k] = 0; tim[k] = self.T
        return xs[:, :k + 1], tim[:k + 1], fs[:, :k + 1], cost, maxf
