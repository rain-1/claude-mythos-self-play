"""Geodesic flow on a triaxial ellipsoid  x^2/a^2 + y^2/b^2 + z^2/c^2 = 1.

Geodesic ODE (ambient, constrained):  r'' = -( r'^T A r' / (r^T A^2 r) ) * (A r)
with A = diag(1/a^2, 1/b^2, 1/c^2).  Velocity stays tangent and unit-speed
automatically (accel is parallel to A r, which is Euclidean-orthogonal to any
tangent velocity).  Vectorised over an ensemble of geodesics (ensemble = axis 0).
"""
import numpy as np


def make_A(a, b, c):
    return np.array([1.0 / a**2, 1.0 / b**2, 1.0 / c**2])


def _accel(R, V, A):
    # R,V: (N,3); A: (3,)
    AR = R * A                      # A@r per row
    A2R = AR * A                    # A^2 @ r
    num = np.einsum('ij,ij->i', V * A, V)      # r'^T A r'
    den = np.einsum('ij,ij->i', R, A2R)        # r^T A^2 r
    mu = -(num / den)
    return mu[:, None] * AR


def _project_to_surface(R, A):
    # scale each row so r^T A r = 1
    q = np.einsum('ij,ij->i', R * A, R)
    return R / np.sqrt(q)[:, None]


def _project_velocity(R, V, A):
    # remove the component of V along the normal (A r) so V stays tangent
    n = R * A
    n2 = np.einsum('ij,ij->i', n, n)
    dot = np.einsum('ij,ij->i', V, n) / n2
    return V - dot[:, None] * n


def tangent_basis(p, A):
    """orthonormal (e1,e2) spanning the tangent plane at p (normal ~ A p)."""
    n = p * A
    n = n / np.linalg.norm(n)
    # pick a helper not parallel to n
    helper = np.array([0.0, 0.0, 1.0]) if abs(n[2]) < 0.9 else np.array([1.0, 0.0, 0.0])
    e1 = helper - np.dot(helper, n) * n
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(n, e1)
    return e1, e2


def shoot(p, thetas, A, L, nsteps, record_every=1):
    """Integrate geodesics from point p in initial directions `thetas`.

    Returns positions array (nrec, N, 3) and the final (R,V).
    """
    p = _project_to_surface(p[None, :], A)[0]
    e1, e2 = tangent_basis(p, A)
    N = len(thetas)
    R = np.tile(p, (N, 1)).astype(np.float64)
    V = (np.cos(thetas)[:, None] * e1[None, :] +
         np.sin(thetas)[:, None] * e2[None, :])
    V = _project_velocity(R, V, A)
    V /= np.linalg.norm(V, axis=1)[:, None]

    dt = L / nsteps
    nrec = nsteps // record_every + 1
    out = np.empty((nrec, N, 3), dtype=np.float32)
    out[0] = R
    ri = 1
    for step in range(1, nsteps + 1):
        # RK4
        k1v = _accel(R, V, A)
        k1r = V
        k2v = _accel(R + 0.5 * dt * k1r, V + 0.5 * dt * k1v, A)
        k2r = V + 0.5 * dt * k1v
        k3v = _accel(R + 0.5 * dt * k2r, V + 0.5 * dt * k2v, A)
        k3r = V + 0.5 * dt * k2v
        k4v = _accel(R + dt * k3r, V + dt * k3v, A)
        k4r = V + dt * k3v
        R = R + (dt / 6.0) * (k1r + 2 * k2r + 2 * k3r + k4r)
        V = V + (dt / 6.0) * (k1v + 2 * k2v + 2 * k3v + k4v)
        # periodic re-projection to kill drift
        if step % 8 == 0:
            R = _project_to_surface(R, A)
            V = _project_velocity(R, V, A)
            V /= np.linalg.norm(V, axis=1)[:, None]
        if step % record_every == 0:
            out[ri] = R
            ri += 1
    return out[:ri], R, V


if __name__ == "__main__":
    # sanity: a sphere geodesic is a great circle; check closure & speed
    A = make_A(1.0, 1.0, 1.0)
    p = np.array([1.0, 0.0, 0.0])
    th = np.array([0.3, 1.1, 2.0])
    pos, R, V = shoot(p, th, A, L=2 * np.pi, nsteps=2000)
    # should return to start after arclength 2pi
    err = np.linalg.norm(R - p, axis=1)
    print("sphere closure err (should ~0):", err)
    speed = np.linalg.norm(V, axis=1)
    print("final speed (should ~1):", speed)
    # on-surface check
    onsurf = np.abs(np.einsum('ij,ij->i', R * A, R) - 1)
    print("on-surface residual:", onsurf)

    # triaxial: check on-surface stays good over long integration
    A2 = make_A(1.7, 1.15, 0.75)
    p2 = np.array([1.7, 0.0, 0.0])
    th2 = np.linspace(0, 2 * np.pi, 50, endpoint=False)
    pos2, R2, V2 = shoot(p2, th2, A2, L=6.0, nsteps=3000)
    res2 = np.abs(np.einsum('ij,ij->i', R2 * A2, R2) - 1).max()
    print("triaxial max on-surface residual after L=6:", res2)
