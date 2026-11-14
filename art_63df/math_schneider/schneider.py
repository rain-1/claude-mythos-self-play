"""Schneider's non-convexity index c(M) for finite M in the plane (MO 516522).

c(M) = inf{ lam >= 0 : M + lam*K convex },  K = conv(M).

Reformulation used here (see RESULTS.md):  M + lam*K is convex  iff  it equals (1+lam)K,
iff every u in K lies in some  m + s(K - m),  s = lam/(1+lam)  (K shrunk towards m by s).
So with  f_m(u) = gauge of (u-m) in (K-m) = max_j  n_j.(u-m) / (h_j - n_j.m)
          s(u)  = min_m f_m(u),          s* = max_{u in K} s(u),
          c(M)  = s*/(1-s*).
s is piecewise linear, so s* is attained at a vertex and is rational for integer M.
"""
import numpy as np
from numba import njit, prange
from fractions import Fraction
from scipy.spatial import ConvexHull


def hull(M):
    M = np.asarray(M, dtype=np.float64)
    hv = ConvexHull(M).vertices  # CCW
    V = M[hv]
    E = np.roll(V, -1, axis=0) - V
    N = np.stack([E[:, 1], -E[:, 0]], axis=1)  # outward for CCW
    h = (N * V).sum(1)
    return V, N, h


def sumset(M, n):
    M = [tuple(p) for p in M]
    S = set(M)
    for _ in range(n - 1):
        S = {(a[0] + b[0], a[1] + b[1]) for a in S for b in M}
    return np.array(sorted(S), dtype=np.int64)


@njit(cache=True, fastmath=True)
def s_at(x, y, M, N, h, D):
    best = 1e18
    for i in range(M.shape[0]):
        dx = x - M[i, 0]
        dy = y - M[i, 1]
        f = 0.0
        for j in range(N.shape[0]):
            d = D[i, j]
            if d > 1e-12:
                v = (N[j, 0] * dx + N[j, 1] * dy) / d
                if v > f:
                    f = v
                    if f >= best:
                        break
        if f < best:
            best = f
    return best


@njit(cache=True, fastmath=True)
def inside(x, y, N, h, eps):
    for j in range(N.shape[0]):
        if N[j, 0] * x + N[j, 1] * y > h[j] + eps:
            return False
    return True


@njit(parallel=True, cache=True, fastmath=True)
def field(xs, ys, M, N, h, D):
    out = np.full((ys.size, xs.size), -1.0)
    for a in prange(ys.size):
        for b in range(xs.size):
            if inside(xs[b], ys[a], N, h, 1e-9):
                out[a, b] = s_at(xs[b], ys[a], M, N, h, D)
    return out


@njit(parallel=True, cache=True, fastmath=True)
def owner_field(xs, ys, M, N, h, D):
    """also return the index of the m that realises the min"""
    out = np.full((ys.size, xs.size), -1.0)
    own = np.full((ys.size, xs.size), -1, dtype=np.int32)
    for a in prange(ys.size):
        for b in range(xs.size):
            x = xs[b]; y = ys[a]
            if inside(x, y, N, h, 1e-9):
                best = 1e18; bi = -1
                for i in range(M.shape[0]):
                    dx = x - M[i, 0]; dy = y - M[i, 1]
                    f = 0.0
                    for j in range(N.shape[0]):
                        d = D[i, j]
                        if d > 1e-12:
                            v = (N[j, 0] * dx + N[j, 1] * dy) / d
                            if v > f:
                                f = v
                    if f < best:
                        best = f; bi = i
                out[a, b] = best; own[a, b] = bi
    return out, own


def prep(M):
    M = np.asarray(M, dtype=np.float64)
    V, N, h = hull(M)
    D = h[None, :] - M @ N.T
    D[np.abs(D) < 1e-9] = 0.0
    return M, V, N, h, D


def sstar(M, res=500, ncand=24, verbose=False):
    """numeric s* (to ~1e-11) and its location"""
    M, V, N, h, D = prep(M)
    lo = V.min(0); hi = V.max(0)
    xs = np.linspace(lo[0], hi[0], res)
    ys = np.linspace(lo[1], hi[1], res)
    F = field(xs, ys, M, N, h, D)
    # candidates: local maxima of the grid
    P = np.pad(F, 1, constant_values=-1)
    loc = np.ones_like(F, dtype=bool)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dx or dy:
                loc &= F >= P[1 + dy:1 + dy + F.shape[0], 1 + dx:1 + dx + F.shape[1]]
    idx = np.argwhere(loc)
    vals = F[loc]
    order = np.argsort(-vals)[:ncand]
    best = (-1, 0, 0)
    w0 = max(xs[1] - xs[0], ys[1] - ys[0]) * 2.0
    for o in order:
        a, b = idx[o]
        cx, cy = xs[b], ys[a]; w = w0; v = vals[o]
        for it in range(20):
            gx = np.linspace(cx - w, cx + w, 17); gy = np.linspace(cy - w, cy + w, 17)
            G = field(gx, gy, M, N, h, D)
            k = np.unravel_index(np.argmax(G), G.shape)
            v = G[k]; cx, cy = gx[k[1]], gy[k[0]]
            w *= 0.3
        if v > best[0]:
            best = (v, cx, cy)
    return best


def cindex(M, **kw):
    s, x, y = sstar(M, **kw)
    fs = Fraction(s).limit_denominator(200000)
    exact = abs(float(fs) - s) < 1e-8
    c = fs / (1 - fs) if exact else Fraction(s / (1 - s)).limit_denominator(10**9)
    return c, exact, (x, y), s


if __name__ == "__main__":
    tri = [(0, 0), (1, 0), (0, 1)]
    for n in range(1, 6):
        c, ex, u, s = cindex(sumset(tri, n))
        print("simplex", n, c, ex, "expect", Fraction(2, n))
    sq = [(0, 0), (1, 0), (0, 1), (1, 1)]
    for n in range(1, 4):
        print("square", n, cindex(sumset(sq, n))[:2])
    L = [(0, 0), (3, 0), (0, 3), (1, 1)]
    for n in range(1, 5):
        print("L", n, cindex(sumset(L, n))[:2])
