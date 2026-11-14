"""General tool: Schneider index of M = union of convex polygons (points and segments allowed),
and of its sumsets nM, via support functions.

A piece P is stored as its support values H[j] = h_P(nu_j) over a common list of directions nu_j
that contains every edge normal of K = conv(M) and of every piece.  Then
   h_{P+Q} = h_P + h_Q                      (so the pieces of nM are sums of n rows of H)
   u in (1-s)P + sK   <=>   nu_j.u - H[j] <= s (hK[j] - H[j])  for all j
   f_P(u) = max_j (nu_j.u - H[j]) / (hK[j] - H[j])   (terms with zero denominator hold on K)
   s(u) = min_P f_P(u),   s* = max_K s,   c = s*/(1-s*),   a_n = n c(nM).
We always work with the normalised sumset (1/n) nM, whose hull is K again.
"""
import numpy as np, itertools
from numba import njit, prange
from fractions import Fraction
from scipy.spatial import ConvexHull


def _normals(poly):
    P = np.asarray(poly, float)
    if len(P) == 1: return np.zeros((0, 2))
    if len(P) == 2:
        e = P[1] - P[0]; n = np.array([e[1], -e[0]]); return np.array([n, -n])
    E = np.roll(P, -1, 0) - P
    return np.stack([E[:, 1], -E[:, 0]], 1)


def build(pieces):
    """pieces: list of vertex arrays (convex position not required). returns NU, H, hK, hull vertices"""
    allv = np.concatenate([np.asarray(p, float).reshape(-1, 2) for p in pieces])
    hv = ConvexHull(allv).vertices
    V = allv[hv]
    cand = [_normals(V)]
    for p in pieces:
        p = np.asarray(p, float).reshape(-1, 2)
        if len(p) >= 3:
            p = p[ConvexHull(p).vertices]
        cand.append(_normals(p))
    NU = np.concatenate(cand)
    NU = NU / np.linalg.norm(NU, axis=1, keepdims=True)
    ang = np.round(np.arctan2(NU[:, 1], NU[:, 0]), 9)
    _, idx = np.unique(ang, return_index=True)
    NU = NU[idx]
    H = np.array([(np.asarray(p, float).reshape(-1, 2) @ NU.T).max(0) for p in pieces])
    hK = H.max(0)
    return NU, H, hK, V


def nfold(H, n, cap=400000):
    """support rows of the pieces of (1/n) nM, deduplicated"""
    k = H.shape[0]
    if n == 1: return H.copy()
    cur = H.copy()
    for t in range(2, n + 1):
        nxt = (cur[:, None, :] + H[None, :, :]).reshape(-1, H.shape[1])
        _, ix = np.unique(np.round(nxt, 8), axis=0, return_index=True)
        nxt = nxt[ix]
        cur = nxt
        if len(cur) > cap: raise MemoryError
    return cur / n


def prune(Hn):
    """drop pieces contained in another piece (support dominated everywhere)"""
    order = np.argsort(-Hn.sum(1))
    Hs = Hn[order]
    keep = []
    for i in range(len(Hs)):
        dom = False
        for j in keep:
            if np.all(Hs[j] >= Hs[i] - 1e-10):
                dom = True; break
        if not dom: keep.append(i)
    return Hs[keep]


@njit(cache=True, fastmath=True)
def s_at(x, y, NU, H, hK):
    best = 1e18
    for i in range(H.shape[0]):
        f = 0.0
        for j in range(NU.shape[0]):
            d = hK[j] - H[i, j]
            if d > 1e-7:
                v = (NU[j, 0] * x + NU[j, 1] * y - H[i, j]) / d
                if v > f:
                    f = v
                    if f >= best: break
        if f < best: best = f
    return best


@njit(cache=True, fastmath=True)
def inside(x, y, NU, hK, eps):
    for j in range(NU.shape[0]):
        if NU[j, 0] * x + NU[j, 1] * y > hK[j] + eps: return False
    return True


@njit(parallel=True, cache=True, fastmath=True)
def field(xs, ys, NU, H, hK):
    out = np.full((ys.size, xs.size), -1.0)
    for a in prange(ys.size):
        for b in range(xs.size):
            if inside(xs[b], ys[a], NU, hK, 1e-9):
                out[a, b] = s_at(xs[b], ys[a], NU, H, hK)
    return out


@njit(parallel=True, cache=True, fastmath=True)
def field_owner(xs, ys, NU, H, hK):
    out = np.full((ys.size, xs.size), -1.0)
    own = np.full((ys.size, xs.size), -1, dtype=np.int32)
    for a in prange(ys.size):
        for b in range(xs.size):
            x = xs[b]; y = ys[a]
            if inside(x, y, NU, hK, 1e-9):
                best = 1e18; bi = -1
                for i in range(H.shape[0]):
                    f = 0.0
                    for j in range(NU.shape[0]):
                        d = hK[j] - H[i, j]
                        if d > 1e-7:
                            v = (NU[j, 0] * x + NU[j, 1] * y - H[i, j]) / d
                            if v > f: f = v
                    if f < best: best = f; bi = i
                out[a, b] = best; own[a, b] = bi
    return out, own


def sstar(NU, H, hK, V, res=260, ncand=6, iters=20):
    lo = V.min(0); hi = V.max(0)
    xs = np.linspace(lo[0], hi[0], res); ys = np.linspace(lo[1], hi[1], res)
    F = field(xs, ys, NU, H, hK)
    P = np.pad(F, 1, constant_values=-1)
    loc = np.ones_like(F, dtype=bool)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dx or dy:
                loc &= F >= P[1 + dy:1 + dy + F.shape[0], 1 + dx:1 + dx + F.shape[1]]
    idx = np.argwhere(loc); vals = F[loc]
    order = np.argsort(-vals)[:ncand]
    best = (0.0, 0.0, 0.0)
    w0 = max(xs[1] - xs[0], ys[1] - ys[0]) * 2.0
    for o in order:
        a, b = idx[o]; cx, cy = xs[b], ys[a]; w = w0; v = vals[o]
        for it in range(iters):
            gx = np.linspace(cx - w, cx + w, 17); gy = np.linspace(cy - w, cy + w, 17)
            G = field(gx, gy, NU, H, hK)
            k = np.unravel_index(np.argmax(G), G.shape)
            v = G[k]; cx, cy = gx[k[1]], gy[k[0]]; w *= 0.3
        if v > best[0]: best = (v, cx, cy)
    return best


def a_seq(pieces, nmax, **kw):
    """a_n = n c(nM), n = 1..nmax (floats), plus the last-covered points"""
    NU, H, hK, V = build(pieces)
    out = []; pts = []
    for n in range(1, nmax + 1):
        Hn = prune(nfold(H, n))
        s, x, y = sstar(NU, Hn, hK, V, **kw)
        out.append(n * s / (1 - s)); pts.append((x, y))
        if s < 1e-12:
            out += [0.0] * (nmax - n); break
    return out, pts


if __name__ == "__main__":
    tri = [[(0, 0)], [(1, 0)], [(0, 1)]]
    print("simplex", a_seq(tri, 4)[0])
    for eps in (0.2, 0.4, 0.5):
        T = np.array([(0, 0), (1, 0), (0, 1)], float)
        fat = [(1 - eps) * v + eps * T for v in T]
        print("fat simplex eps", eps, a_seq(fat, 4)[0], "predict", [max(0, 2 - (n + 2) * eps) for n in range(1, 5)])
    k = 48
    th = np.linspace(0, 2 * np.pi, k + 1)
    C = np.stack([np.cos(th), np.sin(th)], 1)
    ring = [C[i:i + 2] for i in range(k)]
    print("48-gon boundary", a_seq(ring, 3)[0])
    print("two intervals x two intervals", a_seq([np.array([(x, y), (x + .25, y), (x + .25, y + .25), (x, y + .25)]) for x in (0, .75) for y in (0, .75)], 4)[0])
