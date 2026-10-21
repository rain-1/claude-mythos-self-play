"""Five waves in a round basin: exact refraction caustics over a mosaic floor.

Water height h(x) = A * Re S(x),  S(x) = sum_k a_k U_k(x),  U_k = exp(i(kappa_k khat_k . x + phi_k)).
Wave k 'carries' a point when w_k = Re(a_k U_k / S) > 1/2  (event E_k of MO 392723).
The mosaic tile under every point is glazed once by each wave that carries it.
Sunlight is refracted through the surface (Snell, three wavelengths) and splatted onto the floor.
"""
import numpy as np
from numba import njit, prange

# ---------------------------------------------------------------- the five waves
AMP = np.array([1.0, 0.85, 0.7, 0.55, 0.4])


def waves(seed=3, lam=0.075, spread=0.18, fan=None):
    rng = np.random.default_rng(seed)
    ang = np.array([0.31, 1.62, 2.71, 3.95, 5.12]) + rng.normal(0, 0.06, 5)
    if fan is not None:
        ang = fan[0] + fan[1] * np.array([-1.0, -0.45, 0.1, 0.62, 1.0]) + rng.normal(0, 0.05, 5)
    kap = 2 * np.pi / lam * (1 + spread * rng.uniform(-1, 1, 5))
    phi = rng.uniform(0, 2 * np.pi, 5)
    K = np.stack([kap * np.cos(ang), kap * np.sin(ang)], 1)
    return K, phi, ang


@njit(cache=True)
def field(x, y, K, phi, a):
    """returns Re S, Im S, grad h (of Re S), hessian of Re S, and w_k array."""
    n = a.shape[0]
    sr = 0.0; si = 0.0; gx = 0.0; gy = 0.0; hxx = 0.0; hxy = 0.0; hyy = 0.0
    ur = np.empty(n); ui = np.empty(n)
    for k in range(n):
        th = K[k, 0] * x + K[k, 1] * y + phi[k]
        c = np.cos(th); s = np.sin(th)
        ur[k] = c; ui[k] = s
        sr += a[k] * c; si += a[k] * s
        gx -= a[k] * s * K[k, 0]; gy -= a[k] * s * K[k, 1]
        hxx -= a[k] * c * K[k, 0] * K[k, 0]
        hxy -= a[k] * c * K[k, 0] * K[k, 1]
        hyy -= a[k] * c * K[k, 1] * K[k, 1]
    return sr, si, gx, gy, hxx, hxy, hyy, ur, ui


@njit(cache=True)
def weights(x, y, K, phi, a, out):
    n = a.shape[0]
    sr = 0.0; si = 0.0
    for k in range(n):
        th = K[k, 0] * x + K[k, 1] * y + phi[k]
        out[k] = th
        sr += a[k] * np.cos(th); si += a[k] * np.sin(th)
    m2 = sr * sr + si * si + 1e-30
    for k in range(n):
        c = np.cos(out[k]); s = np.sin(out[k])
        # Re(a U conj(S)) / |S|^2
        out[k] = a[k] * (c * sr + s * si) / m2


@njit(cache=True)
def refract(nx, ny, nz, dx, dy, dz, eta):
    """d incident unit (pointing into surface), n unit facing against d. eta = n1/n2."""
    cosi = -(nx * dx + ny * dy + nz * dz)
    k = 1.0 - eta * eta * (1.0 - cosi * cosi)
    if k < 0:
        return 0.0, 0.0, 0.0, 0.0
    ct = np.sqrt(k)
    tx = eta * dx + (eta * cosi - ct) * nx
    ty = eta * dy + (eta * cosi - ct) * ny
    tz = eta * dz + (eta * cosi - ct) * nz
    # fresnel transmittance (unpolarised)
    rs = (cosi - eta * ct) / (cosi + eta * ct) if False else 0.0
    n1 = 1.0; n2 = 1.0 / eta
    rs = (n1 * cosi - n2 * ct) / (n1 * cosi + n2 * ct)
    rp = (n2 * cosi - n1 * ct) / (n2 * cosi + n1 * ct)
    T = 1.0 - 0.5 * (rs * rs + rp * rp)
    return tx, ty, tz, T


@njit(parallel=True, cache=True)
def caustic(W, x0, x1, K, phi, a, A, depth, Lx, Ly, Lz, eta, ss, R, cope, seed):
    """photon map of floor irradiance (normalised: flat water = 1). Pixel grid W x W over [x0,x1]^2."""
    img = np.zeros((W, W))
    px = (x1 - x0) / W
    M = W * ss
    st = (x1 - x0) / M
    # horizontal direction toward the sun and cot of elevation for rim shadow
    hl = np.sqrt(Lx * Lx + Ly * Ly) + 1e-12
    tan_e = hl / abs(Lz)
    norm = 1.0 / (ss * ss)
    # flat-water floor displacement (so lit patterns line up with the floor)
    for j in prange(M):
        for i in range(M):
            jx = ((i * 7919 + j * 104729 + seed) % 1000) / 1000.0
            jy = ((i * 15485863 + j * 32452843 + seed * 3) % 1000) / 1000.0
            x = x0 + (i + jx) * st
            y = x0 + (j + jy) * st
            r2 = x * x + y * y
            if r2 > R * R:
                continue
            # rim shadow: walk back toward the sun by cope*cot(elev)
            bx = x - Lx / hl * cope * tan_e
            by = y - Ly / hl * cope * tan_e
            if bx * bx + by * by > R * R:
                continue
            sr, si, gx, gy, hxx, hxy, hyy, ur, ui = field(x, y, K, phi, a)
            nx = -A * gx; ny = -A * gy; nz = 1.0
            nn = np.sqrt(nx * nx + ny * ny + 1.0)
            nx /= nn; ny /= nn; nz /= nn
            tx, ty, tz, T = refract(nx, ny, nz, Lx, Ly, Lz, eta)
            if tz == 0.0:
                continue
            d = depth - A * sr  # water column below this surface point
            t = d / (-tz)
            fx = x + tx * t
            fy = y + ty * t
            # stop rays that leave the basin before reaching the floor
            if fx * fx + fy * fy > R * R:
                continue
            u = (fx - x0) / px - 0.5
            v = (fy - x0) / px - 0.5
            iu = int(np.floor(u)); iv = int(np.floor(v))
            if iu < 0 or iv < 0 or iu >= W - 1 or iv >= W - 1:
                continue
            du = u - iu; dv = v - iv
            e = T * norm
            img[iv, iu] += e * (1 - du) * (1 - dv)
            img[iv, iu + 1] += e * du * (1 - dv)
            img[iv + 1, iu] += e * (1 - du) * dv
            img[iv + 1, iu + 1] += e * du * dv
    return img


@njit(parallel=True, cache=True)
def view(W, x0, x1, K, phi, a, A, depth, eta, R):
    """camera straight down: per pixel the floor point seen through the water, surface normal, fresnel R."""
    px = (x1 - x0) / W
    fxy = np.zeros((W, W, 2))
    fres = np.zeros((W, W))
    nrm = np.zeros((W, W, 3))
    hgt = np.zeros((W, W))
    for j in prange(W):
        for i in range(W):
            x = x0 + (i + 0.5) * px
            y = x0 + (j + 0.5) * px
            sr, si, gx, gy, hxx, hxy, hyy, ur, ui = field(x, y, K, phi, a)
            nx = -A * gx; ny = -A * gy; nz = 1.0
            nn = np.sqrt(nx * nx + ny * ny + 1.0)
            nx /= nn; ny /= nn; nz /= nn
            tx, ty, tz, T = refract(nx, ny, nz, 0.0, 0.0, -1.0, eta)
            d = depth - A * sr
            t = d / (-tz)
            fxy[j, i, 0] = x + tx * t
            fxy[j, i, 1] = y + ty * t
            fres[j, i] = 1.0 - T
            nrm[j, i, 0] = nx; nrm[j, i, 1] = ny; nrm[j, i, 2] = nz
            hgt[j, i] = sr
    return fxy, fres, nrm, hgt


@njit(parallel=True, cache=True)
def wmap(W, x0, x1, K, phi, a):
    px = (x1 - x0) / W
    n = a.shape[0]
    out = np.zeros((n, W, W))
    for j in prange(W):
        tmp = np.empty(n)
        for i in range(W):
            weights(x0 + (i + 0.5) * px, x0 + (j + 0.5) * px, K, phi, a, tmp)
            for k in range(n):
                out[k, j, i] = tmp[k]
    return out
