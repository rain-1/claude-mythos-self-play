"""clay.py — soft pastel 'sugared clay' renderer for polycubes (numba ray tracer).
Unit cubes at integer cells, on a paper ground plane z=0. Orthographic camera.
Outputs linear RGB with soft shadows, AO, bevelled edges, subtle subsurface warmth."""
import numpy as np, numba as nb, math

@nb.njit(inline='always')
def hit_boxes(ox, oy, oz, dx, dy, dz, B, tmax):
    # B: (n,3) integer min corners, cube size 1 (slightly inset for bevel gaps)
    best = tmax; bi = -1; ax = -1
    for k in range(B.shape[0]):
        t0 = -1e30; t1 = 1e30; a0 = -1
        o = (ox, oy, oz); d = (dx, dy, dz)
        ok = True
        for a in range(3):
            lo = B[k, a] + 0.02; hi = B[k, a] + B[k, 3 + a] - 0.02
            if abs(d[a]) < 1e-12:
                if o[a] < lo or o[a] > hi: ok = False; break
                continue
            ta = (lo - o[a]) / d[a]; tb = (hi - o[a]) / d[a]
            if ta > tb: ta, tb = tb, ta
            if ta > t0: t0 = ta; a0 = a
            if tb < t1: t1 = tb
        if ok and t0 <= t1 and t0 > 1e-6 and t0 < best:
            best = t0; bi = k; ax = a0
    return best, bi, ax

@nb.njit(inline='always')
def occluded(px, py, pz, dx, dy, dz, B, tmax):
    t, bi, ax = hit_boxes(px, py, pz, dx, dy, dz, B, tmax)
    return bi >= 0

@nb.njit
def hash2(i, j, s):
    h = (i * 374761393 + j * 668265263 + s * 2147483647) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return (h & 0xFFFFFF) / 16777216.0

@nb.njit(parallel=True)
def render(B, col, W, H, cx, cy, cz, scale, az, el, L, nsh, nao, ground_rgb, rb=0.13):
    """col: (n,3) linear albedo per cube. cx,cy: world centre (x,y) of view on ground; scale: px per unit.
    returns (H,W,3) rgb and alpha-ish shadow-free mask"""
    out = np.zeros((H, W, 3)); mask = np.zeros((H, W))
    # camera basis
    dx = -math.cos(el) * math.cos(az); dy = -math.cos(el) * math.sin(az); dz = -math.sin(el)
    rx = -math.sin(az); ry = math.cos(az); rz = 0.0          # screen right
    ux = dy * rz - dz * ry; uy = dz * rx - dx * rz; uz = dx * ry - dy * rx   # up = right x dir? ensure up z>0
    if uz < 0: ux, uy, uz = -ux, -uy, -uz
    Lx, Ly, Lz = L[0], L[1], L[2]
    for i in nb.prange(H):
        for j in range(W):
            acc0 = 0.0; acc1 = 0.0; acc2 = 0.0; m = 0.0
            for s in range(4):  # 2x2 supersample
                sx = (j + 0.25 + 0.5 * (s % 2) - W / 2) / scale
                sy = -(i + 0.25 + 0.5 * (s // 2) - H / 2) / scale
                # origin: far along -dir from point on plane through (cx,cy,0.0)
                px = cx + rx * sx + ux * sy - dx * 50; py = cy + ry * sx + uy * sy - dy * 50; pz = cz + rz * sx + uz * sy - dz * 50
                t, bi, ax = hit_boxes(px, py, pz, dx, dy, dz, B, 1e9)
                # ground
                tg = -pz / dz
                if bi >= 0:
                    hx = px + dx * t; hy = py + dy * t; hz = pz + dz * t
                    nx = 0.0; ny = 0.0; nz = 0.0
                    if ax == 0: nx = -1.0 if dx > 0 else 1.0
                    elif ax == 1: ny = -1.0 if dy > 0 else 1.0
                    else: nz = -1.0 if dz > 0 else 1.0
                    # bevel: distance to cube edges in the face
                    lx = hx - B[bi, 0]; ly = hy - B[bi, 1]; lz = hz - B[bi, 2]
                    e = 1.0
                    bx = 0.0; by = 0.0; bz = 0.0
                    if ax != 0:
                        q = min(lx - 0.02, B[bi, 3] - 0.02 - lx)
                        if q < rb: e = min(e, q / rb); bx += (1 - q / rb) * (-1.0 if lx < 0.5 * B[bi, 3] else 1.0)
                    if ax != 1:
                        q = min(ly - 0.02, B[bi, 4] - 0.02 - ly)
                        if q < rb: e = min(e, q / rb); by += (1 - q / rb) * (-1.0 if ly < 0.5 * B[bi, 4] else 1.0)
                    if ax != 2:
                        q = min(lz - 0.02, B[bi, 5] - 0.02 - lz)
                        if q < rb: e = min(e, q / rb); bz += (1 - q / rb) * (-1.0 if lz < 0.5 * B[bi, 5] else 1.0)
                    mx = nx + 0.9 * bx; my = ny + 0.9 * by; mz = nz + 0.9 * bz
                    nn = math.sqrt(mx * mx + my * my + mz * mz); mx /= nn; my /= nn; mz /= nn
                    ndl = mx * Lx + my * Ly + mz * Lz
                    # soft shadow
                    vis = 0.0
                    for k in range(nsh):
                        jx = (hash2(i * 4 + s, j, k) - 0.5) * 0.35; jy = (hash2(j, i * 4 + s, k + 7) - 0.5) * 0.35
                        qx = Lx + jx; qy = Ly + jy; qz = Lz
                        qn = math.sqrt(qx * qx + qy * qy + qz * qz)
                        if not occluded(hx + nx * 1e-4, hy + ny * 1e-4, hz + nz * 1e-4, qx / qn, qy / qn, qz / qn, B, 1e9): vis += 1.0
                    vis /= nsh
                    # AO
                    ao = 0.0
                    for k in range(nao):
                        u1 = hash2(i * 4 + s, j, 100 + k); u2 = hash2(j, i * 4 + s, 200 + k)
                        r = math.sqrt(u1); ph = 6.2831853 * u2
                        # tangent frame
                        if abs(nz) > 0.5: t1x, t1y, t1z = 1.0, 0.0, 0.0
                        else: t1x, t1y, t1z = 0.0, 0.0, 1.0
                        t2x = ny * t1z - nz * t1y; t2y = nz * t1x - nx * t1z; t2z = nx * t1y - ny * t1x
                        t1x = t2y * nz - t2z * ny; t1y = t2z * nx - t2x * nz; t1z = t2x * ny - t2y * nx
                        a1 = r * math.cos(ph); a2 = r * math.sin(ph); a3 = math.sqrt(max(0.0, 1 - u1))
                        qx = a1 * t1x + a2 * t2x + a3 * nx; qy = a1 * t1y + a2 * t2y + a3 * ny; qz = a1 * t1z + a2 * t2z + a3 * nz
                        hit = occluded(hx + nx * 1e-4, hy + ny * 1e-4, hz + nz * 1e-4, qx, qy, qz, B, 1.2)
                        if (not hit) and (hz + nz * 1e-4 + qz * 0.6 > 0 or qz >= 0): ao += 1.0
                    ao /= nao
                    dif = max(0.0, ndl) * (0.35 + 0.65 * vis)
                    wrap = (ndl * 0.5 + 0.5)
                    amb = 0.42 + 0.18 * mz
                    # specular (soft sheen)
                    hxv = Lx - dx; hyv = Ly - dy; hzv = Lz - dz
                    hn = math.sqrt(hxv * hxv + hyv * hyv + hzv * hzv)
                    sp = max(0.0, (mx * hxv + my * hyv + mz * hzv) / hn) ** 40 * vis * 0.35
                    for c in range(3):
                        alb = col[bi, c]
                        v = alb * (0.62 * dif + amb * (0.55 + 0.45 * ao) + 0.12 * wrap * (1 - alb)) + sp
                        # warm subsurface lift in shadowed parts
                        if c == 0: v += 0.04 * (1 - vis) * alb
                        if c == 0: acc0 += v
                        elif c == 1: acc1 += v
                        else: acc2 += v
                    m += 1.0
                elif tg > 0:
                    gx = px + dx * tg; gy = py + dy * tg
                    vis = 0.0
                    for k in range(nsh):
                        jx = (hash2(i * 4 + s, j, k) - 0.5) * 0.35; jy = (hash2(j, i * 4 + s, k + 7) - 0.5) * 0.35
                        qx = Lx + jx; qy = Ly + jy; qz = Lz
                        qn = math.sqrt(qx * qx + qy * qy + qz * qz)
                        if not occluded(gx, gy, 1e-4, qx / qn, qy / qn, qz / qn, B, 1e9): vis += 1.0
                    vis /= nsh
                    ao = 0.0
                    for k in range(nao):
                        u1 = hash2(i * 4 + s, j, 100 + k); u2 = hash2(j, i * 4 + s, 200 + k)
                        r = math.sqrt(u1); ph = 6.2831853 * u2
                        qx = r * math.cos(ph); qy = r * math.sin(ph); qz = math.sqrt(max(0.0, 1 - u1))
                        if not occluded(gx, gy, 1e-4, qx, qy, qz, B, 1.5): ao += 1.0
                    ao /= nao
                    f = (0.80 + 0.20 * vis) * (0.80 + 0.20 * ao)
                    acc0 += ground_rgb[0] * f; acc1 += ground_rgb[1] * f; acc2 += ground_rgb[2] * f
                else:
                    acc0 += ground_rgb[0]; acc1 += ground_rgb[1]; acc2 += ground_rgb[2]
            out[i, j, 0] = acc0 / 4; out[i, j, 1] = acc1 / 4; out[i, j, 2] = acc2 / 4
            mask[i, j] = m / 4
    return out, mask
