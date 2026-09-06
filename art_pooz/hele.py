"""hele.py — zero-surface-tension Hele-Shaw flow with one sink/source, by the exact
Polubarinova–Galin equation for a polynomial conformal map.

Fluid occupies Ω(t) = f(D, t), f(ζ,t) = Σ_{k=1}^K a_k(t) ζ^k, f(0) = the sink.
Polubarinova–Galin (1945):  Re[ f_t(ζ) · conj(ζ f'(ζ)) ] = Q / (2π)   on |ζ| = 1,
Q < 0 suction, Q > 0 injection.  Polynomial maps stay polynomial (exact), the
Richardson moments M_m = (1/π)∫_Ω z^m dA (m ≥ 1) are conserved and the area
changes linearly: A(t) = A(0) + Q t.  Under suction the map loses univalence in
finite time: a zero of f' reaches the unit circle and the boundary forms a
cusp (Shraiman–Bensimon 1984 / Howison 1986) — the model ends there.
"""
import numpy as np
from numpy.polynomial import polynomial as P

def rhs_coeffs(a, Q):
    """a: complex array a_1..a_K.  Solve for a' (complex), with Im a_1' = 0 (rotation gauge).
    Equation: Re[ Σ_j a_j' ζ^j · Σ_k k conj(a_k) ζ^{-k} ] = Q/2π  for all |ζ|=1.
    Fourier mode m = j-k:  mode 0 real, modes m=1..K-1 complex, must vanish; mode 0 = Q/2π.
    Write a_j' = u_j + i v_j.  For each m≥0: Σ_{j-k=m} a_j' k conj(a_k) + conj(Σ_{k-j=m} a_j' k conj(a_k)) = 2 δ_{m0} Q/2π  ... derive numerically."""
    K = len(a)
    # real unknown vector x = [u_1..u_K, v_1..v_K]; build linear map by sampling on circle
    # F(θ) = Re[ f_t conj(ζ f') ] must equal Q/2π ; f_t = Σ a_j' ζ^j.  Linear in (u,v).
    # Use least squares on N = 4K points (exact: trig poly of degree K-1 → 2K-1 constraints).
    N = 8 * K
    th = 2 * np.pi * (np.arange(N) + 0.5) / N
    z = np.exp(1j * th)
    ks = np.arange(1, K + 1)
    zf = np.sum((ks * a)[None, :] * z[:, None] ** ks[None, :], axis=1)   # ζ f'(ζ)
    zj = z[:, None] ** ks[None, :]                                        # ζ^j
    M = np.conj(zf)[:, None] * zj                                          # coefficient of a_j'
    # Re[(u + i v) M] = u Re M - v Im M
    A = np.concatenate([M.real, -M.imag], axis=1)                          # N × 2K
    b = np.full(N, Q / (2 * np.pi))
    # gauge: v_1 = 0 -> drop column K (index of v_1)
    keep = [i for i in range(2 * K) if i != K]
    x, *_ = np.linalg.lstsq(A[:, keep], b, rcond=None)
    full = np.zeros(2 * K)
    full[keep] = x
    resid = np.abs(A @ full - b).max()
    return full[:K] + 1j * full[K:], resid

def fprime_roots(a):
    """zeros of f'(ζ) = Σ k a_k ζ^{k-1}"""
    ks = np.arange(1, len(a) + 1)
    c = ks * a                      # coefficients of ζ^{k-1}, ascending
    # strip trailing ~0
    while len(c) > 1 and abs(c[-1]) < 1e-14:
        c = c[:-1]
    if len(c) <= 1:
        return np.array([])
    return P.polyroots(c)

def area(a):
    ks = np.arange(1, len(a) + 1)
    return np.pi * np.sum(ks * np.abs(a) ** 2)

def moments(a, mmax, n=4096):
    """Richardson moments M_m = (1/π) ∫_Ω z^m dA = (1/(2πi)) ∮ z^m conj(z) dz, m=0..mmax, by quadrature"""
    th = 2 * np.pi * np.arange(n) / n
    z = np.exp(1j * th)
    ks = np.arange(1, len(a) + 1)
    f = np.sum(a[None, :] * z[:, None] ** ks[None, :], axis=1)
    df = np.sum((ks * a)[None, :] * z[:, None] ** ks[None, :], axis=1) * 1j   # df/dθ
    out = []
    for m in range(mmax + 1):
        out.append(np.sum(f ** m * np.conj(f) * df) * (2 * np.pi / n) / (2j * np.pi))
    return np.array(out)

def boundary(a, n=2048):
    th = 2 * np.pi * np.arange(n) / n
    z = np.exp(1j * th)
    ks = np.arange(1, len(a) + 1)
    return np.sum(a[None, :] * z[:, None] ** ks[None, :], axis=1)

def integrate(a0, Q, dt, tmax=None, stop_at_cusp=True, ghost=0.0, verbose=False):
    """RK4 in time.  Returns list of (t, a).  Stops when min|root of f'| reaches 1 (cusp),
    optionally continuing 'ghost' time units past it (non-univalent continuation)."""
    a = np.array(a0, complex)
    t = 0.0
    out = [(t, a.copy())]
    cusp_t = None
    resid_max = 0.0
    dt0 = dt
    while True:
        def F(aa):
            d, r = rhs_coeffs(aa, Q)
            return d, r
        # adaptive: shrink the step as a zero of f' approaches the unit circle (the ODE stiffens)
        rmin_now = np.min(np.abs(fprime_roots(a))) if len(a) > 1 else np.inf
        dt = dt0 * float(np.clip((rmin_now - 1.0) / 0.06, 0.02, 1.0)) if cusp_t is None else dt0
        k1, r1 = F(a); k2, r2 = F(a + 0.5 * dt * k1); k3, r3 = F(a + 0.5 * dt * k2); k4, r4 = F(a + dt * k3)
        resid_max = max(resid_max, r1, r2, r3, r4)
        a_new = a + dt * (k1 + 2 * k2 + 2 * k3 + k4) / 6
        t_new = t + dt
        rmin_new = np.min(np.abs(fprime_roots(a_new))) if len(a_new) > 1 else np.inf
        if cusp_t is None and rmin_new <= 1.0:
            # bisect for the cusp time
            lo, hi = a, a_new
            tlo, thi = t, t_new
            for _ in range(40):
                dtm = (thi - tlo) / 2
                k1, _ = F(lo); k2, _ = F(lo + 0.5 * dtm * k1); k3, _ = F(lo + 0.5 * dtm * k2); k4, _ = F(lo + dtm * k3)
                am = lo + dtm * (k1 + 2 * k2 + 2 * k3 + k4) / 6
                if np.min(np.abs(fprime_roots(am))) <= 1.0:
                    hi, thi = am, tlo + dtm
                else:
                    lo, tlo = am, tlo + dtm
            cusp_t = tlo
            out.append((tlo, lo.copy()))
            if verbose:
                print(f"cusp at t={tlo:.6f}, area={area(lo):.6f}")
            if stop_at_cusp and ghost <= 0:
                break
        a, t = a_new, t_new
        out.append((t, a.copy()))
        if verbose and len(out) % 200 == 0:
            print(f"t={t:.3f} area={area(a):.5f} rmin={rmin_new:.4f}")
        if cusp_t is not None and t >= cusp_t + ghost:
            break
        if tmax is not None and t >= tmax:
            break
        if area(a) <= 0.02 * area(np.array(a0, complex)):
            break
    return out, cusp_t, resid_max

if __name__ == '__main__':
    import sys, json
    rng = np.random.default_rng(int(sys.argv[1]) if len(sys.argv) > 1 else 3)
    K = 7
    a0 = np.zeros(K, complex)
    a0[0] = 1.0
    for k in range(2, K + 1):
        a0[k - 1] = rng.uniform(0.02, 0.16) / k * np.exp(1j * rng.uniform(0, 2 * np.pi))
    # make sure it's univalent to start
    print('initial rmin', np.min(np.abs(fprime_roots(a0))))
    out, tc, res = integrate(a0, Q=-1.0, dt=0.002, verbose=True, ghost=0.0)
    print('cusp time', tc, 'max PG residual', res)
    M0 = moments(out[0][1], 6)
    Mc = moments(out[-1][1], 6)
    print('area0', area(out[0][1]), 'areac', area(out[-1][1]), 'A0+Q t', area(out[0][1]) - tc)
    print('moment drift', np.abs(Mc[1:] - M0[1:]))
