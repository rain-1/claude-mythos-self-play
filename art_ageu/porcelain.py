"""porcelain.py — a studio ray tracer for glazed porcelain with crystalline glaze.

Triangle meshes in a BVH, a paper/cloth ground plane, one soft key light, a pastel
studio environment with softboxes (what the glaze reflects).  Glaze colour is a
SOLID texture: zinc-silicate crystals nucleate at seed points (time t0) and grow at
speed v; arrival time T(p) = min_i t0_i + |p - s_i| / v_i (a Johnson–Mehl tessellation).
Crystals exist where T < Tend; rings are isochrones of T; halos sit just beyond.

World is y-up.  All numba kernels; `render()` is the entry point.
"""
import numpy as np
from numba import njit, prange
import math

# ----------------------------------------------------------------------------- meshes
def load_obj(path):
    V, F = [], []
    for l in open(path):
        if l.startswith('v '):
            V.append([float(x) for x in l.split()[1:4]])
        elif l.startswith('f '):
            idx = [int(t.split('/')[0]) - 1 for t in l.split()[1:]]
            for k in range(1, len(idx) - 1):
                F.append([idx[0], idx[k], idx[k + 1]])
    return np.array(V, float), np.array(F, np.int64)


def weld(V, F, eps=1e-5):
    key = np.round(V / eps).astype(np.int64)
    _, inv, = np.unique(key, axis=0, return_inverse=True)[0:2], None
    u, idx, inv = np.unique(key, axis=0, return_index=True, return_inverse=True)
    V2 = V[idx]
    F2 = inv.ravel()[F]
    good = (F2[:, 0] != F2[:, 1]) & (F2[:, 1] != F2[:, 2]) & (F2[:, 0] != F2[:, 2])
    return V2, F2[good]


def vertex_normals(V, F):
    N = np.zeros_like(V)
    fn = np.cross(V[F[:, 1]] - V[F[:, 0]], V[F[:, 2]] - V[F[:, 0]])
    for k in range(3):
        np.add.at(N, F[:, k], fn)
    N /= np.linalg.norm(N, axis=1, keepdims=True) + 1e-12
    return N


def grid_mesh(H, x0, x1, z0, z1, wrapx=False):
    """height field y = H[iz, ix] on a regular grid -> (V, F)."""
    nz, nx = H.shape
    xs = np.linspace(x0, x1, nx); zs = np.linspace(z0, z1, nz)
    X, Z = np.meshgrid(xs, zs)
    V = np.stack([X.ravel(), H.ravel(), Z.ravel()], 1)
    i = np.arange(nz - 1)[:, None] * nx + np.arange(nx - 1)[None, :]
    i = i.ravel()
    F = np.concatenate([np.stack([i, i + nx, i + 1], 1), np.stack([i + 1, i + nx, i + nx + 1], 1)])
    return V, F


def revolve(profile, nseg=256):
    """profile: (n,2) array of (r, y) from bottom centre to ... ; surface of revolution."""
    n = len(profile)
    th = np.linspace(0, 2 * np.pi, nseg, endpoint=False)
    V = np.zeros((n * nseg, 3))
    for j in range(nseg):
        V[j * n:(j + 1) * n, 0] = profile[:, 0] * np.cos(th[j])
        V[j * n:(j + 1) * n, 1] = profile[:, 1]
        V[j * n:(j + 1) * n, 2] = profile[:, 0] * np.sin(th[j])
    F = []
    for j in range(nseg):
        a = j * n; b = ((j + 1) % nseg) * n
        for i in range(n - 1):
            F.append([a + i, b + i, a + i + 1]); F.append([a + i + 1, b + i, b + i + 1])
    return V, np.array(F, np.int64)


# ----------------------------------------------------------------------------- BVH
def build_bvh(V, F, leaf=4):
    tri = V[F]                       # (m,3,3)
    lo = tri.min(1); hi = tri.max(1); c = 0.5 * (lo + hi)
    m = len(F)
    order = np.arange(m)
    nodes_lo, nodes_hi, nodes_a, nodes_b = [], [], [], []   # a: left child or -first-1 ; b: right or count
    stack = [(0, m, -1, 0)]
    # iterative build: allocate nodes in DFS order
    out = []
    def build(s, e):
        idx = order[s:e]
        bl = lo[idx].min(0); bh = hi[idx].max(0)
        me = len(nodes_lo)
        nodes_lo.append(bl); nodes_hi.append(bh); nodes_a.append(0); nodes_b.append(0)
        if e - s <= leaf:
            nodes_a[me] = -(s + 1); nodes_b[me] = e - s
            return me
        cc = c[idx]; ax = int(np.argmax(cc.max(0) - cc.min(0)))
        srt = np.argsort(cc[:, ax], kind='stable')
        order[s:e] = idx[srt]
        mid = (s + e) // 2
        l = build(s, mid); r = build(mid, e)
        nodes_a[me] = l; nodes_b[me] = r
        return me
    import sys
    sys.setrecursionlimit(100000)
    build(0, m)
    F2 = F[order]
    return (np.array(nodes_lo), np.array(nodes_hi), np.array(nodes_a, np.int64),
            np.array(nodes_b, np.int64), order, F2)


class Scene:
    def __init__(self):
        self.V = []; self.F = []; self.N = []; self.M = []; self.nv = 0

    def add(self, V, F, mat, N=None, smooth=True):
        if N is None:
            N = vertex_normals(V, F)
        self.V.append(V); self.F.append(F + self.nv); self.N.append(N)
        self.M.append(np.full(len(F), mat, np.int64)); self.nv += len(V)

    def finish(self):
        V = np.concatenate(self.V); F = np.concatenate(self.F); N = np.concatenate(self.N)
        M = np.concatenate(self.M)
        blo, bhi, ba, bb, order, F2 = build_bvh(V, F)
        self.arr = (V, F2, N, M[order], blo, bhi, ba, bb)
        return self


# ----------------------------------------------------------------------------- kernels
@njit(cache=True, fastmath=True)
def hit_scene(ox, oy, oz, dx, dy, dz, tmax, V, F, blo, bhi, ba, bb):
    """returns (t, tri, u, v); tri=-1 if none."""
    idx = 1.0 / (dx if abs(dx) > 1e-12 else 1e-12)
    idy = 1.0 / (dy if abs(dy) > 1e-12 else 1e-12)
    idz = 1.0 / (dz if abs(dz) > 1e-12 else 1e-12)
    stack = np.empty(96, np.int64)
    sp = 0; stack[0] = 0; sp = 1
    best = tmax; bt = -1; bu = 0.0; bv = 0.0
    while sp > 0:
        sp -= 1; n = stack[sp]
        t1 = (blo[n, 0] - ox) * idx; t2 = (bhi[n, 0] - ox) * idx
        tn = min(t1, t2); tf = max(t1, t2)
        t1 = (blo[n, 1] - oy) * idy; t2 = (bhi[n, 1] - oy) * idy
        tn = max(tn, min(t1, t2)); tf = min(tf, max(t1, t2))
        t1 = (blo[n, 2] - oz) * idz; t2 = (bhi[n, 2] - oz) * idz
        tn = max(tn, min(t1, t2)); tf = min(tf, max(t1, t2))
        if tf < max(tn, 0.0) or tn > best:
            continue
        a = ba[n]
        if a < 0:
            s = -a - 1
            for k in range(s, s + bb[n]):
                i0 = F[k, 0]; i1 = F[k, 1]; i2 = F[k, 2]
                e1x = V[i1, 0] - V[i0, 0]; e1y = V[i1, 1] - V[i0, 1]; e1z = V[i1, 2] - V[i0, 2]
                e2x = V[i2, 0] - V[i0, 0]; e2y = V[i2, 1] - V[i0, 1]; e2z = V[i2, 2] - V[i0, 2]
                px = dy * e2z - dz * e2y; py = dz * e2x - dx * e2z; pz = dx * e2y - dy * e2x
                det = e1x * px + e1y * py + e1z * pz
                if abs(det) < 1e-14:
                    continue
                inv = 1.0 / det
                tx = ox - V[i0, 0]; ty = oy - V[i0, 1]; tz = oz - V[i0, 2]
                u = (tx * px + ty * py + tz * pz) * inv
                if u < 0.0 or u > 1.0:
                    continue
                qx = ty * e1z - tz * e1y; qy = tz * e1x - tx * e1z; qz = tx * e1y - ty * e1x
                v = (dx * qx + dy * qy + dz * qz) * inv
                if v < 0.0 or u + v > 1.0:
                    continue
                t = (e2x * qx + e2y * qy + e2z * qz) * inv
                if t > 1e-6 and t < best:
                    best = t; bt = k; bu = u; bv = v
        else:
            stack[sp] = a; sp += 1
            stack[sp] = bb[n]; sp += 1
    return best, bt, bu, bv


@njit(cache=True, fastmath=True)
def hash11(i):
    x = (i * 0x27d4eb2d) & 0xffffffff
    x ^= x >> 15
    x = (x * 0x85ebca6b) & 0xffffffff
    x ^= x >> 13
    return (x & 0xffffff) / 16777216.0


@njit(cache=True, fastmath=True)
def pnoise1(x, period, seed):
    """periodic smooth value noise in [0,1)."""
    i = math.floor(x); f = x - i
    a = hash11(((int(i) % period) + period) % period + seed * 7919)
    b = hash11(((int(i + 1) % period) + period) % period + seed * 7919)
    f = f * f * (3 - 2 * f)
    return a + (b - a) * f


@njit(cache=True, fastmath=True)
def vnoise2(x, y, seed):
    ix = math.floor(x); iy = math.floor(y); fx = x - ix; fy = y - iy
    ix = int(ix); iy = int(iy)
    a = hash11(ix * 73856093 + iy * 19349663 + seed)
    b = hash11((ix + 1) * 73856093 + iy * 19349663 + seed)
    c = hash11(ix * 73856093 + (iy + 1) * 19349663 + seed)
    d = hash11((ix + 1) * 73856093 + (iy + 1) * 19349663 + seed)
    fx = fx * fx * (3 - 2 * fx); fy = fy * fy * (3 - 2 * fy)
    return (a + (b - a) * fx) * (1 - fy) + (c + (d - c) * fx) * fy


# --- crystalline glaze --------------------------------------------------------
# per material glaze params G[mat, :] :
#  0-2 ground glaze rgb, 3-5 halo rgb, 6 Tend, 7 halo width (in T units), 8 ring period,
#  9 ring strength, 10 fibre count, 11 fibre strength, 12 seam width, 13 has_crystals,
#  14 seed offset into seed arrays, 15 seed count, 16 grid offset, 17-19 grid lo, 20 grid cell, 21 grid n
#  22 gloss (spec scale), 23 bump strength
# seeds: S (k,3) pos, SN (k,3) normal, ST (k,3) tangent, SP (k,4): t0, speed, species, phase
# species palette SC (s, 6): crystal rgb core, crystal rgb rim
@njit(cache=True, fastmath=True)
def glaze_color(px, py, pz, mat, G, S, SN, ST, SP, SC, gstart, glist):
    pool = (vnoise2(px * 0.9 + pz * 0.6, py * 1.3 - pz * 0.4, 5) - 0.5) * 2.0
    r0 = G[mat, 0] * (1 - pool * 0.12); g0 = G[mat, 1] * (1 - pool * 0.18); b0 = G[mat, 2] * (1 - pool * 0.10)
    if G[mat, 13] < 0.5:
        return r0, g0, b0, 0.0, 0.0, 0.0, 0.0
    off = int(G[mat, 14]); goff = int(G[mat, 16])
    cell = G[mat, 20]; gn = int(G[mat, 21])
    ix = int((px - G[mat, 17]) / cell); iy = int((py - G[mat, 18]) / cell); iz = int((pz - G[mat, 19]) / cell)
    ix = min(max(ix, 0), gn - 1); iy = min(max(iy, 0), gn - 1); iz = min(max(iz, 0), gn - 1)
    ci = goff + (ix * gn + iy) * gn + iz
    T1 = 1e30; T2 = 1e30; own = -1
    lob = G[mat, 24]
    for q in range(gstart[ci], gstart[ci + 1]):
        i = off + glist[q]
        dx = px - S[i, 0]; dy = py - S[i, 1]; dz = pz - S[i, 2]
        vv = SP[i, 1]
        if lob > 0:
            tx_ = ST[i, 0]; ty_ = ST[i, 1]; tz_ = ST[i, 2]
            nx_ = SN[i, 0]; ny_ = SN[i, 1]; nz_ = SN[i, 2]
            bx_ = ny_ * tz_ - nz_ * ty_; by_ = nz_ * tx_ - nx_ * tz_; bz_ = nx_ * ty_ - ny_ * tx_
            ph_ = math.atan2(dx * bx_ + dy * by_ + dz * bz_, dx * tx_ + dy * ty_ + dz * tz_) / (2 * math.pi) + 0.5
            vv *= 1.0 + lob * (0.65 * pnoise1(ph_ * 7.0, 7, i + 31) + 0.35 * pnoise1(ph_ * 17.0, 17, i + 57) - 0.5)
        T = SP[i, 0] + math.sqrt(dx * dx + dy * dy + dz * dz) / vv
        if T < T1:
            T2 = T1; T1 = T; own = i
        elif T < T2:
            T2 = T
    Tend = G[mat, 6]
    if own < 0 or T1 > Tend:
        # ground glaze + halo just outside crystal fronts
        h = 0.0
        if own >= 0:
            h = math.exp(-(T1 - Tend) / G[mat, 7])
        r = r0 + (G[mat, 3] - r0) * h; g = g0 + (G[mat, 4] - g0) * h; b = b0 + (G[mat, 5] - b0) * h
        return r, g, b, 0.0, 0.0, 0.0, 0.0
    i = own
    dx = px - S[i, 0]; dy = py - S[i, 1]; dz = pz - S[i, 2]
    rr = math.sqrt(dx * dx + dy * dy + dz * dz) + 1e-9
    # tangent frame at seed
    nx = SN[i, 0]; ny = SN[i, 1]; nz = SN[i, 2]
    tx = ST[i, 0]; ty = ST[i, 1]; tz = ST[i, 2]
    bx = ny * tz - nz * ty; by = nz * tx - nx * tz; bz = nx * ty - ny * tx
    a1 = dx * tx + dy * ty + dz * tz; a2 = dx * bx + dy * by + dz * bz
    phi = math.atan2(a2, a1) / (2 * math.pi) + 0.5
    sp = int(SP[i, 2]); ph = SP[i, 3]
    K = int(G[mat, 10])
    # fibres: periodic noise in angle, slowly twisting with radius
    tw = G[mat, 22] * (vnoise2(rr * 6.0, ph * 10.0, 3) - 0.5)
    f = 0.6 * pnoise1((phi + tw) * K, K, i) + 0.4 * pnoise1((phi + tw) * K * 3.0, K * 3, i + 999)
    f = min(max((f - 0.5) * 2.2 + 0.5, 0.0), 1.0)
    fib = (f - 0.5) * G[mat, 11]
    # growth rings = isochrones of T
    u = (T1 - SP[i, 0]) / max(Tend - SP[i, 0], 1e-6)       # 0 at nucleus .. 1 at rim (own time)
    ringT = T1 / G[mat, 8] + ph
    ring = 0.5 + 0.5 * math.cos(2 * math.pi * ringT)
    ring = ring ** 6 * G[mat, 9]
    # colour: core -> rim gradient along own growth
    w = min(max(u, 0.0), 1.0)
    w = w * w
    cr = SC[sp, 0] + (SC[sp, 3] - SC[sp, 0]) * w
    cg = SC[sp, 1] + (SC[sp, 4] - SC[sp, 1]) * w
    cb = SC[sp, 2] + (SC[sp, 5] - SC[sp, 2]) * w
    pet = (pnoise1(phi * 11.0, 11, i + 77) - 0.5) * G[mat, 25]
    cr += (1.0 - cr) * max(pet, 0.0) * 1.5; cg += (1.0 - cg) * max(pet, 0.0) * 1.5; cb += (1.0 - cb) * max(pet, 0.0) * 1.5
    cr *= 1 + min(pet, 0.0) * 0.5; cg *= 1 + min(pet, 0.0) * 0.5; cb *= 1 + min(pet, 0.0) * 0.5
    wf = max(fib, 0.0) * 1.6
    cr += (1.0 - cr) * wf; cg += (1.0 - cg) * wf; cb += (1.0 - cb) * wf
    lum = 1.0 + min(fib, 0.0) * 0.6 - ring
    cr *= lum; cg *= lum; cb *= lum
    # seam between crystals
    seam = 1.0 - math.exp(-(T2 - T1) / G[mat, 12])
    sm = 0.82 + 0.18 * seam
    cr *= sm; cg *= sm; cb *= sm
    # nucleus
    nuc = math.exp(-(rr * SP[i, 1] / G[mat, 8] * 6.0) ** 2)
    cr *= 1 - 0.25 * nuc; cg *= 1 - 0.25 * nuc; cb *= 1 - 0.25 * nuc
    # fibre direction (for anisotropic sheen) = radial in tangent plane, and a bump amount
    return cr, cg, cb, dx / rr, dy / rr, dz / rr, fib


@njit(cache=True, fastmath=True)
def env(dx, dy, dz, E, boxes=True):
    """pastel studio: E = [sky_top rgb, horizon rgb, floor rgb, nbox, boxes (dir xyz, cos size, rgb)...]"""
    t = max(min(dy, 1.0), -1.0)
    if t > 0:
        w = t ** 0.6
        r = E[3] + (E[0] - E[3]) * w; g = E[4] + (E[1] - E[4]) * w; b = E[5] + (E[2] - E[5]) * w
    else:
        w = (-t) ** 0.5
        r = E[3] + (E[6] - E[3]) * w; g = E[4] + (E[7] - E[4]) * w; b = E[5] + (E[8] - E[5]) * w
    nb = int(E[9]) if boxes else 0
    for k in range(nb):
        o = 10 + k * 7
        c = dx * E[o] + dy * E[o + 1] + dz * E[o + 2]
        if c > E[o + 3]:
            s = (c - E[o + 3]) / (1 - E[o + 3])
            s = min(s * 6.0, 1.0)
            r += E[o + 4] * s; g += E[o + 5] * s; b += E[o + 6] * s
    return r, g, b


@njit(cache=True, fastmath=True)
def onb(nx, ny, nz):
    if abs(nx) > 0.9:
        ax, ay, az = 0.0, 1.0, 0.0
    else:
        ax, ay, az = 1.0, 0.0, 0.0
    tx = ay * nz - az * ny; ty = az * nx - ax * nz; tz = ax * ny - ay * nx
    l = math.sqrt(tx * tx + ty * ty + tz * tz)
    tx /= l; ty /= l; tz /= l
    bx = ny * tz - nz * ty; by = nz * tx - nx * tz; bz = nx * ty - ny * tx
    return tx, ty, tz, bx, by, bz


@njit(cache=True, fastmath=True)
def ground_albedo(x, z, GP):
    """ground plane y=GP[0]: base rgb GP[1:4], second rgb GP[4:7], pattern type GP[7], scale GP[8]"""
    r = GP[1]; g = GP[2]; b = GP[3]
    typ = int(GP[7])
    if typ == 1:     # gingham
        s = GP[8]
        a = 1.0 if (math.floor(x / s) % 2 == 0) else 0.0
        c = 1.0 if (math.floor(z / s) % 2 == 0) else 0.0
        m = 0.5 * (a + c)
        r = r + (GP[4] - r) * m; g = g + (GP[5] - g) * m; b = b + (GP[6] - b) * m
    elif typ == 2:   # radial gradient
        d = math.sqrt(x * x + z * z) / GP[8]
        m = min(d, 1.0)
        r = r + (GP[4] - r) * m; g = g + (GP[5] - g) * m; b = b + (GP[6] - b) * m
    # linen weave
    wv = 0.5 * (vnoise2(x * GP[15], z * 3.0, 11) + vnoise2(x * 3.0, z * GP[15], 12))
    k = 1.0 - GP[16] + 2 * GP[16] * wv
    return r * k, g * k, b * k


@njit(cache=True, fastmath=True)
def shade_point(px, py, pz, nx, ny, nz, mat, rdx, rdy, rdz, primary, rng_a, rng_b, rng_c,
                V, F, N, M, blo, bhi, ba, bb, G, S, SN, ST, SP, SC, gstart, glist, MT, E, L, GP):
    """returns rgb at a surface point. MT[mat]: 0 glaze,1 gold lustre,2 matte biscuit,3 ground"""
    typ = int(MT[mat, 0])
    if typ == 3:
        ar, ag, ab = ground_albedo(px, pz, GP)
        fr = 0.0; fx = 0.0; fy = 0.0; fz = 0.0
    elif typ == 0:
        ar, ag, ab, fx, fy, fz, fr = glaze_color(px, py, pz, mat, G, S, SN, ST, SP, SC, gstart, glist)
    else:
        ar = MT[mat, 1]; ag = MT[mat, 2]; ab = MT[mat, 3]; fr = 0.0; fx = 0.0; fy = 0.0; fz = 0.0
    # make shading normal face the viewer
    if nx * rdx + ny * rdy + nz * rdz > 0:
        nx = -nx; ny = -ny; nz = -nz
    # bump from fibres
    if typ == 0 and G[mat, 23] > 0:
        bmp = G[mat, 23] * fr
        tx = fy * nz - fz * ny; ty = fz * nx - fx * nz; tz = fx * ny - fy * nx
        nx += bmp * tx; ny += bmp * ty; nz += bmp * tz
        l = math.sqrt(nx * nx + ny * ny + nz * nz); nx /= l; ny /= l; nz /= l
    eps = 1e-4 * L[10]
    ox = px + nx * eps; oy = py + ny * eps; oz = pz + nz * eps
    # --- key light: rectangle-ish disc light at L[0:3], radius L[3], colour L[4:7]
    lx = L[0] + (rng_a - 0.5) * 2 * L[3]; ly = L[1] + (rng_b - 0.5) * 2 * L[3]; lz = L[2] + (rng_c - 0.5) * 2 * L[3]
    dx = lx - ox; dy = ly - oy; dz = lz - oz
    dist = math.sqrt(dx * dx + dy * dy + dz * dz); dx /= dist; dy /= dist; dz /= dist
    ndl = nx * dx + ny * dy + nz * dz
    wrap = MT[mat, 4]
    lam = max((ndl + wrap) / (1 + wrap), 0.0)
    vis = 1.0
    if ndl > -wrap:
        th, tri, uu, vv = hit_scene(ox, oy, oz, dx, dy, dz, dist, V, F, blo, bhi, ba, bb)
        if tri >= 0:
            vis = 0.0
        if GP[9] > 0 and dy < 0:  # ground occludes
            tg = (GP[0] - oy) / dy
            if tg > 1e-5 and tg < dist:
                vis = 0.0
    dr = L[4] * lam * vis; dg = L[5] * lam * vis; db = L[6] * lam * vis
    # --- ambient / one-bounce sky via a cosine ray (AO with colour bleed)
    tx, ty, tz, bx, by, bz = onb(nx, ny, nz)
    u1 = rng_b; u2 = rng_c
    rr = math.sqrt(u1); ph = 2 * math.pi * u2
    a = rr * math.cos(ph); b = rr * math.sin(ph); c = math.sqrt(max(0.0, 1 - u1))
    qx = a * tx + b * bx + c * nx; qy = a * ty + b * by + c * ny; qz = a * tz + b * bz + c * nz
    th, tri, uu, vv = hit_scene(ox, oy, oz, qx, qy, qz, L[11], V, F, blo, bhi, ba, bb)
    if tri >= 0:
        m2 = M[tri]
        t2 = int(MT[m2, 0])
        if t2 == 0:
            br, bg_, bb_ = G[m2, 0], G[m2, 1], G[m2, 2]
        else:
            br, bg_, bb_ = MT[m2, 1], MT[m2, 2], MT[m2, 3]
        k = L[12]
        sr = br * k; sg = bg_ * k; sb = bb_ * k
    else:
        hitg = False
        if GP[9] > 0 and qy < 0:
            tg = (GP[0] - oy) / qy
            if tg > 1e-5 and tg < L[11]:
                hitg = True
        if hitg:
            gr, gg, gb = ground_albedo(ox + qx * tg, oz + qz * tg, GP)
            sr = gr * L[12]; sg = gg * L[12]; sb = gb * L[12]
        else:
            sr, sg, sb = env(qx, qy, qz, E, False)
            sr *= L[13]; sg *= L[13]; sb *= L[13]
    col_r = ar * (dr + sr * L[7]); col_g = ag * (dg + sg * L[8]); col_b = ab * (db + sb * L[9])
    # --- clear-coat reflection (glaze / gold)
    spec = MT[mat, 5]
    if spec > 0:
        cosi = -(rdx * nx + rdy * ny + rdz * nz)
        cosi = max(cosi, 0.0)
        F0 = MT[mat, 6]
        Fr = F0 + (1 - F0) * (1 - cosi) ** 5
        if typ == 1:
            Fr = 1.0
        rx = rdx + 2 * cosi * nx; ry = rdy + 2 * cosi * ny; rz = rdz + 2 * cosi * nz
        rough = MT[mat, 7]
        rx += (rng_a - 0.5) * rough; ry += (rng_c - 0.5) * rough; rz += (rng_b - 0.5) * rough
        l = math.sqrt(rx * rx + ry * ry + rz * rz); rx /= l; ry /= l; rz /= l
        er, eg, eb = env(rx, ry, rz, E)
        th, tri, uu, vv = hit_scene(ox, oy, oz, rx, ry, rz, 1e30, V, F, blo, bhi, ba, bb)
        if tri >= 0:
            m2 = M[tri]
            t2 = int(MT[m2, 0])
            if t2 == 0:
                br, bg_, bb_ = G[m2, 0], G[m2, 1], G[m2, 2]
            else:
                br, bg_, bb_ = MT[m2, 1], MT[m2, 2], MT[m2, 3]
            er = br * 0.75; eg = bg_ * 0.75; eb = bb_ * 0.75
        elif GP[9] > 0 and ry < 0:
            tg = (GP[0] - oy) / ry
            gr, gg, gb = ground_albedo(ox + rx * tg, oz + rz * tg, GP)
            er = gr * 0.8; eg = gg * 0.8; eb = gb * 0.8
        if typ == 1:
            er *= ar; eg *= ag; eb *= ab
            col_r = col_r * 0.25; col_g = col_g * 0.25; col_b = col_b * 0.25
        col_r += spec * Fr * er; col_g += spec * Fr * eg; col_b += spec * Fr * eb
    return col_r, col_g, col_b


@njit(parallel=True, cache=True, fastmath=True)
def render_kernel(W, H, spp, cam, V, F, N, M, blo, bhi, ba, bb, G, S, SN, ST, SP, SC, gstart, glist,
                  MT, E, L, GP, row0, row1):
    img = np.zeros((row1 - row0, W, 4), np.float32)
    ex, ey, ez = cam[0], cam[1], cam[2]
    fx_, fy_, fz_ = cam[3], cam[4], cam[5]
    rx_, ry_, rz_ = cam[6], cam[7], cam[8]
    ux_, uy_, uz_ = cam[9], cam[10], cam[11]
    tanh_ = cam[12]; aper = cam[13]; focus = cam[14]
    for j in prange(row0, row1):
        for i in range(W):
            ar = 0.0; ag = 0.0; ab = 0.0; aa = 0.0
            for s in range(spp):
                h0 = (j * W + i) * 64 + s
                r1 = hash11(h0 * 4 + 1); r2 = hash11(h0 * 4 + 2); r3 = hash11(h0 * 4 + 3); r4 = hash11(h0 * 4 + 7)
                # stratified-ish
                sx = (i + (s % 4 + r1) / 4.0) / W * 2 - 1
                sy = 1 - (j + ((s // 4) % 4 + r2) / 4.0) / H * 2
                asp = W / H
                dx = fx_ + (sx * tanh_ * asp) * rx_ + (sy * tanh_) * ux_
                dy = fy_ + (sx * tanh_ * asp) * ry_ + (sy * tanh_) * uy_
                dz = fz_ + (sx * tanh_ * asp) * rz_ + (sy * tanh_) * uz_
                l = math.sqrt(dx * dx + dy * dy + dz * dz); dx /= l; dy /= l; dz /= l
                ox = ex; oy = ey; oz = ez
                if aper > 0:
                    # thin lens
                    px = ox + dx * focus / (dx * fx_ + dy * fy_ + dz * fz_)
                    py = oy + dy * focus / (dx * fx_ + dy * fy_ + dz * fz_)
                    pz = oz + dz * focus / (dx * fx_ + dy * fy_ + dz * fz_)
                    rr = aper * math.sqrt(r3); ph = 2 * math.pi * r4
                    ox += rr * math.cos(ph) * rx_ + rr * math.sin(ph) * ux_
                    oy += rr * math.cos(ph) * ry_ + rr * math.sin(ph) * uy_
                    oz += rr * math.cos(ph) * rz_ + rr * math.sin(ph) * uz_
                    dx = px - ox; dy = py - oy; dz = pz - oz
                    l = math.sqrt(dx * dx + dy * dy + dz * dz); dx /= l; dy /= l; dz /= l
                t, tri, u, v = hit_scene(ox, oy, oz, dx, dy, dz, 1e30, V, F, blo, bhi, ba, bb)
                tg = 1e30
                if GP[9] > 0 and dy < 0:
                    tg = (GP[0] - oy) / dy
                q1 = hash11(h0 * 4 + 11); q2 = hash11(h0 * 4 + 13); q3 = hash11(h0 * 4 + 17)
                if tri >= 0 and t < tg:
                    px = ox + dx * t; py = oy + dy * t; pz = oz + dz * t
                    i0 = F[tri, 0]; i1 = F[tri, 1]; i2 = F[tri, 2]
                    w0 = 1 - u - v
                    nx = N[i0, 0] * w0 + N[i1, 0] * u + N[i2, 0] * v
                    ny = N[i0, 1] * w0 + N[i1, 1] * u + N[i2, 1] * v
                    nz = N[i0, 2] * w0 + N[i1, 2] * u + N[i2, 2] * v
                    ll = math.sqrt(nx * nx + ny * ny + nz * nz); nx /= ll; ny /= ll; nz /= ll
                    cr, cg, cb = shade_point(px, py, pz, nx, ny, nz, M[tri], dx, dy, dz, True, q1, q2, q3,
                                             V, F, N, M, blo, bhi, ba, bb, G, S, SN, ST, SP, SC, gstart, glist,
                                             MT, E, L, GP)
                    aa += 1.0
                elif tg < 1e29:
                    px = ox + dx * tg; py = GP[0]; pz = oz + dz * tg
                    cr, cg, cb = shade_point(px, py, pz, 0.0, 1.0, 0.0, int(GP[10]), dx, dy, dz, True, q1, q2, q3,
                                             V, F, N, M, blo, bhi, ba, bb, G, S, SN, ST, SP, SC, gstart, glist,
                                             MT, E, L, GP)
                    # distance haze into the backdrop colour
                    hz = 1 - math.exp(-tg * GP[11])
                    br, bgc, bbc = env(dx, -dy if dy < 0 else dy, dz, E)
                    cr = cr + (GP[12] - cr) * hz; cg = cg + (GP[13] - cg) * hz; cb = cb + (GP[14] - cb) * hz
                else:
                    cr, cg, cb = env(dx, dy, dz, E)
                    cr *= L[14]; cg *= L[14]; cb *= L[14]
                ar += cr; ag += cg; ab += cb
            img[j - row0, i, 0] = ar / spp; img[j - row0, i, 1] = ag / spp; img[j - row0, i, 2] = ab / spp; img[j - row0, i, 3] = aa / spp
    return img


# ----------------------------------------------------------------------------- python side
def look_at(eye, target, fov_deg, aperture=0.0, focus=None, up=(0, 1, 0)):
    eye = np.array(eye, float); target = np.array(target, float)
    f = target - eye; d = np.linalg.norm(f); f /= d
    r = np.cross(f, up); r /= np.linalg.norm(r)
    u = np.cross(r, f)
    return np.array([*eye, *f, *r, *u, math.tan(math.radians(fov_deg) / 2), aperture,
                     focus if focus is not None else d], float)


class Glazes:
    """collects glaze materials + crystal seeds + acceleration grids"""
    def __init__(self, nmat=8):
        self.G = np.zeros((nmat, 28)); self.MT = np.zeros((nmat, 8))
        self.S = [np.zeros((0, 3))]; self.SN = [np.zeros((0, 3))]; self.ST = [np.zeros((0, 3))]
        self.SP = [np.zeros((0, 4))]; self.nseed = 0
        self.gstart = [np.zeros(1, np.int64)]; self.glist = [np.zeros(0, np.int64)]; self.ncell = 0; self.nlist = 0
        self.SC = np.zeros((16, 6))

    def material(self, mat, typ, rgb=(1, 1, 1), wrap=0.15, spec=0.0, F0=0.04, rough=0.0):
        self.MT[mat] = [typ, *rgb, wrap, spec, F0, rough]

    def glaze(self, mat, ground, halo=None, spec=1.0, F0=0.045, rough=0.02, wrap=0.25, **kw):
        self.material(mat, 0, ground, wrap, spec, F0, rough)
        self.G[mat, 0:3] = ground
        self.G[mat, 3:6] = halo if halo is not None else ground
        self.G[mat, 7] = kw.get('halo_w', 0.05); self.G[mat, 8] = kw.get('ring', 0.08)
        self.G[mat, 9] = kw.get('ring_k', 0.08); self.G[mat, 10] = kw.get('fibres', 180)
        self.G[mat, 11] = kw.get('fib_k', 0.16); self.G[mat, 12] = kw.get('seam', 0.01)
        self.G[mat, 23] = kw.get('bump', 0.0); self.G[mat, 22] = kw.get('twist', 0.01); self.G[mat, 24] = kw.get('lobe', 0.0); self.G[mat, 25] = kw.get('petal', 0.0)

    def crystals(self, mat, S, SN, t0, speed, species, Tend, grid_n=48, margin=None):
        S = np.asarray(S, float); SN = np.asarray(SN, float)
        SN = SN / np.linalg.norm(SN, axis=1, keepdims=True)
        k = len(S)
        a = np.where(np.abs(SN[:, 0:1]) > 0.9, [[0, 1, 0]], [[1, 0, 0]])
        ST = np.cross(a, SN); ST /= np.linalg.norm(ST, axis=1, keepdims=True)
        rng = np.random.default_rng(mat)
        SP = np.stack([t0, speed, species, rng.random(k)], 1)
        G = self.G
        G[mat, 6] = Tend; G[mat, 13] = 1; G[mat, 14] = self.nseed; G[mat, 15] = k
        lo = S.min(0) - 0.05 * np.ptp(S, axis=0).max() - 1.0
        hi = S.max(0) + 0.05 * np.ptp(S, axis=0).max() + 1.0
        ext = (hi - lo).max(); cell = ext / grid_n
        G[mat, 16] = self.ncell; G[mat, 17:20] = lo; G[mat, 20] = cell; G[mat, 21] = grid_n
        # candidate lists per cell (conservative w.r.t. 2nd-nearest for seams)
        idx = np.arange(grid_n)
        cx = lo[0] + (idx + 0.5) * cell
        C = np.stack(np.meshgrid(lo[0] + (idx + .5) * cell, lo[1] + (idx + .5) * cell, lo[2] + (idx + .5) * cell,
                                 indexing='ij'), -1).reshape(-1, 3)
        h = cell * math.sqrt(3) / 2
        starts = [0]; lists = []
        for c0 in range(0, len(C), 4096):
            Cc = C[c0:c0 + 4096]
            d = np.linalg.norm(Cc[:, None, :] - S[None, :, :], axis=2)
            Tmin = t0[None] + np.maximum(d - h, 0) / speed[None]
            Tmax = t0[None] + (d + h) / speed[None]
            # 2nd smallest Tmax
            part = np.partition(Tmax, 1, axis=1)[:, 1] if k > 1 else Tmax[:, 0]
            for r in range(len(Cc)):
                sel = np.nonzero(Tmin[r] <= part[r] + 1e-9)[0]
                lists.append(sel); starts.append(starts[-1] + len(sel))
        gs = np.array(starts, np.int64)[1:] + self.nlist
        gl = np.concatenate(lists).astype(np.int64) if lists else np.zeros(0, np.int64)
        self.gstart.append(gs); self.glist.append(gl)
        self.ncell += len(C); self.nlist += len(gl)
        self.S.append(S); self.SN.append(SN); self.ST.append(ST); self.SP.append(SP); self.nseed += k

    def arrays(self):
        gstart = np.concatenate(self.gstart)
        return (self.G, np.concatenate(self.S), np.concatenate(self.SN), np.concatenate(self.ST),
                np.concatenate(self.SP), self.SC, gstart, np.concatenate(self.glist), self.MT)


def render(scene, gl, cam, E, L, GP, W, H, spp, bands=8, verbose=True):
    import time
    V, F, N, M, blo, bhi, ba, bb = scene.arr
    G, S, SN, ST, SP, SC, gstart, glist, MT = gl.arrays()
    out = np.zeros((H, W, 4), np.float32)
    t0 = time.time()
    step = (H + bands - 1) // bands
    for r0 in range(0, H, step):
        r1 = min(H, r0 + step)
        out[r0:r1] = render_kernel(W, H, spp, cam, V, F, N, M, blo, bhi, ba, bb, G, S, SN, ST, SP, SC,
                                   gstart, glist, MT, np.asarray(E, float), np.asarray(L, float),
                                   np.asarray(GP, float), r0, r1)
        if verbose:
            print(f'  rows {r1}/{H}  {time.time() - t0:.0f}s', flush=True)
    return out


def tonemap(img, exposure=1.0, gamma=2.2, white=None):
    x = np.maximum(img[..., :3] * exposure, 0)
    # soft shoulder that keeps pastels light: Reinhard-ish on luminance above 0.8
    lum = x.mean(2, keepdims=True)
    k = np.where(lum > 0.8, (0.8 + (1 - np.exp(-(lum - 0.8) * 2.5)) * 0.2 / 1.0) / np.maximum(lum, 1e-6), 1.0)
    x = x * k
    x = np.clip(x, 0, 1) ** (1 / gamma)
    return (x * 255 + 0.5).astype(np.uint8)


def tube(C, rad, nseg=24, closed=True):
    """tube mesh along polyline C (n,3)."""
    n = len(C)
    T = np.roll(C, -1, 0) - np.roll(C, 1, 0) if closed else np.gradient(C, axis=0)
    T /= np.linalg.norm(T, axis=1, keepdims=True)
    a = np.array([0, 1, 0.0]) if abs(T[0, 1]) < 0.9 else np.array([1, 0, 0.0])
    Nn = np.zeros_like(C); B = np.zeros_like(C)
    nv = np.cross(T[0], a); nv /= np.linalg.norm(nv)
    for i in range(n):           # parallel transport
        nv = nv - T[i] * np.dot(nv, T[i]); nv /= np.linalg.norm(nv)
        Nn[i] = nv; B[i] = np.cross(T[i], nv)
    th = np.linspace(0, 2 * np.pi, nseg, endpoint=False)
    V = (C[:, None, :] + rad * (np.cos(th)[None, :, None] * Nn[:, None, :] + np.sin(th)[None, :, None] * B[:, None, :]))
    NV = (np.cos(th)[None, :, None] * Nn[:, None, :] + np.sin(th)[None, :, None] * B[:, None, :]).reshape(-1, 3)
    V = V.reshape(-1, 3)
    F = []
    m = n if closed else n - 1
    for i in range(m):
        i2 = (i + 1) % n
        for j in range(nseg):
            j2 = (j + 1) % nseg
            a0 = i * nseg + j; a1 = i * nseg + j2; b0 = i2 * nseg + j; b1 = i2 * nseg + j2
            F.append([a0, b0, a1]); F.append([a1, b0, b1])
    return V, np.array(F, np.int64), NV


def sphere(c, r, nu=128, nv=64):
    t = np.linspace(0, np.pi, nv)
    prof = np.stack([np.sin(t)[::-1] * 0 + np.sin(t), -np.cos(t)], 1) * r
    V, F = revolve(prof, nu)
    V2, F2 = weld(V, F, 1e-7 * max(r, 1e-3))
    N = V2 / np.linalg.norm(V2, axis=1, keepdims=True)
    # orientation: make outward (signed volume > 0)
    T = V2[F2]
    if np.einsum('ij,ij->i', T[:, 0], np.cross(T[:, 1], T[:, 2])).sum() < 0:
        F2 = F2[:, ::-1]
    return V2 + np.asarray(c, float), F2, N


def surface_points(V, F, k, rng):
    A = np.linalg.norm(np.cross(V[F[:, 1]] - V[F[:, 0]], V[F[:, 2]] - V[F[:, 0]]), axis=1)
    fi = rng.choice(len(F), k, p=A / A.sum()); a = rng.random(k); b = rng.random(k)
    m = a + b > 1; a[m] = 1 - a[m]; b[m] = 1 - b[m]
    S = V[F[fi, 0]] * (1 - a - b)[:, None] + V[F[fi, 1]] * a[:, None] + V[F[fi, 2]] * b[:, None]
    return S, np.cross(V[F[fi, 1]] - V[F[fi, 0]], V[F[fi, 2]] - V[F[fi, 0]])


def poisson_surface(V, F, k, rmin, rng, tries=40):
    """dart-throwing on the surface for well-spaced seeds."""
    S, Nn = surface_points(V, F, k * tries, rng)
    keep = []
    from scipy.spatial import cKDTree
    pts = []
    for i in range(len(S)):
        p = S[i]
        if pts:
            if min(np.linalg.norm(np.array(pts) - p, axis=1)) < rmin:
                continue
        pts.append(p); keep.append(i)
        if len(keep) >= k:
            break
    keep = np.array(keep)
    return S[keep], Nn[keep]


def project(cam, p, W, H):
    """world point -> pixel (x, y) for a look_at camera."""
    e = cam[0:3]; f = cam[3:6]; r = cam[6:9]; u = cam[9:12]; th = cam[12]
    d = np.asarray(p, float) - e
    z = d @ f
    sx = (d @ r) / z / (th * W / H); sy = (d @ u) / z / th
    return (sx + 1) / 2 * W, (1 - sy) / 2 * H, z
