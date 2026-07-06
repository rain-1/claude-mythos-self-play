"""Chirikov standard map core: vectorised iteration, classification, splatting.

Map (on the torus [0,1)^2):
    p' = p + (K/2pi) sin(2pi x)   (mod 1, centered)
    x' = x + p'                    (mod 1)

Rotation number of an orbit: W = lim (x_N - x_0)/N using the UNLIFTED x sum
(x is lifted by accumulating p' increments).
"""
import numpy as np

TWO_PI = 2.0 * np.pi


def step(x, p, K):
    p = p + (K / TWO_PI) * np.sin(TWO_PI * x)
    x = x + p
    return x % 1.0, p


def iterate_splat(x, p, K, nsteps, S, acc=None, weight=1.0, pmod=True, chunk=None):
    """Iterate ensemble (x,p) nsteps, bilinear-splat every visited point into acc (S,S).
    Canvas: x horizontal in [0,1), p vertical in [0,1) (p wrapped to [0,1))."""
    if acc is None:
        acc = np.zeros((S, S), np.float32)
    x = np.asarray(x, np.float64).copy()
    p = np.asarray(p, np.float64).copy()
    for _ in range(nsteps):
        x, p = step(x, p, K)
        pv = p % 1.0
        fx = x * S
        fy = pv * S
        ix = np.floor(fx).astype(np.int64)
        iy = np.floor(fy).astype(np.int64)
        ax = (fx - ix).astype(np.float32)
        ay = (fy - iy).astype(np.float32)
        ix0 = ix % S; iy0 = iy % S
        ix1 = (ix + 1) % S; iy1 = (iy + 1) % S
        w = np.float32(weight)
        flat = acc.ravel()
        np.add.at(flat, iy0 * S + ix0, w * (1 - ax) * (1 - ay))
        np.add.at(flat, iy0 * S + ix1, w * ax * (1 - ay))
        np.add.at(flat, iy1 * S + ix0, w * (1 - ax) * ay)
        np.add.at(flat, iy1 * S + ix1, w * ax * ay)
    return acc, x, p


def lyapunov_classify(x0, p0, K, nsteps=600, eps=1e-9):
    """Finite-time max Lyapunov estimate per orbit via twin-orbit renormalisation."""
    x = np.asarray(x0, np.float64).copy(); p = np.asarray(p0, np.float64).copy()
    dx = np.full_like(x, eps); dp = np.zeros_like(p)
    logsum = np.zeros_like(x)
    for _ in range(nsteps):
        # tangent map: dp' = dp + K cos(2pi x) dx ; dx' = dx + dp'
        c = K * np.cos(TWO_PI * x)
        dp = dp + c * dx
        dx = dx + dp
        x, p = step(x, p, K)
        nrm = np.sqrt(dx * dx + dp * dp)
        logsum += np.log(nrm / eps)
        dx *= eps / nrm; dp *= eps / nrm
    return logsum / nsteps


def rotation_number(x0, p0, K, nsteps=20000):
    """W = mean of p' over the orbit (since lifted x_N - x_0 = sum p'_k)."""
    x = np.asarray(x0, np.float64).copy(); p = np.asarray(p0, np.float64).copy()
    s = np.zeros_like(p)
    for _ in range(nsteps):
        p = p + (K / TWO_PI) * np.sin(TWO_PI * x)
        x = (x + p) % 1.0
        s += p
    return s / nsteps
