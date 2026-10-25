"""Hot-air balloon festival over a still lake — numba ray-marcher.

Scene units are metres; y up, camera looks roughly +z.
Balloon envelope = solid of revolution (sphere crown, cosine taper to a mouth),
coloured panels between azimuth boundaries (arbitrary widths), 24 physical gores
that bulge between load tapes, cables + wicker basket. Translucent nylon: light
from behind the fabric glows through in its own colour.
Background = sky gradient + sun + wispy clouds, layered hill 'curtains' with
aerial perspective and valley mist, and a lake that reflects everything.
"""
import numpy as np
from numba import njit, prange
import math

# ---------------------------------------------------------------- noise
@njit(cache=True, inline='always')
def _h(i, j, s):
    n = (i * 374761393 + j * 668265263 + s * 2147483647) & 0xFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
    n = n ^ (n >> 16)
    return (n & 0xFFFFFF) / 16777216.0

@njit(cache=True)
def vnoise(x, y, s):
    i = math.floor(x); j = math.floor(y)
    fx = x - i; fy = y - j
    ux = fx * fx * (3 - 2 * fx); uy = fy * fy * (3 - 2 * fy)
    i = int(i); j = int(j)
    a = _h(i, j, s); b = _h(i + 1, j, s); c = _h(i, j + 1, s); d = _h(i + 1, j + 1, s)
    return a + (b - a) * ux + (c - a) * uy + (a - b - c + d) * ux * uy

@njit(cache=True)
def fbm(x, y, s, oct):
    v = 0.0; a = 0.5; f = 1.0; tot = 0.0
    for o in range(oct):
        v += a * vnoise(x * f, y * f, s + o * 17)
        tot += a; a *= 0.5; f *= 2.03
    return v / tot

# ---------------------------------------------------------------- balloon profile (unit R)
ZTOP = 1.0
ZMOUTH = -1.5
RMOUTH = 0.2

@njit(cache=True)
def prof(z):
    """radius of envelope at height z (unit balloon), and d rho/dz"""
    if z >= 0.0:
        r2 = 1.0 - z * z
        if r2 <= 0: return 0.0, -1e3
        r = math.sqrt(r2)
        return r, -z / r
    t = -z / 1.5
    if t > 1: t = 1.0
    c = math.cos(0.5 * math.pi * t)
    if c < 1e-6: c = 1e-6
    r = RMOUTH + (1 - RMOUTH) * c ** 1.3
    drdt = (1 - RMOUTH) * 1.3 * c ** 0.3 * (-math.sin(0.5 * math.pi * t)) * 0.5 * math.pi
    return r, drdt * (-1.0 / 1.5)

def build_sdf(res=0.004):
    """signed distance in (rho, z) plane for the envelope solid, unit R."""
    from scipy.ndimage import distance_transform_edt
    rho = np.arange(-0.1, 1.4, res)
    zz = np.arange(-2.2, 1.3, res)
    R, Z = np.meshgrid(rho, zz, indexing='xy')  # [nz, nrho]
    inside = np.zeros(R.shape, bool)
    for k, z in enumerate(zz):
        if ZMOUTH <= z <= ZTOP:
            r, _ = prof(z)
            inside[k] = np.abs(rho) <= r
    dout = distance_transform_edt(~inside) * res
    din = distance_transform_edt(inside) * res
    sdf = (dout - din).astype(np.float32)
    return sdf, rho[0], zz[0], res

@njit(cache=True, inline='always')
def sdf_env(sdf, r0, z0, res, rho, z):
    fx = (rho - r0) / res; fy = (z - z0) / res
    nx = sdf.shape[1]; ny = sdf.shape[0]
    if fx < 0 or fy < 0 or fx >= nx - 1 or fy >= ny - 1:
        # outside the grid: crude bound
        dx = max(rho - 1.3, 0.0); dz = max(z - 1.2, -2.1 - z, 0.0)
        return math.sqrt(dx * dx + dz * dz) + 0.05
    i = int(fx); j = int(fy); ax = fx - i; ay = fy - j
    a = sdf[j, i]; b = sdf[j, i + 1]; c = sdf[j + 1, i]; d = sdf[j + 1, i + 1]
    return (a * (1 - ax) + b * ax) * (1 - ay) + (c * (1 - ax) + d * ax) * ay

@njit(cache=True, inline='always')
def sd_capsule(px, py, pz, ax, ay, az, bx, by, bz, r):
    pax = px - ax; pay = py - ay; paz = pz - az
    bax = bx - ax; bay = by - ay; baz = bz - az
    h = (pax * bax + pay * bay + paz * baz) / (bax * bax + bay * bay + baz * baz)
    if h < 0: h = 0.0
    if h > 1: h = 1.0
    dx = pax - bax * h; dy = pay - bay * h; dz = paz - baz * h
    return math.sqrt(dx * dx + dy * dy + dz * dz) - r

@njit(cache=True, inline='always')
def sd_box(px, py, pz, hx, hy, hz):
    qx = abs(px) - hx; qy = abs(py) - hy; qz = abs(pz) - hz
    ox = max(qx, 0.0); oy = max(qy, 0.0); oz = max(qz, 0.0)
    return math.sqrt(ox * ox + oy * oy + oz * oz) + min(max(qx, max(qy, qz)), 0.0)

BASK_TOP = -1.86
BASK_BOT = -2.0
BASK_H = 0.105

@njit(cache=True)
def sd_balloon(sdf, r0, z0, res, x, y, z):
    """unit-balloon local coords; returns (dist, part) part 0 env,1 cable,2 basket"""
    rho = math.sqrt(x * x + z * z)
    d = sdf_env(sdf, r0, z0, res, rho, y)
    part = 0
    # basket
    db = sd_box(x, y - 0.5 * (BASK_TOP + BASK_BOT), z, BASK_H, 0.5 * (BASK_TOP - BASK_BOT), BASK_H) - 0.008
    if db < d:
        d = db; part = 2
    if rho < 0.32 and y < -1.4 and y > -1.9:
        for k in range(4):
            a = (k + 0.5) * 0.5 * math.pi
            ca = math.cos(a); sa = math.sin(a)
            dc = sd_capsule(x, y, z, RMOUTH * 0.97 * ca, ZMOUTH + 0.01, RMOUTH * 0.97 * sa,
                            BASK_H * 0.95 * ca * 1.41, BASK_TOP, BASK_H * 0.95 * sa * 1.41, 0.006)
            if dc < d:
                d = dc; part = 1
    return d, part

# ---------------------------------------------------------------- scene globals packed in arrays
# B: [nb, 8] = cx, cy, cz, R, yaw, tilt, burner, seed
# GB: [nb, 65] panel boundaries in [0,1) (cumulative), GN [nb] panel count, GC [nb,64,3] colours

@njit(cache=True)
def hit_balloons(ox, oy, oz, dx, dy, dz, B, sdf, r0, z0, res, tmax, skip):
    best = tmax; bi = -1; bpart = 0
    nb = B.shape[0]
    for b in range(nb):
        if b == skip: continue
        cx = B[b, 0]; cy = B[b, 1]; cz = B[b, 2]; R = B[b, 3]
        # bounding sphere centred at local y=-0.5, radius 1.75
        sx = cx - ox; sy = cy - 0.5 * R - oy; sz = cz - oz
        tc = sx * dx + sy * dy + sz * dz
        rr = 1.75 * R
        d2 = sx * sx + sy * sy + sz * sz - tc * tc
        if d2 > rr * rr: continue
        th = math.sqrt(rr * rr - d2)
        t0 = tc - th; t1 = tc + th
        if t1 < 1e-3 or t0 > best: continue
        if t0 < 1e-3: t0 = 1e-3
        t = t0
        cyaw = math.cos(B[b, 4]); syaw = math.sin(B[b, 4])
        for it in range(160):
            px = (ox + dx * t - cx) / R; py = (oy + dy * t - cy) / R; pz = (oz + dz * t - cz) / R
            lx = cyaw * px + syaw * pz; lz = -syaw * px + cyaw * pz
            d, part = sd_balloon(sdf, r0, z0, res, lx, py, lz)
            if d < 4e-4:
                if t < best:
                    best = t; bi = b; bpart = part
                break
            t += d * R * 0.9
            if t > t1 or t > best: break
    return best, bi, bpart

# ---------------------------------------------------------------- environment
@njit(cache=True)
def sky(dx, dy, dz, P):
    # P: sun(3) , zen(3), mid(3), hor(3), sunc(3), cloud params
    sx = P[0]; sy = P[1]; sz = P[2]
    e = dy
    if e < 0: e = 0.0
    zen_w = e ** 0.55
    hr = P[9]; hg = P[10]; hb = P[11]
    mr = P[6]; mg = P[7]; mb = P[8]
    zr = P[3]; zg = P[4]; zb = P[5]
    if zen_w < 0.35:
        u = zen_w / 0.35
        r = hr + (mr - hr) * u; g = hg + (mg - hg) * u; b = hb + (mb - hb) * u
    else:
        u = (zen_w - 0.35) / 0.65
        r = mr + (zr - mr) * u; g = mg + (zg - mg) * u; b = mb + (zb - mb) * u
    cs = dx * sx + dy * sy + dz * sz
    if cs < -1: cs = -1.0
    glow = 0.22 * max(cs, 0.0) ** 6 + 0.5 * max(cs, 0.0) ** 60 + 3.0 * max(cs, 0.0) ** 900
    disc = 0.0
    if cs > 0.99993: disc = 18.0
    r += (glow + disc) * P[12]; g += (glow + disc) * P[13]; b += (glow + disc) * P[14]
    # clouds on a plane
    if dy > 0.01:
        t = P[15] / dy
        cx = dx * t / P[16]; cz = dz * t / P[16]
        n = fbm(cx * 1.0 + 3.1, cz * 1.3, 7, 6)
        n2 = fbm(cx * 3.0 + 9.0, cz * 6.0, 11, 4)
        c = (n - P[17]) * 5.0 + 0.3 * (n2 - 0.5)
        if c > 0:
            if c > 1: c = 1.0
            c = c * c * (3 - 2 * c) * P[18]
            fade = min(1.0, dy * 12.0)
            c *= fade
            # shade by density gradient toward the sun: lit tops, lilac undersides
            nb_ = fbm(cx * 1.0 + 3.1 + 0.02, cz * 1.3 + 0.02, 7, 6)
            sl = (n - nb_) * 40.0
            sh_ = max(min(sl, 1.0), -1.0)
            lit = 1.0 + 0.08 * max(cs, 0.0) ** 3 + 0.06 * sh_
            und = 0.5 - 0.5 * sh_
            cr = (1.0 - 0.10 * und) * lit; cg = (0.965 - 0.12 * und) * lit; cb = (0.975 - 0.02 * und) * lit
            r = r * (1 - c) + cr * c; g = g * (1 - c) + cg * c; b = b * (1 - c) + cb * c
    return r, g, b

@njit(cache=True)
def ridge_h(L, x, Hh):
    # Hh: [nl, 8] = z, base, amp, freq, seed, r,g,b
    return Hh[L, 1] + Hh[L, 2] * (fbm(x * Hh[L, 3], 0.37 * L, int(Hh[L, 4]), 5) - 0.35)

@njit(cache=True)
def hills(ox, oy, oz, dx, dy, dz, Hh, tmax):
    """returns t, layer, hx, hy (hit position on layer plane)"""
    best = tmax; lay = -1; hx = 0.0; hy = 0.0
    if dz <= 1e-6: return best, lay, hx, hy
    for L in range(Hh.shape[0]):
        t = (Hh[L, 0] - oz) / dz
        if t <= 0 or t >= best: continue
        x = ox + dx * t; y = oy + dy * t
        if y < -1.0: continue
        h = ridge_h(L, x, Hh)
        if y < h:
            best = t; lay = L; hx = x; hy = y
    return best, lay, hx, hy

@njit(cache=True)
def hill_col(L, x, y, Hh, P, haze_r, haze_g, haze_b, sx):
    h = ridge_h(L, x, Hh)
    z = Hh[L, 0]
    r = Hh[L, 5]; g = Hh[L, 6]; b = Hh[L, 7]
    depth = h - y  # metres below ridge
    # sunlit ridge rim + gentle darkening downwards
    rel = depth / max(Hh[L, 2], 1.0)
    shade = 1.06 - 0.16 * min(rel, 1.5)
    # patchwork fields on near layers
    if L >= Hh.shape[0] - 3:
        u = x / (60.0 + 25 * L); v = depth / 14.0
        f = vnoise(u + 0.3 * v, v * 0.6, 91 + L)
        k = int(f * 4.0)
        if k == 0:
            r = r * 0.96 + 0.04; g = g * 1.0; b = b * 0.92
        elif k == 1:
            r = r * 1.04 + 0.02; g = g * 1.02; b = b * 0.86
        elif k == 2:
            r = r * 0.94; g = g * 1.03; b = b * 0.98
        # tree dots near ridge
        tt = vnoise(x / 3.5, depth / 3.5, 300 + L)
        if tt > 0.72 and depth < 30:
            m = (tt - 0.72) / 0.28
            r *= 1 - 0.18 * m; g *= 1 - 0.08 * m; b *= 1 - 0.12 * m
    r *= shade; g *= shade; b *= shade
    # valley mist at the base, aerial perspective by distance
    mist = math.exp(-(y - 0.0) / (5.0 + 0.008 * z))
    a = 1.0 - math.exp(-z / P[19])
    a = a + (1 - a) * 0.7 * mist
    r = r * (1 - a) + haze_r * a; g = g * (1 - a) + haze_g * a; b = b * (1 - a) + haze_b * a
    return r, g, b

# ---------------------------------------------------------------- balloon shading
@njit(cache=True)
def balloon_shade(b, part, px, py, pz, dx, dy, dz, B, GB, GN, GC, sdf, r0, z0, res, P, Hh):
    cx = B[b, 0]; cy = B[b, 1]; cz = B[b, 2]; R = B[b, 3]
    cyaw = math.cos(B[b, 4]); syaw = math.sin(B[b, 4])
    gx = (px - cx) / R; gy = (py - cy) / R; gz = (pz - cz) / R
    lx = cyaw * gx + syaw * gz; lz = -syaw * gx + cyaw * gz
    ly = gy
    sx = P[0]; sy = P[1]; sz = P[2]
    if part == 0:
        rho = math.sqrt(lx * lx + lz * lz) + 1e-9
        phi = math.atan2(lz, lx)
        u = (phi / (2 * math.pi)) % 1.0
        # local normal from analytic profile
        if ly <= ZMOUTH + 0.003 and rho < RMOUTH * 0.98:
            nlx = 0.0; nly = -1.0; nlz = 0.0; mouth = True
        else:
            mouth = False
            r, drdz = prof(ly)
            nr = 1.0; nz = -drdz
            nn = math.sqrt(nr * nr + nz * nz); nr /= nn; nz /= nn
            # gore bulge
            NG = 24.0
            gu = (u * NG) % 1.0
            bul = 0.22 * math.cos(math.pi * gu) * min(1.0, (rho / 0.35))
            tx = -lz / rho; tz = lx / rho
            nlx = nr * lx / rho + bul * tx * (-1.0)
            nlz = nr * lz / rho + bul * tz * (-1.0)
            nly = nz
            nn = math.sqrt(nlx * nlx + nly * nly + nlz * nlz)
            nlx /= nn; nly /= nn; nlz /= nn
        # panel colour
        ng = GN[b]
        k = 0
        for i in range(ng):
            if u >= GB[b, i]: k = i
        ar = GC[b, k, 0]; ag = GC[b, k, 1]; ab = GC[b, k, 2]
        # white seams between colour panels and at physical gores
        du = min(u - GB[b, k], (GB[b, k + 1] if k + 1 < ng else 1.0) - u) * 2 * math.pi * rho
        seam = 0.0
        if du < 0.012: seam = 1.0 - du / 0.012
        gu2 = (u * 24.0) % 1.0
        dg = min(gu2, 1 - gu2) * 2 * math.pi * rho / 24.0
        if dg < 0.006: seam = max(seam, 0.6 * (1 - dg / 0.006))
        # horizontal load tapes
        for zt in (0.62, 0.0, -0.75):
            dzt = abs(ly - zt)
            if dzt < 0.008: seam = max(seam, 0.5 * (1 - dzt / 0.008))
        ar = ar + (0.99 - ar) * seam; ag = ag + (0.97 - ag) * seam; ab = ab + (0.96 - ab) * seam
        if mouth:
            ar = 0.95; ag = 0.72; ab = 0.66
        # back to world normal
        nx = cyaw * nlx - syaw * nlz; nz2 = syaw * nlx + cyaw * nlz; ny = nly
    elif part == 1:
        ar = 0.42; ag = 0.36; ab = 0.38
        nx = -dx; ny = -dy; nz2 = -dz
    else:
        # wicker basket
        wv = math.sin(lx * 260) * math.sin(ly * 300) + math.sin(lz * 260) * math.sin(ly * 300 + 1.0)
        ar = 0.80 + 0.06 * wv; ag = 0.64 + 0.05 * wv; ab = 0.46 + 0.04 * wv
        if ly > BASK_TOP - 0.018:
            ar = 0.66; ag = 0.50; ab = 0.40
        # box normal
        ax = abs(lx); az = abs(lz)
        yy = ly - 0.5 * (BASK_TOP + BASK_BOT)
        if ax > az and ax > abs(yy) * 1.4:
            nlx = 1.0 if lx > 0 else -1.0; nly = 0.0; nlz = 0.0
        elif az >= ax and az > abs(yy) * 1.4:
            nlx = 0.0; nly = 0.0; nlz = 1.0 if lz > 0 else -1.0
        else:
            nlx = 0.0; nly = 1.0 if yy > 0 else -1.0; nlz = 0.0
        nx = cyaw * nlx - syaw * nlz; nz2 = syaw * nlx + cyaw * nlz; ny = nly
    # face the viewer for the two-sided cases
    ndv = nx * dx + ny * dy + nz2 * dz
    front = ndv < 0
    ndl = nx * sx + ny * sy + nz2 * sz
    # shadow toward the sun (other balloons)
    sh = 1.0
    ts, bs, _ = hit_balloons(px + nx * 0.02 * R, py + ny * 0.02 * R, pz + nz2 * 0.02 * R, sx, sy, sz,
                             B, sdf, r0, z0, res, 1e5, b)
    if bs >= 0: sh = 0.5
    # self-shadow for basket/cables under the envelope: occluded when sun ray hits own envelope
    if part != 0:
        ts2, bs2, _ = hit_balloons(px + sx * 0.03 * R, py + sy * 0.03 * R, pz + sz * 0.03 * R, sx, sy, sz,
                                   B[b:b + 1], sdf, r0, z0, res, 1e5, -1)
        if bs2 >= 0: sh = min(sh, 0.25)
    suncr = P[12] * 2.1; suncg = P[13] * 2.1; suncb = P[14] * 2.1
    diff = max(ndl, 0.0)
    # sky ambient
    up = 0.5 + 0.5 * ny
    ambr = (P[9] * (1 - up) + P[3] * up) * 0.75 + 0.10 * (1 - up)
    ambg = (P[10] * (1 - up) + P[4] * up) * 0.75 + 0.14 * (1 - up)
    ambb = (P[11] * (1 - up) + P[5] * up) * 0.75 + 0.10 * (1 - up)
    r = ar * (ambr + suncr * diff * sh)
    g = ag * (ambg + suncg * diff * sh)
    bb = ab * (ambb + suncb * diff * sh)
    if part == 0:
        # translucency: sun behind the fabric (relative to viewer)
        if ndl < 0:
            tr = (-ndl) ** 1.2 * 0.85 * sh
            r += ar * ar * suncr * tr; g += ag * ag * suncg * tr; bb += ab * ab * suncb * tr
        # nylon sheen
        hx = sx - dx; hy = sy - dy; hz = sz - dz
        hn = math.sqrt(hx * hx + hy * hy + hz * hz)
        sp = max((nx * hx + ny * hy + nz2 * hz) / hn, 0.0) ** 40 * 0.25 * sh
        r += sp * suncr; g += sp * suncg; bb += sp * suncb
        # burner glow in the mouth
        if ly < -1.0 and B[b, 6] > 0:
            gl = B[b, 6] * math.exp(-(ly - ZMOUTH) * 6.0)
            r += gl * 1.0 * ar; g += gl * 0.55 * ag; bb += gl * 0.25 * ab
    return r, g, bb

# ---------------------------------------------------------------- trace one ray (with one lake bounce)
@njit(cache=True)
def trace_dry(ox, oy, oz, dx, dy, dz, B, GB, GN, GC, sdf, r0, z0, res, P, Hh):
    """balloons / hills / sky. returns colour and lake-hit distance (or -1)"""
    haze_r = P[9] * 0.97 + 0.03; haze_g = P[10] * 0.98 + 0.02; haze_b = P[11]
    tmax = 1e6
    tb, bi, part = hit_balloons(ox, oy, oz, dx, dy, dz, B, sdf, r0, z0, res, tmax, -1)
    th, lay, hx, hy = hills(ox, oy, oz, dx, dy, dz, Hh, tmax)
    tl = 1e9
    if dy < -1e-6:
        tl = -oy / dy
    t = min(tb, th, tl)
    if t >= 1e5:
        r, g, b = sky(dx, dy, dz, P)
        return r, g, b, -1.0
    if tb <= th and tb <= tl and bi >= 0:
        px = ox + dx * tb; py = oy + dy * tb; pz = oz + dz * tb
        r, g, b = balloon_shade(bi, part, px, py, pz, dx, dy, dz, B, GB, GN, GC, sdf, r0, z0, res, P, Hh)
        a = 1.0 - math.exp(-tb / (P[19] * 1.6))
        return r * (1 - a) + haze_r * a, g * (1 - a) + haze_g * a, b * (1 - a) + haze_b * a, -1.0
    if th <= tl and lay >= 0:
        r, g, b = hill_col(lay, hx, hy, Hh, P, haze_r, haze_g, haze_b, P[0])
        return r, g, b, -1.0
    return P[20], P[21], P[22], tl

@njit(cache=True)
def trace(ox, oy, oz, dx, dy, dz, B, GB, GN, GC, sdf, r0, z0, res, P, Hh):
    haze_r = P[9] * 0.97 + 0.03; haze_g = P[10] * 0.98 + 0.02; haze_b = P[11]
    r, g, b, tl = trace_dry(ox, oy, oz, dx, dy, dz, B, GB, GN, GC, sdf, r0, z0, res, P, Hh)
    if tl < 0:
        return r, g, b
    px = ox + dx * tl; pz = oz + dz * tl
    sc = P[24]
    e = 0.05
    n0 = fbm(px * sc * 0.2, pz * sc, 501, 4)
    nxp = fbm((px + e) * sc * 0.2, pz * sc, 501, 4)
    nzp = fbm(px * sc * 0.2, (pz + e) * sc, 501, 4)
    wind = fbm(px * 0.004, pz * 0.02, 77, 3)
    amp = P[23] * (0.3 + 1.6 * max(wind - 0.35, 0.0)) * (1.0 + P[26] * math.exp(-tl / P[27])) * (0.25 + 0.75 * math.exp(-tl / 500.0))
    gx = (nxp - n0) / e * amp; gz = (nzp - n0) / e * amp
    nx = -gx; ny = 1.0; nz = -gz
    nn = math.sqrt(nx * nx + ny * ny + nz * nz); nx /= nn; ny /= nn; nz /= nn
    dn = dx * nx + dy * ny + dz * nz
    rx = dx - 2 * dn * nx; ry = dy - 2 * dn * ny; rz = dz - 2 * dn * nz
    if ry < 0.002: ry = 0.002
    c = -dn
    if c < 0: c = 0.0
    F = 0.02 + 0.98 * (1 - c) ** 5
    F = P[25] + (1 - P[25]) * F
    rr, rg, rb, _ = trace_dry(px, 0.01, pz, rx, ry, rz, B, GB, GN, GC, sdf, r0, z0, res, P, Hh)
    wr = P[20]; wg = P[21]; wb = P[22]
    r = rr * F + wr * (1 - F); g = rg * F + wg * (1 - F); b = rb * F + wb * (1 - F)
    a = 1.0 - math.exp(-tl / P[19])
    return r * (1 - a) + haze_r * a, g * (1 - a) + haze_g * a, b * (1 - a) + haze_b * a

@njit(parallel=True, cache=True)
def render(W, H, spp, cam, B, GB, GN, GC, sdf, r0, z0, res, P, Hh, seed):
    img = np.zeros((H, W, 3), np.float32)
    ox = cam[0]; oy = cam[1]; oz = cam[2]
    fx_ = cam[3]; fy_ = cam[4]; fz_ = cam[5]
    ux = cam[6]; uy = cam[7]; uz = cam[8]
    rx = cam[9]; ry = cam[10]; rz = cam[11]
    tanf = cam[12]
    ss = int(math.sqrt(spp))
    for j in prange(H):
        for i in range(W):
            ar = 0.0; ag = 0.0; ab = 0.0
            for s in range(ss * ss):
                jx = ((s % ss) + _h(i, j, seed + s)) / ss
                jy = ((s // ss) + _h(j, i, seed + 7 * s + 3)) / ss
                u = ((i + jx) / W * 2 - 1) * tanf
                v = (1 - (j + jy) / H * 2) * tanf * H / W
                dx = fx_ + u * rx + v * ux; dy = fy_ + u * ry + v * uy; dz = fz_ + u * rz + v * uz
                n = math.sqrt(dx * dx + dy * dy + dz * dz)
                r, g, b = trace(ox, oy, oz, dx / n, dy / n, dz / n, B, GB, GN, GC, sdf, r0, z0, res, P, Hh)
                ar += r; ag += g; ab += b
            img[j, i, 0] = ar / (ss * ss); img[j, i, 1] = ag / (ss * ss); img[j, i, 2] = ab / (ss * ss)
    return img

def camera(pos, look, fov_deg):
    pos = np.array(pos, float); f = np.array(look, float) - pos; f /= np.linalg.norm(f)
    r = np.cross(np.array([0, 1.0, 0]), f); r /= np.linalg.norm(r)
    u = np.cross(f, r)
    return np.array([*pos, *f, *u, *r, math.tan(math.radians(fov_deg) / 2)], np.float64)
