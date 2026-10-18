"""Polished terrazzo: stone chips set flush in a pale cement matrix, then polished.

Chips are convex polygons rasterised by their exact signed distance (analytic AA); each chip
has its own mottling, a faint darker cut rim and a polished glint.  The matrix carries a fine
aggregate of tiny grains.  A soft reflection of a window lies over everything (the polish).
"""
import numpy as np
from numba import njit, prange
from scipy import ndimage as ndi


def chip_shape(rng, r, nv=None, elong=1.0, rot=None):
    """random convex shard of radius ~r: sorted random angles, jittered radii, convex hull."""
    nv = nv or rng.integers(6, 11)
    a = np.sort(rng.random(nv) * 2 * np.pi)
    rr = r * (0.72 + 0.4 * rng.random(nv))
    p = np.c_[np.cos(a) * rr * elong, np.sin(a) * rr / elong]
    rot = rng.random() * 2 * np.pi if rot is None else rot
    c, s = np.cos(rot), np.sin(rot)
    p = p @ np.array([[c, s], [-s, c]])
    # convex hull (gift wrap via scipy)
    from scipy.spatial import ConvexHull
    h = ConvexHull(p)
    return p[h.vertices]


@njit(cache=True)
def _halfplanes(P):
    n = P.shape[0]
    out = np.zeros((n, 3))
    # orientation
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += P[i, 0] * P[j, 1] - P[j, 0] * P[i, 1]
    sgn = 1.0 if area > 0 else -1.0
    for i in range(n):
        j = (i + 1) % n
        ex, ey = P[j, 0] - P[i, 0], P[j, 1] - P[i, 1]
        L = (ex * ex + ey * ey) ** 0.5
        if L < 1e-12:
            out[i, 0], out[i, 1], out[i, 2] = 0.0, 0.0, -1e9
            continue
        # outward normal
        nx, ny = sgn * ey / L, -sgn * ex / L
        out[i, 0], out[i, 1], out[i, 2] = nx, ny, -(nx * P[i, 0] + ny * P[i, 1])
    return out


@njit(parallel=True, cache=True)
def draw_chips(img, polys, offs, cols, mott, seeds, rim, glint, gdir):
    """polys: (K, V, 2) padded by repeating last vertex; offs (K+1) unused; cols (K,3)."""
    H, W = img.shape[0], img.shape[1]
    K = polys.shape[0]
    # parallel over rows of chips is unsafe (overlaps) -> chips assumed non-overlapping
    for k in prange(K):
        P = polys[k]
        hp = _halfplanes(P)
        x0 = int(np.floor(P[:, 0].min())) - 1
        x1 = int(np.ceil(P[:, 0].max())) + 2
        y0 = int(np.floor(P[:, 1].min())) - 1
        y1 = int(np.ceil(P[:, 1].max())) + 2
        cx = P[:, 0].mean()
        cy = P[:, 1].mean()
        rad = 0.0
        for v in range(P.shape[0]):
            rad = max(rad, ((P[v, 0] - cx) ** 2 + (P[v, 1] - cy) ** 2) ** 0.5)
        s1 = seeds[k, 0]
        s2 = seeds[k, 1]
        s3 = seeds[k, 2]
        for y in range(max(0, y0), min(H, y1)):
            for x in range(max(0, x0), min(W, x1)):
                px = x + 0.5
                py = y + 0.5
                sd = -1e9
                for e in range(hp.shape[0]):
                    d = hp[e, 0] * px + hp[e, 1] * py + hp[e, 2]
                    if d > sd:
                        sd = d
                cov = min(1.0, max(0.0, 0.5 - sd))
                if cov <= 0:
                    continue
                u = (px - cx) / rad
                v = (py - cy) / rad
                # mottling: three sines with random phases (stone cloudiness)
                m = (np.sin(u * 3.1 + s1) * np.sin(v * 2.7 + s2) + 0.5 * np.sin((u + v) * 5.3 + s3)
                     + 0.25 * np.sin((u - v) * 9.7 + s1 * 2))
                m = m * mott[k]
                # cut rim: slightly deeper colour near the edge
                rr = min(1.0, max(0.0, (-sd) / (rim * rad + 1e-6)))
                rimf = 1.0 - 0.10 * (1.0 - rr) ** 2
                # polished glint along gdir
                gl = glint[k] * max(0.0, (u * gdir[0] + v * gdir[1]) * 0.7 + 0.2) ** 3
                for c in range(3):
                    val = cols[k, c] * (1.0 + m) * rimf + gl
                    img[y, x, c] = img[y, x, c] * (1 - cov) + val * cov


def pack_polys(polys):
    V = max(len(p) for p in polys)
    out = np.zeros((len(polys), V, 2))
    for i, p in enumerate(polys):
        out[i, :len(p)] = p
        out[i, len(p):] = p[-1]
    return out


def matrix(shape, rng, base=(0.955, 0.945, 0.93), grains=None, scale=1.0):
    H, W = shape
    img = np.ones((H, W, 3), np.float32) * np.array(base, np.float32)
    # cement cloudiness
    n = ndi.gaussian_filter(rng.standard_normal((H // 8 + 1, W // 8 + 1)), 3)
    n = ndi.zoom(n, 8, order=1)[:H, :W]
    n = n / (np.abs(n).max() + 1e-9)
    img *= (1 + 0.018 * n[..., None]).astype(np.float32)
    fine = ndi.gaussian_filter(rng.standard_normal((H, W)), 0.7)
    img *= (1 + 0.025 * fine / fine.std() * 0.5)[..., None].astype(np.float32)
    return img


def window_reflection(shape, cx=0.32, cy=0.22, w=0.30, h=0.36, strength=0.05, soft=0.08):
    H, W = shape
    y, x = np.mgrid[0:H, 0:W]
    u, v = x / W, y / H
    # skewed quad (a window seen across the polished surface)
    uu = u - cx - 0.25 * (v - cy)
    vv = v - cy
    def box(a, lo, hi, s):
        return 1 / (1 + np.exp(-(a - lo) / s)) * 1 / (1 + np.exp((a - hi) / s))
    r = box(uu, -w / 2, w / 2, soft * 0.3) * box(vv, -h / 2, h / 2, soft * 0.3)
    # mullions
    r *= 1 - 0.7 * np.exp(-((uu) / 0.006) ** 2) * 0
    return (strength * r).astype(np.float32)
