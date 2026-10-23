# Petits fours on a tray: any convex shape, cut fairly into three, the pieces nudged apart.
# Shape = intersection of half-planes and discs (polygons, Reuleaux, half-disc, disc) or an ellipse.
import numpy as np
from numba import njit, prange
from cake import h3, fbm, cells, sd_cyl, env

# S: (n_cakes, 64) rows:
#  0 cx, 1 cy, 2 H, 3 kind(0 = halfplanes/discs, 1 = ellipse a,b in 5,6), 4 n_prims, 5.. prims (4 each: type, a, b, c)
#    type 0 half-plane: a*x+b*y-c <= 0 ; type 1 disc: centre (a,b) radius c
# PCS: (n_cakes, 3, 9): pieces: h1 (nx,ny,c), h2 (nx,ny,c), offx, offy, colour index
@njit
def sd_shape2(x, y, S, i):
    if S[i, 3] == 1.0:
        a = S[i, 5]; b = S[i, 6]
        k0 = np.sqrt((x/a)**2 + (y/b)**2)
        k1 = np.sqrt((x/(a*a))**2 + (y/(b*b))**2) + 1e-9
        return k0 * (k0 - 1.0) / k1
    d = -1e9
    n = int(S[i, 4])
    for j in range(n):
        t = S[i, 5 + 4*j]; a = S[i, 6 + 4*j]; b = S[i, 7 + 4*j]; c = S[i, 8 + 4*j]
        if t == 0.0:
            v = a*x + b*y - c
        else:
            v = np.sqrt((x-a)**2 + (y-b)**2) - c
        if v > d:
            d = v
    return d

@njit
def sd_prism(x, y, z, S, i, rr):
    H = S[i, 2]
    d2 = sd_shape2(x, y, S, i) + rr
    w = abs(z - H*0.5) - (H*0.5 - rr)
    ox = max(d2, 0.0); oy = max(w, 0.0)
    return min(max(d2, w), 0.0) + np.sqrt(ox*ox + oy*oy) - rr

@njit
def sd_tray(px, py, pz, T):
    rr = 0.22
    qx = abs(px) - (T[0] - rr); qy = abs(py) - (T[1] - rr)
    d2 = np.sqrt(max(qx, 0.0)**2 + max(qy, 0.0)**2) + min(max(qx, qy), 0.0) - rr
    # shallow lip: the tray rises 0.025 near its edge
    lip = 0.025 * min(1.0, max(0.0, (d2 + 0.09) / 0.06))
    w = max(pz - lip, -0.08 - pz)
    ox = max(d2, 0.0); oy = max(w, 0.0)
    return (min(max(d2, w), 0.0) + np.sqrt(ox*ox + oy*oy)) * 0.8, d2

@njit
def scene(px, py, pz, S, PCS, T):
    # tray: rounded slab top at z=0; table below at z=-0.08; table plane
    d = pz + 0.09; m = 0.0; mid = 0.0
    dt, e2 = sd_tray(px, py, pz, T)
    # tray rim lip
    if dt < d:
        d = dt; m = 1.0
    n = S.shape[0]
    for i in range(n):
        lx = px - S[i, 0]; ly = py - S[i, 1]
        dd = np.sqrt(lx*lx + ly*ly + max(0.0, pz - S[i, 2])**2) - 0.7
        if dd > d:
            continue
        for k in range(3):
            qx = lx - PCS[i, k, 6]; qy = ly - PCS[i, k, 7]
            h1 = PCS[i, k, 0]*qx + PCS[i, k, 1]*qy - PCS[i, k, 2]
            h2 = PCS[i, k, 3]*qx + PCS[i, k, 4]*qy - PCS[i, k, 5]
            dc = max(sd_prism(qx, qy, pz, S, i, 0.012), max(h1, h2))
            if dc < d:
                d = dc; m = 2.0; mid = i*3 + k
            if PCS[i, k, 11] > 0:
                rp = PCS[i, k, 11]
                dpe = np.sqrt((qx - PCS[i, k, 9])**2 + (qy - PCS[i, k, 10])**2 + (pz - S[i, 2] - rp*0.8)**2) - rp
                if dpe < d:
                    d = dpe; m = 3.0; mid = i*3 + k
    return d, m, mid

@njit
def dist(px, py, pz, S, PCS, T):
    d, m, mid = scene(px, py, pz, S, PCS, T)
    return d

@njit
def normal(px, py, pz, S, PCS, T, e):
    a = dist(px+e, py-e, pz-e, S, PCS, T); b = dist(px-e, py-e, pz+e, S, PCS, T)
    c = dist(px-e, py+e, pz-e, S, PCS, T); d = dist(px+e, py+e, pz+e, S, PCS, T)
    nx = a - b - c + d; ny = -a - b + c + d; nz = -a + b - c + d
    l = np.sqrt(nx*nx + ny*ny + nz*nz) + 1e-12
    return nx/l, ny/l, nz/l

@njit
def march(ox, oy, oz, dx, dy, dz, S, PCS, T):
    t = 0.0
    for i in range(500):
        d = dist(ox+t*dx, oy+t*dy, oz+t*dz, S, PCS, T)
        if d < 0.00008 * (1 + t):
            return t
        t += d * 0.85
        if t > 40:
            return -1.0
    return t

@njit
def softshadow(ox, oy, oz, lx, ly, lz, S, PCS, T, k):
    res = 1.0; t = 0.006
    for i in range(110):
        h = dist(ox+t*lx, oy+t*ly, oz+t*lz, S, PCS, T)
        if h < 0.0003:
            return 0.0
        res = min(res, k*h/t)
        t += min(max(h, 0.004), 0.15)
        if t > 5.0:
            break
    return max(res, 0.0)

@njit
def ao(px, py, pz, nx, ny, nz, S, PCS, T):
    s = 0.0; w = 1.0
    for i in range(1, 6):
        hh = 0.015 * i
        d = dist(px+nx*hh, py+ny*hh, pz+nz*hh, S, PCS, T)
        s += w * (hh - d); w *= 0.6
    return max(0.0, 1.0 - 4.0*s)

@njit
def shade(px, py, pz, dx, dy, dz, S, PCS, T, COL, LC, L):
    d, m, mid = scene(px, py, pz, S, PCS, T)
    nx, ny, nz = normal(px, py, pz, S, PCS, T, 0.0012)
    lx, ly, lz = L[0], L[1], L[2]
    ndl = nx*lx + ny*ly + nz*lz
    sh = 0.0
    if ndl > -0.3:
        sh = softshadow(px+nx*0.0015, py+ny*0.0015, pz+nz*0.0015, lx, ly, lz, S, PCS, T, 12.0)
    oc = ao(px, py, pz, nx, ny, nz, S, PCS, T)
    ks = 0.0; rough = 40.0; wrap = 0.3; glow = 0.0
    if m == 0.0:
        cr, cg, cb = T[2], T[3], T[4]
        g = fbm(px*25, py*25, 0.0, 3, 3)
        f = 0.97 + 0.05*g
        cr *= f; cg *= f; cb *= f; wrap = 0.5
    elif m == 1.0:
        cr, cg, cb = T[5], T[6], T[7]
        ks = 0.12; rough = 150.0
        # faint rim line on the tray
        dt, e = sd_tray(px, py, pz, T)
        if e > -0.13 and e < -0.115:
            cr = 0.98; cg = 0.96; cb = 0.95
    elif m == 3.0:
        cr, cg, cb = 0.97, 0.95, 0.96
        ks = 0.6; rough = 160.0; wrap = 0.2
    else:
        i = int(mid) // 3; k = int(mid) % 3
        lx_ = px - S[i, 0] - PCS[i, k, 6]; ly_ = py - S[i, 1] - PCS[i, k, 7]
        h1 = PCS[i, k, 0]*lx_ + PCS[i, k, 1]*ly_ - PCS[i, k, 2]
        h2 = PCS[i, k, 3]*lx_ + PCS[i, k, 4]*ly_ - PCS[i, k, 5]
        ci = int(PCS[i, k, 8])
        H = S[i, 2]
        sd2 = sd_shape2(lx_, ly_, S, i)
        ft = 0.022
        if max(h1, h2) > -0.0015 and sd2 < -ft and pz < H - ft and pz > 0.004:
            # cut face: sponge layers with jam/cream between
            u = pz / (H - ft) * 3.0
            kk = int(u); f = u - kk
            if f > 0.86 and kk < 2:
                cr, cg, cb = COL[ci, 0]*0.85 + 0.15, COL[ci, 1]*0.85 + 0.15, COL[ci, 2]*0.85 + 0.15
                ks = 0.15; rough = 60.0; wrap = 0.5
            else:
                cr, cg, cb = LC[kk, 0], LC[kk, 1], LC[kk, 2]
                c = cells(lx_*60, ly_*60, pz*60, 5)
                pore = min(1.0, max(0.0, (0.30 - c) / 0.1))
                gg = fbm(lx_*40, ly_*40, pz*40, 9, 3)
                f2 = (1.0 - 0.2*pore) * (0.9 + 0.18*gg)
                cr *= f2; cg *= f2; cb *= f2
                wrap = 0.55; glow = 0.2
        else:
            # fondant: smooth, faint sugar sheen
            cr, cg, cb = COL[ci, 0], COL[ci, 1], COL[ci, 2]
            ks = 0.08; rough = 25.0; wrap = 0.45
            if pz > H - 0.004:
                # a white piped dot pattern on top? keep plain: a soft lighter top
                cr = cr*0.85 + 0.15; cg = cg*0.85 + 0.15; cb = cb*0.85 + 0.15
    dif = max(0.0, (ndl + wrap)/(1 + wrap))
    hx = lx - dx; hy = ly - dy; hz = lz - dz
    hl = np.sqrt(hx*hx + hy*hy + hz*hz) + 1e-9
    nh = max(0.0, (nx*hx + ny*hy + nz*hz)/hl)
    spec = ks * nh**rough * sh * 2.5
    sky = 0.5 + 0.5*nz
    key = 1.0 * dif * (0.25 + 0.75*sh)
    fill = 0.45 * sky * oc + 0.12 * (1 - sky) * oc
    shr = 1.0 - 0.07*(1 - sh); shg = 1.0 - 0.09*(1 - sh)
    r = cr*(key + fill*shr + glow) + spec
    g = cg*(key + fill*shg + glow) + spec
    b = cb*(key + fill + glow) + spec
    if ks > 0:
        vn = -(dx*nx + dy*ny + dz*nz)
        fr = ks*0.5 + (1 - ks*0.5)*(1 - vn)**5*0.25
        rx = dx + 2*vn*nx; ry = dy + 2*vn*ny; rz = dz + 2*vn*nz
        er, eg, eb = env(rx, ry, rz)
        r = r*(1-fr) + er*fr*0.9; g = g*(1-fr) + eg*fr*0.9; b = b*(1-fr) + eb*fr*0.9
    return r, g, b

@njit(parallel=True)
def render(W, Hh, cam, S, PCS, T, COL, LC, L, spp, seed):
    img = np.zeros((Hh, W, 3))
    ex, ey, ez = cam[0], cam[1], cam[2]
    fx, fy, fz = cam[3], cam[4], cam[5]
    rx, ry, rz = cam[6], cam[7], cam[8]
    ux, uy, uz = cam[9], cam[10], cam[11]
    fov = cam[12]
    for y in prange(Hh):
        for x in range(W):
            ar = 0.0; ag = 0.0; ab = 0.0
            for s in range(spp):
                jx = h3(x, y, s, seed); jy = h3(x, y, s, seed+1)
                sx = (2*(x + jx)/W - 1)*fov
                sy = (1 - 2*(y + jy)/Hh)*fov*Hh/W
                dx = fx + sx*rx + sy*ux; dy = fy + sx*ry + sy*uy; dz = fz + sx*rz + sy*uz
                l = np.sqrt(dx*dx + dy*dy + dz*dz); dx /= l; dy /= l; dz /= l
                t = march(ex, ey, ez, dx, dy, dz, S, PCS, T)
                if t < 0:
                    r, g, b = T[2], T[3], T[4]
                else:
                    r, g, b = shade(ex+t*dx, ey+t*dy, ez+t*dz, dx, dy, dz, S, PCS, T, COL, LC, L)
                ar += r; ag += g; ab += b
            img[y, x, 0] = ar/spp; img[y, x, 1] = ag/spp; img[y, x, 2] = ab/spp
    return img
