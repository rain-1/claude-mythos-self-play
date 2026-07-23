"""Osculating-conic engine for a smooth convex oval.
Conic Q(x,y)=ax^2+bxy+cy^2+dx+ey+f with 5th-order contact at r(t):
g(t)=Q(r(t)) must satisfy g=g'=g''=g'''=g''''=0 -- 5 linear eqs in 6 unknowns.
Sextactic points: 6th-order contact <=> det of the 6x6 (adding g''''') = 0.
Mukhopadhyaya: a convex oval has >= 6 sextactic points."""
import numpy as np

# the oval: r(t) = rho(t)*(cos t, sin t), analytic derivatives via FFT spectral
K = 4096
t = np.linspace(0, 2*np.pi, K, endpoint=False)

def make_curve(coefs):
    """coefs: dict harmonic -> (amp, phase). Returns x(t), y(t) and derivs to order 5."""
    rho = np.ones_like(t)
    for m, (a, ph) in coefs.items():
        rho = rho + a*np.cos(m*t + ph)
    x, y = rho*np.cos(t), rho*np.sin(t)
    # spectral derivatives (exact for trig polynomials)
    def dfft(f, order):
        F = np.fft.rfft(f)
        F[np.abs(F) < 1e-9 * np.abs(F).max()] = 0   # curve is a finite trig poly
        F[64:] = 0
        k = np.arange(len(F))
        return np.fft.irfft(F * (1j*k)**order, n=len(f))
    dx = [x] + [dfft(x, o) for o in range(1, 6)]
    dy = [y] + [dfft(y, o) for o in range(1, 6)]
    return dx, dy

def contact_rows(dx, dy, idx):
    """Rows of derivatives of g(t)=Q(r(t)) wrt t at samples idx, for Q coeffs
    (a,b,c,d,e,f) ordered [u^2, uv, v^2, u, v, 1] in coordinates u=x-x0, v=y-y0
    CENTERED at the contact point (conditioning).  Use Leibniz on monomials."""
    x = [d[idx].copy() for d in dx]; y = [d[idx].copy() for d in dy]
    x0, y0 = x[0].copy(), y[0].copy()
    x[0] = np.zeros_like(x0); y[0] = np.zeros_like(y0)   # u = x - x0
    from math import comb
    def mono_derivs(u, v, n):
        # derivatives 0..n of u(t)*v(t)
        return [sum(comb(o, i) * u[i] * v[o-i] for i in range(o+1)) for o in range(n+1)]
    x2 = mono_derivs(x, x, 5); xy = mono_derivs(x, y, 5); y2 = mono_derivs(y, y, 5)
    one = [np.ones_like(x[0])] + [np.zeros_like(x[0])]*5
    rows = []
    for o in range(6):
        rows.append(np.stack([x2[o], xy[o], y2[o], x[o], y[o], one[o]], axis=-1))
    return np.stack(rows, axis=-2)   # (..., 6 orders, 6 coeffs)

def osculating_conics(dx, dy, idx):
    """Null vector of the first 5 rows -> conic coeffs; also the 6x6 det (sextactic fn)."""
    M = contact_rows(dx, dy, idx)          # (n, 6, 6)
    M = M / (np.linalg.norm(M, axis=-1, keepdims=True) + 1e-300)   # row-normalize
    A5 = M[:, :5, :]                        # (n, 5, 6)
    U, s, Vt = np.linalg.svd(A5)
    Q = Vt[:, -1, :]                        # (n, 6) conic in CENTERED coords
    sex = np.linalg.det(M)                  # 6th-order contact indicator (normalized rows)
    return Q, sex, s[:, -2] / s[:, 0]       # coeffs, sextactic det, gap ratio
