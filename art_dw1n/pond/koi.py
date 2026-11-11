# Koi pond engine: a graph as lily pads, directed cycles as schools of koi.
# Top view, layered painter with numba kernels. World units: one cube edge = 1.
import numpy as np, math
from numba import njit

# ---------------------------------------------------------------- palette
def hexc(h): return np.array([int(h[i:i+2], 16) / 255 for i in (1, 3, 5)], dtype=np.float32)
PAPER = np.array([0.992, 0.985, 0.975], dtype=np.float32)
INK = hexc('#5c4d66')
# school: (base, patch, fin tint, trail)
SCHOOLS = [
    dict(name='coral', base=hexc('#fff3ea'), patch=hexc('#ff6f5c'), patch2=hexc('#ffb39c'), fin=hexc('#ffb5a6'), trail=hexc('#ff8f7c')),
    dict(name='butter', base=hexc('#ffe9a0'), patch=hexc('#ffbe2e'), patch2=hexc('#fff6da'), fin=hexc('#ffe08a'), trail=hexc('#ffc93f')),
    dict(name='orchid', base=hexc('#f0dcfa'), patch=hexc('#b565dc'), patch2=hexc('#dcb6f2'), fin=hexc('#d9a9f0'), trail=hexc('#c07fe3')),
    dict(name='pearl', base=hexc('#ffffff'), patch=hexc('#5f86ea'), patch2=hexc('#ffffff'), fin=hexc('#dfe8ff'), trail=hexc('#6f93ee')),
    dict(name='rose', base=hexc('#ffd9e8'), patch=hexc('#f0609c'), patch2=hexc('#fff0f5'), fin=hexc('#ffc0d8'), trail=hexc('#f78bb6')),
    dict(name='peach', base=hexc('#ffe2c8'), patch=hexc('#ff9a4d'), patch2=hexc('#fff2e2'), fin=hexc('#ffd0a8'), trail=hexc('#ffb070')),
    dict(name='plum', base=hexc('#d9c8e6'), patch=hexc('#77588f'), patch2=hexc('#f4ecfa'), fin=hexc('#cdb8dc'), trail=hexc('#9a7fb0')),
]

# ---------------------------------------------------------------- geometry
def catmull_closed(P, per=24):
    """closed centripetal-ish Catmull-Rom through points P (n,2) -> dense polyline"""
    n = len(P); out = []
    for i in range(n):
        p0, p1, p2, p3 = P[(i - 1) % n], P[i], P[(i + 1) % n], P[(i + 2) % n]
        t = np.linspace(0, 1, per, endpoint=False)[:, None]
        a = 0.5
        m1 = a * (p2 - p0); m2 = a * (p3 - p1)
        h00 = 2 * t**3 - 3 * t**2 + 1; h10 = t**3 - 2 * t**2 + t
        h01 = -2 * t**3 + 3 * t**2; h11 = t**3 - t**2
        out.append(h00 * p1 + h10 * m1 + h01 * p2 + h11 * m2)
    return np.concatenate(out)

def loop_path(pos, cyc, delta=0.045, rin=0.2, bulge=0.0, per=20):
    """directed cycle through pads -> smooth closed lane, offset to the right of travel"""
    n = len(cyc); C = []
    for k in range(n):
        u = pos[cyc[k]]; v = pos[cyc[(k + 1) % n]]
        t = v - u; L = np.linalg.norm(t); t = t / L
        nr = np.array([t[1], -t[0]])          # right of travel (y down on screen -> visual left; consistent anyway)
        r = min(rin, 0.33 * L)
        C.append(u + r * t + delta * nr)
        C.append(0.5 * (u + v) + (delta + bulge) * nr)
        C.append(v - r * t + delta * nr)
    return catmull_closed(np.array(C), per)

def resample(poly, ds):
    d = np.linalg.norm(np.roll(poly, -1, 0) - poly, axis=1)
    s = np.concatenate([[0], np.cumsum(d)]); L = s[-1]
    P = np.vstack([poly, poly[:1]])
    m = int(L / ds)
    q = np.linspace(0, L, m, endpoint=False)
    return np.stack([np.interp(q, s, P[:, 0]), np.interp(q, s, P[:, 1])], 1), L

def make_fish(path, L_path, s_head, flen, fw, phase, rng, K=36):
    """spine from head (index 0) backwards along the path, with a tail sway"""
    m = len(path); ds = L_path / m
    tt = np.linspace(0, 1, K)
    idx = (s_head - tt * flen) / ds
    i0 = np.floor(idx).astype(int); f = (idx - i0)[:, None]
    P = path[i0 % m] * (1 - f) + path[(i0 + 1) % m] * f
    T = path[(i0 + 1) % m] - path[i0 % m]; T /= np.linalg.norm(T, axis=1)[:, None]
    N = np.stack([-T[:, 1], T[:, 0]], 1)
    sway = fw * 0.9 * (tt**1.6) * np.sin(2 * np.pi * (tt * 0.85 + phase))
    return (P + N * sway[:, None]).astype(np.float32)

# ---------------------------------------------------------------- numba kernels
@njit(cache=True)
def hash2(ix, iy, seed):
    h = (ix * 374761393 + iy * 668265263 + seed * 1274126177) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1103515245) & 0xFFFFFFFF
    h = h ^ (h >> 16)
    return (h & 0xFFFFFF) / 16777216.0

@njit(cache=True)
def vnoise(x, y, seed):
    ix = math.floor(x); iy = math.floor(y)
    fx = x - ix; fy = y - iy
    fx = fx * fx * (3 - 2 * fx); fy = fy * fy * (3 - 2 * fy)
    a = hash2(ix, iy, seed); b = hash2(ix + 1, iy, seed)
    c = hash2(ix, iy + 1, seed); d = hash2(ix + 1, iy + 1, seed)
    return a + (b - a) * fx + (c - a) * fy + (a - b - c + d) * fx * fy

@njit(cache=True)
def sstep(a, b, x):
    t = (x - a) / (b - a)
    if t < 0: t = 0.0
    if t > 1: t = 1.0
    return t * t * (3 - 2 * t)

@njit(cache=True)
def body_w(t):
    if t < 0.0 or t > 0.8: return 0.0
    if t < 0.28:
        q = (0.28 - t) / 0.28
        return math.sqrt(max(0.0, 1 - q * q * q * 0.999 * q ** 0.2))
    q = (t - 0.28) / 0.52
    return 1 - 0.74 * q ** 1.3

@njit(cache=True)
def stroke_max(cov, pts, closed, hw, soft, S, ox, oy):
    """max-coverage soft stroke of a polyline (world coords) into cov (H,W)"""
    H, W = cov.shape; n = len(pts)
    m = n if closed else n - 1
    R = hw + soft
    for k in range(m):
        ax = pts[k, 0]; ay = pts[k, 1]; bx = pts[(k + 1) % n, 0]; by = pts[(k + 1) % n, 1]
        x0 = int((min(ax, bx) - R - ox) * S); x1 = int((max(ax, bx) + R - ox) * S) + 1
        y0 = int((min(ay, by) - R - oy) * S); y1 = int((max(ay, by) + R - oy) * S) + 1
        if x1 < 0 or y1 < 0 or x0 >= W or y0 >= H: continue
        x0 = max(x0, 0); y0 = max(y0, 0); x1 = min(x1, W - 1); y1 = min(y1, H - 1)
        dx = bx - ax; dy = by - ay; ll = dx * dx + dy * dy + 1e-12
        for i in range(y0, y1 + 1):
            py = (i + 0.5) / S + oy
            for j in range(x0, x1 + 1):
                px = (j + 0.5) / S + ox
                u = ((px - ax) * dx + (py - ay) * dy) / ll
                if u < 0: u = 0.0
                if u > 1: u = 1.0
                d = math.hypot(px - ax - u * dx, py - ay - u * dy)
                c = 1 - sstep(hw - soft, hw + soft, d)
                if c > cov[i, j]: cov[i, j] = c

@njit(cache=True)
def fish_sil(shad, sp, fw, flen, soft, S, ox, oy, offx, offy):
    """soft silhouette (for the shadow on the pond floor), max into shad"""
    H, W = shad.shape; K = len(sp)
    R = fw * 1.3 + soft
    xmin = 1e9; xmax = -1e9; ymin = 1e9; ymax = -1e9
    for k in range(K):
        xmin = min(xmin, sp[k, 0]); xmax = max(xmax, sp[k, 0]); ymin = min(ymin, sp[k, 1]); ymax = max(ymax, sp[k, 1])
    x0 = max(int((xmin - R + offx - ox) * S), 0); x1 = min(int((xmax + R + offx - ox) * S) + 1, W - 1)
    y0 = max(int((ymin - R + offy - oy) * S), 0); y1 = min(int((ymax + R + offy - oy) * S) + 1, H - 1)
    for i in range(y0, y1 + 1):
        py = (i + 0.5) / S + oy - offy
        for j in range(x0, x1 + 1):
            px = (j + 0.5) / S + ox - offx
            best = 1e9; bt = 0.0
            for k in range(K - 1):
                ax = sp[k, 0]; ay = sp[k, 1]; dx = sp[k + 1, 0] - ax; dy = sp[k + 1, 1] - ay
                u = ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy + 1e-12)
                if u < 0: u = 0.0
                if u > 1: u = 1.0
                d = math.hypot(px - ax - u * dx, py - ay - u * dy)
                if d < best: best = d; bt = (k + u) / (K - 1)
            w = body_w(bt) * fw
            if bt > 0.74:
                q = (bt - 0.74) / 0.26
                w = max(w, fw * (0.2 + 0.7 * q ** 0.8))
            c = 1 - sstep(-soft, soft, best - w)
            if c > shad[i, j]: shad[i, j] = c

@njit(cache=True)
def draw_fish(img, sp, fins, fw, flen, base, patch, patch2, fin, seed, thr, depth_tint, wcol, S, ox, oy, lx, ly):
    H, W, _ = img.shape; K = len(sp)
    R = fw * 3.0
    aa = 1.0 / S
    xmin = 1e9; xmax = -1e9; ymin = 1e9; ymax = -1e9
    for k in range(K):
        xmin = min(xmin, sp[k, 0]); xmax = max(xmax, sp[k, 0]); ymin = min(ymin, sp[k, 1]); ymax = max(ymax, sp[k, 1])
    x0 = max(int((xmin - R - ox) * S), 0); x1 = min(int((xmax + R - ox) * S) + 1, W - 1)
    y0 = max(int((ymin - R - oy) * S), 0); y1 = min(int((ymax + R - oy) * S) + 1, H - 1)
    nf = len(fins)
    for i in range(y0, y1 + 1):
        py = (i + 0.5) / S + oy
        for j in range(x0, x1 + 1):
            px = (j + 0.5) / S + ox
            best = 1e9; bt = 0.0; bs = 0.0; nxs = 0.0; nys = 0.0
            for k in range(K - 1):
                ax = sp[k, 0]; ay = sp[k, 1]; dx = sp[k + 1, 0] - ax; dy = sp[k + 1, 1] - ay
                ll = dx * dx + dy * dy + 1e-12
                u = ((px - ax) * dx + (py - ay) * dy) / ll
                if u < 0: u = 0.0
                if u > 1: u = 1.0
                ex = px - ax - u * dx; ey = py - ay - u * dy
                d = math.hypot(ex, ey)
                if d < best:
                    best = d; bt = (k + u) / (K - 1)
                    il = 1 / math.sqrt(ll)
                    bs = (ex * (-dy) + ey * dx) * il      # signed lateral
                    nxs = -dy * il; nys = dx * il
            cr = 0.0; cg = 0.0; cb = 0.0; al = 0.0
            # ---- fins (under the body): translucent, rayed
            for f in range(nf):
                cx = fins[f, 0]; cy = fins[f, 1]; ddx = fins[f, 2]; ddy = fins[f, 3]; a = fins[f, 4]; b = fins[f, 5]
                qx = (px - cx) * ddx + (py - cy) * ddy; qy = -(px - cx) * ddy + (py - cy) * ddx
                # teardrop: narrower near the root (qx<0)
                bb = b * (0.55 + 0.45 * sstep(-a, a * 0.6, qx))
                e = math.sqrt((qx / a) ** 2 + (qy / bb) ** 2)
                c = 1 - sstep(1 - 2.5 * aa / b, 1 + 2.5 * aa / b, e)
                if c > 0:
                    ray = 0.82 + 0.18 * math.sin(math.atan2(qy, qx + 1.6 * a) * 70.0)
                    fa = c * (0.72 + 0.2 * (1 - e)) * ray
                    fr = 0.2 + 0.8 * fin[0]; fg = 0.2 + 0.8 * fin[1]; fb = 0.2 + 0.8 * fin[2]
                    cr = cr * (1 - fa) + fr * fa; cg = cg * (1 - fa) + fg * fa; cb = cb * (1 - fa) + fb * fa
                    al = al + fa * (1 - al)
            # ---- tail fin
            if bt > 0.74:
                q = (bt - 0.74) / 0.26
                wt = fw * (0.20 + 0.92 * q ** 1.1)
                notch = fw * 0.80 * sstep(0.55, 1.0, q) ** 1.5
                ad = abs(bs)
                c = (1 - sstep(-aa, aa, ad - wt)) * sstep(-aa, aa, ad - notch) * (1 - sstep(0.985, 1.0, bt + best * 0.0))
                if best > ad + 2 * aa and bt >= 0.999: c = 0.0
                if c > 0:
                    ray = 0.88 + 0.12 * math.sin(bs / (wt + 1e-9) * 14.0)
                    fa = c * (0.95 - 0.25 * q) * ray
                    fr = 0.15 + 0.85 * fin[0]; fg = 0.15 + 0.85 * fin[1]; fb = 0.15 + 0.85 * fin[2]
                    cr = cr * (1 - fa) + fr * fa; cg = cg * (1 - fa) + fg * fa; cb = cb * (1 - fa) + fb * fa
                    al = al + fa * (1 - al)
            # ---- body
            w = body_w(bt) * fw
            if w > 0:
                c = 1 - sstep(-aa, aa, best - w)
                if c > 0:
                    u = bs / w
                    if u > 1: u = 1.0
                    if u < -1: u = -1.0
                    h = math.sqrt(max(0.0, 1 - u * u))
                    # koi pattern: big soft blobs in body coordinates
                    nz = 0.65 * vnoise(bt * 4.2 + 3.1, u * 0.9 + 7.7, seed) + 0.35 * vnoise(bt * 9.0, u * 2.0, seed + 5)
                    m1 = sstep(thr - 0.035, thr + 0.035, nz)
                    nz2 = vnoise(bt * 6.0 + 11.0, u * 1.4, seed + 9)
                    m2 = sstep(0.60, 0.66, nz2) * (1 - m1)
                    r = base[0] * (1 - m1) + patch[0] * m1; g = base[1] * (1 - m1) + patch[1] * m1; bl = base[2] * (1 - m1) + patch[2] * m1
                    r = r * (1 - m2) + patch2[0] * m2; g = g * (1 - m2) + patch2[1] * m2; bl = bl * (1 - m2) + patch2[2] * m2
                    # scales
                    sc = math.sin(bt * flen / fw * 9.0 + math.asin(u) * 5.0) * math.sin(bt * flen / fw * 9.0 - math.asin(u) * 5.0)
                    scl = 1 + 0.035 * sc * sstep(0.2, 0.3, bt)
                    lit = (nxs * lx + nys * ly) * u      # which flank faces the light
                    sh = (0.80 + 0.22 * h - 0.10 * lit) * scl
                    spec = 0.30 * math.exp(-((u + 0.38 * (1.0 if (nxs * lx + nys * ly) > 0 else -1.0)) / 0.2) ** 2) * sstep(0.02, 0.2, bt) * (1 - sstep(0.5, 0.78, bt))
                    edge = sstep(0.75, 1.0, abs(u))
                    r = r * sh * (1 - 0.22 * edge) + spec; g = g * sh * (1 - 0.26 * edge) + spec; bl = bl * sh * (1 - 0.18 * edge) + spec
                    # dorsal fin line
                    dl = (1 - sstep(0.05, 0.11, abs(u))) * sstep(0.30, 0.36, bt) * (1 - sstep(0.56, 0.62, bt))
                    r = r * (1 - 0.25 * dl) + patch2[0] * 0.25 * dl; g = g * (1 - 0.25 * dl) + patch2[1] * 0.25 * dl; bl = bl * (1 - 0.25 * dl) + patch2[2] * 0.25 * dl
                    # eyes
                    te = 0.085
                    ew = body_w(te) * fw * 0.62
                    de = math.hypot((bt - te) * flen, abs(bs) - ew)
                    eye = 1 - sstep(fw * 0.085, fw * 0.085 + 2 * aa, de)
                    r = r * (1 - eye) + 0.25 * eye; g = g * (1 - eye) + 0.2 * eye; bl = bl * (1 - eye) + 0.3 * eye
                    cr = cr * (1 - c) + r * c; cg = cg * (1 - c) + g * c; cb = cb * (1 - c) + bl * c
                    al = al + c * (1 - al)
            if al > 0:
                # premultiplied composite, tinted by the water above the fish
                tr = cr * (1 - depth_tint) + wcol[0] * depth_tint * al
                tg = cg * (1 - depth_tint) + wcol[1] * depth_tint * al
                tb = cb * (1 - depth_tint) + wcol[2] * depth_tint * al
                img[i, j, 0] = img[i, j, 0] * (1 - al) + tr
                img[i, j, 1] = img[i, j, 1] * (1 - al) + tg
                img[i, j, 2] = img[i, j, 2] * (1 - al) + tb

@njit(cache=True)
def draw_pad(img, cx, cy, r, rot, col, col2, flower, seed, S, ox, oy, pet1, pet2, pet3, gold):
    H, W, _ = img.shape
    aa = 1.0 / S
    x0 = max(int((cx - r * 1.1 - ox) * S), 0); x1 = min(int((cx + r * 1.1 - ox) * S) + 1, W - 1)
    y0 = max(int((cy - r * 1.1 - oy) * S), 0); y1 = min(int((cy + r * 1.1 - oy) * S) + 1, H - 1)
    for i in range(y0, y1 + 1):
        py = (i + 0.5) / S + oy - cy
        for j in range(x0, x1 + 1):
            px = (j + 0.5) / S + ox - cx
            d = math.hypot(px, py)
            th = math.atan2(py, px) - rot
            th = (th + math.pi) % (2 * math.pi) - math.pi
            # wavy rim + notch
            rr = r * (1 + 0.018 * math.sin(th * 9 + seed) + 0.012 * math.sin(th * 17 + 2.0 * seed))
            c = 1 - sstep(-aa, aa, d - rr)
            notch = abs(th) * d - 0.10 * r * (d / r) ** 0.6   # distance-ish from the notch wedge
            c *= sstep(-aa, aa, notch + 0.0 * r) if d > 0.08 * r else 1.0
            if c <= 0: continue
            q = d / r
            veins = abs(math.sin(th * 5.5 + 0.25 * math.sin(q * 5.0 + seed))) ** 0.12
            vein = (1 - veins) * sstep(0.05, 0.3, q) * 1.6
            mix = 0.25 + 0.75 * q * q
            rcol = col2[0] * (1 - mix) + col[0] * mix; g = col2[1] * (1 - mix) + col[1] * mix; b = col2[2] * (1 - mix) + col[2] * mix
            mott = 0.94 + 0.12 * vnoise(px / r * 3.0 + 10, py / r * 3.0 + 10, seed)
            rcol *= mott; g *= mott; b *= mott
            rcol += 0.22 * vein; g += 0.16 * vein; b += 0.14 * vein
            rim = sstep(0.86, 1.0, q)
            lit = -(px * 0.6 + py * 0.8) / (d + 1e-9)
            rcol = rcol * (1 - 0.10 * rim) + 0.16 * rim * max(lit, 0.0); g = g * (1 - 0.06 * rim) + 0.16 * rim * max(lit, 0.0); b = b * (1 - 0.10 * rim) + 0.14 * rim * max(lit, 0.0)
            if flower > 0:
                R1 = r * 0.82
                # flower shadow on the pad
                ds = math.hypot(px - 0.07 * r, py - 0.09 * r)
                s = (1 - sstep(R1 * 0.55, R1 * 1.05, ds)) * 0.20
                rcol *= 1 - s; g *= 1 - 0.8 * s; b *= 1 - 0.7 * s
                for ring in range(3):
                    npet = 9 if ring < 2 else 6
                    Rr = R1 * (1.0, 0.70, 0.42)[ring]
                    off = rot + seed * 0.37 + ring * math.pi / npet
                    a = math.atan2(py, px) - off
                    sp_ = abs(math.sin(a * npet / 2))
                    rho = Rr * (1 - 0.72 * sp_ ** 1.25)
                    cp = 1 - sstep(-aa, aa, d - rho)
                    if cp > 0:
                        tt = d / (rho + 1e-9)
                        if ring == 0: pc = pet1
                        elif ring == 1: pc = pet2
                        else: pc = pet3
                        tip = tt ** 1.5
                        pr = pc[0] * (1 - 0.0) + (1 - pc[0]) * 0.55 * tip
                        pg = pc[1] + (1 - pc[1]) * 0.55 * tip
                        pb = pc[2] + (1 - pc[2]) * 0.55 * tip
                        mid = 1 - 0.10 * (1 - sstep(0.0, 0.25, sp_))    # midrib
                        sep = 1 - 0.16 * sstep(0.80, 1.0, tt) * (1 - sstep(0.0, 0.3, sp_) * 0.0) * 0.0 - 0.22 * sstep(0.55, 1.0, sp_ / (1 - 0.72 * 0.0))  # darker between petals
                        pr *= mid * sep; pg *= mid * sep; pb *= mid * sep
                        rcol = rcol * (1 - cp) + pr * cp; g = g * (1 - cp) + pg * cp; b = b * (1 - cp) + pb * cp
                cc = 1 - sstep(-aa, aa, d - R1 * 0.17)
                if cc > 0:
                    dots = 0.9 + 0.2 * vnoise(px / r * 40, py / r * 40, seed)
                    rcol = rcol * (1 - cc) + gold[0] * dots * cc; g = g * (1 - cc) + gold[1] * dots * cc; b = b * (1 - cc) + gold[2] * dots * cc
            img[i, j, 0] = img[i, j, 0] * (1 - c) + rcol * c
            img[i, j, 1] = img[i, j, 1] * (1 - c) + g * c
            img[i, j, 2] = img[i, j, 2] * (1 - c) + b * c

@njit(cache=True)
def disc_soft(buf, cx, cy, r, soft, S, ox, oy):
    H, W = buf.shape
    R = r + soft
    x0 = max(int((cx - R - ox) * S), 0); x1 = min(int((cx + R - ox) * S) + 1, W - 1)
    y0 = max(int((cy - R - oy) * S), 0); y1 = min(int((cy + R - oy) * S) + 1, H - 1)
    for i in range(y0, y1 + 1):
        py = (i + 0.5) / S + oy - cy
        for j in range(x0, x1 + 1):
            px = (j + 0.5) / S + ox - cx
            c = 1 - sstep(r - soft, r + soft, math.hypot(px, py))
            if c > buf[i, j]: buf[i, j] = c

@njit(cache=True)
def terrazzo(img, mask, S, ox, oy, chips, seed, cell):
    """pastel chips on the pond rim; mask (H,W) = rim coverage"""
    H, W, _ = img.shape
    nc = len(chips)
    for i in range(H):
        py = (i + 0.5) / S + oy
        for j in range(W):
            m = mask[i, j]
            if m <= 0: continue
            px = (j + 0.5) / S + ox
            gx = math.floor(px / cell); gy = math.floor(py / cell)
            best = 1e9; bi = 0; bj = 0
            for a in range(-1, 2):
                for b in range(-1, 2):
                    hx = hash2(gx + a, gy + b, seed); hy = hash2(gx + a, gy + b, seed + 1)
                    qx = (gx + a + hx) * cell; qy = (gy + b + hy) * cell
                    ang = hash2(gx + a, gy + b, seed + 2) * 3.14159
                    ca = math.cos(ang); sa = math.sin(ang)
                    ex = (px - qx) * ca + (py - qy) * sa; ey = -(px - qx) * sa + (py - qy) * ca
                    rad = cell * (0.16 + 0.26 * hash2(gx + a, gy + b, seed + 3))
                    # angular chip: superellipse-ish polygon
                    dd = max(abs(ex) / rad, abs(ey) / (rad * 0.7), (abs(ex) + abs(ey)) / (rad * 1.25))
                    if dd < best: best = dd; bi = gx + a; bj = gy + b
            c = (1 - sstep(1 - 0.08, 1 + 0.08, best)) * m
            if c > 0 and hash2(bi, bj, seed + 4) < 0.8:
                k = int(hash2(bi, bj, seed + 5) * nc) % nc
                img[i, j, 0] = img[i, j, 0] * (1 - c) + chips[k, 0] * c
                img[i, j, 1] = img[i, j, 1] * (1 - c) + chips[k, 1] * c
                img[i, j, 2] = img[i, j, 2] * (1 - c) + chips[k, 2] * c

@njit(cache=True)
def draw_petal(img, cx, cy, a, b, rot, col, S, ox, oy):
    H, W, _ = img.shape; aa = 1.0 / S
    x0 = max(int((cx - a * 1.6 - ox) * S), 0); x1 = min(int((cx + a * 1.6 - ox) * S) + 1, W - 1)
    y0 = max(int((cy - a * 1.6 - oy) * S), 0); y1 = min(int((cy + a * 1.6 - oy) * S) + 1, H - 1)
    ca = math.cos(rot); sa = math.sin(rot)
    for i in range(y0, y1 + 1):
        py = (i + 0.5) / S + oy - cy
        for j in range(x0, x1 + 1):
            px = (j + 0.5) / S + ox - cx
            # soft shadow first
            qx = (px - 0.012) * ca + (py - 0.016) * sa; qy = -(px - 0.012) * sa + (py - 0.016) * ca
            e = math.sqrt((qx / a) ** 2 + (qy / b) ** 2)
            s = (1 - sstep(0.6, 1.5, e)) * 0.16
            img[i, j, 0] *= 1 - s; img[i, j, 1] *= 1 - 0.6 * s; img[i, j, 2] *= 1 - 0.5 * s
            qx = px * ca + py * sa; qy = -px * sa + py * ca
            bb = b * (0.45 + 0.55 * sstep(-a, a * 0.3, qx)) * (1 - 0.5 * sstep(0.2 * a, a, qx))
            e = math.sqrt((qx / a) ** 2 + (qy / bb) ** 2)
            c = 1 - sstep(1 - 2 * aa / b, 1 + 2 * aa / b, e)
            if c > 0:
                t = 0.5 + 0.5 * qx / a
                sh = 1.0 - 0.10 * (1 - sstep(0.0, 0.25, abs(qy) / bb))
                for k in range(3):
                    v = (col[k] + (1 - col[k]) * (0.2 + 0.6 * t)) * sh
                    img[i, j, k] = img[i, j, k] * (1 - c) + v * c

# ---------------------------------------------------------------- numpy layers
def caustic(X, Y, t=3.7, scale=1.0):
    TAU = 2 * np.pi
    px = np.mod(X * scale * TAU, TAU) - 250.0; py = np.mod(Y * scale * TAU, TAU) - 250.0
    ix = px.copy(); iy = py.copy(); c = np.ones_like(X); inten = 0.005
    for n in range(5):
        tt = t * (1.0 - 3.5 / (n + 1))
        ix, iy = px + np.cos(tt - ix) + np.sin(tt + iy), py + np.sin(tt - iy) + np.cos(tt + ix)
        c += 1.0 / np.hypot(px / (np.sin(ix + tt) / inten), py / (np.cos(iy + tt) / inten))
    c /= 5.0
    c = 1.17 - np.power(c, 1.4)
    return np.power(np.abs(c), 8.0)

def render(scene, Wout, Hout, ss=2, strip=512, quiet=False):
    """scene: dict(center=(cx,cy) px fraction, ppu fraction, R pond, pads, loops, fish, ripples)"""
    S = scene['ppu'] * Wout * ss
    out = np.zeros((Hout, Wout, 3), np.float32)
    Rp = scene['R']; rimw = scene.get('rimw', 0.085)
    cxw = scene['center'][0] * Wout * ss / S; cyw = scene['center'][1] * Wout * ss / S
    lx, ly = -0.6, -0.8
    wcol = np.array([0.60, 0.86, 0.86], np.float32)
    chips = np.array([hexc(h) for h in ['#ffb3a7', '#ffd9a0', '#fff0a8', '#c9efb8', '#a8e6d4', '#a9d8f5', '#b9bff5', '#d9b8f2', '#f7b6d8', '#ffffff', '#e9dccf']], np.float32)
    for ys in range(0, Hout, strip):
        h = min(strip, Hout - ys)
        Hs, Ws = h * ss, Wout * ss
        ox = -cxw; oy = ys * ss / S - cyw
        x = (np.arange(Ws, dtype=np.float32) + 0.5) / S + ox
        y = (np.arange(Hs, dtype=np.float32) + 0.5) / S + oy
        X, Y = np.meshgrid(x, y)
        Rr = np.hypot(X, Y)
        # ---- water floor
        dep = np.clip(Rr / Rp, 0, 1) ** 2.2
        c0 = np.array([0.80, 0.955, 0.925], np.float32); c1 = np.array([0.585, 0.865, 0.895], np.float32)
        img = c0[None, None, :] * (1 - dep[..., None]) + c1[None, None, :] * dep[..., None]
        ca = caustic(X * 0.8660 + Y * 0.5, -X * 0.5 + Y * 0.8660, 3.7, 1.15) * 0.6 + caustic(X + 0.37, Y + 0.11, 9.2, 0.63) * 0.5
        img += (np.clip(ca, 0, 1.5) * 0.13)[..., None] * np.array([1.0, 1.0, 0.92], np.float32)
        # ---- trails (long exposure of each school)
        for li, lp in enumerate(scene['loops']):
            cov = np.zeros((Hs, Ws), np.float32)
            stroke_max(cov, lp['path'], True, scene['trail_w'], scene['trail_w'] * 0.8, S, ox, oy)
            a = cov[..., None] * scene.get('trail_a', 0.30)
            img = img * (1 - a) + (0.45 + 0.55 * lp['trail'])[None, None, :] * a
            cov[:] = 0
            stroke_max(cov, lp['path'], True, scene['trail_w'] * 0.30, max(scene['trail_w'] * 0.10, 1.0 / S), S, ox, oy)
            a = cov[..., None] * scene.get('core_a', 0.80)
            img = img * (1 - a) + (0.12 + 0.88 * lp['trail'])[None, None, :] * a
        # ---- shadows on the floor: pads + fish
        sh = np.zeros((Hs, Ws), np.float32)
        for p in scene['pads']:
            disc_soft(sh, p['x'] + 0.045, p['y'] + 0.06, p['r'] * 0.97, 0.03, S, ox, oy)
        sh *= 0.8
        sh2 = np.zeros((Hs, Ws), np.float32)
        for f in scene['fish']:
            fish_sil(sh2, f['sp'], f['fw'], f['flen'], f['fw'] * 0.55, S, ox, oy, 0.022 + 0.03 * f['depth'], 0.03 + 0.04 * f['depth'])
        sh = np.maximum(sh, sh2 * 0.62)
        img *= (1 - sh[..., None] * np.array([0.34, 0.20, 0.16], np.float32))
        del sh, sh2
        # ---- fish, deepest first
        for f in sorted(scene['fish'], key=lambda f: -f['depth']):
            draw_fish(img, f['sp'], f['fins'], f['fw'], f['flen'], f['base'], f['patch'], f['patch2'], f['fin'], f['seed'], f['thr'],
                      0.10 + 0.22 * f['depth'], wcol, S, ox, oy, lx, ly)
        # ---- surface ripples
        for (rx, ry, rr0, n, amp) in scene.get('ripples', []):
            d = np.hypot(X - rx, Y - ry)
            env = np.exp(-((d - rr0 * 0.55) / (rr0 * 0.45)) ** 2) * (d < rr0 * 1.6)
            wv = np.sin(d / rr0 * n * 2 * np.pi)
            img += (env * amp * np.where(wv > 0, wv ** 3, 0.35 * wv))[..., None]
        for (qx, qy, qa, qb, qr, qc) in scene.get('petals', []):
            draw_petal(img, qx, qy, qa, qb, qr, qc, S, ox, oy)
        # ---- pads
        for p in scene['pads']:
            draw_pad(img, p['x'], p['y'], p['r'], p['rot'], p['col'], p['col2'], p['flower'], p['seed'], S, ox, oy,
                     p['pet'][0], p['pet'][1], p['pet'][2], hexc('#ffd257'))
        # ---- rim shadow on the water (light from top-left)
        dsh = np.hypot(X - 0.05, Y - 0.065)
        rs = np.clip((dsh - (Rp - 0.075)) / 0.075, 0, 1) ** 1.5
        img *= (1 - rs[..., None] * np.array([0.42, 0.26, 0.22], np.float32))
        # ---- paper, rim, drop shadow
        aa = 1.0 / S
        paper = np.broadcast_to(PAPER, img.shape).copy()
        dd = np.hypot(X - 0.03, Y - 0.045)
        ds = np.clip(1 - (dd - (Rp + rimw)) / 0.11, 0, 1) ** 2 * (dd > Rp)
        paper *= (1 - ds[..., None] * np.array([0.20, 0.19, 0.12], np.float32))
        rim = np.broadcast_to(np.array([0.985, 0.955, 0.925], np.float32), img.shape).copy()
        rmask = (np.clip((Rr - Rp) / aa + 0.5, 0, 1) * np.clip((Rp + rimw - Rr) / aa + 0.5, 0, 1)).astype(np.float32)
        terrazzo(rim, rmask, S, ox, oy, chips, 77, 0.03)
        q = np.clip((Rr - Rp) / rimw, 0, 1)
        nd = -(X * 0.6 + Y * 0.8) / (Rr + 1e-9)          # +1 facing the light
        bevel = (np.exp(-((q - 0.12) / 0.10) ** 2) * (-nd) + np.exp(-((q - 0.88) / 0.10) ** 2) * nd) * 0.09
        rim = rim * (1 + bevel[..., None]) * (0.985 - 0.03 * np.exp(-((q - 0.0) / 0.06) ** 2))[..., None]
        win = np.clip((Rp - Rr) / aa + 0.5, 0, 1)[..., None]
        comp = paper * (1 - rmask[..., None]) + rim * rmask[..., None]
        img = img * win + comp * (1 - win)
        out[ys:ys + h] = img.reshape(h, ss, Wout, ss, 3).mean((1, 3))
        if not quiet: print('strip', ys, flush=True)
    return out

def finish(out, seed=1):
    rng = np.random.default_rng(seed)
    g = rng.normal(0, 0.004, out.shape[:2]).astype(np.float32)[..., None]
    return (np.clip(out + g, 0, 1) * 255 + 0.5).astype(np.uint8)
