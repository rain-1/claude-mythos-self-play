"""street.py — a von Kármán vortex street passing over a fixed dye source.

The street is the exact staggered two-row point-vortex configuration (rows at y = ±h/2, spacing a,
circulations ∓Γ, stagger a/2), regularised with Krasny's δ: for one periodic row at (x_k, y_0),
   (u, v) = (Γ/2a) · (−sinh(κ y'), sin(κ x')) / (cosh(κ y') − cos(κ x') + δ²),  κ = 2π/a.
The street drifts through the fluid at U_s = (Γ/2a) tanh(κ h/2) against the direction the top row
would push; with a free stream U the vortices move at U_v = U − U_s (they lag the water).
Dye is released at fixed points (x = 0, y_j) every Δt; every particle is advected with RK4 in the LAB
frame. The picture at time T is the set of streaklines: the pattern (the street) is steady in its own
frame while the water — the dye — is left wound behind it. What persists is the shape, not the stuff.
"""
import numpy as np

A_SP = 1.0                       # vortex spacing along the street
H_ROW = 0.2806 * A_SP            # von Kármán's stable ratio: h/a = arccosh(√2)/π = 0.28055
GAMMA = 1.0
DELTA = 0.16                     # Krasny core (fraction of a)
U_INF = 0.0                      # set by the caller
KAPPA = 2 * np.pi / A_SP


def row_velocity(x, y, x0, y0, gamma):
    xp = KAPPA * (x - x0); yp = KAPPA * (y - y0)
    den = np.cosh(yp) - np.cos(xp) + DELTA ** 2
    u = -(gamma / (2 * A_SP)) * np.sinh(yp) / den
    v = (gamma / (2 * A_SP)) * np.sin(xp) / den
    return u, v


def street_speed():
    return (GAMMA / (2 * A_SP)) * np.tanh(KAPPA * H_ROW / 2)


def velocity(x, y, t, U):
    """lab-frame velocity: free stream U plus the street translated by U_v t.
    Top row: −Γ (clockwise, as behind a cylinder in a +x stream) at (k a, +h/2); bottom row: +Γ at ((k+1/2) a, −h/2). With these signs the street
    self-propels in −x (against the stream) at U_s, so U_v = U − U_s."""
    Uv = U - street_speed()
    x0 = Uv * t
    u1, v1 = row_velocity(x, y, x0, +H_ROW / 2, -GAMMA)
    u2, v2 = row_velocity(x, y, x0 + A_SP / 2, -H_ROW / 2, +GAMMA)
    return U + u1 + u2, v1 + v2


def streaklines(ys, U, T, dt, release_every, xsrc=0.0):
    """release a particle at (xsrc, y_j) every `release_every` steps for all j; RK4 advect all in the lab
    frame until T. Returns positions (N, 2), release times (N,), source index (N,)."""
    nsteps = int(round(T / dt))
    px, py, pt, pj = [], [], [], []
    X = np.zeros(0); Y = np.zeros(0); TR = np.zeros(0); J = np.zeros(0, int)
    ys = np.asarray(ys, float)
    for s in range(nsteps + 1):
        t = s * dt
        if s % release_every == 0:
            X = np.concatenate([X, np.full(len(ys), xsrc)]); Y = np.concatenate([Y, ys])
            TR = np.concatenate([TR, np.full(len(ys), t)]); J = np.concatenate([J, np.arange(len(ys))])
        if s == nsteps:
            break
        k1x, k1y = velocity(X, Y, t, U)
        k2x, k2y = velocity(X + 0.5 * dt * k1x, Y + 0.5 * dt * k1y, t + 0.5 * dt, U)
        k3x, k3y = velocity(X + 0.5 * dt * k2x, Y + 0.5 * dt * k2y, t + 0.5 * dt, U)
        k4x, k4y = velocity(X + dt * k3x, Y + dt * k3y, t + dt, U)
        X = X + dt / 6 * (k1x + 2 * k2x + 2 * k3x + k4x)
        Y = Y + dt / 6 * (k1y + 2 * k2y + 2 * k3y + k4y)
    return np.stack([X, Y], 1), TR, J


def streamfunction_street_frame(x, y, U):
    """ψ in the frame moving with the street (steady): ψ_row = −(Γ/4π) log(cosh κy' − cos κx' + δ²)
    for a row of +Γ (u = ∂ψ/∂y, v = −∂ψ/∂x) — check: ∂ψ/∂y = −(Γ/4π)·κ sinh/den = −(Γ/2a) sinh/den ✓."""
    Uv = U - street_speed()
    rel = U - Uv           # in the street frame the stream is U − U_v = U_s
    def psi_row(x0, y0, gamma):
        xp = KAPPA * (x - x0); yp = KAPPA * (y - y0)
        return -(gamma / (4 * np.pi)) * np.log(np.cosh(yp) - np.cos(xp) + DELTA ** 2)
    return rel * y + psi_row(0.0, +H_ROW / 2, -GAMMA) + psi_row(A_SP / 2, -H_ROW / 2, +GAMMA)


if __name__ == '__main__':
    import time
    # certificate: the street translates rigidly — the velocity at a vortex centre due to the OTHER row
    # equals U_v; and the stagger ratio is the stable one.
    Us = street_speed()
    U = 1.0
    x0 = 0.0
    # velocity induced at the top-row vortex (0, h/2) by the bottom row only:
    u2, v2 = row_velocity(np.array([0.0]), np.array([H_ROW / 2]), A_SP / 2, -H_ROW / 2, +GAMMA)
    print('self-induced speed of the street from the other row:', u2[0], 'predicted -U_s =', -Us, 'v =', v2[0])
    # (the own row induces zero velocity at its own vortex by symmetry; check numerically near it)
    print('ratio h/a =', H_ROW / A_SP, ' arccosh(sqrt2)/pi =', np.arccosh(2 ** 0.5) / np.pi)
    t0 = time.time()
    P, TR, J = streaklines(np.linspace(-0.6, 0.6, 9), U, 6.0, 0.01, 10)
    print('particles', len(P), 'in', time.time() - t0, 's; x range', P[:, 0].min(), P[:, 0].max())
