"""Perspective view of the basin: pinhole camera, exact refraction through the wave surface to the
mosaic floor / tiled wall, Fresnel reflection of a pastel sky with sun glints, coping and paving."""
import numpy as np
from numba import njit, prange
import pool


@njit(cache=True)
def bilin(img, u, v):
    H, W = img.shape[0], img.shape[1]
    u = min(max(u, 0.0), W - 1.001); v = min(max(v, 0.0), H - 1.001)
    i = int(u); j = int(v); du = u - i; dv = v - j
    return (img[j, i] * (1 - du) * (1 - dv) + img[j, i + 1] * du * (1 - dv)
            + img[j + 1, i] * (1 - du) * dv + img[j + 1, i + 1] * du * dv)


@njit(cache=True)
def sky(dx, dy, dz, sx, sy, sz):
    # pastel dome: periwinkle at the zenith, rose then butter at the horizon, warm glow round the sun
    e = max(dz, 0.0)
    t = 1.0 - e
    r = 0.78 + 0.20 * t ** 1.5
    g = 0.83 + 0.10 * t ** 1.5
    b = 1.00 - 0.06 * t ** 2
    c = dx * sx + dy * sy + dz * sz
    glow = np.exp((c - 1.0) / 0.08) * 0.35
    return r + glow, g + glow * 0.95, b + glow * 0.8


@njit(parallel=True, cache=True)
def trace(Wd, Hd, eye, fwd, right, up, fov, K, phi, a, A, depth, R, rimw, cope, eta,
          floor_alb, floor_caus, fx0, fpx, sun, ss, seed):
    out = np.zeros((Hd, Wd, 3))
    alpha_w = np.zeros((Hd, Wd))  # water mask (for compositing reflections of boats)
    sx, sy, sz = sun[0], sun[1], sun[2]   # direction TOWARD the sun
    tanf = np.tan(fov / 2)
    aspect = Wd / Hd
    for j in prange(Hd):
        for i in range(Wd):
            acc0 = 0.0; acc1 = 0.0; acc2 = 0.0; wacc = 0.0
            for s in range(ss * ss):
                ox = ((s % ss) + 0.5 + 0.3 * np.sin(s * 12.9898 + i * 0.1)) / ss
                oy = ((s // ss) + 0.5 + 0.3 * np.sin(s * 78.233 + j * 0.1)) / ss
                px = (2 * (i + ox) / Wd - 1) * tanf * aspect
                py = (1 - 2 * (j + oy) / Hd) * tanf
                dx = fwd[0] + px * right[0] + py * up[0]
                dy = fwd[1] + px * right[1] + py * up[1]
                dz = fwd[2] + px * right[2] + py * up[2]
                nn = np.sqrt(dx * dx + dy * dy + dz * dz)
                dx /= nn; dy /= nn; dz /= nn
                c0, c1, c2, isw = shade(eye[0], eye[1], eye[2], dx, dy, dz, K, phi, a, A, depth, R, rimw, cope,
                                        eta, floor_alb, floor_caus, fx0, fpx, sx, sy, sz)
                acc0 += c0; acc1 += c1; acc2 += c2; wacc += isw
            n = ss * ss
            out[j, i, 0] = acc0 / n; out[j, i, 1] = acc1 / n; out[j, i, 2] = acc2 / n
            alpha_w[j, i] = wacc / n
    return out, alpha_w


@njit(cache=True)
def wall_tile(th, z, depth, R):
    # small square tiles on the inner wall: white with every fourth row a pale sky blue
    s = R * th / 0.024
    zz = (z + depth) / 0.024
    fu = s - np.floor(s); fv = zz - np.floor(zz)
    d = min(min(fu, 1 - fu), min(fv, 1 - fv))
    g = 1.0 if d > 0.07 else 0.9
    row = int(np.floor(zz))
    if row % 4 == 3:
        return 0.80 * g, 0.90 * g, 1.0 * g
    return 0.97 * g, 0.96 * g, 0.95 * g


@njit(cache=True)
def shade(ex, ey, ez, dx, dy, dz, K, phi, a, A, depth, R, rimw, cope, eta, falb, fcaus, fx0, fpx, sx, sy, sz):
    ambr, ambg, ambb = 0.80, 0.78, 0.80
    sunr, sung, sunb = 1.0, 0.95, 0.86
    if dz >= 0:
        r_, g_, b_ = sky(dx, dy, dz, sx, sy, sz)
        return r_, g_, b_, 0.0
    # plane of the coping / paving
    t = (cope - ez) / dz
    x = ex + t * dx; y = ey + t * dy
    r = np.sqrt(x * x + y * y)
    if r >= R:
        # coping ring or paving (flat, lit), with a rounded inner nose
        ndl = sz
        if r < R + rimw:
            q = (r - R) / rimw
            # stripes of glazed tiles
            th = np.arctan2(y, x)
            k = int(np.floor((th / (2 * np.pi) + 0.5) * 96))
            if k % 2 == 0:
                cr, cg, cb = 0.99, 0.97, 0.96
            else:
                cr, cg, cb = 1.0, 0.86, 0.84
            # rounded profile: normal tilts inward near the water
            tilt = (1 - q) ** 2 * 0.9
            nx = -x / r * tilt; ny = -y / r * tilt; nz = 1.0
            l = np.sqrt(nx * nx + ny * ny + 1); nx /= l; ny /= l; nz /= l
            ndl = max(nx * sx + ny * sy + nz * sz, 0.0)
            # glossy glaze highlight
            hx = sx - dx; hy = sy - dy; hz = sz - dz
            hl = np.sqrt(hx * hx + hy * hy + hz * hz)
            spec = max((nx * hx + ny * hy + nz * hz) / hl, 0.0) ** 400 * 1.2
            lit = 0.55 + 0.6 * ndl
            return cr * lit * ambr + spec, cg * lit * ambg + spec, cb * lit * ambb + spec, 0.0
        rr = r - (R + rimw)
        if rr > 0.30:
            # lawn: soft mint with a mown stripe and a scatter of tiny daisies
            q = (np.sin(x * 211.0 + np.sin(y * 97.0)) * 43758.5) % 1.0
            st = 1.0
            fl = 0.0
            cx = np.floor(x / 0.018); cy = np.floor(y / 0.018)
            hh = (np.sin(cx * 12.9898 + cy * 78.233) * 43758.5453) % 1.0
            if hh > 0.93:
                ox = (cx + 0.5) * 0.018 - x; oy = (cy + 0.5) * 0.018 - y
                if ox * ox + oy * oy < (0.0035) ** 2:
                    fl = 1.0
            lit = (0.62 + 0.55 * sz) * (0.97 + 0.03 * q) * st
            if fl > 0:
                hue = (hh * 37.0) % 1.0
                if hue < 0.33:
                    return 1.0 * lit, 0.80 * lit, 0.84 * lit, 0.0
                elif hue < 0.66:
                    return 1.0 * lit, 0.98 * lit, 0.94 * lit, 0.0
                return 1.0 * lit, 0.90 * lit, 0.62 * lit, 0.0
            return 0.70 * lit, 0.88 * lit, 0.70 * lit, 0.0
        # paving: big pale-peach slabs in rings
        ring = np.floor(rr / 0.07)
        th = np.arctan2(y, x)
        nseg = max(12.0, np.round(2 * np.pi * (R + rimw + (ring + 0.5) * 0.07) / 0.09))
        u = (th / (2 * np.pi) + 0.5 + ring * 0.37) * nseg
        seg = np.floor(u)
        hsh = (np.sin(ring * 91.7 + seg * 13.3) * 43758.5) % 1.0
        fr = rr / 0.07 - ring; fs = u - seg
        dd = min(min(fr, 1 - fr) * 0.07, min(fs, 1 - fs) * 2 * np.pi * (R + rimw + rr) / nseg)
        jt = 0.88 if dd < 0.0018 else 1.0
        base = (0.95 + 0.05 * hsh) * jt
        # soft shadow of the coping lip falls away from the sun just outside the ring
        shd = 1.0
        if rr < 0.02:
            shd = 0.80 + 0.2 * rr / 0.02
        lit = (0.70 + 0.50 * sz) * shd
        return 0.99 * base * lit, 0.90 * base * lit, 0.84 * base * lit, 0.0
    # inside the ring at coping height: continue down to the water plane, maybe hitting the inner wall
    t0 = -ez / dz
    x0 = ex + t0 * dx; y0 = ey + t0 * dy
    if x0 * x0 + y0 * y0 > R * R:
        # wall between water and coping (above water line): solve |p + s d| = R
        bq = x * dx + y * dy; aq = dx * dx + dy * dy; cq = x * x + y * y - R * R
        sq = (-bq + np.sqrt(max(bq * bq - aq * cq, 0.0))) / aq
        zw = cope + sq * dz
        th = np.arctan2(y + sq * dy, x + sq * dx)
        cr, cg, cb = wall_tile(th, zw, depth, R)
        return cr * 0.85, cg * 0.85, cb * 0.88, 0.0
    # water surface: fixed-point for z = A*h(x,y)
    tt = t0
    for it in range(4):
        xx = ex + tt * dx; yy = ey + tt * dy
        sr, si, gx, gy, hxx, hxy, hyy, ur, ui = pool.field(xx, yy, K, phi, a)
        tt = (A * sr - ez) / dz
    xx = ex + tt * dx; yy = ey + tt * dy; zz = ez + tt * dz
    sr, si, gx, gy, hxx, hxy, hyy, ur, ui = pool.field(xx, yy, K, phi, a)
    nx = -A * gx; ny = -A * gy; nz = 1.0
    l = np.sqrt(nx * nx + ny * ny + 1); nx /= l; ny /= l; nz /= l
    tx, ty, tz, T = pool.refract(nx, ny, nz, dx, dy, dz, eta)
    Fr = 1 - T
    # reflection
    dn = dx * nx + dy * ny + dz * nz
    rx = dx - 2 * dn * nx; ry = dy - 2 * dn * ny; rz = dz - 2 * dn * nz
    if rz < 0.02:
        rz = 0.02
    kr, kg, kb = sky(rx, ry, rz, sx, sy, sz)
    # reflected coping: rays that leave low toward the rim see the pink-white coping instead of sky
    tr = (cope * 0.6 - zz) / rz
    qx = xx + tr * rx; qy = yy + tr * ry
    if qx * qx + qy * qy > R * R and rz < 0.35:
        kr, kg, kb = 0.95, 0.88, 0.88
    cs = rx * sx + ry * sy + rz * sz
    glint = np.exp((cs - 1.0) / 1.5e-5) * 60.0 + np.exp((cs - 1.0) / 6e-4) * 1.2
    if tz == 0.0:
        return kr + glint, kg + glint, kb + glint, 1.0
    # refracted ray to the floor or the wall
    tf = (-depth - zz) / tz
    fx = xx + tf * tx; fy = yy + tf * ty
    path = tf
    if fx * fx + fy * fy > R * R:
        bq = xx * tx + yy * ty; aq = tx * tx + ty * ty; cq = xx * xx + yy * yy - R * R
        sq = (-bq + np.sqrt(max(bq * bq - aq * cq, 0.0))) / aq
        zw = zz + sq * tz
        th = np.arctan2(yy + sq * ty, xx + sq * tx)
        cr, cg, cb = wall_tile(th, zw, depth, R)
        # walls get sky light and a little scattered caustic light
        lr = ambr * 0.9 + 0.12; lg = ambg * 0.9 + 0.12; lb = ambb * 0.9 + 0.12
        cr *= lr; cg *= lg; cb *= lb
        path = sq
    else:
        u = (fx - fx0) / fpx - 0.5; v = (fy - fx0) / fpx - 0.5
        cr = bilin(falb[:, :, 0], u, v); cg = bilin(falb[:, :, 1], u, v); cb = bilin(falb[:, :, 2], u, v)
        ir = bilin(fcaus[:, :, 0], u, v); ig = bilin(fcaus[:, :, 1], u, v); ib = bilin(fcaus[:, :, 2], u, v)
        cr *= 0.72 + sunr * ir; cg *= 0.71 + sung * ig; cb *= 0.74 + sunb * ib
    # pale aqua water
    cr *= np.exp(-0.9 * path); cg *= np.exp(-0.28 * path); cb *= np.exp(-0.22 * path)
    return (cr * (1 - Fr) + Fr * kr + glint, cg * (1 - Fr) + Fr * kg + glint, cb * (1 - Fr) + Fr * kb + glint, 1.0)
