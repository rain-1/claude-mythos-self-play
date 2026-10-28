"""A paper-pulp egg carton of reaction-diffusion eggs.  python3 carton.py cfg.json out.png [size]

SDF ray-marcher (numba).  Each egg's dye pattern is a Gray-Scott state on an
icosphere (gs.py), baked to a cubemap and looked up by the egg's own direction.
"""
import sys, json, math, numpy as np
from numba import njit, prange
from scipy.spatial import cKDTree
from PIL import Image

CM = 384  # cubemap face size

def bake_cubemap(npz, sharp=0.0):
    d = np.load(npz); V, v = d["V"], d["v"]
    tree = cKDTree(V)
    a = (np.arange(CM) + 0.5) / CM * 2 - 1
    U, W = np.meshgrid(a, a)
    faces = []
    for f in range(6):
        o = np.ones_like(U)
        D = [np.stack([o, -W, -U], -1), np.stack([-o, -W, U], -1), np.stack([U, o, W], -1),
             np.stack([U, -o, -W], -1), np.stack([U, -W, o], -1), np.stack([-U, -W, -o], -1)][f]
        D = D / np.linalg.norm(D, axis=-1, keepdims=True)
        dist, idx = tree.query(D.reshape(-1, 3), k=4)
        w = 1 / (dist + 1e-4) ** 2
        val = (v[idx] * w).sum(1) / w.sum(1)
        faces.append(val.reshape(CM, CM))
    return np.stack(faces).astype(np.float32)

@njit(cache=True, fastmath=True)
def cube_lookup(cm, e, x, y, z):
    ax, ay, az = abs(x), abs(y), abs(z)
    if ax >= ay and ax >= az:
        if x > 0: f = 0; u = -z / ax; w = -y / ax
        else: f = 1; u = z / ax; w = -y / ax
    elif ay >= az:
        if y > 0: f = 2; u = x / ay; w = z / ay
        else: f = 3; u = x / ay; w = -z / ay
    else:
        if z > 0: f = 4; u = x / az; w = -y / az
        else: f = 5; u = -x / az; w = -y / az
    n = cm.shape[2]
    fx = (u + 1) * 0.5 * n - 0.5; fy = (w + 1) * 0.5 * n - 0.5
    i0 = int(math.floor(fx)); j0 = int(math.floor(fy))
    tx = fx - i0; ty = fy - j0
    i0 = min(max(i0, 0), n - 1); j0 = min(max(j0, 0), n - 1)
    i1 = min(i0 + 1, n - 1); j1 = min(j0 + 1, n - 1)
    return ((cm[e, f, j0, i0] * (1 - tx) + cm[e, f, j0, i1] * tx) * (1 - ty)
            + (cm[e, f, j1, i0] * (1 - tx) + cm[e, f, j1, i1] * tx) * ty)

@njit(cache=True, fastmath=True)
def hash3(x, y, z):
    h = math.sin(x * 127.1 + y * 311.7 + z * 74.7) * 43758.5453
    return h - math.floor(h)

@njit(cache=True, fastmath=True)
def vnoise(x, y, z):
    ix = math.floor(x); iy = math.floor(y); iz = math.floor(z)
    fx = x - ix; fy = y - iy; fz = z - iz
    fx = fx * fx * (3 - 2 * fx); fy = fy * fy * (3 - 2 * fy); fz = fz * fz * (3 - 2 * fz)
    r = 0.0
    for dx in range(2):
        for dy in range(2):
            for dz in range(2):
                w = (fx if dx else 1 - fx) * (fy if dy else 1 - fy) * (fz if dz else 1 - fz)
                r += w * hash3(ix + dx, iy + dy, iz + dz)
    return r

# ---------------- scene SDF ----------------
# carton: rows x cols cups, pitch P, top surface at z=Ht, cups are bowls.
@njit(cache=True, fastmath=True)
def sd_box(px, py, pz, bx, by, bz, r):
    qx = abs(px) - bx + r; qy = abs(py) - by + r; qz = abs(pz) - bz + r
    ox = max(qx, 0.0); oy = max(qy, 0.0); oz = max(qz, 0.0)
    return math.sqrt(ox * ox + oy * oy + oz * oz) + min(max(qx, max(qy, qz)), 0.0) - r

@njit(cache=True, fastmath=True)
def smin(a, b, k):
    h = max(k - abs(a - b), 0.0) / k
    return min(a, b) - h * h * k * 0.25

@njit(cache=True, fastmath=True)
def smax(a, b, k):
    return -smin(-a, -b, k)

@njit(cache=True, fastmath=True)
def egg_sd(px, py, pz, ex, ey, ez, R, tilt_x, tilt_y):
    # egg axis tilted; local frame: axis = (sin tx ... ) -- simple rotation about x then y
    x = px - ex; y = py - ey; z = pz - ez
    c = math.cos(tilt_x); s = math.sin(tilt_x)
    y, z = c * y - s * z, s * y + c * z
    c = math.cos(tilt_y); s = math.sin(tilt_y)
    x, z = c * x + s * z, -s * x + c * z
    # egg: long axis z, radius shrinks toward +z (pointy end)
    zz = z / (1.32 * R)
    rad = R * (1.0 - 0.13 * zz)
    q = math.sqrt(x * x + y * y) / rad
    d = (math.sqrt(q * q + zz * zz) - 1.0) * min(rad, 1.32 * R) * 0.92
    return d, x / rad, y / rad, zz

@njit(cache=True, fastmath=True)
def carton_sd(px, py, pz, nr, ncl, P, Ht, cupR, cupD):
    # outer tray
    W2 = ncl * P * 0.5 + 0.10 * P; D2 = nr * P * 0.5 + 0.10 * P
    d = sd_box(px, py, pz - Ht * 0.5, W2, D2, Ht * 0.5, 0.18 * P)
    # cups: nearest cup centre
    cx = (math.floor(px / P + ncl * 0.5) + 0.5 - ncl * 0.5) * P
    cy = (math.floor(py / P + nr * 0.5) + 0.5 - nr * 0.5) * P
    cx = min(max(cx, (0.5 - ncl * 0.5) * P), (ncl * 0.5 - 0.5) * P)
    cy = min(max(cy, (0.5 - nr * 0.5) * P), (nr * 0.5 - 0.5) * P)
    dx = px - cx; dy = py - cy; dz = pz - (Ht + cupR - cupD)
    # slightly square-ish bowl (pulp cups are rounded squares)
    ax = abs(dx); ay = abs(dy)
    rr = (ax ** 4 + ay ** 4) ** 0.25 * 0.35 + math.sqrt(dx * dx + dy * dy) * 0.65
    cup = math.sqrt(rr * rr + dz * dz) - cupR
    d = smax(d, -cup, 0.12 * P)
    # posts at interior cup corners (cones rising between cups)
    gx = (math.floor(px / P + ncl * 0.5 + 0.5) - ncl * 0.5) * P
    gy = (math.floor(py / P + nr * 0.5 + 0.5) - nr * 0.5) * P
    if abs(gx) < ncl * 0.5 * P - 0.1 * P and abs(gy) < nr * 0.5 * P - 0.1 * P:
        qx = px - gx; qy = py - gy; qz = pz - Ht
        rxy = math.sqrt(qx * qx + qy * qy)
        hc = 0.55 * P
        t = min(max(qz / hc, 0.0), 1.0)
        rc = 0.20 * P * (1 - t) + 0.07 * P * t
        cone = max((rxy - rc) * 0.9, max(-qz, qz - hc))
        d = smin(d, cone - 0.02 * P, 0.15 * P)
    return d

@njit(cache=True, fastmath=True)
def scene(px, py, pz, eggs, nr, ncl, P, Ht, cupR, cupD):
    # returns distance, material id (0 table,1 carton,2+i egg i), egg local coords
    dt = pz  # table plane z=0
    best = dt; mat = 0; lx = 0.0; ly = 0.0; lz = 0.0
    dc = carton_sd(px, py, pz, nr, ncl, P, Ht, cupR, cupD)
    if dc < best: best = dc; mat = 1
    for i in range(eggs.shape[0]):
        ex, ey, ez, R = eggs[i, 0], eggs[i, 1], eggs[i, 2], eggs[i, 3]
        # bound
        bx = px - ex; by = py - ey; bz = pz - ez
        bd = math.sqrt(bx * bx + by * by + bz * bz) - 1.45 * R
        if bd > best: continue
        if bd > 0.02:
            best = bd; mat = 2 + i; continue
        d, a, b, c = egg_sd(px, py, pz, ex, ey, ez, R, eggs[i, 4], eggs[i, 5])
        if d < best:
            best = d; mat = 2 + i; lx = a; ly = b; lz = c
    return best, mat, lx, ly, lz

@njit(cache=True, fastmath=True)
def dist(px, py, pz, eggs, nr, ncl, P, Ht, cupR, cupD):
    return scene(px, py, pz, eggs, nr, ncl, P, Ht, cupR, cupD)[0]

@njit(cache=True, fastmath=True)
def normal(px, py, pz, eggs, nr, ncl, P, Ht, cupR, cupD):
    e = 0.0015
    nx = dist(px + e, py, pz, eggs, nr, ncl, P, Ht, cupR, cupD) - dist(px - e, py, pz, eggs, nr, ncl, P, Ht, cupR, cupD)
    ny = dist(px, py + e, pz, eggs, nr, ncl, P, Ht, cupR, cupD) - dist(px, py - e, pz, eggs, nr, ncl, P, Ht, cupR, cupD)
    nz = dist(px, py, pz + e, eggs, nr, ncl, P, Ht, cupR, cupD) - dist(px, py, pz - e, eggs, nr, ncl, P, Ht, cupR, cupD)
    l = math.sqrt(nx * nx + ny * ny + nz * nz) + 1e-12
    return nx / l, ny / l, nz / l

@njit(cache=True, fastmath=True)
def softshadow(px, py, pz, lx, ly, lz, k, eggs, nr, ncl, P, Ht, cupR, cupD):
    res = 1.0; t = 0.01
    for i in range(80):
        h = dist(px + lx * t, py + ly * t, pz + lz * t, eggs, nr, ncl, P, Ht, cupR, cupD)
        res = min(res, k * h / t)
        t += min(max(h, 0.006), 0.25)
        if res < 0.002 or t > 6: break
    return max(res, 0.0)

@njit(cache=True, fastmath=True)
def ao(px, py, pz, nx, ny, nz, eggs, nr, ncl, P, Ht, cupR, cupD):
    occ = 0.0; sc = 1.0
    for i in range(5):
        h = 0.02 + 0.09 * i
        d = dist(px + nx * h, py + ny * h, pz + nz * h, eggs, nr, ncl, P, Ht, cupR, cupD)
        occ += (h - d) * sc; sc *= 0.7
    return min(max(1 - 1.6 * occ, 0.0), 1.0)

@njit(parallel=True, fastmath=True)
def render(W, H, spp, cam, eggs, ecol, cms, nr, ncl, P, Ht, cupR, cupD, sun, cols, row0, row1):
    img = np.zeros((row1 - row0, W, 3), np.float32)
    ox, oy, oz = cam[0], cam[1], cam[2]
    fx_, fy_, fz_ = cam[3], cam[4], cam[5]      # forward
    rx_, ry_, rz_ = cam[6], cam[7], cam[8]      # right
    ux_, uy_, uz_ = cam[9], cam[10], cam[11]    # up
    fl = cam[12]
    for j in prange(row0, row1):
        for i in range(W):
            acc0 = 0.0; acc1 = 0.0; acc2 = 0.0
            for s in range(spp):
                jx = hash3(i * 1.31, j * 0.77, s * 3.1); jy = hash3(i * 0.53, j * 1.91, s * 7.7)
                sx = (i + jx - W * 0.5) / (W * 0.5); sy = -(j + jy - H * 0.5) / (W * 0.5)
                dx = fx_ * fl + rx_ * sx + ux_ * sy; dy = fy_ * fl + ry_ * sx + uy_ * sy; dz = fz_ * fl + rz_ * sx + uz_ * sy
                l = math.sqrt(dx * dx + dy * dy + dz * dz); dx /= l; dy /= l; dz /= l
                t = 0.0; hit = False; mat = 0; lx = 0.0; ly = 0.0; lz = 0.0
                for it in range(220):
                    px = ox + dx * t; py = oy + dy * t; pz = oz + dz * t
                    d, mat, lx, ly, lz = scene(px, py, pz, eggs, nr, ncl, P, Ht, cupR, cupD)
                    if d < 0.0007 * t:
                        hit = True; break
                    t += d * 0.85
                    if t > 40: break
                if not hit:
                    acc0 += cols[0, 0]; acc1 += cols[0, 1]; acc2 += cols[0, 2]; continue
                px = ox + dx * t; py = oy + dy * t; pz = oz + dz * t
                nx, ny, nz = normal(px, py, pz, eggs, nr, ncl, P, Ht, cupR, cupD)
                # jittered sun direction (soft)
                j1 = hash3(i * 2.1, j * 1.3, s * 5.3) - 0.5; j2 = hash3(i * 0.9, j * 2.7, s * 1.9) - 0.5
                sx_ = sun[0] + j1 * 0.06; sy_ = sun[1] + j2 * 0.06; sz_ = sun[2]
                sl = math.sqrt(sx_ * sx_ + sy_ * sy_ + sz_ * sz_); sx_ /= sl; sy_ /= sl; sz_ /= sl
                ndl = nx * sx_ + ny * sy_ + nz * sz_
                sh = 0.0
                if ndl > 0:
                    sh = softshadow(px + nx * 0.012, py + ny * 0.012, pz + nz * 0.012, sx_, sy_, sz_, 10.0, eggs, nr, ncl, P, Ht, cupR, cupD)
                occ = ao(px, py, pz, nx, ny, nz, eggs, nr, ncl, P, Ht, cupR, cupD)
                # albedo
                spec = 0.0
                if mat == 0:
                    # linen table: soft weave + faint polka dots
                    wv = 0.5 + 0.5 * math.sin(px * 260) * math.sin(py * 260)
                    a0 = cols[1, 0] * (0.97 + 0.03 * wv); a1 = cols[1, 1] * (0.97 + 0.03 * wv); a2 = cols[1, 2] * (0.97 + 0.03 * wv)
                    gx = px / 0.55; gy = py / 0.55
                    off = 0.5 * (math.floor(gy) % 2)
                    ddx = gx + off - math.floor(gx + off) - 0.5; ddy = gy - math.floor(gy) - 0.5
                    if ddx * ddx + ddy * ddy < 0.018:
                        a0 = cols[2, 0]; a1 = cols[2, 1]; a2 = cols[2, 2]
                elif mat == 1:
                    n = vnoise(px * 140, py * 140, pz * 140) * 0.5 + vnoise(px * 40, py * 40, pz * 40) * 0.3 + vnoise(px * 9, py * 9, pz * 9) * 0.2
                    fib = vnoise(px * 400, py * 31, pz * 400) * vnoise(px * 37, py * 420, pz * 37)
                    f = 0.90 + 0.12 * n + 0.05 * fib
                    # pulp bump: tilt the normal along the noise gradient
                    e2 = 0.004; q = 110.0
                    g0 = vnoise(px * q, py * q, pz * q)
                    bx = (vnoise((px + e2) * q, py * q, pz * q) - g0); by = (vnoise(px * q, (py + e2) * q, pz * q) - g0); bz = (vnoise(px * q, py * q, (pz + e2) * q) - g0)
                    bs = 0.55
                    nx -= bx * bs; ny -= by * bs; nz -= bz * bs
                    nl = math.sqrt(nx * nx + ny * ny + nz * nz); nx /= nl; ny /= nl; nz /= nl
                    ndl = nx * sx_ + ny * sy_ + nz * sz_
                    a0 = cols[3, 0] * f; a1 = cols[3, 1] * f; a2 = cols[3, 2] * f
                else:
                    e = mat - 2
                    vv = cube_lookup(cms, e, lx, ly, lz * 1.0)
                    th0 = ecol[e, 6]
                    m = min(max((vv - th0) / 0.06 + 0.5, 0.0), 1.0)
                    m = m * m * (3 - 2 * m)
                    a0 = ecol[e, 0] * (1 - m) + ecol[e, 3] * m
                    a1 = ecol[e, 1] * (1 - m) + ecol[e, 4] * m
                    a2 = ecol[e, 2] * (1 - m) + ecol[e, 5] * m
                    sp = 0.96 + 0.06 * vnoise(lx * 60, ly * 60, lz * 60)
                    a0 *= sp; a1 *= sp; a2 *= sp
                    # sheen
                    hx = sx_ - dx; hy = sy_ - dy; hz = sz_ - dz
                    hl = math.sqrt(hx * hx + hy * hy + hz * hz)
                    ndh = max((nx * hx + ny * hy + nz * hz) / hl, 0.0)
                    spec = 0.10 * ndh ** 40 * sh
                # lighting: sun + sky (blue-lilac from above) + bounce (warm from table)
                wrap = max((ndl + 0.15) / 1.15, 0.0)
                dif = wrap * sh * sun[3]
                sky = (0.55 + 0.45 * nz) * occ
                L0 = dif * cols[4, 0] + sky * cols[5, 0]
                L1 = dif * cols[4, 1] + sky * cols[5, 1]
                L2 = dif * cols[4, 2] + sky * cols[5, 2]
                fog = min(max((t - cam[13]) / cam[14], 0.0), 1.0)
                c0 = a0 * L0 + spec; c1 = a1 * L1 + spec; c2 = a2 * L2 + spec
                acc0 += c0 * (1 - fog) + cols[0, 0] * fog; acc1 += c1 * (1 - fog) + cols[0, 1] * fog; acc2 += c2 * (1 - fog) + cols[0, 2] * fog
            img[j - row0, i, 0] = acc0 / spp; img[j - row0, i, 1] = acc1 / spp; img[j - row0, i, 2] = acc2 / spp
    return img

def look(eye, tgt, fov):
    eye = np.array(eye, float); f = np.array(tgt, float) - eye; f /= np.linalg.norm(f)
    r = np.cross(f, [0, 0, 1]); r /= np.linalg.norm(r); u = np.cross(r, f)
    fl = 1 / math.tan(math.radians(fov) / 2)
    return np.array([*eye, *f, *r, *u, fl, 0.0, 1.0])

def main(cfg, out, size=None):
    W = size or cfg["size"]; H = int(W * cfg.get("aspect", 1.0))
    nr, ncl, P = cfg["rows"], cfg["cols"], cfg["pitch"]
    Ht, cupR, cupD = cfg["Ht"], cfg["cupR"], cfg["cupD"]
    eggs = []; ecol = []; cms = []
    rng = np.random.default_rng(cfg.get("seed", 1))
    for k, e in enumerate(cfg["eggs"]):
        r, c = divmod(k, ncl)
        x = (c + 0.5 - ncl / 2) * P; y = -(r + 0.5 - nr / 2) * P
        R = cfg["eggR"]
        tx = e.get("tilt", [0, 0])
        # egg sits in the cup: lift so the egg's lowest point rests on the bowl
        z = Ht - cupD + 1.32 * R * 0.87 + cfg.get("lift", 0.0)
        eggs.append([x, y, z, R, math.radians(tx[0]), math.radians(tx[1])])
        ecol.append(e["base"] + e["dye"] + [e.get("th", 0.17)])
        cms.append(bake_cubemap(e["file"]))
    eggs = np.array(eggs, np.float64); ecol = np.array(ecol, np.float64); cms = np.stack(cms)
    cols = np.array([cfg["bg"], cfg["table"], cfg["dots"], cfg["pulp"], cfg["sun_col"], cfg["sky_col"]], np.float64)
    sun = np.array(cfg["sun"] + [cfg.get("sun_I", 1.0)], np.float64)
    cam = look(cfg["eye"], cfg["tgt"], cfg["fov"])
    cam[13], cam[14] = cfg.get("fog", [12.0, 6.0])
    spp = cfg.get("spp", 4)
    r0 = int(cfg.get("row0", 0) * H); r1 = int(cfg.get("row1", 1) * H)
    img = render(W, H, spp, cam, eggs, ecol, cms, nr, ncl, P, Ht, cupR, cupD, sun, cols, r0, r1)
    if out.endswith(".npy"):
        np.save(out, img); return
    img = img * cfg.get("expo", 1.0)
    img = img / (1 + img / 4) * 1.25
    Image.fromarray((np.clip(img, 0, 1) ** (1 / 1.0) * 255 + 0.5).astype(np.uint8)).save(out)
    print("saved", out)

if __name__ == "__main__":
    cfg = json.load(open(sys.argv[1]))
    main(cfg, sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else None)
