"""Guilloché enamel brooch renderer (Opus 5.5 run 21).

A silver plate engraved along the level sets of a homogeneous field G(z),
under domed translucent enamel (Beer-Lambert tint, thicker in the grooves),
gold cloisonné wires along given polylines, seed pearls, a milgrain bezel,
lying on cool white paper.  Orthographic camera looking straight down,
image-based lighting from a soft studio environment.
"""
import numpy as np
from numba import njit, prange
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- environment
@njit(cache=True, fastmath=True)
def env(dx, dy, dz):
    # soft studio: bright overall, a big softbox upper-left, a smaller one right,
    # a faint warm floor bounce; never dark (pastel brief)
    up = max(dz, 0.0)
    base = 0.62 + 0.20 * up
    # softbox 1 (upper left, elevation ~55 deg)
    lx, ly, lz = -0.50, 0.42, 0.757
    c1 = dx * lx + dy * ly + dz * lz
    s1 = 1.0 / (1.0 + np.exp(-(c1 - 0.86) * 38.0))
    # softbox 2 (right, lower, dimmer)
    mx, my, mz = 0.78, -0.10, 0.62
    c2 = dx * mx + dy * my + dz * mz
    s2 = 1.0 / (1.0 + np.exp(-(c2 - 0.90) * 40.0))
    return base + 0.95 * s1 + 0.45 * s2


@njit(cache=True, fastmath=True)
def reflect_env(nx, ny, nz):
    # view vector V = (0,0,1); reflected R = 2(n.V)n - V
    d = nz
    rx = 2 * d * nx
    ry = 2 * d * ny
    rz = 2 * d * nz - 1.0
    return env(rx, ry, rz)


# ---------------------------------------------------------------- the field
@njit(cache=True, fastmath=True)
def field(x, y, kpow, ksym):
    # G = |z|^(k-3) Re z^3 style homogeneous fields; returns signed |G|^(1/k)
    # kpow: degree; ksym: rotational order of the angular factor
    r2 = x * x + y * y
    r = np.sqrt(r2) + 1e-30
    th = np.arctan2(y, x)
    g = np.cos(ksym * th)
    s = 1.0 if g >= 0 else -1.0
    return s * r * np.abs(g) ** (1.0 / kpow), th, r


@njit(cache=True, fastmath=True)
def engrave(x, y, P):
    # P: [pitch_lines_per_unit, wave_amp, wave_n, kpow, ksym, mode, rays]
    u, th, r = field(x, y, P[3], P[4])
    lines = P[0]
    w = u * lines + P[1] * np.sin(P[2] * th)
    h = 0.5 - 0.5 * np.cos(2 * np.pi * w)
    if P[5] > 0.5:
        # basket: multiply by a fine sunray pattern (moiré of two families)
        v = 0.5 - 0.5 * np.cos(P[6] * th)
        h = h * (0.55 + 0.45 * v)
    return h, u


# ---------------------------------------------------------------- colour of enamel
@njit(cache=True, fastmath=True)
def lerp3(a, b, t):
    return a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t


@njit(cache=True, fastmath=True)
def ramp(pal, t):
    # pal: (n,3) colours; t in [0,1]
    n = pal.shape[0]
    t = min(max(t, 0.0), 1.0) * (n - 1)
    i = int(t)
    if i >= n - 1:
        i = n - 2
    f = t - i
    f = f * f * (3 - 2 * f)
    return (pal[i, 0] + (pal[i + 1, 0] - pal[i, 0]) * f,
            pal[i, 1] + (pal[i + 1, 1] - pal[i, 1]) * f,
            pal[i, 2] + (pal[i + 1, 2] - pal[i, 2]) * f)


@njit(cache=True, fastmath=True)
def gold_col(nx, ny, nz, gold, out, amb=1.0):
    nn = np.sqrt(nx * nx + ny * ny + nz * nz)
    L = reflect_env(nx / nn, ny / nn, nz / nn)
    k = (0.42 + 0.50 * L) * amb
    hi = max(L - 1.25, 0.0) * 0.9 * amb
    out[0] = gold[0] * k + hi
    out[1] = gold[1] * k + hi
    out[2] = gold[2] * k + hi


# ---------------------------------------------------------------- main shader
@njit(cache=True, fastmath=True)
def shade(px, py, W, H, cx, cy, Rin, Rbez, Rz, P, warm, cool, segs, grid, gcell, gofs,
          gidx, wire_w, pearls, gold, Nmil, Npearl, dome, depth, out):
    # returns rgb in out (linear, ~[0,1.4])
    dxp = px - cx
    dyp = cy - py
    rp = np.sqrt(dxp * dxp + dyp * dyp)
    # ---- paper + shadow
    if rp > Rbez:
        # shadow offset lower-right
        sx = dxp - 0.018 * Rbez
        sy = dyp + 0.026 * Rbez
        rs = np.sqrt(sx * sx + sy * sy)
        t = (rs - Rbez * 0.985) / (0.07 * Rbez)
        sh = 0.0
        if t < 0:
            sh = 1.0
        else:
            sh = np.exp(-t * t * 1.4)
        out[0] = 0.992 - 0.10 * sh
        out[1] = 0.985 - 0.13 * sh
        out[2] = 0.975 - 0.06 * sh
        return
    # ---- bezel
    if rp > Rin:
        q = (rp - Rin) / (Rbez - Rin)       # 0..1 across bezel
        # profile: inner bevel up, milgrain row, outer pearl row
        nxr = 0.0
        nzr = 1.0
        col_r, col_g, col_b = gold[0], gold[1], gold[2]
        ang = np.arctan2(dyp, dxp)
        ur = dxp / (rp + 1e-9)
        vr = dyp / (rp + 1e-9)
        if q < 0.28:
            # milgrain beads
            qq = (q - 0.14) / 0.14
            a = ang * Nmil / (2 * np.pi)
            fa = a - np.floor(a) - 0.5
            arc = fa * 2 * np.pi * (Rin + 0.14 * (Rbez - Rin)) / Nmil / (0.14 * (Rbez - Rin))
            d2 = qq * qq + arc * arc
            if d2 < 1.0:
                nzb = np.sqrt(1 - d2)
                # normal in (radial, tangential, z)
                nr = qq
                nt = arc
                nx = nr * ur - nt * vr
                ny = nr * vr + nt * ur
                gold_col(nx, ny, nzb, gold, out)
                return
            else:
                gold_col(0.0, 0.0, 1.0, gold, out, 0.80)
                return
        if q < 0.40:
            # polished band (convex)
            s = (q - 0.34) / 0.06
            nr = 0.55 * s
            nz = np.sqrt(max(1 - nr * nr, 0.05))
            gold_col(nr * ur, nr * vr, nz, gold, out)
            return
        # outer ring of seed pearls set in gold
        qq = (q - 0.70) / 0.30
        Rm = Rin + 0.70 * (Rbez - Rin)
        a = ang * Npearl / (2 * np.pi)
        fa = a - np.floor(a) - 0.5
        arc = fa * 2 * np.pi * Rm / Npearl / (0.30 * (Rbez - Rin))
        d2 = qq * qq + arc * arc
        if d2 < 0.92:
            nzb = np.sqrt(1 - d2)
            nx = qq * ur - arc * vr
            ny = qq * vr + arc * ur
            pearl_col(nx, ny, nzb, out)
            return
        # gold cup between pearls
        sq = (q - 0.70) / 0.30
        nr = 0.75 * sq
        cup = max(0.0, 1.0 - d2)
        gold_col(nr * ur, nr * vr, np.sqrt(max(1 - nr * nr, 0.05)), gold, out, 0.86 - 0.22 * np.exp(-(d2 - 0.92) * 8.0) + 0.1 * cup)
        return
    # ---- enamel field
    x = dxp / Rin * Rz
    y = dyp / Rin * Rz
    rho = rp / Rin
    # pearls on the enamel
    sh_p = 0.0
    for i in range(pearls.shape[0]):
        ddx = x - pearls[i, 0]
        ddy = y - pearls[i, 1]
        pr = pearls[i, 2]
        d2 = (ddx * ddx + ddy * ddy) / (pr * pr)
        if d2 < 1.0:
            nzb = np.sqrt(1 - d2)
            pearl_col(ddx / pr, ddy / pr, nzb, out, pearls[i, 3], pearls[i, 4], pearls[i, 5])
            return
        # contact shadow (offset lower-right)
        sdx = (ddx + 0.25 * pr) / pr
        sdy = (ddy - 0.35 * pr) / pr
        s2 = sdx * sdx + sdy * sdy
        if s2 < 4.0:
            sh_p = max(sh_p, np.exp(-(np.sqrt(s2) - 0.85) ** 2 * 6.0) if s2 > 0.72 else 1.0)
    # gold wires: nearest segment via grid
    best = 1e30
    bvx = 0.0
    bvy = 0.0
    gi = int((x + Rz) / gcell)
    gj = int((y + Rz) / gcell)
    ng = grid
    if gi >= 0 and gj >= 0 and gi < ng and gj < ng:
        c = gi * ng + gj
        for kk in range(gofs[c], gofs[c + 1]):
            s = gidx[kk]
            ax_ = segs[s, 0]
            ay_ = segs[s, 1]
            bx_ = segs[s, 2]
            by_ = segs[s, 3]
            ex = bx_ - ax_
            ey = by_ - ay_
            ll = ex * ex + ey * ey + 1e-30
            t = ((x - ax_) * ex + (y - ay_) * ey) / ll
            t = min(max(t, 0.0), 1.0)
            vx = x - (ax_ + t * ex)
            vy = y - (ay_ + t * ey)
            d = vx * vx + vy * vy
            if d < best:
                best = d
                bvx = vx
                bvy = vy
    dw = np.sqrt(best)
    if dw < wire_w:
        s = dw / wire_w
        nzw = np.sqrt(max(1 - s * s, 0.0))
        nx = bvx / (dw + 1e-30) * s
        ny = bvy / (dw + 1e-30) * s
        nzw += 0.15
        nn2 = np.sqrt(nx * nx + ny * ny + nzw * nzw)
        L = reflect_env(nx / nn2, ny / nn2, nzw / nn2)
        k = 0.42 + 0.50 * L
        hi = max(L - 1.25, 0.0) * 0.9
        out[0] = gold[0] * k + hi
        out[1] = gold[1] * k + hi
        out[2] = gold[2] * k + hi
        return
    wire_sh = 0.0
    if dw < 2.4 * wire_w:
        wire_sh = 1.0 - (dw - wire_w) / (1.4 * wire_w)
    # engraving normal by central differences
    e = 0.35 * Rz / Rin
    h0, u0 = engrave(x, y, P)
    h1, _ = engrave(x + e, y, P)
    h2, _ = engrave(x, y + e, P)
    gx = (h1 - h0) / e
    gy = (h2 - h0) / e
    gs = depth                       # groove depth in field units
    nx = -gs * gx
    ny = -gs * gy
    nn = np.sqrt(nx * nx + ny * ny + 1.0)
    nx /= nn
    ny /= nn
    nz = 1.0 / nn
    # metal reflection (silver)
    Lm = reflect_env(nx, ny, nz)
    # enamel colour: warm where G>0, cool where G<0, hue walk by radius
    tR = rho
    if u0 >= 0:
        cr, cg, cb = ramp(warm, tR)
    else:
        cr, cg, cb = ramp(cool, tR)
    # near the zero lines blend toward a milky white (the trivial solutions)
    zl = np.abs(u0) / (np.sqrt(x * x + y * y) + 1e-9)    # = |cos k th|^(1/k)
    wz = np.exp(-(zl / 0.42) ** 6)
    cr = cr + (0.97 - cr) * wz * 0.7
    cg = cg + (0.97 - cg) * wz * 0.7
    cb = cb + (0.985 - cb) * wz * 0.7
    # Beer-Lambert: target colour at reference thickness 1
    thick = 0.55 + 0.9 * (1.0 - h0)
    tr = np.exp(np.log(cr) * thick)
    tg = np.exp(np.log(cg) * thick)
    tb = np.exp(np.log(cb) * thick)
    silver_r, silver_g, silver_b = 0.96, 0.955, 0.95
    br = silver_r * Lm * tr
    bg = silver_g * Lm * tg
    bb = silver_b * Lm * tb
    # dome top-coat fresnel reflection
    dz_ = dome
    tnx = 2 * dz_ * dxp / Rin
    tny = 2 * dz_ * dyp / Rin
    tn = np.sqrt(tnx * tnx + tny * tny + 1)
    tnx /= tn
    tny /= tn
    tnz = 1 / tn
    cos = tnz
    Fr = 0.04 + 0.96 * (1 - cos) ** 5
    Lt = reflect_env(tnx, tny, tnz)
    # soft window reflection in the dome (stylised softbox), upper-left
    hx = tnx - (-0.17)
    hy = tny - 0.15
    win = np.exp(-((hx / 0.10) ** 2 + (hy / 0.075) ** 2) ** 2) * 0.22
    occl = 1.0 - 0.30 * sh_p - 0.22 * max(wire_sh, 0.0)
    # inner-rim shadow from the bezel lip
    rim = np.exp(-((1 - rho) / 0.018) ** 2) * 0.25
    occl -= rim
    out[0] = (br * occl) * (1 - Fr) + Fr * Lt * 1.1 + win
    out[1] = (bg * occl) * (1 - Fr) + Fr * Lt * 1.1 + win
    out[2] = (bb * occl) * (1 - Fr) + Fr * Lt * 1.1 + win


@njit(cache=True, fastmath=True)
def pearl_col(nx, ny, nz, out, tr=1.0, tg=0.95, tb=0.95):
    # pastel pearl: soft diffuse, iridescent rim, a gentle highlight
    lx, ly, lz = -0.45, 0.40, 0.80
    dif = max(nx * lx + ny * ly + nz * lz, 0.0)
    rim = (1 - nz) ** 2
    L = reflect_env(nx, ny, nz)
    base_r, base_g, base_b = tr, tg, tb
    ir = 0.5 + 0.5 * np.cos(6.0 * rim + 0.0)
    ig = 0.5 + 0.5 * np.cos(6.0 * rim + 2.1)
    ib = 0.5 + 0.5 * np.cos(6.0 * rim + 4.2)
    k = 0.80 + 0.28 * dif
    spec = max(L - 1.2, 0.0) * 0.8
    out[0] = base_r * k * (1 - 0.18 * rim) + 0.12 * rim * ir + spec
    out[1] = base_g * k * (1 - 0.18 * rim) + 0.12 * rim * ig + spec
    out[2] = base_b * k * (1 - 0.18 * rim) + 0.12 * rim * ib + spec


@njit(parallel=True, cache=True, fastmath=True)
def render(W, H, ss, cx, cy, Rin, Rbez, Rz, P, warm, cool, segs, grid, gcell, gofs, gidx,
           wire_w, pearls, gold, Nmil, Npearl, dome, depth, y0, y1):
    img = np.zeros((y1 - y0, W, 3), np.float32)
    for j in prange(y0, y1):
        out = np.zeros(3)
        for i in range(W):
            ar = 0.0
            ag = 0.0
            ab = 0.0
            for sj in range(ss):
                for si in range(ss):
                    # rotated-grid jitter
                    ox = (si + 0.5) / ss + 0.13 * ((sj % 2) - 0.5) / ss
                    oy = (sj + 0.5) / ss
                    shade(i + ox, j + oy, W, H, cx, cy, Rin, Rbez, Rz, P, warm, cool, segs,
                          grid, gcell, gofs, gidx, wire_w, pearls, gold, Nmil, Npearl, dome,
                          depth, out)
                    ar += out[0]
                    ag += out[1]
                    ab += out[2]
            n = ss * ss
            img[j - y0, i, 0] = ar / n
            img[j - y0, i, 1] = ag / n
            img[j - y0, i, 2] = ab / n
    return img


def build_grid(segs, Rz, wire_w, ng=256):
    """bucket segments into an ng x ng grid over [-Rz,Rz]^2 (with wire margin)."""
    gcell = 2 * Rz / ng
    buckets = [[] for _ in range(ng * ng)]
    m = 2.5 * wire_w
    for s, (ax, ay, bx, by) in enumerate(segs):
        i0 = int((min(ax, bx) - m + Rz) / gcell)
        i1 = int((max(ax, bx) + m + Rz) / gcell)
        j0 = int((min(ay, by) - m + Rz) / gcell)
        j1 = int((max(ay, by) + m + Rz) / gcell)
        for i in range(max(i0, 0), min(i1, ng - 1) + 1):
            for j in range(max(j0, 0), min(j1, ng - 1) + 1):
                buckets[i * ng + j].append(s)
    ofs = np.zeros(ng * ng + 1, np.int64)
    for c in range(ng * ng):
        ofs[c + 1] = ofs[c] + len(buckets[c])
    idx = np.zeros(max(ofs[-1], 1), np.int64)
    for c in range(ng * ng):
        idx[ofs[c]:ofs[c + 1]] = buckets[c]
    return ng, gcell, ofs, idx


def tonemap(img, exposure=1.0):
    x = np.clip(img * exposure, 0, None)
    # soft shoulder above 0.9
    y = np.where(x < 0.9, x, 0.9 + 0.1 * (1 - np.exp(-(x - 0.9) / 0.1)))
    y = np.clip(y, 0, 1)
    return (np.power(y, 1 / 1.12) * 255 + 0.5).astype(np.uint8)


def hexrgb(h):
    h = h.lstrip('#')
    return [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
