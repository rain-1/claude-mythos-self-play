"""stealthy.py — stealthy hyperuniform point patterns by collective-coordinate optimisation
(Uche–Stillinger–Torquato 2004; Zhang–Stillinger–Torquato 2015).

N points in a periodic box Lx × Ly (unit number density).  Minimise
    Φ(r) = Σ_{k ∈ K⁺} |ρ(k)|²,   ρ(k) = Σ_j exp(i k·r_j),   K⁺ = half of {k ≠ 0 : |k| < K}
to Φ = 0 (a ground state): the structure factor S(k) = |ρ(k)|²/N vanishes for every |k| < K —
the pattern has NO density fluctuations at wavelengths longer than 2π/K.  χ = |K⁺| / (2N) is the
fraction of degrees of freedom constrained; χ ≲ 0.5 gives disordered ground states in 2-D.
Certificates: Φ/N at the end; number variance σ²(R) in windows of radius R (∝ R for hyperuniform, ∝ R²
for Poisson); S(k) on a grid.
"""
import numpy as np
from scipy.optimize import minimize
from scipy.spatial import cKDTree


class Stealthy:
    def __init__(self, N, aspect=1.0, chi=0.4, seed=0):
        self.N = N
        self.Ly = np.sqrt(N / aspect); self.Lx = aspect * self.Ly
        self.box = np.array([self.Lx, self.Ly])
        # k-lattice: k = 2π (m/Lx, n/Ly); choose K so that |K⁺| ≈ 2 χ N
        M_target = int(round(2 * chi * N))
        nmax = 60
        m, n = np.meshgrid(np.arange(-nmax, nmax + 1), np.arange(-nmax, nmax + 1), indexing='ij')
        kx = 2 * np.pi * m / self.Lx; ky = 2 * np.pi * n / self.Ly
        k2 = kx ** 2 + ky ** 2
        half = (kx > 0) | ((kx == 0) & (ky > 0))
        order = np.argsort(k2[half])
        kxs, kys, k2s = kx[half][order], ky[half][order], k2[half][order]
        # take the M_target smallest, then complete the shell (same |k|) for isotropy
        Kcut2 = k2s[M_target - 1]
        sel = k2s <= Kcut2 + 1e-9
        self.kx, self.ky = kxs[sel], kys[sel]
        self.K = np.sqrt(Kcut2); self.M = int(sel.sum()); self.chi = self.M / (2 * N)
        rng = np.random.default_rng(seed)
        self.r0 = rng.uniform(0, 1, (N, 2)) * self.box

    def rho(self, r):
        ph = np.outer(r[:, 0], self.kx) + np.outer(r[:, 1], self.ky)      # (N, M)
        E = np.exp(1j * ph)
        return E.sum(axis=0), E

    def phi_grad(self, x):
        r = x.reshape(-1, 2)
        rho, E = self.rho(r)
        phi = float((np.abs(rho) ** 2).sum())
        # d|ρ|²/dr_j = -2 k Im(conj(ρ) e^{i k·r_j})
        w = np.imag(np.conj(rho)[None, :] * E)                                 # (N, M)
        gx = -2 * (w * self.kx[None, :]).sum(axis=1)
        gy = -2 * (w * self.ky[None, :]).sum(axis=1)
        return phi, np.stack([gx, gy], 1).ravel()

    def optimise(self, maxiter=3000, tol=1e-10, verbose=True):
        x0 = self.r0.ravel().copy()
        it = [0]
        def cb(xk):
            it[0] += 1
            if verbose and it[0] % 100 == 0:
                print('  iter', it[0], 'phi/N = %.3e' % (self.phi_grad(xk)[0] / self.N), flush=True)
        res = minimize(self.phi_grad, x0, jac=True, method='L-BFGS-B', callback=cb,
                       options=dict(maxiter=maxiter, maxfun=maxiter * 2, ftol=0, gtol=tol, maxcor=30))
        r = np.mod(res.x.reshape(-1, 2), self.box)
        self.r = r; self.phi_final = res.fun
        return r, res.fun / self.N, res.nit

    # ---- certificates ----
    def structure_factor_grid(self, r, kmax_factor=3.0, nk=121):
        """S(k) = |ρ(k)|²/N on a square grid of lattice wavevectors out to kmax_factor·K"""
        kmax = kmax_factor * self.K
        mmax = int(np.ceil(kmax * self.Lx / (2 * np.pi))); nmax = int(np.ceil(kmax * self.Ly / (2 * np.pi)))
        m = np.arange(-mmax, mmax + 1); n = np.arange(-nmax, nmax + 1)
        kx = 2 * np.pi * m / self.Lx; ky = 2 * np.pi * n / self.Ly
        S = np.empty((len(n), len(m)))
        for i, kyy in enumerate(ky):
            ph = np.outer(r[:, 0], kx) + kyy * r[:, 1][:, None]
            S[i] = np.abs(np.exp(1j * ph).sum(axis=0)) ** 2 / self.N
        S[len(n) // 2, len(m) // 2] = 0.0
        return kx, ky, S

    def number_variance(self, r, radii, nwin=4000, seed=1):
        tree = cKDTree(r, boxsize=self.box)
        rng = np.random.default_rng(seed)
        out = []
        for R in radii:
            c = rng.uniform(0, 1, (nwin, 2)) * self.box
            counts = np.array([len(x) for x in tree.query_ball_point(c, R)])
            out.append((float(counts.mean()), float(counts.var())))
        return np.array(out)


def poisson(N, box, seed=5):
    rng = np.random.default_rng(seed)
    return rng.uniform(0, 1, (N, 2)) * np.asarray(box)


if __name__ == '__main__':
    import time
    st = Stealthy(1500, aspect=1.0, chi=0.4, seed=0)
    print('N', st.N, 'M', st.M, 'chi', round(st.chi, 4), 'K', round(st.K, 4))
    t0 = time.time()
    r, phiN, nit = st.optimise(maxiter=1500)
    print('optimised in %.0fs, %d iterations, phi/N = %.3e' % (time.time() - t0, nit, phiN))
    radii = np.array([1, 2, 3, 4, 6, 8])
    nv = st.number_variance(r, radii); nvp = st.number_variance(poisson(st.N, st.box), radii)
    for R, (m1, v1), (m2, v2) in zip(radii, nv, nvp):
        print(f'R={R}: mean {m1:.1f}  var stealthy {v1:.2f}  var poisson {v2:.2f}  (πR² = {np.pi*R*R:.1f})')
