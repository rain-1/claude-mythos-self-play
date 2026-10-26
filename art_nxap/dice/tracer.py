"""Sorbet-glass dice tracer.

Convex solids as intersections of half-spaces (n.x <= d), glass with Fresnel + Snell +
Beer-Lambert, opaque inked numerals painted on faces (glyph atlas), on a paper sweep
(floor z=0 curving up into a back wall). Sun: direct light with hard-ish shadows (glass opaque
to the shadow ray) + a photon-mapped caustic grid for the light that went THROUGH the glass.
"""
import numpy as np
from numba import njit, prange
import math

IOR = 1.5
MAXINT = 3


@njit(cache=True, fastmath=True)
def hit_obj(ox, oy, oz, dx, dy, dz, PL, s, c):
    """slab test against planes PL[s:s+c]; returns (tin, tout, pin, pout)."""
    tin = -1e30; tout = 1e30; pin = -1; pout = -1
    for k in range(s, s + c):
        nx, ny, nz, d = PL[k, 0], PL[k, 1], PL[k, 2], PL[k, 3]
        den = nx*dx + ny*dy + nz*dz
        num = d - (nx*ox + ny*oy + nz*oz)
        if abs(den) < 1e-12:
            if num < 0:
                return 1e30, -1e30, -1, -1
            continue
        t = num / den
        if den < 0:
            if t > tin:
                tin = t; pin = k
        else:
            if t < tout:
                tout = t; pout = k
        if tin > tout:
            return 1e30, -1e30, -1, -1
    return tin, tout, pin, pout


@njit(cache=True, fastmath=True)
def nearest_obj(ox, oy, oz, dx, dy, dz, PL, OB, skip):
    best = 1e30; bk = -1; bp = -1
    for k in range(OB.shape[0]):
        if k == skip:
            continue
        cx = OB[k, 2] - ox; cy = OB[k, 3] - oy; cz = OB[k, 4] - oz
        b = cx*dx + cy*dy + cz*dz
        r = OB[k, 5]
        disc = b*b - (cx*cx + cy*cy + cz*cz) + r*r
        if disc < 0:
            continue
        if b + math.sqrt(disc) < 1e-6:
            continue
        tin, tout, pin, pout = hit_obj(ox, oy, oz, dx, dy, dz, PL, int(OB[k, 0]), int(OB[k, 1]))
        if tin <= tout and tin > 1e-6 and tin < best:
            best = tin; bk = k; bp = pin
    return best, bk, bp


@njit(cache=True, fastmath=True)
def sweep_hit(ox, oy, oz, dx, dy, dz, SW):
    """floor z=0 for y<y0, quarter cylinder radius Rc (axis x at y=y0, z=Rc), wall y=y0+Rc."""
    y0 = SW[0]; Rc = SW[1]
    best = 1e30; kind = -1
    if dz < -1e-12:
        t = -oz / dz
        if t > 1e-6 and oy + t*dy <= y0:
            best = t; kind = 0
    # cylinder (y-y0)^2 + (z-Rc)^2 = Rc^2, part y>y0, z<Rc
    py = oy - y0; pz = oz - Rc
    a = dy*dy + dz*dz
    if a > 1e-12:
        b = py*dy + pz*dz
        cc = py*py + pz*pz - Rc*Rc
        disc = b*b - a*cc
        if disc >= 0:
            sq = math.sqrt(disc)
            for sgn in (-1.0, 1.0):
                t = (-b + sgn*sq) / a
                if t > 1e-6 and t < best:
                    yy = py + t*dy; zz = pz + t*dz
                    if yy >= 0 and zz <= 0:
                        best = t; kind = 1
    if dy > 1e-12:
        t = (y0 + Rc - oy) / dy
        if t > 1e-6 and t < best and oz + t*dz >= Rc:
            best = t; kind = 2
    return best, kind


@njit(cache=True, fastmath=True)
def sweep_normal(px, py, pz, kind, SW):
    if kind == 0:
        return 0.0, 0.0, 1.0
    if kind == 2:
        return 0.0, -1.0, 0.0
    y0 = SW[0]; Rc = SW[1]
    ny = -(py - y0); nz = -(pz - Rc)
    l = math.sqrt(ny*ny + nz*nz)
    return 0.0, ny/l, nz/l


@njit(cache=True, fastmath=True)
def paper(px, py, pz, kind, SW, PAP):
    """albedo of the sweep. PAP: [floor rgb(3), wall-bottom rgb(3), wall-top rgb(3), dot rgb(3), dot pitch, dot r, wall h]"""
    y0 = SW[0]; Rc = SW[1]
    if kind == 0:
        r = PAP[0]; g = PAP[1]; b = PAP[2]
        pitch = PAP[12]
        if pitch > 0:
            # sparse hex polka dots on the floor
            u = px / pitch; v = py / (pitch * 0.8660254)
            j = math.floor(v + 0.5)
            uu = u - 0.5 * (j % 2)
            i = math.floor(uu + 0.5)
            ex = (uu - i) * pitch; ey = (v - j) * pitch * 0.8660254
            dd = math.sqrt(ex*ex + ey*ey)
            w = min(max((PAP[13] - dd) / (0.004 + 1e-9) + 0.5, 0.0), 1.0)
            # dot colour hue walks with i,j
            hsel = (i * 3 + j * 5) % 4
            f = 0.55 + 0.15 * hsel
            r = r*(1-w) + w*(PAP[9]*f + r*(1-f))
            g = g*(1-w) + w*(PAP[10]*f + g*(1-f))
            b = b*(1-w) + w*(PAP[11]*f + b*(1-f))
        return r, g, b
    # height along sweep for wall gradient
    if kind == 1:
        h = 0.0
        ang = math.atan2(py - y0, Rc - pz)
        s = ang / (0.5*math.pi)
        h = s * 0.25
    else:
        h = 0.25 + (pz - Rc) / PAP[14]
    h = min(max(h, 0.0), 1.0)
    hh = h**0.8
    r = PAP[0]*(1-hh*0) * 0 + PAP[3]*(1-hh) + PAP[6]*hh
    g = PAP[4]*(1-hh) + PAP[7]*hh
    b = PAP[5]*(1-hh) + PAP[8]*hh
    # blend floor colour into the bottom of the curve
    if kind == 1:
        m = min(s*2.5, 1.0)
        r = PAP[0]*(1-m) + r*m; g = PAP[1]*(1-m) + g*m; b = PAP[2]*(1-m) + b*m
    return r, g, b


@njit(cache=True, fastmath=True)
def env(dx, dy, dz, EN):
    """EN: [sun dir(3), sun cos radius, sun radiance(3), horizon rgb(3), zenith rgb(3),
            box az0, az1, el0, el1, box radiance]"""
    el = math.asin(max(min(dz, 1.0), -1.0))
    t = max(el, 0.0) / (0.5*math.pi)
    t = t**0.6
    r = EN[7]*(1-t) + EN[10]*t
    g = EN[8]*(1-t) + EN[11]*t
    b = EN[9]*(1-t) + EN[12]*t
    if dz < 0:
        r *= 0.8; g *= 0.8; b *= 0.8
    az = math.atan2(dy, dx)
    if az > EN[13] and az < EN[14] and el > EN[15] and el < EN[16]:
        # soft-edged window
        ea = min(az - EN[13], EN[14] - az) / 0.06
        ee = min(el - EN[15], EN[16] - el) / 0.06
        w = min(1.0, ea) * min(1.0, ee)
        r += EN[17]*w; g += EN[17]*w; b += EN[17]*w
    c = dx*EN[0] + dy*EN[1] + dz*EN[2]
    if c > EN[3]:
        r += EN[4]; g += EN[5]; b += EN[6]
    return r, g, b


@njit(cache=True, fastmath=True)
def glyph_at(px, py, pz, k, GL, ATL):
    gid = int(GL[k, 0])
    if gid < 0:
        return 0.0
    a = (px - GL[k, 1])*GL[k, 4] + (py - GL[k, 2])*GL[k, 5] + (pz - GL[k, 3])*GL[k, 6]
    b = (px - GL[k, 1])*GL[k, 7] + (py - GL[k, 2])*GL[k, 8] + (pz - GL[k, 3])*GL[k, 9]
    if a < -1 or a > 1 or b < -1 or b > 1:
        return 0.0
    S = ATL.shape[1]
    fx = (a + 1) * 0.5 * (S - 1); fy = (1 - b) * 0.5 * (S - 1)
    ix = int(fx); iy = int(fy)
    if ix >= S - 1: ix = S - 2
    if iy >= S - 1: iy = S - 2
    tx = fx - ix; ty = fy - iy
    v = (ATL[gid, iy, ix]*(1-tx) + ATL[gid, iy, ix+1]*tx)*(1-ty) + (ATL[gid, iy+1, ix]*(1-tx) + ATL[gid, iy+1, ix+1]*tx)*ty
    return v


@njit(cache=True, fastmath=True)
def fresnel(cosi, eta):
    """unpolarised Fresnel reflectance, eta = n1/n2, cosi>0. returns (F, cost) cost<0 -> TIR"""
    s2 = eta*eta*(1 - cosi*cosi)
    if s2 >= 1.0:
        return 1.0, -1.0
    cost = math.sqrt(1 - s2)
    rs = (eta*cosi - cost) / (eta*cosi + cost)
    rp = (cosi - eta*cost) / (cosi + eta*cost)
    return 0.5*(rs*rs + rp*rp), cost


@njit(cache=True, fastmath=True)
def shadow(px, py, pz, lx, ly, lz, PL, OB):
    t, k, p = nearest_obj(px, py, pz, lx, ly, lz, PL, OB, -1)
    return 0.0 if k >= 0 else 1.0


@njit(cache=True, fastmath=True)
def transmit(px, py, pz, lx, ly, lz, PL, OB):
    """straight-line transmittance through glass (for ambient occlusion rays)"""
    tr = 1.0; tg = 1.0; tb = 1.0
    for k in range(OB.shape[0]):
        tin, tout, pin, pout = hit_obj(px, py, pz, lx, ly, lz, PL, int(OB[k, 0]), int(OB[k, 1]))
        if tin <= tout and tout > 1e-6:
            L = tout - max(tin, 0.0)
            tr *= 0.8*math.exp(-OB[k, 6]*L); tg *= 0.8*math.exp(-OB[k, 7]*L); tb *= 0.8*math.exp(-OB[k, 8]*L)
    return tr, tg, tb


@njit(cache=True, fastmath=True)
def caustic_at(px, py, CG, CB):
    """bilinear lookup in caustic grid CG (H,W,3) covering CB=[x0,x1,y0,y1]"""
    H = CG.shape[0]; W = CG.shape[1]
    fx = (px - CB[0]) / (CB[1] - CB[0]) * W - 0.5
    fy = (py - CB[2]) / (CB[3] - CB[2]) * H - 0.5
    if fx < 0 or fy < 0 or fx >= W - 1 or fy >= H - 1:
        return 0.0, 0.0, 0.0
    ix = int(fx); iy = int(fy); tx = fx - ix; ty = fy - iy
    out = np.zeros(3)
    r = (CG[iy, ix, 0]*(1-tx) + CG[iy, ix+1, 0]*tx)*(1-ty) + (CG[iy+1, ix, 0]*(1-tx) + CG[iy+1, ix+1, 0]*tx)*ty
    g = (CG[iy, ix, 1]*(1-tx) + CG[iy, ix+1, 1]*tx)*(1-ty) + (CG[iy+1, ix, 1]*(1-tx) + CG[iy+1, ix+1, 1]*tx)*ty
    b = (CG[iy, ix, 2]*(1-tx) + CG[iy, ix+1, 2]*tx)*(1-ty) + (CG[iy+1, ix, 2]*(1-tx) + CG[iy+1, ix+1, 2]*tx)*ty
    return r, g, b


@njit(cache=True, fastmath=True)
def sun_sample(EN, LT):
    # jittered direction inside the sun cone (soft shadows)
    sx, sy, sz = EN[0], EN[1], EN[2]
    ax = 1.0 if abs(sx) < 0.9 else 0.0
    ay = 0.0 if abs(sx) < 0.9 else 1.0
    ux = ay*sz; uy = -ax*sz; uz = ax*sy - ay*sx
    l = math.sqrt(ux*ux+uy*uy+uz*uz); ux /= l; uy /= l; uz /= l
    vx = sy*uz - sz*uy; vy = sz*ux - sx*uz; vz = sx*uy - sy*ux
    r = LT[4] * math.sqrt(np.random.random()); a = 2*math.pi*np.random.random()
    dx = sx + r*math.cos(a)*ux + r*math.sin(a)*vx
    dy = sy + r*math.cos(a)*uy + r*math.sin(a)*vy
    dz = sz + r*math.cos(a)*uz + r*math.sin(a)*vz
    l = math.sqrt(dx*dx+dy*dy+dz*dz)
    return dx/l, dy/l, dz/l


@njit(cache=True, fastmath=True)
def shade_diffuse(px, py, pz, nx, ny, nz, ar, ag, ab, PL, OB, EN, LT, CG, CB, on_floor):
    """LT: [sun irradiance rgb(3), ambient scale, sun jitter radius]"""
    lx, ly, lz = sun_sample(EN, LT)
    cs = nx*lx + ny*ly + nz*lz
    r = 0.0; g = 0.0; b = 0.0
    ox = px + nx*1e-4; oy = py + ny*1e-4; oz = pz + nz*1e-4
    if cs > 0:
        s = shadow(ox, oy, oz, lx, ly, lz, PL, OB)
        r += LT[0]*cs*s; g += LT[1]*cs*s; b += LT[2]*cs*s
    if on_floor:
        cr, cg, cb = caustic_at(px, py, CG, CB)
        r += cr; g += cg; b += cb
    # ambient: one cosine sample
    u1 = np.random.random(); u2 = np.random.random()
    rr = math.sqrt(u1); ph = 2*math.pi*u2
    ax = 1.0 if abs(nx) < 0.9 else 0.0
    ay = 0.0 if abs(nx) < 0.9 else 1.0
    tx = ay*nz; ty = -ax*nz; tz = ax*ny - ay*nx
    l = math.sqrt(tx*tx+ty*ty+tz*tz); tx /= l; ty /= l; tz /= l
    bx = ny*tz - nz*ty; by = nz*tx - nx*tz; bz = nx*ty - ny*tx
    zz = math.sqrt(max(0.0, 1 - u1))
    dx = rr*math.cos(ph)*tx + rr*math.sin(ph)*bx + zz*nx
    dy = rr*math.cos(ph)*ty + rr*math.sin(ph)*by + zz*ny
    dz = rr*math.cos(ph)*tz + rr*math.sin(ph)*bz + zz*nz
    er, eg, eb = env(dx, dy, dz, EN)
    if dz < 0.15 and on_floor:
        # bounce light from the (bright) sweep itself instead of the sky below/near horizon
        er = 0.9; eg = 0.88; eb = 0.9
    tr, tg, tb = transmit(ox, oy, oz, dx, dy, dz, PL, OB)
    r += LT[3]*er*tr; g += LT[3]*eg*tg; b += LT[3]*eb*tb
    return r*ar, g*ag, b*ab


@njit(cache=True, fastmath=True)
def radiance(ox, oy, oz, dx, dy, dz, PL, OB, GL, ATL, SW, PAP, EN, LT, CG, CB, maxd):
    Tr = 1.0; Tg = 1.0; Tb = 1.0
    Lr = 0.0; Lg = 0.0; Lb = 0.0
    inside = -1
    done = False
    nint = 0
    for depth in range(maxd):
        if inside >= 0:
            k = inside
            tin, tout, pin, pout = hit_obj(ox, oy, oz, dx, dy, dz, PL, int(OB[k, 0]), int(OB[k, 1]))
            t = max(tout, 0.0)
            if pout < 0 or t > 1e9:
                break
            Tr *= math.exp(-OB[k, 6]*t); Tg *= math.exp(-OB[k, 7]*t); Tb *= math.exp(-OB[k, 8]*t)
            px = ox + t*dx; py = oy + t*dy; pz = oz + t*dz
            nx, ny, nz = PL[pout, 0], PL[pout, 1], PL[pout, 2]
            ink = glyph_at(px, py, pz, pout, GL, ATL)
            if ink > 0 and np.random.random() < ink:
                # back of the paint seen through glass: lit by what the glass passes
                a = 0.55
                Lr += Tr*OB[k, 9]*a; Lg += Tg*OB[k, 10]*a; Lb += Tb*OB[k, 11]*a
                done = True
                break
            cosi = dx*nx + dy*ny + dz*nz  # >0 leaving
            F, cost = fresnel(cosi, IOR)
            if cost < 0 or np.random.random() < F:
                nint += 1
                if nint > MAXINT:
                    # imperfect glass: a long internal path scatters out (no crisp light-pipe streaks)
                    er, eg, eb = env(dx, dy, dz, EN)
                    Lr += Tr*0.75; Lg += Tg*0.75; Lb += Tb*0.75
                    done = True
                    break
                dx -= 2*cosi*nx; dy -= 2*cosi*ny; dz -= 2*cosi*nz
                ox = px - nx*1e-6; oy = py - ny*1e-6; oz = pz - nz*1e-6
            else:
                eta = IOR
                # refract out: t = eta*d + (cost - eta*cosi) n   (n outward, cosi>0)
                dx = eta*dx + (cost - eta*cosi)*nx
                dy = eta*dy + (cost - eta*cosi)*ny
                dz = eta*dz + (cost - eta*cosi)*nz
                l = math.sqrt(dx*dx+dy*dy+dz*dz); dx /= l; dy /= l; dz /= l
                ox = px + nx*1e-6; oy = py + ny*1e-6; oz = pz + nz*1e-6
                inside = -1
            continue
        to, k, pin = nearest_obj(ox, oy, oz, dx, dy, dz, PL, OB, -1)
        ts, kind = sweep_hit(ox, oy, oz, dx, dy, dz, SW)
        if k < 0 and kind < 0:
            er, eg, eb = env(dx, dy, dz, EN)
            Lr += Tr*er; Lg += Tg*eg; Lb += Tb*eb
            done = True
            break
        if k >= 0 and to < ts:
            px = ox + to*dx; py = oy + to*dy; pz = oz + to*dz
            nx, ny, nz = PL[pin, 0], PL[pin, 1], PL[pin, 2]
            ink = glyph_at(px, py, pz, pin, GL, ATL)
            if ink > 0 and np.random.random() < ink:
                sr, sg, sb = shade_diffuse(px, py, pz, nx, ny, nz, OB[k, 9], OB[k, 10], OB[k, 11], PL, OB, EN, LT, CG, CB, False)
                Lr += Tr*sr; Lg += Tg*sg; Lb += Tb*sb
                done = True
                break
            cosi = -(dx*nx + dy*ny + dz*nz)
            F, cost = fresnel(cosi, 1.0/IOR)
            if np.random.random() < F:
                dx += 2*cosi*nx; dy += 2*cosi*ny; dz += 2*cosi*nz
                ox = px + nx*1e-6; oy = py + ny*1e-6; oz = pz + nz*1e-6
            else:
                eta = 1.0/IOR
                dx = eta*dx + (eta*cosi - cost)*nx
                dy = eta*dy + (eta*cosi - cost)*ny
                dz = eta*dz + (eta*cosi - cost)*nz
                l = math.sqrt(dx*dx+dy*dy+dz*dz); dx /= l; dy /= l; dz /= l
                ox = px - nx*1e-6; oy = py - ny*1e-6; oz = pz - nz*1e-6
                inside = k
            continue
        # paper
        px = ox + ts*dx; py = oy + ts*dy; pz = oz + ts*dz
        nx, ny, nz = sweep_normal(px, py, pz, kind, SW)
        ar, ag, ab = paper(px, py, pz, kind, SW, PAP)
        sr, sg, sb = shade_diffuse(px, py, pz, nx, ny, nz, ar, ag, ab, PL, OB, EN, LT, CG, CB, kind == 0)
        # studio fill on the sweep (a soft light from the camera side washes the backdrop), ramped in on the floor
        fw = 1.0 if kind != 0 else min(max((py - (SW[0] - 4.0)) / 4.0, 0.0), 1.0)
        fw = fw*fw*(3 - 2*fw)
        sr += LT[5]*ar*fw; sg += LT[5]*ag*fw; sb += LT[5]*ab*fw
        Lr += Tr*sr; Lg += Tg*sg; Lb += Tb*sb
        done = True
        break
    if not done:
        er, eg, eb = env(dx, dy, dz, EN)
        Lr += Tr*er*0.8; Lg += Tg*eg*0.8; Lb += Tb*eb*0.8
    return Lr, Lg, Lb


@njit(parallel=True, cache=True, fastmath=True)
def render(H, W, y0r, y1r, CAM, PL, OB, GL, ATL, SW, PAP, EN, LT, CG, CB, spp, maxd, seed):
    """CAM: [eye(3), fwd(3), right(3), up(3), tan half fov x, aperture, focus dist]"""
    img = np.zeros((y1r - y0r, W, 3))
    for jj in prange(y1r - y0r):
        j = jj + y0r
        np.random.seed(seed * 100003 + j)
        for i in range(W):
            r = 0.0; g = 0.0; b = 0.0
            for s in range(spp):
                sx = (2*(i + np.random.random())/W - 1) * CAM[12]
                sy = (1 - 2*(j + np.random.random())/H) * CAM[12] * H / W
                dx = CAM[3] + sx*CAM[6] + sy*CAM[9]
                dy = CAM[4] + sx*CAM[7] + sy*CAM[10]
                dz = CAM[5] + sx*CAM[8] + sy*CAM[11]
                l = math.sqrt(dx*dx+dy*dy+dz*dz); dx /= l; dy /= l; dz /= l
                ox, oy, oz = CAM[0], CAM[1], CAM[2]
                if CAM[13] > 0:
                    # thin lens
                    fd = CAM[14] / (dx*CAM[3] + dy*CAM[4] + dz*CAM[5])
                    fx = ox + fd*dx; fy = oy + fd*dy; fz = oz + fd*dz
                    rr = CAM[13]*math.sqrt(np.random.random()); a = 2*math.pi*np.random.random()
                    ox += rr*(math.cos(a)*CAM[6] + math.sin(a)*CAM[9])
                    oy += rr*(math.cos(a)*CAM[7] + math.sin(a)*CAM[10])
                    oz += rr*(math.cos(a)*CAM[8] + math.sin(a)*CAM[11])
                    dx = fx - ox; dy = fy - oy; dz = fz - oz
                    l = math.sqrt(dx*dx+dy*dy+dz*dz); dx /= l; dy /= l; dz /= l
                lr, lg, lb = radiance(ox, oy, oz, dx, dy, dz, PL, OB, GL, ATL, SW, PAP, EN, LT, CG, CB, maxd)
                m = max(lr, lg, lb)
                if m > 12.0:
                    lr *= 12.0/m; lg *= 12.0/m; lb *= 12.0/m
                r += lr; g += lg; b += lb
            img[jj, i, 0] = r/spp; img[jj, i, 1] = g/spp; img[jj, i, 2] = b/spp
    return img


@njit(parallel=True, cache=True, fastmath=True)
def photons(PL, OB, GL, ATL, EN, LT, CB, GH, GW, nper, seed):
    """Sun photons through each object's bounding disc; deposit the light that went through glass on
    the floor grid. Returns irradiance grid (GH, GW, 3)."""
    K = OB.shape[0]
    NT = 4
    acc = np.zeros((NT, GH, GW, 3))
    sx, sy, sz = EN[0], EN[1], EN[2]
    ax = 1.0 if abs(sx) < 0.9 else 0.0
    ay = 0.0 if abs(sx) < 0.9 else 1.0
    ux = ay*sz; uy = -ax*sz; uz = ax*sy - ay*sx
    l = math.sqrt(ux*ux+uy*uy+uz*uz); ux /= l; uy /= l; uz /= l
    vx = sy*uz - sz*uy; vy = sz*ux - sx*uz; vz = sx*uy - sy*ux
    cell = (CB[1]-CB[0])/GW * (CB[3]-CB[2])/GH
    for th in prange(NT):
        np.random.seed(seed*7919 + th)
        for k in range(K):
            R = OB[k, 5]*1.02
            area = math.pi*R*R
            n = nper // NT
            wr = LT[0]*area/(n*NT)/cell; wg = LT[1]*area/(n*NT)/cell; wb = LT[2]*area/(n*NT)/cell
            for s in range(n):
                rr = R*math.sqrt(np.random.random()); a = 2*math.pi*np.random.random()
                cx = OB[k, 2] + rr*(math.cos(a)*ux + math.sin(a)*vx) + sx*4*R
                cy = OB[k, 3] + rr*(math.cos(a)*uy + math.sin(a)*vy) + sy*4*R
                cz = OB[k, 4] + rr*(math.cos(a)*uz + math.sin(a)*vz) + sz*4*R
                ox, oy, oz = cx, cy, cz
                dx, dy, dz = -sx, -sy, -sz
                Tr = 1.0; Tg = 1.0; Tb = 1.0
                inside = -1
                touched = False
                alive = True
                for depth in range(12):
                    if inside >= 0:
                        kk = inside
                        tin, tout, pin, pout = hit_obj(ox, oy, oz, dx, dy, dz, PL, int(OB[kk, 0]), int(OB[kk, 1]))
                        t = max(tout, 0.0)
                        if pout < 0:
                            alive = False; break
                        Tr *= math.exp(-OB[kk, 6]*t); Tg *= math.exp(-OB[kk, 7]*t); Tb *= math.exp(-OB[kk, 8]*t)
                        px = ox + t*dx; py = oy + t*dy; pz = oz + t*dz
                        nx, ny, nz = PL[pout, 0], PL[pout, 1], PL[pout, 2]
                        if glyph_at(px, py, pz, pout, GL, ATL) > np.random.random():
                            alive = False; break
                        cosi = dx*nx + dy*ny + dz*nz
                        F, cost = fresnel(cosi, IOR)
                        if cost < 0 or np.random.random() < F:
                            dx -= 2*cosi*nx; dy -= 2*cosi*ny; dz -= 2*cosi*nz
                            ox = px - nx*1e-6; oy = py - ny*1e-6; oz = pz - nz*1e-6
                        else:
                            dx = IOR*dx + (cost - IOR*cosi)*nx
                            dy = IOR*dy + (cost - IOR*cosi)*ny
                            dz = IOR*dz + (cost - IOR*cosi)*nz
                            l = math.sqrt(dx*dx+dy*dy+dz*dz); dx /= l; dy /= l; dz /= l
                            ox = px + nx*1e-6; oy = py + ny*1e-6; oz = pz + nz*1e-6
                            inside = -1
                        continue
                    to, kk, pin = nearest_obj(ox, oy, oz, dx, dy, dz, PL, OB, -1)
                    if kk >= 0:
                        touched = True
                        px = ox + to*dx; py = oy + to*dy; pz = oz + to*dz
                        nx, ny, nz = PL[pin, 0], PL[pin, 1], PL[pin, 2]
                        if glyph_at(px, py, pz, pin, GL, ATL) > np.random.random():
                            alive = False; break
                        cosi = -(dx*nx + dy*ny + dz*nz)
                        F, cost = fresnel(cosi, 1.0/IOR)
                        if np.random.random() < F:
                            dx += 2*cosi*nx; dy += 2*cosi*ny; dz += 2*cosi*nz
                            ox = px + nx*1e-6; oy = py + ny*1e-6; oz = pz + nz*1e-6
                        else:
                            eta = 1.0/IOR
                            dx = eta*dx + (eta*cosi - cost)*nx
                            dy = eta*dy + (eta*cosi - cost)*ny
                            dz = eta*dz + (eta*cosi - cost)*nz
                            l = math.sqrt(dx*dx+dy*dy+dz*dz); dx /= l; dy /= l; dz /= l
                            ox = px - nx*1e-6; oy = py - ny*1e-6; oz = pz - nz*1e-6
                            inside = kk
                        continue
                    break
                if not alive or not touched or inside >= 0 or dz >= 0:
                    continue
                t = -oz/dz
                px = ox + t*dx; py = oy + t*dy
                gx = int((px - CB[0])/(CB[1]-CB[0])*GW); gy = int((py - CB[2])/(CB[3]-CB[2])*GH)
                if gx < 0 or gy < 0 or gx >= GW or gy >= GH:
                    continue
                acc[th, gy, gx, 0] += wr*Tr; acc[th, gy, gx, 1] += wg*Tg; acc[th, gy, gx, 2] += wb*Tb
    out = np.zeros((GH, GW, 3))
    for th in range(NT):
        out += acc[th]
    return out
