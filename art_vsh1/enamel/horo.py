"""Looking up out of the pretzel knot P(-2,3,7): the horoballs of its maximal cusp
seen from the cusp (upper half-space, view from infinity), as sugared pearls on
a white ground, with the canonical (Epstein-Penner) triangulation, dual to the
Ford domain, drawn as gold threads beneath them.  Data: SnapPy, K12n242 = m016.

usage: python3 horo.py OUT.png W H SS CUTOFF
"""
import sys, time, json
import numpy as np
from numba import njit, prange
from brooch import reflect_env, ramp, hexrgb, tonemap


def data(cutoff):
    import snappy
    M = snappy.Manifold('K12n242')
    C = M.cusp_neighborhood()
    C.set_displacement(C.stopping_displacement())
    hb = C.horoballs(cutoff)
    m, l = C.translations()
    m = complex(m)
    l = complex(l)
    # reduce the lattice: shortest vector not parallel to m
    best = None
    for k in range(-40, 41):
        v = l + k * m
        if best is None or abs(v) < abs(best):
            best = v
    l2 = best
    tri = C.triangulation()
    return hb, m, l2, tri, M.volume()


def tile(hb, tri, m, l2, x0, x1, y0, y1):
    balls = {}
    segs = []
    pad = 1.0
    for i in range(-12, 13):
        for j in range(-6, 7):
            t = i * m + j * l2
            for h in hb:
                c = h['center'] + t
                r = h['radius']
                if x0 - r < c.real < x1 + r and y0 - r < c.imag < y1 + r:
                    key = (round(c.real, 6), round(c.imag, 6))
                    balls[key] = (c.real, c.imag, r)
            for e in tri:
                a, b = e['endpoints']
                a = a + t
                b = b + t
                if (min(a.real, b.real) < x1 + pad and max(a.real, b.real) > x0 - pad and
                        min(a.imag, b.imag) < y1 + pad and max(a.imag, b.imag) > y0 - pad):
                    segs.append((a.real, a.imag, b.real, b.imag))
    segs = list({(round(s[0], 6), round(s[1], 6), round(s[2], 6), round(s[3], 6)) for s in segs})
    return np.array(list(balls.values())), np.array(segs)


def grid(objs, kind, x0, y0, cell, nx, ny):
    buckets = [[] for _ in range(nx * ny)]
    for s, o in enumerate(objs):
        if kind == 'ball':
            cx, cy, r = o
            m = r * 1.9   # include the shadow halo
            ax, bx, ay, by = cx - m, cx + m, cy - m, cy + m
        else:
            m = 0.02
            ax, bx = min(o[0], o[2]) - m, max(o[0], o[2]) + m
            ay, by = min(o[1], o[3]) - m, max(o[1], o[3]) + m
        i0 = max(int((ax - x0) / cell), 0)
        i1 = min(int((bx - x0) / cell), nx - 1)
        j0 = max(int((ay - y0) / cell), 0)
        j1 = min(int((by - y0) / cell), ny - 1)
        for i in range(i0, i1 + 1):
            for j in range(j0, j1 + 1):
                buckets[j * nx + i].append(s)
    ofs = np.zeros(nx * ny + 1, np.int64)
    for c in range(nx * ny):
        ofs[c + 1] = ofs[c] + len(buckets[c])
    idx = np.zeros(max(ofs[-1], 1), np.int64)
    for c in range(nx * ny):
        idx[ofs[c]:ofs[c + 1]] = buckets[c]
    return ofs, idx


@njit(cache=True, fastmath=True)
def shade(x, y, balls, bcol, bofs, bidx, segs, sofs, sidx, gx0, gy0, cell, nx, ny, wire, gold, out):
    i = int((x - gx0) / cell)
    j = int((y - gy0) / cell)
    if i < 0 or j < 0 or i >= nx or j >= ny:
        out[0] = 0.99
        out[1] = 0.985
        out[2] = 0.98
        return
    c = j * nx + i
    ar = 0.0
    ag = 0.0
    ab = 0.0
    glow = 0.0
    spec = 0.0
    occ = 1.0
    for kk in range(bofs[c], bofs[c + 1]):
        b = bidx[kk]
        dx = x - balls[b, 0]
        dy = y - balls[b, 1]
        r = balls[b, 2]
        d2 = (dx * dx + dy * dy) / (r * r)
        if d2 < 1.0:
            nz = np.sqrt(1 - d2)
            # glass: absorbance by normalised chord, same peak density for every size
            ar += bcol[b, 0] * nz
            ag += bcol[b, 1] * nz
            ab += bcol[b, 2] * nz
            rim = (1 - nz) ** 3
            glow += (0.10 + 0.9 * min(r / 0.5, 1.0)) * 0.35 * rim
            L = reflect_env(dx / r, dy / r, nz)
            spec = max(spec, max(L - 1.50, 0.0) * 1.2)
        else:
            # coloured shadow pool, light from upper-left
            sx = (dx + 0.30 * r) / r
            sy = (dy - 0.40 * r) / r
            q = sx * sx + sy * sy
            if q < 1.0:
                occ *= 1.0 - 0.10 * (1 - q)
    T0 = np.exp(-ar)
    T1 = np.exp(-ag)
    T2 = np.exp(-ab)
    # ground: white sugar paper, with gold threads of the canonical triangulation
    gr = 0.985
    gg = 0.975
    gb = 0.97
    best = 1e30
    for kk in range(sofs[c], sofs[c + 1]):
        s = sidx[kk]
        ax = segs[s, 0]
        ay = segs[s, 1]
        ex = segs[s, 2] - ax
        ey = segs[s, 3] - ay
        t = ((x - ax) * ex + (y - ay) * ey) / (ex * ex + ey * ey + 1e-30)
        t = min(max(t, 0.0), 1.0)
        vx = x - ax - t * ex
        vy = y - ay - t * ey
        d = vx * vx + vy * vy
        if d < best:
            best = d
    d = np.sqrt(best)
    if d < wire:
        s_ = d / wire
        L = 0.9 + 0.5 * np.sqrt(max(1 - s_ * s_, 0.0))
        gr = gold[0] * L
        gg = gold[1] * L
        gb = gold[2] * L
    elif d < 2.2 * wire:
        sh = 0.10 * (1 - (d - wire) / (1.2 * wire))
        gr -= sh
        gg -= sh
        gb -= sh * 0.5
    g = min(glow, 0.5)
    sp = min(spec, 1.0)
    out[0] = gr * occ * T0 * (1 - g) + g * 1.0 + sp
    out[1] = gg * occ * T1 * (1 - g) + g * 0.98 + sp
    out[2] = gb * occ * T2 * (1 - g) + g * 1.0 + sp


@njit(parallel=True, cache=True, fastmath=True)
def render(W, H, ss, X0, Y1, scale, balls, bcol, bofs, bidx, segs, sofs, sidx, gx0, gy0, cell, nx, ny,
           wire, gold, py0, py1):
    img = np.zeros((py1 - py0, W, 3), np.float32)
    for j in prange(py0, py1):
        out = np.zeros(3)
        for i in range(W):
            ar = 0.0
            ag = 0.0
            ab = 0.0
            for sj in range(ss):
                for si in range(ss):
                    x = X0 + (i + (si + 0.5) / ss) / scale
                    y = Y1 - (j + (sj + 0.5) / ss) / scale
                    shade(x, y, balls, bcol, bofs, bidx, segs, sofs, sidx, gx0, gy0, cell, nx, ny, wire,
                          gold, out)
                    ar += out[0]
                    ag += out[1]
                    ab += out[2]
            img[j - py0, i, 0] = ar / (ss * ss)
            img[j - py0, i, 1] = ag / (ss * ss)
            img[j - py0, i, 2] = ab / (ss * ss)
    return img


PAL = ["#fbeef4", "#ffd9e4", "#f8c6e6", "#dccbf6", "#c8d5f8", "#c4e8f4", "#ccf1e0", "#e6f4c4", "#fde8b0", "#ffd6b0"]


if __name__ == "__main__":
    out = sys.argv[1]
    W = int(sys.argv[2])
    H = int(sys.argv[3])
    ss = int(sys.argv[4])
    cutoff = float(sys.argv[5])
    span = float(sys.argv[6]) if len(sys.argv) > 6 else 5.0
    cxw = float(sys.argv[7]) if len(sys.argv) > 7 else 0.0
    cyw = float(sys.argv[8]) if len(sys.argv) > 8 else -0.4
    hb, m, l2, tri, vol = data(cutoff)
    print("m", m, "l'", l2, "vol", vol, "balls/domain", len(hb))
    scale = W / span
    X0 = cxw - span / 2
    X1 = cxw + span / 2
    Y1 = cyw + H / scale / 2
    Y0 = cyw - H / scale / 2
    balls, segs = tile(hb, tri, m, l2, X0, X1, Y0, Y1)
    print("balls", len(balls), "segs", len(segs))
    # colour by radius: log scale, biggest = pearl white
    rmax = balls[:, 2].max()
    t = np.log(rmax / balls[:, 2]) / np.log(rmax / balls[:, 2].min())
    pal = np.array([hexrgb(h) for h in PAL])
    bcol = -np.log(np.array([ramp(pal, tt) for tt in t])) * 1.25
    cell = 0.02
    nx = int((X1 - X0) / cell) + 3
    ny = int((Y1 - Y0) / cell) + 3
    gx0 = X0 - cell
    gy0 = Y0 - cell
    bofs, bidx = grid(balls, 'ball', gx0, gy0, cell, nx, ny)
    sofs, sidx = grid(segs, 'seg', gx0, gy0, cell, nx, ny)
    gold = np.array([0.98, 0.80, 0.50])
    t0 = time.time()
    img = render(W, H, ss, X0, Y1, scale, balls, bcol, bofs, bidx, segs, sofs, sidx, gx0, gy0, cell, nx, ny,
                 2.4 / scale * (W / 1400), gold, 0, H)
    print("render", time.time() - t0)
    np.save(out.replace('.png', '.npy'), img)
    from PIL import Image
    Image.fromarray(tonemap(img, 1.0)).save(out)
