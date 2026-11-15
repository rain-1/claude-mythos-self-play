"""The Wythoff arcade: piers at 1,2,3,...; the k-th arch has span k and stands on the first
free pier.  Every pier carries exactly one arch, every span occurs exactly once (MO 453577).
usage: python3 arcade.py SIZE out.png [seed]"""
import sys, numpy as np
from math import isqrt
from mosaic import *

def wythoff(k):
    a = (k + isqrt(5 * k * k)) // 2
    return a, a + k

def build(size, seed=4):
    M = Mosaic(size, seed); S = M.S; X, Y = M.X, M.Y
    h = 17.0 * S                               # tessera
    # ---------------- layout
    x0, x1, y0, y1 = 210 * S, 3886 * S, 210 * S, 3500 * S        # picture box
    XL, XR = 0.30, 22.70
    U = (x1 - x0) / (XR - XL)                   # pixels per pier
    yw = y0 + 0.56 * (y1 - y0)                  # waterline
    px = lambda t: x0 + (t - XL) * U
    sunx, suny, sunr = px(5.4), yw - 6.6 * U, 1.05 * U
    arcs = []
    k = 1
    while True:
        a, b = wythoff(k)
        if a > XR: break
        arcs.append((k, px((a + b) / 2), k * U / 2)); k += 1
    band = 1.5 * h                               # half thickness of the gold

    def sky(x, y):
        """the cartoon of the dawn: colour as a function of place"""
        d = np.hypot(x - sunx, y - suny) / U
        up = np.clip((yw - y) / (yw - y0), 0, 1)
        stops = [(0.0, C("apr0")), (1.6, C("apr0")), (2.6, C("apr1")), (3.9, C("apr2")), (5.2, C("ros0")), (6.6, C("ros1")),
                 (8.2, C("mau0")), (10.0, C("mau1")), (12.2, C("lap2")), (14.5, C("lap1")), (18.0, C("lap0"))]
        # the horizon stays warm: distance is stretched upward, compressed along the water
        dd = d * (0.62 + 0.75 * up ** 0.8) + 2.2 * up ** 2
        out = np.zeros(x.shape + (3,), np.float32)
        for (a0, c0), (a1, c1) in zip(stops[:-1], stops[1:]):
            t = np.clip((dd - a0) / (a1 - a0), 0, 1)[..., None]
            m = (dd >= a0)[..., None]
            out = np.where(m, c0 * (1 - t) + c1 * t, out)
        return out

    def arch_hit(x, y):
        """index (1-based k) of the front-most arch whose gold covers (x,y), 0 if none; y above water"""
        hit = np.zeros(x.shape, np.int32)
        for k, cx, R in reversed(arcs):
            hit = np.where(np.abs(np.hypot(x - cx, y - yw) - R) < band, k, hit)
        return hit

    inbox = (X > x0) & (X < x1) & (Y > y0) & (Y < y1)
    # ---------------- sky: rows are rings about the sun
    T, xc, yc = polar_tess(X, Y, sunx, suny, h, 101, w=1.08 * h)
    rho = np.hypot(xc - sunx, yc - suny)
    col = sky(xc, yc)
    insun = rho < sunr
    col = np.where(insun[..., None], np.where((rho < sunr - 2 * h)[..., None], C("gol0"), C("gol1")), col)
    ring = (rho >= sunr) & (rho < sunr + h)
    col = np.where(ring[..., None], C("mar0"), col)
    star = (col.sum(-1) < 0.95) & (rnd(T.id, 77) < 0.011) & (yc < yw - 3 * h)
    col = np.where(star[..., None], C("gol0"), col)
    m = inbox & (Y < yw)
    M.lay(m, T, col, mat=np.where(insun | star, 1, 0).astype(np.uint8))
    # a few birds? no: the sky is left to the rings.
    # ---------------- sea: rows are swells
    sw = 0.42 * h * np.sin(X / (5.3 * h) + 2.1 * np.sin(Y / (9.0 * h))) + 0.25 * h * np.sin(X / (2.3 * h) + Y / (3.1 * h))
    T = tess(X, (Y - yw) + sw * np.clip((Y - yw) / (3 * h), 0, 1), h, 202, w=1.25 * h)
    xc = T.uc; yc = yw + T.vc
    depth = (yc - yw) / (y1 - yw)
    rr = rnd(T.id, 41); r2 = rnd(T.id, 42); rowr = rnd(T.row, 43)
    wob = (rowr - 0.5) * 2 * (0.10 + 0.9 * depth) * 0.55 * U
    xm = xc + wob; ym = 2 * yw - yc                      # the mirrored point
    refl = sky(xm, np.maximum(ym, y0 + 1))
    deep = (1 - depth)[..., None] * C("tur2") + depth[..., None] * C("lap0")
    kf = np.clip(0.80 - 0.50 * depth, 0, 1)[..., None]
    col = refl * kf * np.array([0.86, 0.84, 0.90], np.float32) + deep * (1 - kf) * np.array([0.9, 1.0, 1.1], np.float32)
    sat = col.mean(-1, keepdims=True); col = sat + (col - sat) * 1.45          # keep the water from going to mud
    # swell shadows: every few rows a darker band
    dark = (np.sin(T.row * 0.9 + 1.3 * np.sin(xc / (11 * h))) > 0.55)
    col = np.where(dark[..., None], col * 0.72 + 0.28 * C("tur0"), col)
    # reflections of the arches, broken by the swell
    hk = arch_hit(xm, ym)
    seen = (hk > 0) & (rr < 0.92 - 0.75 * depth) & ~dark
    gcol = np.where((hk == 1)[..., None], C("red1"), C("gol2") * 0.92)
    col = np.where(seen[..., None], gcol, col)
    # the sun's road
    road = np.exp(-((xc - sunx) / (0.55 * U + 1.3 * U * depth)) ** 2) * (0.75 - 0.35 * depth)
    sunm = (ym < suny + sunr) & (np.hypot(xm - sunx, ym - suny) < sunr)
    glit = ((r2 < road * 0.55) | sunm) & ~seen
    col = np.where(glit[..., None], np.where((rnd(T.id, 44) < 0.5)[..., None], C("gol0"), C("apr0")), col)
    m = inbox & (Y >= yw)
    M.lay(m, T, col, mat=np.where(glit | seen, 1, 2).astype(np.uint8))
    # ---------------- arches (largest first; smaller stand in front)
    fig = np.zeros((size, size), bool)
    for k, cx, R in reversed(arcs):
        xa = int(max(0, cx - R - 4 * h)); xb = int(min(size, cx + R + 4 * h)) + 1
        ya = int(max(0, yw - R - 4 * h)); yb = int(yw) + 1
        sl = (slice(ya, yb), slice(xa, xb))
        Xs, Ys = X[sl], Y[sl]
        # rows: [-2.5h,-1.5h) sky halo | [-1.5h,-0.5h) white | [-0.5h,1.5h) gold | [1.5h,2.5h) outline
        T, xc, yc = polar_tess(Xs, Ys, cx, yw, h, 300 + k, w=1.15 * h, r0=R - 2.5 * h - 40 * h)
        row = T.row - 40
        colr = np.zeros(Xs.shape + (3,), np.float32)
        colr[:] = sky(xc, yc)
        main = C("red0") if k == 1 else C("gol1")
        lo = C("red1") if k == 1 else C("gol2")
        colr = np.where((row == 1)[..., None], C("mar0"), colr)
        colr = np.where((row == 2)[..., None], main, colr)
        colr = np.where((row == 3)[..., None], lo, colr)
        colr = np.where((row == 4)[..., None], C("umb1"), colr)
        mat = np.where((row == 2) | (row == 3), 1, 0).astype(np.uint8)
        m = (row >= 0) & (row <= 5) & (Ys < yw) & inbox[sl]
        M.lay(m, T, colr, mat=mat, sl=sl)
        fig[sl] |= m
    M.cut(fig | ~inbox | (Y >= yw))
    # ---------------- piers: one dark stone at each foot on the waterline
    # (the waterline itself is a seam; piers are marked by a row of marble along it)
    T = tess(X - x0, Y - (yw - 0.5 * h), h, 404, w=1.2 * h)
    m = inbox & (np.abs(Y - yw) < 0.5 * h)
    xc = T.uc + x0
    t = (xc - x0) / U + XL
    near = np.abs(t - np.round(t)) * U < 0.62 * h
    col = np.where(near[..., None], C("umb1"), C("mar1"))
    M.lay(m, T, col)
    # ---------------- border: marble, a dark fillet, marble
    bw = 3 * h
    bo = (X > x0 - bw) & (X < x1 + bw) & (Y > y0 - bw) & (Y < y1 + bw) & ~inbox
    d = np.maximum(np.maximum(x0 - X, X - x1), np.maximum(y0 - Y, Y - y1))    # distance outside the box
    horiz = np.maximum(y0 - Y, Y - y1) >= np.maximum(x0 - X, X - x1)
    T = tess(np.where(horiz, X, Y), d + 50 * h, h, 505 + horiz.astype(np.int32), w=1.1 * h)
    row = T.row - 50
    col = np.where((row == 1)[..., None], C("lap0"), C("mar0"))
    M.lay(bo, T, col)
    M.cut(horiz & bo, sl=None)
    M.cut(inbox)
    # ---------------- the surround: a marble slab with the inscription
    out_m = ~inbox & ~bo
    slab = marble(size, seed + 9)
    txt = text_mask(size, [
        ("EVERY ARCH A DIFFERENT SPAN", size / 2, 3742 * S, 104 * S, "Regular", 15 * S),
        ("Fourteen arches on twenty-two piers: each pier carries one arch, and the spans are 1, 2, 3, … with none repeated.",
         size / 2, 3850 * S, 49 * S, "Italic", 0.6 * S),
        ("Each arch was put on the first free pier. Nobody chose where; the feet fall at ⌊kφ⌋ and ⌊kφ²⌋.",
         size / 2, 3922 * S, 49 * S, "Italic", 0.6 * S),
    ])
    slab = incise(slab, txt, S)
    # the bed of the mosaic is sunk a little: a soft shadow on the slab's inner edge
    dout = ndi.distance_transform_edt(out_m).astype(np.float32)
    slab *= (1 - 0.18 * np.exp(-dout / (10 * S)))[..., None]
    M.mat[out_m] = 9; M.rgb[out_m] = slab[out_m]
    return M

if __name__ == "__main__":
    size = int(sys.argv[1]); out = sys.argv[2]; seed = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    M = build(size, seed)
    img = M.finish()
    # keep slab pixels unquantised
    save(img, out)
