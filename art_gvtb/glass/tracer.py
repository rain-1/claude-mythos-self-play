"""Suncatcher tracer: stained-glass panels + a glass geodesic globe on a sunlit sill.

Geometry (z up, y away from the camera):
  table / sill  z = 0, y < YW
  back wall     y = YW with a window opening; sun shines in through it
  panels        flat stained-glass triangles hanging in vertical-ish planes
  globe         convex polyhedron of stained-glass faces (thin panes, air inside)
Rendering: camera rays (thin lens, jittered) + a photon-mapped sun light map on the sill.
"""
import numpy as np, numba as nb
from numba import njit, prange

INF = 1e30


@njit(cache=True, fastmath=True)
def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


@njit(cache=True, fastmath=True)
def panel_hit(o, d, PO, PU, PV, PN, half, res, k):
    dn = d[0] * PN[k, 0] + d[1] * PN[k, 1] + d[2] * PN[k, 2]
    if abs(dn) < 1e-9:
        return INF, -1, -1
    t = ((PO[k, 0] - o[0]) * PN[k, 0] + (PO[k, 1] - o[1]) * PN[k, 1] + (PO[k, 2] - o[2]) * PN[k, 2]) / dn
    if t <= 1e-6:
        return INF, -1, -1
    px = o[0] + t * d[0] - PO[k, 0]
    py = o[1] + t * d[1] - PO[k, 1]
    pz = o[2] + t * d[2] - PO[k, 2]
    a = px * PU[k, 0] + py * PU[k, 1] + pz * PU[k, 2]
    b = px * PV[k, 0] + py * PV[k, 1] + pz * PV[k, 2]
    i = int((half - b) / (2 * half) * (res - 1) + 0.5)
    j = int((a + half) / (2 * half) * (res - 1) + 0.5)
    if i < 0 or j < 0 or i >= res or j >= res:
        return INF, -1, -1
    return t, i, j


@njit(cache=True, fastmath=True)
def globe_hit(o, d, GN, GD, gc):
    # convex polytope {x : GN.(x-gc) <= GD}
    t0 = -INF; t1 = INF; f0 = -1; f1 = -1
    for p in range(GN.shape[0]):
        dn = GN[p, 0] * d[0] + GN[p, 1] * d[1] + GN[p, 2] * d[2]
        on = GN[p, 0] * (o[0] - gc[0]) + GN[p, 1] * (o[1] - gc[1]) + GN[p, 2] * (o[2] - gc[2])
        if abs(dn) < 1e-12:
            if on > GD[p]:
                return INF, INF, -1, -1
            continue
        t = (GD[p] - on) / dn
        if dn < 0:
            if t > t0:
                t0 = t; f0 = p
        else:
            if t < t1:
                t1 = t; f1 = p
    if t0 > t1 or t1 < 1e-6:
        return INF, INF, -1, -1
    return t0, t1, f0, f1


@njit(cache=True, fastmath=True)
def globe_edge(x, GN, GD, gc, f):
    # smallest slack to any other plane at point x on face f (distance to the face's edges, approx)
    best = 1e9
    for p in range(GN.shape[0]):
        if p == f:
            continue
        s = GD[p] - (GN[p, 0] * (x[0] - gc[0]) + GN[p, 1] * (x[1] - gc[1]) + GN[p, 2] * (x[2] - gc[2]))
        c = GN[p, 0] * GN[f, 0] + GN[p, 1] * GN[f, 1] + GN[p, 2] * GN[f, 2]
        sn = np.sqrt(max(1e-6, 1 - c * c))
        s = s / sn
        if s < best:
            best = s
    return best


@njit(cache=True, fastmath=True)
def _h2(i, j):
    h = (i * 374761393 + j * 668265263) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return (h & 0xFFFF) / 65535.0


@njit(cache=True, fastmath=True)
def vnoise(x, y):
    i = int(np.floor(x)); j = int(np.floor(y))
    fx = x - i; fy = y - j
    fx = fx * fx * (3 - 2 * fx); fy = fy * fy * (3 - 2 * fy)
    a = _h2(i, j); b = _h2(i + 1, j); c = _h2(i, j + 1); e = _h2(i + 1, j + 1)
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + e * fx) * fy


@njit(cache=True, fastmath=True)
def fbm(x, y):
    s = 0.0; a = 0.5
    for o in range(5):
        s += a * vnoise(x, y)
        x = x * 2.03 + 17.1; y = y * 2.01 + 3.7; a *= 0.5
    return s


@njit(cache=True, fastmath=True)
def sky(d, sun, prm):
    # prm: sun_size, sun_power
    e = d[2]
    hz = np.empty(3)
    if e < 0:
        # a pastel sea: pale at the horizon, aqua below, sky-coloured by Fresnel
        g = min(1.0, -e * 4.5)
        fr = 0.25 + 0.75 * np.exp(-(-e) * 14.0)
        hz[0] = (0.50 * (1 - g) + 0.42 * g) * (1 - fr) + 0.98 * fr
        hz[1] = (0.86 * (1 - g) + 0.80 * g) * (1 - fr) + 0.95 * fr
        hz[2] = (0.88 * (1 - g) + 0.86 * g) * (1 - fr) + 0.96 * fr
        # sun glitter: mirror the sun in a rough sea
        az = np.arctan2(d[0], d[1]) - np.arctan2(sun[0], sun[1])
        ew = -e
        dz = (ew - sun[2] * 0.95)
        lobe = np.exp(-(az * az) / (2 * (0.03 + 0.25 * ew) ** 2)) * np.exp(-dz * dz / 0.05)
        # hashed glitter cells
        ca = int(az * 2200.0 + 100000); ce = int(ew * 5200.0)
        hsh = ((ca * 73856093) ^ (ce * 19349663)) & 1048575
        sp = 0.0
        if hsh < 26000:
            sp = 7.0 * (hsh / 26000.0)
        gl = lobe * (0.25 + sp)
        hz[0] += gl * 1.0; hz[1] += gl * 0.95; hz[2] += gl * 0.85
    else:
        s = min(1.0, e / 0.35)
        s = np.sqrt(s)
        hz[0] = 1.00 * (1 - s) + 0.62 * s
        hz[1] = 0.90 * (1 - s) + 0.76 * s
        hz[2] = 0.88 * (1 - s) + 1.00 * s
        # soft pastel cumulus, flattened toward the horizon
        az = np.arctan2(d[0], d[1])
        cl = fbm(az * 5.0 + 3.0, (e + 0.02) * 26.0 / (0.3 + 3.0 * e))
        cv = min(1.0, max(0.0, (cl - 0.50) / 0.18))
        cv = cv * cv * (3 - 2 * cv) * min(1.0, e * 30.0)
        hz[0] = hz[0] * (1 - cv) + 1.04 * cv
        hz[1] = hz[1] * (1 - cv) + 0.97 * cv
        hz[2] = hz[2] * (1 - cv) + 0.98 * cv
    cs = d[0] * sun[0] + d[1] * sun[1] + d[2] * sun[2]
    glow = np.exp((cs - 1) * 18.0) * 0.55 + np.exp((cs - 1) * 120.0) * 0.9
    disc = 0.0
    if cs > np.cos(prm[0]):
        disc = prm[1]
    out = np.empty(3)
    out[0] = hz[0] * 1.05 + glow * 1.0 + disc
    out[1] = hz[1] * 1.05 + glow * 0.93 + disc * 0.97
    out[2] = hz[2] * 1.05 + glow * 0.80 + disc * 0.9
    return out


@njit(cache=True, fastmath=True)
def wall_hit(o, d, YW, WIN):
    # back wall plane y = YW ; returns t and whether inside the window opening
    if d[1] <= 1e-9:
        return INF, False
    t = (YW - o[1]) / d[1]
    if t < 1e-6:
        return INF, False
    x = o[0] + t * d[0]; z = o[2] + t * d[2]
    inwin = (x > WIN[0]) and (x < WIN[1]) and (z > WIN[2]) and (z < WIN[3])
    return t, inwin


@njit(cache=True, fastmath=True)
def propagate(o, d, thr, PO, PU, PV, PN, FID, LEAD, HW, RG, FT, half, ramp,
              GN, GD, gc, GF, YW, WIN, TB, TH, for_photon):
    """March a ray through glass. Returns (kind, point, dir, thr, extra)
    kind: 0 sky, 1 table, 2 lead(panel), 3 wall, 4 lead(globe), 5 frame-wall-of-window
    extra: (panel index, lead coordinate, halfwidth) for shading."""
    K = PO.shape[0]
    res = FID.shape[1]
    p = np.empty(3)
    ex = np.zeros(4)
    for bounce in range(14):
        tb = INF; kind = 0
        # table
        if d[2] < -1e-9:
            t = -o[2] / d[2]
            x = o[0] + t * d[0]; y = o[1] + t * d[1]
            if t > 1e-6 and y < YW and y > TB[0] and x > TB[1] and x < TB[2]:
                tb = t; kind = 1
        tw, inwin = wall_hit(o, d, YW, WIN)
        if tw < tb and not inwin:
            tb = tw; kind = 3
        kp = -1; ip = 0; jp = 0
        for k in range(K):
            t, i, j = panel_hit(o, d, PO, PU, PV, PN, half, res, k)
            if t < tb:
                if FID[k, i, j] >= 0 or LEAD[k, i, j] < 0:
                    tb = t; kind = 10; kp = k; ip = i; jp = j
        for m in range(TH.shape[0]):
            # vertical thread cylinder through (TH0, TH1) above z = TH2
            ox = o[0] - TH[m, 0]; oy = o[1] - TH[m, 1]
            A = d[0] * d[0] + d[1] * d[1]
            if A < 1e-12:
                continue
            Bq = ox * d[0] + oy * d[1]
            Cq = ox * ox + oy * oy - TH[m, 3] * TH[m, 3]
            disc = Bq * Bq - A * Cq
            if disc < 0:
                continue
            t = (-Bq - np.sqrt(disc)) / A
            if t > 1e-6 and t < tb and o[2] + t * d[2] > TH[m, 2]:
                tb = t; kind = 5
                ex[0] = (Bq + A * t) / np.sqrt(A) / TH[m, 3]
        g0, g1, gf0, gf1 = globe_hit(o, d, GN, GD, gc)
        if g0 > 1e-6 and g0 < tb:
            tb = g0; kind = 20
        elif g0 <= 1e-6 and g1 > 1e-6 and g1 < tb:
            # starting inside the globe
            tb = g1; kind = 21
        p[0] = o[0] + tb * d[0]; p[1] = o[1] + tb * d[1]; p[2] = o[2] + tb * d[2]
        if kind == 0 or kind == 1 or kind == 3 or kind == 5:
            return kind, p, d, thr, ex
        if kind == 10:
            ld = LEAD[kp, ip, jp]
            if ld < 0:
                ex[0] = kp; ex[1] = ld; ex[2] = HW[kp, ip, jp]
                return 2, p, d, thr, ex
            f = FID[kp, ip, jp]
            mt = 1.0 + 0.22 * RG[kp, ip, jp]
            for c in range(3):
                thr[c] *= FT[f, c] ** mt
            # ripple deflection
            i1 = min(res - 1, ip + 1); i0 = max(0, ip - 1)
            j1 = min(res - 1, jp + 1); j0 = max(0, jp - 1)
            ga = (RG[kp, ip, j1] - RG[kp, ip, j0])
            gb = (RG[kp, i0, jp] - RG[kp, i1, jp])
            for c in range(3):
                d[c] = d[c] + ramp * (ga * PU[kp, c] + gb * PV[kp, c])
            nrm = np.sqrt(_dot(d, d))
            for c in range(3):
                d[c] /= nrm
            for c in range(3):
                o[c] = p[c] + 1e-5 * d[c]
            continue
        # globe: pass entry face (kind 20) or exit face (kind 21)
        f = gf0 if kind == 20 else gf1
        if f < 0:
            return 0, p, d, thr, ex
        e = globe_edge(p, GN, GD, gc, f)
        if e < GD[0] * 0.022:
            ex[0] = f; ex[1] = e / (GD[0] * 0.022); ex[2] = kind
            return 4, p, d, thr, ex
        ff = GF[f]
        for c in range(3):
            thr[c] *= FT[ff, c]
        for c in range(3):
            o[c] = p[c] + 1e-5 * d[c]
    return 0, p, d, thr, ex


@njit(parallel=True, cache=True, fastmath=True)
def photon_map(nphot, sun, cone, PO, PU, PV, PN, FID, LEAD, HW, RG, FT, half, ramp,
               GN, GD, gc, GF, YW, WIN, TB, TH, LB, LH, LW, seed, nchunk):
    maps = np.zeros((nchunk, 3, LH, LW), np.float32)
    # photon source plane perpendicular to sun, centred above the table
    up = np.array([0.0, 0.0, 1.0])
    ax = np.cross(sun, up); ax /= np.sqrt(_dot(ax, ax))
    ay = np.cross(ax, sun)
    cen = np.array([(LB[0] + LB[1]) / 2, (LB[2] + LB[3]) / 2, 0.0])
    src = cen + sun * 8.0
    # extent of the light map footprint as seen from the sun
    ext = max(LB[1] - LB[0], LB[3] - LB[2]) * 0.75 + 1.0
    per = nphot // nchunk
    for ch in prange(nchunk):
        np.random.seed(seed + ch * 7919)
        o = np.empty(3); d = np.empty(3); thr = np.empty(3)
        for it in range(per):
            u = (np.random.random() * 2 - 1) * ext
            v = (np.random.random() * 2 - 1) * ext
            for c in range(3):
                o[c] = src[c] + u * ax[c] + v * ay[c]
            # sun cone jitter
            r = cone * np.sqrt(np.random.random()); th = 2 * np.pi * np.random.random()
            for c in range(3):
                d[c] = -sun[c] + r * np.cos(th) * ax[c] + r * np.sin(th) * ay[c]
            nn = np.sqrt(_dot(d, d))
            for c in range(3):
                d[c] /= nn
            thr[0] = 1.0; thr[1] = 1.0; thr[2] = 1.0
            kind, p, dd, tt, ex = propagate(o, d, thr, PO, PU, PV, PN, FID, LEAD, HW, RG, FT, half, ramp,
                                            GN, GD, gc, GF, YW, WIN, TB, TH, True)
            if kind != 1:
                continue
            fx = (p[0] - LB[0]) / (LB[1] - LB[0]) * (LW - 1)
            fy = (p[1] - LB[2]) / (LB[3] - LB[2]) * (LH - 1)
            ix = int(fx); iy = int(fy)
            if ix < 0 or iy < 0 or ix >= LW - 1 or iy >= LH - 1:
                continue
            wx = fx - ix; wy = fy - iy
            for c in range(3):
                maps[ch, c, iy, ix] += tt[c] * (1 - wx) * (1 - wy)
                maps[ch, c, iy, ix + 1] += tt[c] * wx * (1 - wy)
                maps[ch, c, iy + 1, ix] += tt[c] * (1 - wx) * wy
                maps[ch, c, iy + 1, ix + 1] += tt[c] * wx * wy
    out = np.zeros((3, LH, LW), np.float32)
    for ch in range(nchunk):
        out += maps[ch]
    # normalise by expected unobstructed density
    area_src = (2 * ext) ** 2
    dens = nphot / area_src * sun[2]  # photons per unit table area for unobstructed light
    texel = (LB[1] - LB[0]) / (LW - 1) * (LB[3] - LB[2]) / (LH - 1)
    return out / (dens * texel)


@njit(cache=True, fastmath=True)
def sample_map(LM, LB, x, y):
    LH = LM.shape[1]; LW = LM.shape[2]
    fx = (x - LB[0]) / (LB[1] - LB[0]) * (LW - 1)
    fy = (y - LB[2]) / (LB[3] - LB[2]) * (LH - 1)
    ix = int(fx); iy = int(fy)
    out = np.zeros(3)
    if ix < 0 or iy < 0 or ix >= LW - 1 or iy >= LH - 1:
        out[:] = 1.0
        return out
    wx = fx - ix; wy = fy - iy
    for c in range(3):
        out[c] = (LM[c, iy, ix] * (1 - wx) * (1 - wy) + LM[c, iy, ix + 1] * wx * (1 - wy)
                  + LM[c, iy + 1, ix] * (1 - wx) * wy + LM[c, iy + 1, ix + 1] * wx * wy)
    return out


@njit(parallel=True, cache=True, fastmath=True)
def render(H, W, spp, cam, PO, PU, PV, PN, FID, LEAD, HW, RG, FT, half, ramp,
           GN, GD, gc, GF, YW, WIN, TB, TH, LM, LB, AO, sun, sp, seed, row0, row1):
    # cam: eye(3) fwd(3) right(3) up(3) fov_scale aperture focus_dist
    img = np.zeros((row1 - row0, W, 3), np.float32)
    eye = cam[0:3]; fw = cam[3:6]; rt = cam[6:9]; upv = cam[9:12]
    fs = cam[12]; ap = cam[13]; fd = cam[14]
    asp = W / H
    for yy in prange(row1 - row0):
        y = yy + row0
        np.random.seed(seed + y * 131)
        o = np.empty(3); d = np.empty(3); thr = np.empty(3); acc = np.empty(3)
        for x in range(W):
            acc[:] = 0.0
            for s in range(spp):
                u = ((x + np.random.random()) / W * 2 - 1) * fs * asp
                v = (1 - (y + np.random.random()) / H * 2) * fs
                for c in range(3):
                    d[c] = fw[c] + u * rt[c] + v * upv[c]
                nn = np.sqrt(_dot(d, d))
                for c in range(3):
                    d[c] /= nn
                # thin lens
                r = ap * np.sqrt(np.random.random()); th = 2 * np.pi * np.random.random()
                lx = r * np.cos(th); ly = r * np.sin(th)
                tf = fd / _dot(d, fw)
                for c in range(3):
                    fp = eye[c] + d[c] * tf
                    o[c] = eye[c] + lx * rt[c] + ly * upv[c]
                    d[c] = fp - o[c]
                nn = np.sqrt(_dot(d, d))
                for c in range(3):
                    d[c] /= nn
                thr[0] = 1.0; thr[1] = 1.0; thr[2] = 1.0
                kind, p, dd, tt, ex = propagate(o, d, thr, PO, PU, PV, PN, FID, LEAD, HW, RG, FT, half, ramp,
                                                GN, GD, gc, GF, YW, WIN, TB, TH, False)
                col = np.zeros(3)
                if kind == 0:
                    col = sky(dd, sun, sp[0:2])
                elif kind == 1:
                    L = sample_map(LM, LB, p[0], p[1])
                    ao = sample_map(AO, LB, p[0], p[1])
                    # linen-white sill with a faint weave
                    wv = 1.0
                    alb0 = 0.94 * wv; alb1 = 0.925 * wv; alb2 = 0.92 * wv
                    sunk = sp[2] * sun[2]
                    col[0] = alb0 * (L[0] * sunk * 1.0 + sp[3] * 0.92 * ao[0])
                    col[1] = alb1 * (L[1] * sunk * 0.97 + sp[3] * 0.90 * ao[0])
                    col[2] = alb2 * (L[2] * sunk * 0.90 + sp[3] * 1.05 * ao[0])
                elif kind == 3:
                    # window wall (inside face, in shade): blush plaster lit by the room
                    col[0] = 0.98 * sp[3] * 1.85; col[1] = 0.90 * sp[3] * 1.85; col[2] = 0.90 * sp[3] * 1.9
                    # window reveal darkening near the opening
                    dxw = min(abs(p[0] - WIN[0]), abs(p[0] - WIN[1]))
                    dzw = min(abs(p[2] - WIN[2]), abs(p[2] - WIN[3]))
                    dm = min(dxw, dzw)
                    if dm < 0.08:
                        f = 0.82 + 0.18 * dm / 0.08
                        for c in range(3):
                            col[c] *= f
                elif kind == 5:
                    q = ex[0]
                    sh = 0.75 + 0.25 * np.sqrt(max(0.0, 1 - q * q))
                    col[0] = 1.05 * sh * sp[3] * 2.2; col[1] = 1.02 * sh * sp[3] * 2.2; col[2] = 1.0 * sh * sp[3] * 2.2
                elif kind == 2:
                    # champagne-gold came, rounded profile
                    q = -ex[1] / ex[2]  # 0 at edge, 1 at centre
                    q = min(1.0, max(0.0, q))
                    k = int(ex[0])
                    hl = np.sqrt(q)
                    base0 = 0.80; base1 = 0.70; base2 = 0.56
                    spec = 0.35 * hl ** 6 + 0.08
                    sh = 0.55 + 0.45 * hl
                    col[0] = (base0 * sh + spec) * sp[4]
                    col[1] = (base1 * sh + spec * 0.95) * sp[4]
                    col[2] = (base2 * sh + spec * 0.85) * sp[4]
                elif kind == 4:
                    q = 1 - ex[1]
                    hl = np.sqrt(max(0.0, 1 - q))
                    spec = 0.35 * hl ** 6 + 0.08
                    sh = 0.55 + 0.45 * hl
                    col[0] = (0.80 * sh + spec) * sp[4]
                    col[1] = (0.70 * sh + spec * 0.95) * sp[4]
                    col[2] = (0.56 * sh + spec * 0.85) * sp[4]
                for c in range(3):
                    acc[c] += col[c] * tt[c]
            for c in range(3):
                img[yy, x, c] = acc[c] / spp
    return img
