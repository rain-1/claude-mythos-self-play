"""THE UNIVERSAL BOARD (MO 516225): an incremental cyclic Latin square L[i][j] = (i + q(j)) mod n
as stacks of pastel coins, height n - L.  Slice the city at height k and the coins you cut are a
placement with n-k+1 per row and column and at most that many on every diagonal; the top layer is
n queens.
usage: python3 towers.py OUT.png W H SPP [n q0 q1 ...]
"""
import sys, numpy as np
from numba import njit, prange
from PIL import Image

W, H, SPP = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
if len(sys.argv) > 5:
    n = int(sys.argv[5]); q = [int(v) for v in sys.argv[6:6 + n]]
else:
    n = 8; q = [0, 4, 1, 3, 6, 2, 7, 5]
L = np.array([[(i + q[j]) % n for j in range(n)] for i in range(n)])
Hs = n - L                      # coins in each stack

def lin(h):
    h = h.lstrip('#'); return (np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)]) / 255.0) ** 2.2
# layer colours bottom -> top: a sorbet walk ending in coral for the queens
LAYER = ['8fe3c8', '9ad8f2', 'a9bdf6', 'c4acf3', 'eaa8e6', 'ffa8bd', 'ffc08f', 'ff7a6a']
if n != 8:
    import colorsys
LC = np.array([lin(LAYER[min(len(LAYER) - 1, int(round(k * (len(LAYER) - 1) / max(n - 1, 1))))]) for k in range(n)])

CR, CT = 0.37, 0.145            # coin radius, coin thickness (cell = 1)

@njit(cache=True)
def hit_stack(o, d, cx, cy, h):
    # vertical cylinder radius CR from z=0 to z=h centred (cx,cy): returns t, kind(1 side, 2 top)
    best = 1e30; kind = 0
    ox = o[0] - cx; oy = o[1] - cy
    a = d[0] * d[0] + d[1] * d[1]
    b = ox * d[0] + oy * d[1]
    c = ox * ox + oy * oy - CR * CR
    disc = b * b - a * c
    if disc >= 0 and a > 1e-12:
        t = (-b - np.sqrt(disc)) / a
        z = o[2] + t * d[2]
        if t > 1e-6 and z >= 0 and z <= h:
            best = t; kind = 1
    if d[2] < 0:
        t = (h - o[2]) / d[2]
        if t > 1e-6 and t < best:
            x = o[0] + t * d[0] - cx; y = o[1] + t * d[1] - cy
            if x * x + y * y <= CR * CR:
                best = t; kind = 2
    return best, kind

@njit(cache=True)
def trace(o, d, Hs, n):
    bt = 1e30; bk = 0; bi = -1; bj = -1
    for i in range(n):
        for j in range(n):
            t, k = hit_stack(o, d, j + 0.5, i + 0.5, Hs[i, j] * CT)
            if k > 0 and t < bt:
                bt = t; bk = k; bi = i; bj = j
    if d[2] < 0:
        t = -o[2] / d[2]
        if t > 1e-6 and t < bt:
            bt = t; bk = 3
    return bt, bk, bi, bj

@njit(cache=True)
def occluded(o, d, Hs, n):
    for i in range(n):
        for j in range(n):
            t, k = hit_stack(o, d, j + 0.5, i + 0.5, Hs[i, j] * CT)
            if k > 0:
                return True
    return False

@njit(cache=True)
def onb(nv):
    if abs(nv[2]) < 0.9:
        t = np.array([0.0, 0.0, 1.0])
    else:
        t = np.array([1.0, 0.0, 0.0])
    u = np.cross(nv, t); u /= np.sqrt(u @ u)
    return u, np.cross(nv, u)

@njit(parallel=True, cache=True)
def render(W, H, spp, eye, fwd, right, up, fov, Hs, n, LC, sun, sunrad, suncol, skycol,
           boardA, boardB, table, gold, focus, aper):
    img = np.zeros((H, W, 3), np.float32)
    for y in prange(H):
        np.random.seed(y * 7717 + 3)
        for x in range(W):
            acc = np.zeros(3)
            for s in range(spp):
                jx = (x + np.random.random()) / W * 2 - 1
                jy = 1 - (y + np.random.random()) / H * 2
                d = fwd + right * (jx * fov) + up * (jy * fov * H / W)
                d /= np.sqrt(d @ d)
                # thin lens
                fp = eye + d * (focus / (d @ fwd))
                r0 = np.sqrt(np.random.random()) * aper; a0 = 2 * np.pi * np.random.random()
                o = eye + right * (r0 * np.cos(a0)) + up * (r0 * np.sin(a0))
                d = fp - o; d /= np.sqrt(d @ d)
                t, k, i, j = trace(o, d, Hs, n)
                if k == 0:
                    acc += table
                    continue
                p = o + t * d
                spec = 0.0; shin = 30.0
                if k == 3:
                    nv = np.array([0.0, 0.0, 1.0])
                    if p[0] >= 0 and p[0] <= n and p[1] >= 0 and p[1] <= n:
                        ci = int(np.floor(p[1])); cj = int(np.floor(p[0]))
                        alb = boardA if (ci + cj) % 2 == 0 else boardB
                        # thin gold inlay around the board
                    elif p[0] > -0.35 and p[0] < n + 0.35 and p[1] > -0.35 and p[1] < n + 0.35:
                        alb = gold; spec = 0.5
                    else:
                        alb = table
                else:
                    cx = j + 0.5; cy = i + 0.5
                    if k == 2:
                        nv = np.array([0.0, 0.0, 1.0])
                        lay = Hs[i, j] - 1
                        rr = np.sqrt((p[0] - cx) ** 2 + (p[1] - cy) ** 2) / CR
                        # embossed rim ring on the top coin
                        if rr > 0.78 and rr < 0.86:
                            alb = LC[lay] * 0.86
                        else:
                            alb = LC[lay]
                        spec = 0.25
                    else:
                        nv = np.array([p[0] - cx, p[1] - cy, 0.0]); nv /= np.sqrt(nv @ nv)
                        u = p[2] / CT
                        lay = min(int(np.floor(u)), Hs[i, j] - 1)
                        f = u - np.floor(u)
                        # rounded coin edges: tilt normal near the seams, darken the seam
                        e = 0.0
                        if f < 0.18:
                            e = -(0.18 - f) / 0.18
                        elif f > 0.82:
                            e = (f - 0.82) / 0.18
                        nv = nv * np.sqrt(1 - 0.5 * e * e) + np.array([0.0, 0.0, 0.7 * e])
                        nv /= np.sqrt(nv @ nv)
                        # milled edge (reeding)
                        ang = np.arctan2(p[1] - cy, p[0] - cx)
                        reed = 0.94 + 0.06 * np.cos(ang * 60)
                        alb = LC[lay] * reed
                        spec = 0.18
                su, sv = onb(sun)
                r1 = np.sqrt(np.random.random()) * sunrad; a1 = 2 * np.pi * np.random.random()
                ld = sun + su * (r1 * np.cos(a1)) + sv * (r1 * np.sin(a1)); ld /= np.sqrt(ld @ ld)
                ndl = nv @ ld
                col = np.zeros(3)
                if ndl > 0 and not occluded(p + nv * 1e-4, ld, Hs, n):
                    col += alb * suncol * ndl
                    hv = ld - d; hv /= np.sqrt(hv @ hv)
                    col += suncol * spec * max(nv @ hv, 0.0) ** shin
                nu, nw = onb(nv)
                r2 = np.random.random(); a2 = 2 * np.pi * np.random.random(); sr = np.sqrt(r2)
                ad = nu * (sr * np.cos(a2)) + nw * (sr * np.sin(a2)) + nv * np.sqrt(1 - r2)
                if not occluded(p + nv * 1e-4, ad, Hs, n):
                    col += alb * skycol
                else:
                    col += alb * skycol * 0.4
                acc += col
            img[y, x, 0] = acc[0] / spp; img[y, x, 1] = acc[1] / spp; img[y, x, 2] = acc[2] / spp
    return img

def camera(target, elev, azim, dist):
    e, a = np.radians(elev), np.radians(azim)
    eye = target + dist * np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])
    fwd = target - eye; fwd /= np.linalg.norm(fwd)
    right = np.cross(fwd, [0, 0, 1.0]); right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    return eye, fwd, right, up

if __name__ == '__main__':
    import json
    cfg = json.loads(sys.argv[1]) if sys.argv[1].startswith('{') else {}
    out = cfg.get('out', sys.argv[1])
    tgt = np.array([n / 2 + cfg.get('tx', 0), n / 2 + cfg.get('ty', 0), 0.25])
    eye, fwd, right, up = camera(tgt, cfg.get('elev', 34), cfg.get('azim', -62), cfg.get('dist', 2.3 * n))
    sun = np.array(cfg.get('sun', [-0.55, -0.15, 0.62])); sun /= np.linalg.norm(sun)
    img = render(W, H, SPP, eye, fwd, right, up, cfg.get('fov', 0.36), Hs.astype(np.int64), n, LC, sun, 0.07,
                 np.array([0.80, 0.74, 0.66]), np.array([0.46, 0.47, 0.56]),
                 lin('fbf3ea'), lin('f3dfe6'), lin('e9e2f4'), lin('e8c98c'),
                 float(np.linalg.norm(tgt - eye)), cfg.get('aper', 0.0))
    img = img / (1 + img / 4) * 1.25
    srgb = (np.clip(img, 0, 1) ** (1 / 2.2) * 255 + 0.5).astype(np.uint8)
    Image.fromarray(srgb).save(out)
