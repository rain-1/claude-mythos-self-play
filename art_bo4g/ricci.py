"""ricci.py — rotationally symmetric Ricci flow on S^3 (Angenent–Knopf neckpinch) with surgery.

Metric on [0, L] x S^2 in ARCLENGTH gauge:  g = ds^2 + psi(s,t)^2 g_{S^2}   (n = 2 fibre dimension).
Ricci flow (Angenent–Knopf 2004, eq. for the warping function):
    psi_t = psi_ss - (n-1)(1 - psi_s^2)/psi,
and the arclength itself moves: a point at arclength s from the left pole drifts with speed
    V(s) = n * int_0^s (psi_ss / psi) ds'          (from  phi_t = n phi psi_ss/psi).
Each step: explicit Euler for psi, move the nodes by dt*V, re-interpolate on a uniform grid of
the new length L' = L + dt*V(L).  Poles: psi = 0, psi_s = ±1, and the regular limit of the
right-hand side at a pole is n*psi_ss (psi = s - K s^3/6 + ...), which is what the node next to
each pole uses.  |psi_s| <= 1 is preserved (max principle), so the metric always embeds in R^4
as a hypersurface of revolution with profile curve (z(s), psi(s)),  dz/ds = sqrt(1 - psi_s^2).

Surgery (Hamilton–Perelman, cartoon version): when the neck radius < eps, cut where psi = h_cut
on both sides of the minimum and glue a spherical cap to each side; the children flow on until
each rounds off and dies at a point (finite extinction).
"""
import numpy as np

N_FIB = 2  # fibre sphere S^2  ->  ambient S^3
POLE_FIT = 8  # nodes used for the pole curvature fit


def dumbbell(theta, a, w):
    """profile of a unit sphere squeezed at its equator: z = -cos(th), r = sin(th)*(1 - a*exp(-(z/w)^2))"""
    z = -np.cos(theta)
    r = np.sin(theta) * (1 - a * np.exp(-(z / w) ** 2))
    return z, r


def resample(s, psi, N):
    """uniform grid of N+1 nodes on [0, s[-1]], poles pinned to 0"""
    L = s[-1]
    sn = np.linspace(0.0, L, N + 1)
    p = np.interp(sn, s, psi)
    p[0] = 0.0
    p[-1] = 0.0
    return sn, p


class Profile:
    def __init__(self, psi, L, t=0.0, name='S'):
        self.psi = np.asarray(psi, np.float64).copy()
        self.N = len(self.psi) - 1
        self.L = float(L)
        self.t = t
        self.name = name
        self.psi[0] = 0.0
        self.psi[-1] = 0.0

    @classmethod
    def from_curve(cls, z, r, N, name='S'):
        seg = np.hypot(np.diff(z), np.diff(r))
        s = np.concatenate([[0.0], np.cumsum(seg)])
        sn, p = resample(s, r, N)
        return cls(p, s[-1], name=name)

    @property
    def ds(self):
        return self.L / self.N

    def s(self):
        return np.linspace(0.0, self.L, self.N + 1)

    def derivs(self):
        """psi_s and psi_ss at nodes, using the odd extension through the poles"""
        ds = self.ds
        p = np.concatenate([[-self.psi[1]], self.psi, [-self.psi[-2]]])
        ps = (p[2:] - p[:-2]) / (2 * ds)
        pss = (p[2:] - 2 * p[1:-1] + p[:-2]) / (ds * ds)
        return ps, pss

    def embed(self):
        ps, _ = self.derivs()
        d = np.clip(ps, -1, 1)
        dz = np.sqrt(np.clip(1 - d * d, 0, None))
        z = np.concatenate([[0.0], np.cumsum(0.5 * (dz[1:] + dz[:-1]) * self.ds)])
        return z, self.psi.copy(), self.s()

    def rmin(self):
        """neck radius: smallest INTERIOR local minimum of psi"""
        p = self.psi
        loc = np.where((p[1:-1] < p[:-2]) & (p[1:-1] <= p[2:]))[0] + 1
        if len(loc) == 0:
            return np.inf
        return p[loc].min()

    def rmax(self):
        return self.psi.max()

    def drift(self):
        """arclength drift V(s) = n * int_0^s psi_ss/psi from the current profile"""
        ps, pss = self.derivs()
        q = np.zeros_like(self.psi)
        q[1:-1] = pss[1:-1] / np.maximum(self.psi[1:-1], 1e-12)
        # at the poles psi_ss/psi -> -K, the curvature of the profile; the raw stencil amplifies a node-1 error
        # by 1/ds^2 (unstable), so fit psi = s - K s^3/6 over the first POLE_FIT nodes (linear least squares)
        m = POLE_FIT
        sg = np.arange(1, m + 1) * self.ds
        for side in (0, 1):
            p = self.psi[1:m + 1] if side == 0 else self.psi[-2:-m - 2:-1]
            K = -6.0 * np.sum((p - sg) * sg ** 3) / np.sum(sg ** 6)
            if side == 0:
                q[:m // 2 + 1] = -K
            else:
                q[-(m // 2 + 1):] = -K
        return N_FIB * np.concatenate([[0.0], np.cumsum(0.5 * (q[1:] + q[:-1]) * self.ds)])

    def cfl_dt(self, lam=0.4, dt_max=2e-4):
        """u = psi^2 obeys u_t = u_ss - 2 (n = 2): explicit Euler needs dt <= 0.5 ds^2; the drift dt|V| < ds/2"""
        V = np.abs(self.drift()).max()
        return min(dt_max, lam * self.ds ** 2, 0.5 * self.ds / max(V, 1e-9))

    def step(self, dt):
        """u = psi^2:  u_t = u_ss - 2  (explicit Euler, u = 0 at the poles), then the arclength drift
        V(s) = n * int_0^s psi_ss/psi and a resampling of psi = sqrt(u) (linear near the poles, so exact there)."""
        n = N_FIB
        assert n == 2
        psi = self.psi
        ds = self.ds
        u = psi * psi
        u_ext = np.concatenate([[u[1]], u, [u[-2]]])       # even extension of u through the poles
        uss = (u_ext[2:] - 2 * u_ext[1:-1] + u_ext[:-2]) / (ds * ds)
        u_new = u + dt * (uss - 2.0)
        u_new[0] = 0.0
        u_new[-1] = 0.0
        p_new = np.sqrt(np.clip(u_new, 0.0, None))
        self.psi = p_new
        V = self.drift()
        s_new = self.s() + dt * V
        s_new = np.maximum.accumulate(s_new)
        sn, p = resample(s_new, p_new, self.N)
        self.psi = p
        self.L = float(s_new[-1])
        self.t += dt
        return dt

    # ---- surgery ------------------------------------------------------------------
    def split(self, h_cut, N_child):
        psi = self.psi
        # interior local minima; take the deepest
        loc = np.where((psi[1:-1] < psi[:-2]) & (psi[1:-1] <= psi[2:]))[0] + 1
        imin = loc[np.argmin(psi[loc])]
        i_l = imin
        while i_l > 0 and psi[i_l] < h_cut:
            i_l -= 1
        i_r = imin
        while i_r < len(psi) - 1 and psi[i_r] < h_cut:
            i_r += 1
        left = self._child(0, i_l, side='right', name=self.name + 'L', N=N_child)
        right = self._child(i_r, len(psi) - 1, side='left', name=self.name + 'R', N=N_child)
        return left, right, (i_l, i_r, imin)

    def _child(self, i0, i1, side, name, N):
        s = self.s()[i0:i1 + 1] - self.s()[i0]
        psi = self.psi[i0:i1 + 1].copy()
        if side == 'left':
            psi = psi[::-1]
            s = (s[-1] - s)[::-1]
        # the cut end is now on the right: psi[-1] = h; glue a spherical cap of radius h
        h = psi[-1]
        cap_s = np.linspace(0, np.pi / 2 * h, 60)[1:]
        cap_psi = h * np.cos(cap_s / h)
        s_all = np.concatenate([s, s[-1] + cap_s])
        psi_all = np.concatenate([psi, cap_psi])
        psi_all[-1] = 0.0
        sn, p = resample(s_all, psi_all, N)
        # smooth the glue point a little (poles pinned)
        for _ in range(3):
            p[1:-1] = 0.25 * p[:-2] + 0.5 * p[1:-1] + 0.25 * p[2:]
        p[0] = 0.0
        p[-1] = 0.0
        if side == 'left':
            p = p[::-1]
        return Profile(p, s_all[-1], t=self.t, name=name)


def run_flow(a=0.8, w=0.35, N=1600, eps=0.02, h_cut=None, t_max=3.0, log_every=None, record_dt=0.005,
             cap_grow=4.0, verbose=True, N_child=None):
    th = np.linspace(0, np.pi, 4 * N + 1)
    z, r = dumbbell(th, a, w)
    P = Profile.from_curve(z, r, N, name='S')
    bodies = [P]
    rec = []
    cert = dict(a=a, w=w, N=N, eps=eps, neck=[], events=[], radius={})
    t_next = 0.0
    steps = 0
    t = 0.0
    while bodies and t < t_max:
        if t >= t_next - 1e-12:
            rec.append((t, [(b.name,) + b.embed() for b in bodies]))
            t_next += record_dt
        dt = min(b.cfl_dt() for b in bodies)
        dt = min(dt, max(t_next - t, 1e-9))
        new_bodies = []
        for b in bodies:
            b.step(dt)
            rmin, rmax = b.rmin(), b.rmax()
            if b.name == 'S':
                cert['neck'].append((b.t, float(rmin) if np.isfinite(rmin) else float(rmax)))
            cert['radius'].setdefault(b.name, []).append((b.t, float(rmax), float(b.L)))
            if rmax < eps:
                cert['events'].append(('extinct', b.name, float(b.t), float(rmax)))
                if verbose:
                    print(f'  {b.name} extinct at t={b.t:.5f}')
                continue
            if np.isfinite(rmin) and rmin < eps and rmax > cap_grow * rmin:
                hc = h_cut or 2.5 * eps
                L_, R_, idx = b.split(hc, N_child or N)
                cert['events'].append(('surgery', b.name, float(b.t), float(rmin)))
                if verbose:
                    print(f'  surgery on {b.name} at t={b.t:.5f}, rmin={rmin:.4f}, cut idx {idx}, '
                          f'children L={L_.L:.3f},{R_.L:.3f}')
                new_bodies += [L_, R_]
            else:
                new_bodies.append(b)
        bodies = new_bodies
        t += dt
        steps += 1
        if verbose and log_every and steps % log_every == 0:
            print(f't={t:.4f} bodies={[b.name for b in bodies]} rmin={[round(float(b.rmin()),4) for b in bodies]} '
                  f'rmax={[round(b.rmax(),4) for b in bodies]} L={[round(b.L,3) for b in bodies]} dt={dt:.2e}')
    # thin the certificate lists
    cert['neck'] = cert['neck'][::max(1, len(cert['neck']) // 4000)]
    for k in cert['radius']:
        cert['radius'][k] = cert['radius'][k][::max(1, len(cert['radius'][k]) // 4000)]
    return rec, cert


if __name__ == '__main__':
    import sys, time
    a = float(sys.argv[1]) if len(sys.argv) > 1 else 0.8
    N = int(sys.argv[2]) if len(sys.argv) > 2 else 800
    t0 = time.time()
    rec, cert = run_flow(a=a, N=N, log_every=5000)
    print('events', cert['events'], 'time %.1f s' % (time.time() - t0))
