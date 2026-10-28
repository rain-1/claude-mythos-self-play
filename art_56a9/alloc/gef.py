# Gravitational allocation of the zeros of a Gaussian entire function f(z) = sum xi_k z^k / sqrt(k!).
# U = log|f| - |z|^2/2 ; the flow dz/dt = -grad U = z - conj(f'/f) carries a.e. point to a zero; every basin has area pi.
import numpy as np, numba, math
from numba import njit, prange

def coeffs(K, seed):
    rng = np.random.default_rng(seed)
    xi = (rng.standard_normal(K) + 1j * rng.standard_normal(K)) / math.sqrt(2)
    lf = np.array([0.5 * math.lgamma(k + 1) for k in range(K)])
    return xi * np.exp(-lf)

@njit(parallel=True, cache=True)
def field(c, W, R):
    # returns logF = log|f| - |z|^2/2 and v = z - conj(f'/f) on a WxW grid over [-R,R]^2 (row 0 = top)
    K = c.shape[0]
    U = np.empty((W, W), np.float32); V = np.empty((W, W, 2), np.float32)
    for y in prange(W):
        for x in range(W):
            z = complex(-R + 2 * R * (x + 0.5) / W, R - 2 * R * (y + 0.5) / W)
            f = 0j; d = 0j
            for k in range(K - 1, -1, -1):
                d = d * z + f
                f = f * z + c[k]
            a2 = z.real * z.real + z.imag * z.imag
            af = abs(f)
            U[y, x] = math.log(af + 1e-300) - a2 / 2
            if af > 1e-300:
                q = d / f
                V[y, x, 0] = z.real - q.real
                V[y, x, 1] = z.imag + q.imag   # conj
            else:
                V[y, x, 0] = 0; V[y, x, 1] = 0
    return U, V

@njit(cache=True)
def fval(c, z):
    K = c.shape[0]; f = 0j; d = 0j
    for k in range(K - 1, -1, -1):
        d = d * z + f
        f = f * z + c[k]
    return f, d

def zeros(c, U, R, W):
    # Newton from local minima of U on the grid
    from scipy import ndimage as ndi
    mn = (U == ndi.minimum_filter(U, size=5)) & (U < -1.0)
    ys, xs = np.nonzero(mn)
    Z = []
    for y, x in zip(ys, xs):
        z = complex(-R + 2 * R * (x + 0.5) / W, R - 2 * R * (y + 0.5) / W)
        for it in range(50):
            f, d = fval(c, z)
            if d == 0: break
            dz = f / d; z -= dz
            if abs(dz) < 1e-13: break
        f, d = fval(c, z)
        if abs(f) * math.exp(-abs(z) ** 2 / 2) > 1e-9 or abs(z) > R * 1.5: continue
        if all(abs(z - w) > 1e-6 for w in Z): Z.append(z)
    return np.array(Z)

@njit(cache=True, inline='always')
def bil(V, x, y, W):
    if x < 0: x = 0.0
    if y < 0: y = 0.0
    if x > W - 1.001: x = W - 1.001
    if y > W - 1.001: y = W - 1.001
    i = int(x); j = int(y); fx = x - i; fy = y - j
    a = V[j, i]; b = V[j, i + 1]; cc = V[j + 1, i]; d = V[j + 1, i + 1]
    return ((a[0] * (1 - fx) + b[0] * fx) * (1 - fy) + (cc[0] * (1 - fx) + d[0] * fx) * fy,
            (a[1] * (1 - fx) + b[1] * fx) * (1 - fy) + (cc[1] * (1 - fx) + d[1] * fx) * fy)

@njit(parallel=True, cache=True)
def basins(V, ZL, W, step, maxit):
    # ZL: int raster, zero id painted in small discs around each zero (-1 elsewhere)
    L = np.full((W, W), -1, np.int32)
    for y in prange(W):
        for x in range(W):
            px = x + 0.0; py = y + 0.0
            lab = -1
            for it in range(maxit):
                ix = int(px + 0.5); iy = int(py + 0.5)
                if ix < 0 or iy < 0 or ix >= W or iy >= W: break
                if ZL[iy, ix] >= 0:
                    lab = ZL[iy, ix]; break
                vx, vy = bil(V, px, py, W)
                n = math.sqrt(vx * vx + vy * vy) + 1e-12
                # image y axis points down: v.imag is up
                mx = px + 0.5 * step * vx / n; my = py - 0.5 * step * vy / n
                vx, vy = bil(V, mx, my, W)
                n = math.sqrt(vx * vx + vy * vy) + 1e-12
                px += step * vx / n; py -= step * vy / n
            L[y, x] = lab
    return L

@njit(parallel=True, cache=True)
def lic(V, noise, W, L):
    out = np.zeros((W, W), np.float32)
    for y in prange(W):
        for x in range(W):
            acc = 0.0; wsum = 0.0
            for sgn in (-1.0, 1.0):
                px = x + 0.0; py = y + 0.0
                for k in range(L):
                    w = 1.0 - k / L
                    ix = int(px + 0.5); iy = int(py + 0.5)
                    if ix < 0 or iy < 0 or ix >= W or iy >= W: break
                    acc += w * noise[iy, ix]; wsum += w
                    vx, vy = bil(V, px, py, W)
                    n = math.sqrt(vx * vx + vy * vy) + 1e-12
                    px += sgn * vx / n; py -= sgn * vy / n
            out[y, x] = acc / max(wsum, 1e-9)
    return out

@njit(parallel=True, cache=True)
def field_pts(P, W, R):
    # points P (complex, intensity 1/pi): U = sum log|z-a| - |z|^2/2, v = z - sum (z-a)/|z-a|^2
    U = np.empty((W, W), np.float32); V = np.empty((W, W, 2), np.float32)
    n = P.shape[0]
    for y in prange(W):
        for x in range(W):
            zr = -R + 2 * R * (x + 0.5) / W; zi = R - 2 * R * (y + 0.5) / W
            u = -(zr * zr + zi * zi) / 2; vx = zr; vy = zi
            for k in range(n):
                dx = zr - P[k].real; dy = zi - P[k].imag
                r2 = dx * dx + dy * dy + 1e-30
                u += 0.5 * math.log(r2)
                vx -= dx / r2; vy -= dy / r2
            U[y, x] = u; V[y, x, 0] = vx; V[y, x, 1] = vy
    return U, V
