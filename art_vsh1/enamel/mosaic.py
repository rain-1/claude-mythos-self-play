"""Hexagonal glazed-tile mosaic of a coin-flip Pascal triangle (MO 479618).

Row n, entry k sits at a pointy-top hexagon; its two parents are the two tiles
touching it from above, exactly the triangle's rule.  Heads (sum) tiles are
domed and glossy, tails (|difference|) tiles flat and satin; zeros are
missing tiles, so the grout bed shows through.  Colour = log of the value.

usage: python3 mosaic.py OUT.png SIZE SS ROWS P SEED
"""
import sys, time
import numpy as np
from numba import njit, prange
from brooch import env, reflect_env, ramp, hexrgb, tonemap

S3 = np.sqrt(3.0)


def triangle(N, p, seed):
    rng = np.random.default_rng(seed)
    T = np.zeros((N, N), np.float64)
    C = np.zeros((N, N), np.uint8)
    T[0, 0] = 1
    for n in range(1, N):
        T[n, 0] = T[n, n] = 1
        a = T[n - 1, :n - 1]
        b = T[n - 1, 1:n]
        c = rng.random(n - 1) < p
        T[n, 1:n] = np.where(c, a + b, np.abs(a - b))
        C[n, 1:n] = c
    return T, C


@njit(cache=True, fastmath=True)
def hexd(dx, dy):
    # pointy-top hexagon "radius" (apothem metric) and its gradient
    ax = abs(dx)
    ay = abs(dy)
    d1 = ax
    d2 = 0.5 * ax + 0.8660254 * ay
    if d1 >= d2:
        return d1, (1.0 if dx >= 0 else -1.0), 0.0
    return d2, (0.5 if dx >= 0 else -0.5), (0.8660254 if dy >= 0 else -0.8660254)


@njit(cache=True, fastmath=True)
def shade(px, py, x0, y0, pitch, N, T, C, col, out):
    # paper background
    out[0] = 0.992
    out[1] = 0.985
    out[2] = 0.975
    rowh = pitch * 0.8660254
    nf = (py - y0) / rowh
    best = 1e30
    bn = -1
    bk = -1
    bdx = 0.0
    bdy = 0.0
    for dn in range(-1, 2):
        n = int(np.floor(nf + 0.5)) + dn
        if n < 0 or n >= N:
            continue
        k = int(np.floor((px - x0) / pitch + n * 0.5 + 0.5))
        for dk in range(-1, 2):
            kk = k + dk
            if kk < 0 or kk > n:
                continue
            cx = x0 + (kk - n * 0.5) * pitch
            cy = y0 + n * rowh
            d, gx, gy = hexd(px - cx, py - cy)
            if d < best:
                best = d
                bn = n
                bk = kk
                bdx = px - cx
                bdy = py - cy
    a = 0.5 * pitch
    if bn < 0 or best > a * 1.02:
        return
    # inside the triangle's hex footprint: grout bed
    gr = 0.955
    out[0] = gr * 0.995
    out[1] = gr * 0.985
    out[2] = gr * 0.99
    gap = 0.085 * a
    e = a - gap - best                    # distance inside the tile edge
    v = T[bn, bk]
    if v <= 0 or e < 0:
        # grout: tiny shadow next to tiles
        sh = 0.0
        if v > 0:
            sh = min(1.0, -e / gap)
            sh = 0.12 * (1 - sh)
        out[0] -= sh
        out[1] -= sh
        out[2] -= sh * 0.6
        return
    d, gx, gy = hexd(bdx, bdy)
    bev = 0.16 * a
    glossy = C[bn, bk] == 1 or bk == 0 or bk == bn
    # height profile: bevel + dome for glossy tiles
    s = min(e / bev, 1.0)
    slope = 0.0
    if s < 1.0:
        slope = 1.2 * (1 - s) ** 2
    nx = gx * slope
    ny = gy * slope
    rr = np.sqrt(bdx * bdx + bdy * bdy) / a
    if glossy:
        nx += 0.30 * bdx / a
        ny += 0.30 * bdy / a
    # screen y down -> world y up
    ny = -ny
    nn = np.sqrt(nx * nx + ny * ny + 1.0)
    nx /= nn
    ny /= nn
    nz = 1.0 / nn
    cr = col[bn, bk, 0]
    cg = col[bn, bk, 1]
    cb = col[bn, bk, 2]
    # diffuse from the softbox direction
    lx, ly, lz = -0.42, 0.40, 0.81
    dif = max(nx * lx + ny * ly + nz * lz, 0.0)
    k = 0.70 + 0.36 * dif
    # glaze pooling: deeper colour toward the edge (thicker glaze)
    pool = 1.0 + 0.35 * (1 - s)
    tr = cr ** pool
    tg = cg ** pool
    tb = cb ** pool
    r = tr * k
    g = tg * k
    b = tb * k
    L = reflect_env(nx, ny, nz)
    if glossy:
        Fr = 0.04 + 0.96 * (1 - nz) ** 5
        sp = max(L - 1.15, 0.0) * 1.1
        r = r * (1 - Fr) + Fr * L + sp
        g = g * (1 - Fr) + Fr * L + sp
        b = b * (1 - Fr) + Fr * L + sp
    else:
        sp = max(L - 1.2, 0.0) * 0.15
        r += sp
        g += sp
        b += sp
    out[0] = r
    out[1] = g
    out[2] = b


@njit(parallel=True, cache=True, fastmath=True)
def render(W, H, ss, x0, y0, pitch, N, T, C, col):
    img = np.zeros((H, W, 3), np.float32)
    for j in prange(H):
        out = np.zeros(3)
        for i in range(W):
            ar = 0.0
            ag = 0.0
            ab = 0.0
            for sj in range(ss):
                for si in range(ss):
                    shade(i + (si + 0.5) / ss, j + (sj + 0.5) / ss, x0, y0, pitch, N, T, C, col, out)
                    ar += out[0]
                    ag += out[1]
                    ab += out[2]
            img[j, i, 0] = ar / (ss * ss)
            img[j, i, 1] = ag / (ss * ss)
            img[j, i, 2] = ab / (ss * ss)
    return img


SORBET = ["#ffeaa0", "#ffd590", "#ffc8a8", "#ffb3bd", "#f5b0d8", "#dcb8f2", "#c0c6f7", "#b5dcf5", "#bdeedd", "#d8f5c0"]


def colours(T, vmax=None):
    N = T.shape[0]
    pal = np.array([hexrgb(h) for h in SORBET])
    L = np.log2(np.maximum(T, 1))
    if vmax is None:
        vmax = np.percentile(L[np.tril_indices(N)], 99.5) + 1e-9
    col = np.zeros((N, N, 3))
    for n in range(N):
        for k in range(n + 1):
            t = min(L[n, k] / vmax, 1.0)
            col[n, k] = ramp(pal, t)
    return col


if __name__ == "__main__":
    out = sys.argv[1]
    S = int(sys.argv[2])
    ss = int(sys.argv[3])
    N = int(sys.argv[4])
    p = float(sys.argv[5])
    seed = int(sys.argv[6])
    T, C = triangle(N, p, seed)
    col = colours(T)
    W = S
    H = int(S * 1.0)
    width = 0.90 * W
    pitch = width / N
    x0 = W / 2
    y0 = 0.06 * H + pitch / 2
    t0 = time.time()
    img = render(W, H, ss, x0, y0, pitch, N, T, C, col)
    print("render", time.time() - t0, "max", T.max())
    from PIL import Image
    from caption import caption
    np.save(out.replace('.png', '_T.npy'), T)
    im = Image.fromarray(tonemap(img, 1.0))
    if len(sys.argv) > 7:
        caption(im, sys.argv[7], sys.argv[8], sys.argv[9], int(H * 0.885), line3=sys.argv[10] if len(sys.argv) > 10 else None)
    im.save(out)
