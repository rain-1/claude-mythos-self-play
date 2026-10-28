# Pastel miniature-city path tracer: one box per lot (height = a[i,j] floors) on a land slab,
# water beyond the two axes, street trees at hashed corners, coral sight-line threads (capsules).
import numpy as np, numba, math
from numba import njit, prange

M_PL, M_BLD = 0.09, 0.165          # plinth inset, building inset (street = 2*M_PL)
PL_H = 0.03                          # sidewalk / lot plinth height
QUAY = 0.12; WATER_Z = -0.07

@njit(cache=True, inline='always')
def rnd(s):
    s[0] ^= (s[0] << np.uint64(13)) & np.uint64(0xFFFFFFFFFFFFFFFF)
    s[0] ^= s[0] >> np.uint64(7)
    s[0] ^= (s[0] << np.uint64(17)) & np.uint64(0xFFFFFFFFFFFFFFFF)
    return (s[0] >> np.uint64(11)) * (1.0 / 9007199254740992.0)

@njit(cache=True, inline='always')
def hsh(i, j):
    h = (i * 374761393 + j * 668265263) & 0xffffffff
    h = ((h ^ (h >> 13)) * 1274126177) & 0xffffffff
    return (h ^ (h >> 16)) / 4294967296.0

@njit(cache=True, inline='always')
def box(ox, oy, oz, ix, iy, iz, x0, x1, y0, y1, z0, z1, tmax):
    # slab test; returns (t, axis*2+side) or (-1, -1)
    ta = (x0 - ox) * ix; tb = (x1 - ox) * ix
    tn = min(ta, tb); tf = max(ta, tb); ax = 0 if ta < tb else 1
    ta = (y0 - oy) * iy; tb = (y1 - oy) * iy
    t2n = min(ta, tb)
    if t2n > tn: tn = t2n; ax = 2 if ta < tb else 3
    tf = min(tf, max(ta, tb))
    ta = (z0 - oz) * iz; tb = (z1 - oz) * iz
    t2n = min(ta, tb)
    if t2n > tn: tn = t2n; ax = 4 if ta < tb else 5
    tf = min(tf, max(ta, tb))
    if tn <= tf and tn > 1e-6 and tn < tmax:
        return tn, ax
    return -1.0, -1

@njit(cache=True)
def trace(ox, oy, oz, dx, dy, dz, A, HU, N, trees, thr, nthr, tr_r, BO):
    """returns t, nx,ny,nz, mat, i, j, face.  mat: 0 sky,1 street,2 plinth,3 wall,4 roof,5 water,6 tree,7 quay wall,8 thread,9 lawn"""
    ix = 1.0 / dx if dx != 0 else 1e30
    iy = 1.0 / dy if dy != 0 else 1e30
    iz = 1.0 / dz if dz != 0 else 1e30
    best = 1e30; mat = 0; nx = 0.0; ny = 0.0; nz = 1.0; bi = -1; bj = -1; face = -1
    # water plane
    if dz < 0:
        t = (WATER_Z - oz) * iz
        if t > 1e-6 and t < best:
            best = t; mat = 5; nx = 0.0; ny = 0.0; nz = 1.0
    # land slab
    t, ax = box(ox, oy, oz, ix, iy, iz, -QUAY, N + 40.0, -QUAY, N + 40.0, WATER_Z - 1.0, 0.0, best)
    if t > 0:
        best = t
        if ax == 5 or ax == 4:
            px = ox + t * dx; py = oy + t * dy
            mat = 1; nx = 0.0; ny = 0.0; nz = 1.0
            bi = int(math.floor(px)); bj = int(math.floor(py))
        else:
            mat = 7; nz = 0.0
            nx = -1.0 if ax == 0 else (1.0 if ax == 1 else 0.0)
            ny = -1.0 if ax == 2 else (1.0 if ax == 3 else 0.0)
    # threads
    for k in range(nthr):
        ax_ = thr[k, 0]; ay_ = thr[k, 1]; az_ = thr[k, 2]
        bx_ = thr[k, 3] - ax_; by_ = thr[k, 4] - ay_; bz_ = thr[k, 5] - az_
        wx = ox - ax_; wy = oy - ay_; wz = oz - az_
        bb = bx_*bx_ + by_*by_ + bz_*bz_
        db = dx*bx_ + dy*by_ + dz*bz_; wb = wx*bx_ + wy*by_ + wz*bz_; wd = wx*dx + wy*dy + wz*dz
        # closest approach between ray and segment
        den = bb - db*db
        if den < 1e-12: continue
        s = (wb - db*wd) / den
        if s < 0: s = 0.0
        if s > 1: s = 1.0
        tt = s*db - wd
        if tt < 1e-6: continue
        cx = ox + tt*dx - (ax_ + s*bx_); cy = oy + tt*dy - (ay_ + s*by_); cz = oz + tt*dz - (az_ + s*bz_)
        d2 = cx*cx + cy*cy + cz*cz
        if d2 < tr_r*tr_r and tt < best:
            best = tt; mat = 8; nx = 0.0; ny = 0.0; nz = 1.0; bi = k
    # boats: ellipsoid hull + triangular sail
    for k in range(BO.shape[0]):
        bx = BO[k, 0]; by = BO[k, 1]; cy_ = math.cos(BO[k, 2]); sy_ = math.sin(BO[k, 2]); Lb = BO[k, 3]; Sh = BO[k, 4]
        # to boat frame
        qx = ox - bx; qy = oy - by; qz = oz - (WATER_Z + 0.005)
        lx = qx * cy_ + qy * sy_; ly = -qx * sy_ + qy * cy_; lz = qz
        ex = dx * cy_ + dy * sy_; ey = -dx * sy_ + dy * cy_; ez = dz
        a_ = Lb * 0.5; b_ = Lb * 0.19; c_ = Lb * 0.16
        X = lx / a_; Y = ly / b_; Z = lz / c_; DX = ex / a_; DY = ey / b_; DZ = ez / c_
        A2 = DX*DX + DY*DY + DZ*DZ; B2 = X*DX + Y*DY + Z*DZ; C2 = X*X + Y*Y + Z*Z - 1
        disc = B2*B2 - A2*C2
        if disc > 0:
            t = (-B2 - math.sqrt(disc)) / A2
            if t > 1e-6 and t < best and lz + t*ez > -0.002:
                hx = (X + t*DX) / a_; hy = (Y + t*DY) / b_; hz = (Z + t*DZ) / c_
                l = math.sqrt(hx*hx + hy*hy + hz*hz)
                best = t; mat = 10; bi = k
                nx = (hx * cy_ - hy * sy_) / l; ny = (hx * sy_ + hy * cy_) / l; nz = hz / l
            elif t > 1e-6 and t < best:
                # deck plane at lz=0 inside ellipse
                if abs(ez) > 1e-9:
                    t2 = -lz / ez
                    if t2 > 1e-6 and t2 < best:
                        u = (lx + t2*ex) / a_; v = (ly + t2*ey) / b_
                        if u*u + v*v < 1:
                            best = t2; mat = 12; bi = k; nx = 0.0; ny = 0.0; nz = 1.0
        # sail in plane ly = 0: triangle (xm,0),(xm,Sh),(xm - 0.75Lb, 0.08) in (lx,lz)
        if abs(ey) > 1e-9:
            t = -ly / ey
            if t > 1e-6 and t < best:
                u = lx + t*ex; w = lz + t*ez
                xm = Lb * 0.12; xb = xm - 0.72 * Lb; zb = 0.06 * Lb
                if u <= xm and u >= xb and w >= zb:
                    # top edge from (xb,zb) to (xm,Sh)
                    if w <= zb + (Sh - zb) * (u - xb) / (xm - xb):
                        best = t; mat = 11; bi = k; face = int(BO[k, 5])
                        sgn = -1.0 if ey > 0 else 1.0
                        nx = -sy_ * sgn; ny = cy_ * sgn; nz = 0.0
    # grid DDA over lots
    Hmax = HU * 40.0
    t0 = 0.0; t1 = best
    # clip to grid AABB
    for a in range(3):
        o = ox if a == 0 else (oy if a == 1 else oz)
        d = dx if a == 0 else (dy if a == 1 else dz)
        lo = -1.0 if a < 2 else -0.1
        hi = N + 1.0 if a < 2 else Hmax
        if abs(d) < 1e-12:
            if o < lo or o > hi: return best, nx, ny, nz, mat, bi, bj, face
        else:
            ta = (lo - o) / d; tb = (hi - o) / d
            if ta > tb: ta, tb = tb, ta
            t0 = max(t0, ta); t1 = min(t1, tb)
    if t0 > t1:
        return best, nx, ny, nz, mat, bi, bj, face
    px = ox + t0 * dx; py = oy + t0 * dy
    ci = int(math.floor(px)); cj = int(math.floor(py))
    sx = 1 if dx > 0 else -1; sy = 1 if dy > 0 else -1
    tdx = abs(ix); tdy = abs(iy)
    tmx = ((ci + (1 if dx > 0 else 0)) - ox) * ix if dx != 0 else 1e30
    tmy = ((cj + (1 if dy > 0 else 0)) - oy) * iy if dy != 0 else 1e30
    tcur = t0
    for it in range(4 * N + 8):
        if tcur > best: break
        if ci >= -1 and cj >= -1 and ci <= N and cj <= N:
            if ci >= 0 and cj >= 0 and ci < N and cj < N:
                h = A[ci, cj]
                t, ax = box(ox, oy, oz, ix, iy, iz, ci + M_PL, ci + 1 - M_PL, cj + M_PL, cj + 1 - M_PL, 0.0, PL_H, best)
                if t > 0:
                    best = t; mat = 2 if h > 0 else 9; bi = ci; bj = cj; face = ax
                    nx = -1.0 if ax == 0 else (1.0 if ax == 1 else 0.0)
                    ny = -1.0 if ax == 2 else (1.0 if ax == 3 else 0.0)
                    nz = -1.0 if ax == 4 else (1.0 if ax == 5 else 0.0)
                if h > 0:
                    t, ax = box(ox, oy, oz, ix, iy, iz, ci + M_BLD, ci + 1 - M_BLD, cj + M_BLD, cj + 1 - M_BLD, 0.0, PL_H + HU * h, best)
                    if t > 0:
                        best = t; mat = 4 if ax == 5 else 3; bi = ci; bj = cj; face = ax
                        nx = -1.0 if ax == 0 else (1.0 if ax == 1 else 0.0)
                        ny = -1.0 if ax == 2 else (1.0 if ax == 3 else 0.0)
                        nz = -1.0 if ax == 4 else (1.0 if ax == 5 else 0.0)
            # trees at this cell's lower-left corner and in parks
            for c in range(trees.shape[1] if (ci >= 0 and cj >= 0 and ci < N and cj < N) else 0):
                tx = trees[0, c] + ci; ty = trees[1, c] + cj
                if hsh(ci * 3 + c, cj * 7 + 11) > trees[3, c]: continue
                tz = trees[2, c]; r = trees[4, c]
                if c == trees.shape[1] - 1:
                    if not (ci >= 0 and cj >= 0 and ci < N and cj < N and A[ci, cj] == 0): continue
                wx = ox - tx; wy = oy - ty; wz = oz - tz
                b = wx*dx + wy*dy + wz*dz
                cc = wx*wx + wy*wy + wz*wz - r*r
                disc = b*b - cc
                if disc > 0:
                    t = -b - math.sqrt(disc)
                    if t > 1e-6 and t < best:
                        best = t; mat = 6; bi = ci; bj = cj; face = c
                        nx = (wx + t*dx) / r; ny = (wy + t*dy) / r; nz = (wz + t*dz) / r
        if tmx < tmy:
            tcur = tmx; tmx += tdx; ci += sx
        else:
            tcur = tmy; tmy += tdy; cj += sy
        if tcur > t1: break
    return best, nx, ny, nz, mat, bi, bj, face

@njit(cache=True)
def sky(dx, dy, dz, P):
    e = max(dz, 0.0)
    g = 1.0 - math.exp(-e * 2.2)
    r = P[0] * (1 - g) + P[3] * g; gg = P[1] * (1 - g) + P[4] * g; b = P[2] * (1 - g) + P[5] * g
    # sun glow
    c = dx * P[6] + dy * P[7] + dz * P[8]
    if c > 0:
        w = c ** 40 * 0.35
        r += w; gg += w * 0.92; b += w * 0.8
    return r, gg, b

@njit(cache=True)
def albedo(mat, px, py, pz, nx, ny, nz, bi, bj, face, A, HU, PAL, hl, dx, dy, dz, P):
    # returns albedo rgb, and 'glass' flag for windows (mirror-ish)
    if mat == 1:   # street: pale lilac grey, zebra crossings near corners, quay promenade
        if px < 0 or py < 0:
            return 0.93, 0.90, 0.84, 0.0
        fx = px - math.floor(px); fy = py - math.floor(py)
        r, g, b = 0.90, 0.87, 0.90
        # zebra crossing stripes across street mouths
        inx = fx < M_PL or fx > 1 - M_PL; iny = fy < M_PL or fy > 1 - M_PL
        if inx and not iny and (fy < 0.3 or fy > 0.7):
            if (int(fy * 40) % 2) == 0: r, g, b = 0.97, 0.96, 0.95
        if iny and not inx and (fx < 0.3 or fx > 0.7):
            if (int(fx * 40) % 2) == 0: r, g, b = 0.97, 0.96, 0.95
        return r, g, b, 0.0
    if mat == 2:
        return 0.96, 0.93, 0.88, 0.0
    if mat == 9:
        return 0.70, 0.88, 0.74, 0.0
    if mat == 10:
        return 0.97, 0.96, 0.95, 0.0
    if mat == 12:
        return 0.93, 0.80, 0.66, 0.0
    if mat == 11:
        k = face % PAL.shape[0]
        if face < 0: return 0.99, 0.99, 0.98, 0.0
        # striped sail: horizontal bands
        if int(pz * 9.0) % 2 == 0: return 0.99, 0.99, 0.98, 0.0
        return PAL[k, 0], PAL[k, 1], PAL[k, 2], 0.0
    if mat == 7:
        return 0.90, 0.85, 0.78, 0.0
    if mat == 6:
        v = hsh(bi * 5 + face, bj * 3 + 1)
        if face == 3: return 0.62, 0.84, 0.62, 0.0
        if v < 0.33: return 0.66, 0.86, 0.66, 0.0
        if v < 0.66: return 0.74, 0.90, 0.70, 0.0
        if v < 0.85: return 0.98, 0.78, 0.84, 0.0   # blossom
        return 0.70, 0.86, 0.78, 0.0
    h = A[bi, bj]
    k = min(h, PAL.shape[0] - 1)
    r = PAL[k, 0]; g = PAL[k, 1]; b = PAL[k, 2]
    if mat == 4:
        # roof: lighter, with parapet band
        fx = px - bi - M_BLD; fy = py - bj - M_BLD; w = 1 - 2 * M_BLD
        e = min(min(fx, w - fx), min(fy, w - fy))
        if e < 0.03:
            return 0.98, 0.97, 0.96, 0.0
        if hl[bi, bj] > 0:
            return 1.0, 0.70, 0.62, 0.0
        return 0.2 + 0.8 * r, 0.2 + 0.8 * g, 0.2 + 0.8 * b, 0.0
    # wall: floors and windows
    if face == 0 or face == 1:
        u = py - bj - M_BLD
    else:
        u = px - bi - M_BLD
    w = 1 - 2 * M_BLD
    v = pz - PL_H
    if v < 0: return r, g, b, 0.0
    fl = v / HU; fi = int(fl); ff = fl - fi
    ncol = 2
    uc = u / w * ncol; ui = int(uc); uf = uc - ui
    # cornice line at the top
    if v > HU * h - 0.02: return 0.98, 0.97, 0.96, 0.0
    if fi == 0 and h >= 3:
        # shopfront: awning stripe + big window
        if ff > 0.62 and ff < 0.8:
            if int(u * 30) % 2 == 0: return 0.99, 0.97, 0.95, 0.0
            return 0.5 + 0.5 * PAL[(k + 4) % PAL.shape[0], 0], 0.5 + 0.5 * PAL[(k + 4) % PAL.shape[0], 1], 0.5 + 0.5 * PAL[(k + 4) % PAL.shape[0], 2], 0.0
        if ff > 0.12 and ff < 0.6 and uf > 0.1 and uf < 0.9:
            return 0.97, 0.92, 0.80, 0.6
        return r, g, b, 0.0
    if ff > 0.38 and ff < 0.74 and u > 0.06 and u < w - 0.06:
        # ribbon window: one band per floor, thin mullions
        if ff < 0.41 or ff > 0.71: return 0.99, 0.98, 0.97, 0.0
        if (u * 14.0) % 1.0 < 0.08: return 0.99, 0.98, 0.97, 0.0
        lit = hsh(bi * 131 + fi, bj * 71 + face * 13)
        if lit < 0.08: return 1.0, 0.93, 0.78, 0.45
        return 0.84, 0.91, 0.99, 0.55
    if ff < 0.05: return 0.3 + 0.7 * r, 0.3 + 0.7 * g, 0.3 + 0.7 * b, 0.0   # floor line
    return r, g, b, 0.0

@njit(cache=True)
def bevel(px, py, pz, nx, ny, nz, bi, bj, h, HU):
    b = 0.035
    x0 = bi + M_BLD; x1 = bi + 1 - M_BLD; y0 = bj + M_BLD; y1 = bj + 1 - M_BLD; z1 = PL_H + HU * h
    ex = 0.0; ey = 0.0; ez = 0.0
    if nx == 0:
        if px - x0 < b: ex = -(1 - (px - x0) / b)
        elif x1 - px < b: ex = (1 - (x1 - px) / b)
    if ny == 0:
        if py - y0 < b: ey = -(1 - (py - y0) / b)
        elif y1 - py < b: ey = (1 - (y1 - py) / b)
    if nz == 0:
        if z1 - pz < b: ez = (1 - (z1 - pz) / b)
    mx = nx + 0.9 * ex; my = ny + 0.9 * ey; mz = nz + 0.9 * ez
    l = math.sqrt(mx*mx + my*my + mz*mz)
    return mx / l, my / l, mz / l

@njit(cache=True)
def shade_direct(px, py, pz, nx, ny, nz, A, HU, N, trees, thr, P, s, BO):
    # soft sun: jitter direction in a cone
    sx = P[6]; sy = P[7]; sz = P[8]
    jr = P[12]
    u1 = rnd(s); u2 = rnd(s)
    rr = jr * math.sqrt(u1); ph = 6.283185307 * u2
    # orthonormal basis around sun
    if abs(sz) < 0.9:
        ax_, ay_, az_ = sy, -sx, 0.0
    else:
        ax_, ay_, az_ = 1.0, 0.0, 0.0
    l = math.sqrt(ax_*ax_ + ay_*ay_ + az_*az_); ax_ /= l; ay_ /= l; az_ /= l
    bx_ = sy*az_ - sz*ay_; by_ = sz*ax_ - sx*az_; bz_ = sx*ay_ - sy*ax_
    lx = sx + rr*(math.cos(ph)*ax_ + math.sin(ph)*bx_)
    ly = sy + rr*(math.cos(ph)*ay_ + math.sin(ph)*by_)
    lz = sz + rr*(math.cos(ph)*az_ + math.sin(ph)*bz_)
    l = math.sqrt(lx*lx + ly*ly + lz*lz); lx /= l; ly /= l; lz /= l
    c = nx*lx + ny*ly + nz*lz
    if c <= 0: return 0.0
    t = trace(px + nx*1e-4, py + ny*1e-4, pz + nz*1e-4, lx, ly, lz, A, HU, N, trees, thr, 0, 0.0, BO)
    if t[4] != 0 and t[4] != 5: return 0.0
    return c

@njit(parallel=True, cache=True)
def render(W, H, cam, A, HU, PAL, hl, trees, thr, tr_r, P, spp, y0, y1, seed, BO):
    N = A.shape[0]
    out = np.zeros((y1 - y0, W, 3), np.float32)
    ex, ey, ez = cam[0], cam[1], cam[2]
    fx_, fy_, fz_ = cam[3], cam[4], cam[5]
    rx, ry, rz = cam[6], cam[7], cam[8]
    ux, uy, uz = cam[9], cam[10], cam[11]
    tanh = cam[12]; ap = cam[13]; fd = cam[14]
    # tilt-shift: focal plane tilted -> focus distance varies with screen y
    tilt = cam[15]
    sunE = P[9]; skyE = P[10]
    nthr = thr.shape[0]
    for yy in prange(y0, y1):
        s = np.zeros(1, np.uint64)
        s[0] = np.uint64(seed * 1000003 + yy * 7919 + 12345)
        for _ in range(4): rnd(s)
        for xx in range(W):
            ar = 0.0; ag = 0.0; ab = 0.0
            for k in range(spp):
                sxp = (2 * (xx + rnd(s)) / W - 1) * tanh
                syp = (1 - 2 * (yy + rnd(s)) / H) * tanh * H / W
                dx = fx_ + sxp * rx + syp * ux; dy = fy_ + sxp * ry + syp * uy; dz = fz_ + sxp * rz + syp * uz
                l = math.sqrt(dx*dx + dy*dy + dz*dz); dx /= l; dy /= l; dz /= l
                # thin lens
                fdist = fd * (1 + tilt * syp)
                fpx = ex + dx * fdist; fpy = ey + dy * fdist; fpz = ez + dz * fdist
                u1 = rnd(s); u2 = rnd(s)
                rr = ap * math.sqrt(u1); ph = 6.283185307 * u2
                ox = ex + rr * (math.cos(ph) * rx + math.sin(ph) * ux)
                oy = ey + rr * (math.cos(ph) * ry + math.sin(ph) * uy)
                oz = ez + rr * (math.cos(ph) * rz + math.sin(ph) * uz)
                dx = fpx - ox; dy = fpy - oy; dz = fpz - oz
                l = math.sqrt(dx*dx + dy*dy + dz*dz); dx /= l; dy /= l; dz /= l
                thr_w = 1.0
                cr = 0.0; cg = 0.0; cb = 0.0
                for bounce in range(2):   # bounce 1 only via water mirror
                    t, nx, ny, nz, mat, bi, bj, face = trace(ox, oy, oz, dx, dy, dz, A, HU, N, trees, thr, nthr, tr_r, BO)
                    if mat == 0:
                        r_, g_, b_ = sky(dx, dy, dz, P)
                        cr += thr_w * r_; cg += thr_w * g_; cb += thr_w * b_
                        break
                    px = ox + t*dx; py = oy + t*dy; pz = oz + t*dz
                    if mat == 8:
                        cr += thr_w * P[13]; cg += thr_w * P[14]; cb += thr_w * P[15]
                        break
                    if mat == 5 and bounce == 0:
                        # water: fresnel mirror + shallow->deep tinted body, ripples
                        dsh = min(max(-px, 0.0) if py > -QUAY else 1e9, max(-py, 0.0) if px > -QUAY else 1e9)
                        if px < -QUAY and py < -QUAY: dsh = math.sqrt(px*px + py*py)
                        sh = math.exp(-dsh / P[23])
                        wr = P[16] * (1 - sh) + P[24] * sh; wg = P[17] * (1 - sh) + P[25] * sh; wb = P[18] * (1 - sh) + P[26] * sh
                        wk = 0.0
                        for kb in range(BO.shape[0]):
                            cy2 = math.cos(BO[kb, 2]); sy2 = math.sin(BO[kb, 2])
                            qx = px - BO[kb, 0]; qy = py - BO[kb, 1]
                            lx = qx * cy2 + qy * sy2; ly = -qx * sy2 + qy * cy2
                            if lx < BO[kb, 3] * 0.3:
                                back = BO[kb, 3] * 0.3 - lx
                                edge = abs(abs(ly) - back * 0.32 - BO[kb, 3] * 0.12)
                                wk += math.exp(-edge * edge / (0.0016 + 0.0004 * back)) * math.exp(-back / (BO[kb, 3] * 4.0))
                        wk = min(wk, 1.0) * 0.55
                        wr = wr * (1 - wk) + wk; wg = wg * (1 - wk) + wk; wb = wb * (1 - wk) + wk
                        wx = 0.0; wy = 0.0
                        fq = 3.0; am = 0.05
                        for o in range(4):
                            ang = 1.7 * o + 0.4
                            kx = math.cos(ang) * fq; ky = math.sin(ang) * fq
                            ph = kx * px + ky * py + 2.1 * o
                            wx += am * kx / fq * math.cos(ph); wy += am * ky / fq * math.cos(ph)
                            fq *= 1.9; am *= 0.6
                        nx = -wx; ny = -wy; nz = 1.0
                        l = math.sqrt(nx*nx + ny*ny + 1); nx /= l; ny /= l; nz /= l
                        c = -(dx*nx + dy*ny + dz*nz)
                        F = 0.04 + 0.96 * (1 - c) ** 5
                        F = 0.12 + 0.7 * F
                        cr += thr_w * (1 - F) * wr; cg += thr_w * (1 - F) * wg; cb += thr_w * (1 - F) * wb
                        thr_w *= F
                        dx = dx + 2 * c * nx; dy = dy + 2 * c * ny; dz = dz + 2 * c * nz
                        ox = px; oy = py; oz = pz + 1e-4
                        continue
                    if mat == 5:
                        cr += thr_w * P[16]; cg += thr_w * P[17]; cb += thr_w * P[18]
                        break
                    if mat == 3 or mat == 4:
                        nx, ny, nz = bevel(px, py, pz, nx, ny, nz, bi, bj, A[bi, bj], HU)
                    ar_, ag_, ab_, glass = albedo(mat, px, py, pz, nx, ny, nz, bi, bj, face, A, HU, PAL, hl, dx, dy, dz, P)
                    d = shade_direct(px, py, pz, nx, ny, nz, A, HU, N, trees, thr, P, s, BO)
                    # one diffuse bounce (cosine hemisphere)
                    u1 = rnd(s); u2 = rnd(s)
                    rr = math.sqrt(u1); ph = 6.283185307 * u2
                    if abs(nz) < 0.9:
                        tx, ty, tz = -ny, nx, 0.0
                    else:
                        tx, ty, tz = 1.0, 0.0, 0.0
                    l = math.sqrt(tx*tx + ty*ty + tz*tz); tx /= l; ty /= l; tz /= l
                    bx_ = ny*tz - nz*ty; by_ = nz*tx - nx*tz; bz_ = nx*ty - ny*tx
                    hz = math.sqrt(max(0.0, 1 - u1))
                    qx = rr*math.cos(ph)*tx + rr*math.sin(ph)*bx_ + hz*nx
                    qy = rr*math.cos(ph)*ty + rr*math.sin(ph)*by_ + hz*ny
                    qz = rr*math.cos(ph)*tz + rr*math.sin(ph)*bz_ + hz*nz
                    t2, n2x, n2y, n2z, m2, b2i, b2j, f2 = trace(px + nx*1e-4, py + ny*1e-4, pz + nz*1e-4, qx, qy, qz, A, HU, N, trees, thr, 0, 0.0, BO)
                    if m2 == 0 or (m2 == 5 and False):
                        r_, g_, b_ = sky(qx, qy, qz, P)
                        ir = skyE * r_; ig = skyE * g_; ib = skyE * b_
                    else:
                        p2x = px + t2*qx; p2y = py + t2*qy; p2z = pz + t2*qz
                        if m2 == 5:
                            a2r, a2g, a2b = P[16], P[17], P[18]
                        else:
                            a2r, a2g, a2b, g2 = albedo(m2, p2x, p2y, p2z, n2x, n2y, n2z, b2i, b2j, f2, A, HU, PAL, hl, qx, qy, qz, P)
                        d2 = shade_direct(p2x, p2y, p2z, n2x, n2y, n2z, A, HU, N, trees, thr, P, s, BO)
                        ir = a2r * (sunE * d2 * P[19] + P[11]); ig = a2g * (sunE * d2 * P[20] + P[11]); ib = a2b * (sunE * d2 * P[21] + P[11])
                    lr = sunE * d * P[19] + ir; lg = sunE * d * P[20] + ig; lb = sunE * d * P[21] + ib
                    er = ar_ * lr; eg = ag_ * lg; eb = ab_ * lb
                    if glass > 0:
                        # windows: mix with reflected sky
                        rdx = dx - 2*(dx*nx + dy*ny + dz*nz)*nx; rdy = dy - 2*(dx*nx + dy*ny + dz*nz)*ny; rdz = dz - 2*(dx*nx + dy*ny + dz*nz)*nz
                        r_, g_, b_ = sky(rdx, rdy, abs(rdz) * 0.6 + 0.1, P)
                        er = er * (1 - glass * 0.5) + glass * 0.5 * r_ * 1.05
                        eg = eg * (1 - glass * 0.5) + glass * 0.5 * g_ * 1.05
                        eb = eb * (1 - glass * 0.5) + glass * 0.5 * b_ * 1.05
                    # aerial haze
                    dist = t if bounce == 0 else t + 0.0
                    hz_ = 1 - math.exp(-dist / P[22])
                    er = er * (1 - hz_) + P[0] * hz_ * 1.05; eg = eg * (1 - hz_) + P[1] * hz_ * 1.05; eb = eb * (1 - hz_) + P[2] * hz_ * 1.05
                    cr += thr_w * er; cg += thr_w * eg; cb += thr_w * eb
                    break
                ar += cr; ag += cg; ab += cb
            out[yy - y0, xx, 0] = ar / spp; out[yy - y0, xx, 1] = ag / spp; out[yy - y0, xx, 2] = ab / spp
    return out
