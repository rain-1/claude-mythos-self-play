# Pastel layer cake, cut fairly, as a numba SDF ray-marcher.
# Pieces = disc ∩ two half-planes through the Y-junction, each nudged outward.
import numpy as np, numba as nb, json, sys, time
from numba import njit, prange

# ---------------------------------------------------------------- noise
@njit(inline='always')
def h3(i, j, k, s):
    n = (i * 73856093) ^ (j * 19349663) ^ (k * 83492791) ^ (s * 2654435761)
    n = (n ^ (n >> 13)) * 1274126177
    n = n ^ (n >> 16)
    return (n & 0xFFFFFF) / 16777215.0

@njit(inline='always')
def sstep(t):
    return t * t * (3 - 2 * t)

@njit
def vnoise(x, y, z, s):
    i = int(np.floor(x)); j = int(np.floor(y)); k = int(np.floor(z))
    fx = sstep(x - i); fy = sstep(y - j); fz = sstep(z - k)
    a = h3(i, j, k, s) + (h3(i+1, j, k, s) - h3(i, j, k, s)) * fx
    b = h3(i, j+1, k, s) + (h3(i+1, j+1, k, s) - h3(i, j+1, k, s)) * fx
    c = h3(i, j, k+1, s) + (h3(i+1, j, k+1, s) - h3(i, j, k+1, s)) * fx
    d = h3(i, j+1, k+1, s) + (h3(i+1, j+1, k+1, s) - h3(i, j+1, k+1, s)) * fx
    e = a + (b - a) * fy; f = c + (d - c) * fy
    return e + (f - e) * fz

@njit
def fbm(x, y, z, s, oct):
    t = 0.0; amp = 0.5; fr = 1.0
    for o in range(oct):
        t += amp * vnoise(x * fr, y * fr, z * fr, s + o)
        amp *= 0.5; fr *= 2.03
    return t

@njit
def cells(x, y, z, s):
    # distance to nearest jittered feature point (worley F1)
    i = int(np.floor(x)); j = int(np.floor(y)); k = int(np.floor(z))
    best = 9.0
    for a in range(-1, 2):
        for b in range(-1, 2):
            for c in range(-1, 2):
                px = i + a + h3(i+a, j+b, k+c, s)
                py = j + b + h3(i+a, j+b, k+c, s+1)
                pz = k + c + h3(i+a, j+b, k+c, s+2)
                d = (x-px)**2 + (y-py)**2 + (z-pz)**2
                if d < best: best = d
    return np.sqrt(best)

# ---------------------------------------------------------------- scene params
# P: [R, H, ft(frost), table_z, nsprinkle_cell, ...]
# pieces: (3, 8): jx, jy, n1x, n1y, n2x, n2y, offx, offy
@njit(inline='always')
def sd_cyl(px, py, pz, R, z0, z1, rr):
    # rounded cylinder from z0 to z1, radius R, edge rounding rr
    q = np.sqrt(px*px + py*py) - (R - rr)
    hz = 0.5*(z1 - z0); cz = 0.5*(z1 + z0)
    w = abs(pz - cz) - (hz - rr)
    ox = max(q, 0.0); oy = max(w, 0.0)
    return min(max(q, w), 0.0) + np.sqrt(ox*ox + oy*oy) - rr

@njit
def sd_cake_body(px, py, pz, P):
    R = P[0]; H = P[1]
    d = sd_cyl(px, py, pz, R, -0.2, H, 0.035)
    return d

@njit
def sd_piping(px, py, pz, P):
    R = P[0]; H = P[1]
    rho = np.sqrt(px*px + py*py); th = np.arctan2(py, px)
    # top shell border
    N = 64.0
    ph = th * N / (2*np.pi)
    f = ph - np.floor(ph)
    bulge = 0.55 + 0.45 * np.sin(np.pi * f) ** 0.7
    rr = 0.042 * bulge
    dx = rho - (R - 0.055 - 0.012*np.sin(2*np.pi*f)); dz = pz - (H + 0.012)
    d1 = np.sqrt(dx*dx + dz*dz) - rr
    # bottom border (beads)
    N2 = 72.0
    ph2 = th * N2 / (2*np.pi)
    f2 = ph2 - np.floor(ph2)
    rr2 = 0.036 * (0.62 + 0.38 * np.sin(np.pi * f2) ** 0.6)
    dx2 = rho - (R + 0.005); dz2 = pz - 0.03
    d2 = np.sqrt(dx2*dx2 + dz2*dz2) - rr2
    return min(d1, d2) * 0.8

@njit
def sprinkle(px, py, pz, P, want_id):
    # capsules lying on the top, hashed in a grid; returns distance (and id if want_id)
    H = P[1]; R = P[0]
    cs = P[4]
    if pz > H + 0.06 or pz < H - 0.03:
        return 1.0, -1.0
    gx = px / cs; gy = py / cs
    i0 = int(np.floor(gx)); j0 = int(np.floor(gy))
    best = 1.0; bid = -1.0
    for a in range(-1, 2):
        for b in range(-1, 2):
            i = i0 + a; j = j0 + b
            if h3(i, j, 7, 11) > P[5]:
                continue
            cx = (i + 0.15 + 0.7*h3(i, j, 1, 12)) * cs
            cy = (j + 0.15 + 0.7*h3(i, j, 2, 13)) * cs
            rc = np.sqrt(cx*cx + cy*cy)
            if rc > R - 0.12:
                continue
            ang = 6.2831853 * h3(i, j, 3, 14)
            L = 0.5 * P[6] * (0.7 + 0.6*h3(i, j, 4, 15))
            r = P[7]
            ux = np.cos(ang); uy = np.sin(ang)
            qx = px - cx; qy = py - cy; qz = pz - (H + 0.006 + r)
            t = qx*ux + qy*uy
            if t > L: t = L
            if t < -L: t = -L
            dx = qx - t*ux; dy = qy - t*uy
            d = np.sqrt(dx*dx + dy*dy + qz*qz) - r
            if d < best:
                best = d; bid = h3(i, j, 5, 16)
    return best, bid

@njit
def sd_top_frost(px, py, pz, P):
    # gentle swirl on the top surface (displacement)
    rho = np.sqrt(px*px + py*py); th = np.arctan2(py, px)
    sw = 0.006 * np.sin(rho * 38.0 + 2.0*np.sin(th*3.0) + 1.5*fbm(px*3, py*3, 0.0, 41, 2))
    return sw

# materials: 0 backdrop/table, 1 stand, 2 cake, 3 piping, 4 sprinkle, 5 knife
@njit
def scene(px, py, pz, P, PC):
    # backdrop sweep: floor z = tz for y < y0, quarter arc to a wall
    tz = P[2]; y0 = P[8]; Rs = P[9]
    if py < y0:
        dfl = pz - tz
    else:
        cy = y0; cz = tz + Rs
        ry = py - cy; rz = pz - cz
        if rz > 0:
            dfl = (y0 + Rs) - py
        else:
            dfl = Rs - np.sqrt(ry*ry + rz*rz)
    d = dfl; m = 0.0; mid = 0.0
    # cake stand: plate z in [-0.07, 0], radius 1.32 with a small lip; stem + foot
    sR = P[10]
    dp = sd_cyl(px, py, pz, sR, -0.075, 0.0, 0.025)
    rho = np.sqrt(px*px + py*py)
    # stem: radius narrows like a column
    zt = -0.075; zb = tz
    if pz < zt and pz > zb:
        u = (pz - zb) / (zt - zb)
        rs = 0.16 + 0.07*(1-u)**6*3.0 + 0.10*u**8
    else:
        rs = 0.16
    ds = max(rho - rs, max(pz - zt, zb - pz))
    dfoot = sd_cyl(px, py, pz, 0.62, tz - 0.02, tz + 0.045, 0.025)
    dst = min(dp, min(ds * 0.7, dfoot))
    if dst < d:
        d = dst; m = 1.0
    # three dessert plates
    for q in range(3):
        cx = P[14 + 2*q]; cy = P[15 + 2*q]
        if cx == 0 and cy == 0:
            continue
        rx_ = px - cx; ry_ = py - cy
        rr_ = np.sqrt(rx_*rx_ + ry_*ry_)
        # shallow dish: profile height grows towards the rim
        prof = tz + 0.012 + 0.035 * max(0.0, (rr_ - 0.22) / 0.2) ** 2
        dpl = max(abs(pz - prof) - 0.012, rr_ - 0.43) * 0.7
        if dpl < d:
            d = dpl; m = 6.0; mid = q
    # cake knife lying on the table
    if P[11] != 0:
        ca = np.cos(P[13]); sa = np.sin(P[13])
        kx = px - P[11]; ky = py - P[12]
        u = kx*ca + ky*sa; v = -kx*sa + ky*ca; w = pz - (tz + 0.012)
        # blade: rounded slab, tip curved
        bu = abs(u - 0.18) - 0.42; bv = abs(v - 0.0) - (0.075 - 0.05*max(0.0, (u-0.2)/0.4)**2); bw = abs(w) - 0.004
        db = min(max(bu, max(bv, bw)), 0.0) + np.sqrt(max(bu,0.0)**2 + max(bv,0.0)**2 + max(bw,0.0)**2) - 0.003
        # bolster + handle capsule
        hu = min(max(u, -0.95), -0.27)
        dh = np.sqrt((u-hu)**2 + v*v + (w - 0.03)**2) - 0.042
        if db < d:
            d = db; m = 5.0; mid = 0.0
        if dh < d:
            d = dh; m = 5.0; mid = 1.0
    # cake pieces
    for k in range(3):
        qx = px - PC[k, 6]; qy = py - PC[k, 7]
        if (qx*qx + qy*qy) > (P[0] + 0.2)**2 and pz < P[1] + 0.2:
            pass
        h1 = (qx - PC[k, 0]) * PC[k, 2] + (qy - PC[k, 1]) * PC[k, 3]
        h2 = (qx - PC[k, 0]) * PC[k, 4] + (qy - PC[k, 1]) * PC[k, 5]
        hp = max(h1, h2)
        # cake solid with tiny cut rounding
        top = sd_top_frost(qx, qy, pz, P)
        db = sd_cake_body(qx, qy, pz - top, P)
        dc = max(db, hp)
        if dc < d:
            d = dc; m = 2.0; mid = k
        dpi = max(sd_piping(qx, qy, pz, P), hp)
        if dpi < d:
            d = dpi; m = 3.0; mid = k
        if P[5] > 0:
            dsp, sid = sprinkle(qx, qy, pz, P, True)
            dsp = max(dsp, hp)
            if dsp < d:
                d = dsp; m = 4.0; mid = sid
    return d, m, mid

@njit
def dist(px, py, pz, P, PC):
    d, m, mid = scene(px, py, pz, P, PC)
    return d

@njit
def normal(px, py, pz, P, PC, e):
    a = dist(px+e, py-e, pz-e, P, PC); b = dist(px-e, py-e, pz+e, P, PC)
    c = dist(px-e, py+e, pz-e, P, PC); d = dist(px+e, py+e, pz+e, P, PC)
    nx = a - b - c + d; ny = -a - b + c + d; nz = -a + b - c + d
    l = np.sqrt(nx*nx + ny*ny + nz*nz) + 1e-12
    return nx/l, ny/l, nz/l

@njit
def march(ox, oy, oz, dx, dy, dz, P, PC, tmax):
    t = 0.0
    for i in range(400):
        d = dist(ox+t*dx, oy+t*dy, oz+t*dz, P, PC)
        if d < 0.00035 * (1 + t):
            return t
        t += d * 0.9
        if t > tmax:
            return -1.0
    return t

@njit
def softshadow(ox, oy, oz, lx, ly, lz, P, PC, k):
    res = 1.0; t = 0.01
    for i in range(90):
        h = dist(ox+t*lx, oy+t*ly, oz+t*lz, P, PC)
        if h < 0.0004:
            return 0.0
        res = min(res, k*h/t)
        t += min(max(h, 0.008), 0.25)
        if t > 8.0:
            break
    return max(res, 0.0)

@njit
def ao(px, py, pz, nx, ny, nz, P, PC):
    s = 0.0; w = 1.0
    for i in range(1, 6):
        hh = 0.03 * i
        d = dist(px+nx*hh, py+ny*hh, pz+nz*hh, P, PC)
        s += w * (hh - d)
        w *= 0.6
    return max(0.0, 1.0 - 3.2*s)

@njit
def layer_colour(z, H, LC, nl, crumbx, crumby):
    # sponge layers separated by cream; returns rgb and 'is cream'
    ft = 0.06
    zz = z / (H - ft)
    if zz >= 1.0 or zz < 0:
        return 1.0, 0.985, 0.975, 1.0
    u = zz * nl
    k = int(u); f = u - k
    cream = 0.075
    if f > 1.0 - cream and k < nl - 1:
        return 0.995, 0.975, 0.96, 1.0
    return LC[k, 0], LC[k, 1], LC[k, 2], 0.0

@njit
def env(dx, dy, dz):
    # bright pastel studio sky for reflections
    t = 0.5*(dz + 1.0)
    r = 1.0 * t + 0.98*(1-t); g = 0.97*t + 0.93*(1-t); b = 0.99*t + 0.95*(1-t)
    # big soft window on the upper left
    w = max(0.0, (-0.55*dx + 0.25*dy + 0.8*dz))
    w = w ** 12 * 4.0
    return r + w, g + w, b + w

@njit
def shade(px, py, pz, dx, dy, dz, P, PC, LC, SC, L, depth):
    d, m, mid = scene(px, py, pz, P, PC)
    nx, ny, nz = normal(px, py, pz, P, PC, 0.0006)
    lx, ly, lz = L[0], L[1], L[2]
    ndl = nx*lx + ny*ly + nz*lz
    sh = 0.0
    if ndl > -0.3:
        sh = softshadow(px + nx*0.002, py + ny*0.002, pz + nz*0.002, lx, ly, lz, P, PC, 10.0)
    occ = ao(px, py, pz, nx, ny, nz, P, PC)
    spec = 0.0; rough = 40.0; wrap = 0.25; ks = 0.0
    R = P[0]; H = P[1]
    if m == 0.0:
        # backdrop: pale blush paper → table linen
        g = fbm(px*30, py*30, pz*30, 3, 3)
        # blend floor -> wall along the sweep
        if py < P[8]:
            bl = 0.0
        else:
            bl = min(1.0, (py - P[8]) / P[9] * 0.9 + max(0.0, pz - P[2] - P[9]) * 0.3)
        bl = bl * bl * (3 - 2*bl)
        u = min(1.0, max(0.0, (pz - P[2]) / 4.0))
        fab = 0.97 + 0.05*fbm(px*18, py*60, 0.0, 77, 3) * (1 - bl)
        cr = 0.64*(1-bl) + (0.96 - 0.02*u)*bl
        cg = 0.76*(1-bl) + (0.66 + 0.10*u)*bl
        cb = 0.93*(1-bl) + (0.72 + 0.08*u)*bl
        cr *= (0.98 + 0.03*g)*fab; cg *= (0.98 + 0.03*g)*fab; cb *= (0.98 + 0.03*g)*fab
        wrap = 0.5
    elif m == 1.0:
        cr, cg, cb = SC[0], SC[1], SC[2]  # glazed stand
        ks = 0.10; rough = 120.0; wrap = 0.3
    elif m == 2.0:
        k = int(mid)
        qx = px - PC[k, 6]; qy = py - PC[k, 7]
        rho = np.sqrt(qx*qx + qy*qy)
        h1 = (qx - PC[k, 0]) * PC[k, 2] + (qy - PC[k, 1]) * PC[k, 3]
        h2 = (qx - PC[k, 0]) * PC[k, 4] + (qy - PC[k, 1]) * PC[k, 5]
        oncut = max(h1, h2) > -0.0025
        ft = 0.06
        if oncut and rho < R - ft and pz < H - ft:
            cr, cg, cb, cream = layer_colour(pz, H, LC, LC.shape[0], qx, qy)
            if cream < 0.5:
                # crumb: pores = tiny absences
                c = cells(qx*34 + pz*3, qy*34, pz*34, 5)
                c2 = cells(qx*90, qy*90, pz*90, 6)
                pore = min(1.0, max(0.0, (0.30 - c) / 0.10)) * 0.8 + 0.5*min(1.0, max(0.0, (0.28 - c2) / 0.1))
                gg = fbm(qx*25, qy*25, pz*25, 9, 3)
                f = (1.0 - 0.20*min(pore, 1.0)) * (0.90 + 0.18*gg)
                cr *= f; cg *= f; cb *= f
                wrap = 0.55
            else:
                ks = 0.05; wrap = 0.5
        else:
            # buttercream: ombré on the side by height, white on top
            u = min(1.0, max(0.0, pz / H))
            if pz > H - 0.03 and rho < R - 0.03:
                cr, cg, cb = 1.0, 0.975, 0.965
            else:
                # strawberry milk at the base -> cream at the top
                cr = SC[3] + (1.0 - SC[3]) * u**1.4
                cg = SC[4] + (0.975 - SC[4]) * u**1.4
                cb = SC[5] + (0.965 - SC[5]) * u**1.4
                # spatula striations
                st = 0.02*np.sin(pz*160 + 3*fbm(qx*4, qy*4, pz*2, 21, 2))
                cr += st*0.5; cg += st*0.5; cb += st*0.5
            ks = 0.05; rough = 30.0; wrap = 0.45
    elif m == 3.0:
        k = int(mid)
        qx = px - PC[k, 6]; qy = py - PC[k, 7]
        if pz > H * 0.5:
            cr, cg, cb = 1.0, 0.975, 0.97
        else:
            cr, cg, cb = SC[3]*0.98, SC[4]*0.98, SC[5]*0.98
        ks = 0.07; rough = 35.0; wrap = 0.45
    elif m == 6.0:
        q = int(mid)
        cr, cg, cb = PLC[q, 0], PLC[q, 1], PLC[q, 2]
        rx_ = px - P[14 + 2*q]; ry_ = py - P[15 + 2*q]
        rr_ = np.sqrt(rx_*rx_ + ry_*ry_)
        if rr_ > 0.39:
            cr = 0.98; cg = 0.96; cb = 0.95   # white rim line
        ks = 0.12; rough = 140.0; wrap = 0.3
    elif m == 5.0:
        if mid > 0.5:
            cr, cg, cb = SC[6], SC[7], SC[8]   # pastel enamel handle
            ks = 0.12; rough = 80.0; wrap = 0.3
        else:
            cr, cg, cb = 0.55, 0.56, 0.6       # polished steel
            ks = 0.85; rough = 200.0; wrap = 0.0
    else:
        # sprinkle colour from the sorbet box
        j = int(mid * 7.999)
        cr, cg, cb = SPRC[j, 0], SPRC[j, 1], SPRC[j, 2]
        ks = 0.25; rough = 90.0; wrap = 0.25
    # lighting
    dif = max(0.0, (ndl + wrap) / (1 + wrap))
    hx = lx - dx; hy = ly - dy; hz = lz - dz
    hl = np.sqrt(hx*hx + hy*hy + hz*hz) + 1e-9
    nh = max(0.0, (nx*hx + ny*hy + nz*hz) / hl)
    spec = ks * nh ** rough * sh * 2.5
    # sky fill (hemispherical), slight warm bounce from below
    sky = 0.5 + 0.5*nz
    key = 1.05 * dif * (0.25 + 0.75*sh)
    fill = 0.42 * sky * occ + 0.12 * (1 - sky) * occ
    # coloured shadow: shadowed areas lean lilac
    shr = 1.0 - 0.06*(1 - sh); shg = 1.0 - 0.08*(1 - sh); shb = 1.0
    glow = 0.0
    if m == 2.0 and wrap > 0.54:
        glow = 0.22
    r = cr * (key + fill * shr + glow) + spec
    g = cg * (key + fill * shg + glow) + spec
    b = cb * (key + fill * shb + glow) + spec
    # warm rim light from the back right
    rl = max(0.0, nx*0.55 + ny*0.75 + nz*0.35)
    rim = 0.18 * rl * rl * (1 - max(0.0, -(dx*nx+dy*ny+dz*nz)))
    r += rim; g += rim*0.85; b += rim*0.8
    # fresnel env for stand & frosting
    if ks > 0:
        vn = -(dx*nx + dy*ny + dz*nz)
        fr = ks * 0.5 + (1 - ks*0.5) * (1 - vn)**5 * 0.25
        rx = dx + 2*vn*nx; ry = dy + 2*vn*ny; rz = dz + 2*vn*nz
        er, eg, eb = env(rx, ry, rz)
        r = r*(1-fr) + er*fr*0.9; g = g*(1-fr) + eg*fr*0.9; b = b*(1-fr) + eb*fr*0.9
    return r, g, b

SPRC = np.array([
    [0.98, 0.62, 0.70],  # strawberry
    [1.00, 0.72, 0.60],  # coral-peach
    [1.00, 0.90, 0.58],  # butter
    [0.70, 0.90, 0.68],  # lime-mint
    [0.62, 0.88, 0.85],  # mint
    [0.62, 0.78, 0.98],  # sky
    [0.76, 0.70, 0.96],  # periwinkle-lilac
    [0.97, 0.70, 0.90],  # bubblegum
]) ** 2.2

PLC = np.array([[255, 214, 186], [214, 200, 250], [255, 236, 170]]) / 255.0
PLC = PLC ** 2.2

@njit(parallel=True)
def render(W, Hh, cam, P, PC, LC, SC, L, spp, seed, aperture, focus):
    img = np.zeros((Hh, W, 3))
    ex, ey, ez = cam[0], cam[1], cam[2]
    fx, fy, fz = cam[3], cam[4], cam[5]   # forward
    rx, ry, rz = cam[6], cam[7], cam[8]   # right
    ux, uy, uz = cam[9], cam[10], cam[11] # up
    fov = cam[12]
    for y in prange(Hh):
        for x in range(W):
            ar = 0.0; ag = 0.0; ab = 0.0
            for s in range(spp):
                jx = h3(x, y, s, seed); jy = h3(x, y, s, seed + 1)
                sx = (2*(x + jx)/W - 1) * fov
                sy = (1 - 2*(y + jy)/Hh) * fov * Hh / W
                dx = fx + sx*rx + sy*ux; dy = fy + sx*ry + sy*uy; dz = fz + sx*rz + sy*uz
                l = np.sqrt(dx*dx + dy*dy + dz*dz); dx /= l; dy /= l; dz /= l
                ox, oy, oz = ex, ey, ez
                if aperture > 0:
                    a1 = 6.2831853*h3(x, y, s, seed+2); r1 = aperture*np.sqrt(h3(x, y, s, seed+3))
                    lx_ = r1*np.cos(a1); ly_ = r1*np.sin(a1)
                    fpx = ex + dx*focus; fpy = ey + dy*focus; fpz = ez + dz*focus
                    ox = ex + lx_*rx + ly_*ux; oy = ey + lx_*ry + ly_*uy; oz = ez + lx_*rz + ly_*uz
                    dx = fpx - ox; dy = fpy - oy; dz = fpz - oz
                    l = np.sqrt(dx*dx + dy*dy + dz*dz); dx /= l; dy /= l; dz /= l
                t = march(ox, oy, oz, dx, dy, dz, P, PC, 40.0)
                if t < 0:
                    r, g, b = 0.99, 0.94, 0.93
                else:
                    r, g, b = shade(ox+t*dx, oy+t*dy, oz+t*dz, dx, dy, dz, P, PC, LC, SC, L, 0)
                ar += r; ag += g; ab += b
            img[y, x, 0] = ar/spp; img[y, x, 1] = ag/spp; img[y, x, 2] = ab/spp
    return img

def look(eye, target, fov_deg):
    eye = np.array(eye, float); f = np.array(target, float) - eye; f /= np.linalg.norm(f)
    r = np.cross(f, [0, 0, 1.0]); r /= np.linalg.norm(r); u = np.cross(r, f)
    return np.r_[eye, f, r, u, np.tan(np.radians(fov_deg)/2)]

def pieces_from_y(p, angs, gap, rot):
    """Y-junction p (2,), boundary angles (3, ccw); returns PC rows."""
    c, s = np.cos(rot), np.sin(rot)
    Rm = np.array([[c, -s], [s, c]])
    p = Rm @ np.asarray(p, float); angs = np.asarray(angs, float) + rot
    B = np.c_[np.cos(angs), np.sin(angs)]
    rows = []
    for i in range(3):
        b1 = B[i]; b2 = B[(i+1) % 3]
        d1 = b1 - p; d2 = b2 - p
        n1 = np.array([d1[1], -d1[0]]); n1 /= np.linalg.norm(n1)   # outward right normal of leg i
        n2 = np.array([-d2[1], d2[0]]); n2 /= np.linalg.norm(n2)   # outward left normal of leg i+1
        # nudge along the bisector of the outward normals (into the piece)
        v = -(n1 + n2); v /= np.linalg.norm(v)
        off = gap * v
        rows.append([p[0], p[1], n1[0], n1[1], n2[0], n2[1], off[0], off[1]])
    return np.array(rows)

def tonemap(img, exposure=1.0):
    x = img * exposure
    # soft shoulder keeps whites luminous, never clipped flat
    y = x / (1 + 0.12 * x)
    y = y / (1 / (1 + 0.12))
    y = np.clip(y, 0, 1)
    return (np.where(y <= 0.0031308, 12.92*y, 1.055*np.power(y, 1/2.4) - 0.055) * 255 + 0.5).clip(0, 255).astype(np.uint8)
