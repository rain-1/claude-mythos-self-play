"""Tiny numba ray tracer for paper-straw polygons: capsules (striped paper straws) joined by pearl beads,
floating over a matte paper tile.  One cell = one small scene.

render(V, cyc, size, straw_rgb, ground_rgb, ...) -> float32 HxWx3 linear image
"""
import numpy as np
from numba import njit, prange

@njit(cache=True)
def _cap_hit(o, d, a, b, r):
    # ray vs capsule (segment a-b radius r); returns t or -1, and axial param s in [0,1]
    ba = b - a; oa = o - a
    baba = ba @ ba; bard = ba @ d; baoa = ba @ oa; rdoa = d @ oa; oaoa = oa @ oa
    A = baba - bard * bard
    B = baba * rdoa - baoa * bard
    C = baba * oaoa - baoa * baoa - r * r * baba
    h = B * B - A * C
    if h >= 0.0 and A > 1e-12:
        t = (-B - np.sqrt(h)) / A
        y = baoa + t * bard
        if y > 0.0 and y < baba and t > 1e-5:
            return t, y / baba
    # caps
    for k in range(2):
        c = a if k == 0 else b
        oc = o - c
        bb = d @ oc; cc = oc @ oc - r * r
        hh = bb * bb - cc
        if hh > 0.0:
            t = -bb - np.sqrt(hh)
            if t > 1e-5:
                y = (o + t * d - a) @ ba
                if (k == 0 and y <= 0.0) or (k == 1 and y >= baba):
                    return t, 0.0 if k == 0 else 1.0
    return -1.0, 0.0

@njit(cache=True)
def _sph_hit(o, d, c, r):
    oc = o - c
    b = d @ oc; cc = oc @ oc - r * r
    h = b * b - cc
    if h < 0.0:
        return -1.0
    t = -b - np.sqrt(h)
    if t > 1e-5:
        return t
    return -1.0

@njit(cache=True)
def _trace(o, d, A, B, rc, C, rs, zg):
    """returns (t, kind, index, s): kind 0 none, 1 straw, 2 bead, 3 ground"""
    bt = 1e30; kind = 0; idx = -1; bs = 0.0
    for i in range(A.shape[0]):
        t, s = _cap_hit(o, d, A[i], B[i], rc)
        if t > 0 and t < bt:
            bt = t; kind = 1; idx = i; bs = s
    for i in range(C.shape[0]):
        t = _sph_hit(o, d, C[i], rs)
        if t > 0 and t < bt:
            bt = t; kind = 2; idx = i
    if d[2] < 0:
        t = (zg - o[2]) / d[2]
        if t > 1e-5 and t < bt:
            bt = t; kind = 3; idx = -1
    return bt, kind, idx, bs

@njit(cache=True)
def _occluded(o, d, A, B, rc, C, rs):
    for i in range(A.shape[0]):
        t, s = _cap_hit(o, d, A[i], B[i], rc)
        if t > 0:
            return True
    for i in range(C.shape[0]):
        if _sph_hit(o, d, C[i], rs) > 0:
            return True
    return False

@njit(cache=True)
def _onb(n):
    if abs(n[2]) < 0.9:
        t = np.array([0.0, 0.0, 1.0])
    else:
        t = np.array([1.0, 0.0, 0.0])
    u = np.cross(n, t); u /= np.sqrt(u @ u)
    v = np.cross(n, u)
    return u, v

@njit(parallel=True, cache=True)
def render_cell(A, B, rc, C, rs, zg, H, W, eye, fwd, right, up, fov, sun, sunrad,
                straw_col, stripe_col, bead_col, ground_col, sky_col, sun_col, spp, pitch, nstripe, seed):
    img = np.zeros((H, W, 3), np.float32)
    alpha = np.zeros((H, W), np.float32)
    for y in prange(H):
        np.random.seed(seed + y * 7919)
        for x in range(W):
            acc = np.zeros(3)
            cov = 0.0
            for s in range(spp):
                jx = (x + np.random.random()) / W * 2 - 1
                jy = 1 - (y + np.random.random()) / H * 2
                d = fwd + right * (jx * fov) + up * (jy * fov * H / W)
                d /= np.sqrt(d @ d)
                o = eye.copy()
                t, kind, idx, sp = _trace(o, d, A, B, rc, C, rs, zg)
                if kind == 0:
                    acc += ground_col
                    continue
                p = o + t * d
                if kind == 1:
                    a = A[idx]; b = B[idx]; ba = b - a
                    L = np.sqrt(ba @ ba); ax = ba / L
                    q = a + ax * ((p - a) @ ax)
                    n = p - q; n /= np.sqrt(n @ n)
                    u, v = _onb(ax)
                    phi = np.arctan2(n @ v, n @ u) / (2 * np.pi)
                    st = ((p - a) @ ax) / pitch + phi * nstripe
                    fr = st - np.floor(st)
                    m = 0.5 + 0.5 * np.tanh((np.abs(fr - 0.5) - 0.25) * 40.0)
                    alb = straw_col * (1 - m) + stripe_col * m
                    spec = 0.10
                    cov += 1
                elif kind == 2:
                    n = p - C[idx]; n /= np.sqrt(n @ n)
                    alb = bead_col
                    spec = 0.45
                    cov += 1
                else:
                    n = np.array([0.0, 0.0, 1.0])
                    alb = ground_col
                    spec = 0.0
                # sun (soft): jittered direction within a cone
                su, sv = _onb(sun)
                r1 = np.sqrt(np.random.random()) * sunrad; a1 = 2 * np.pi * np.random.random()
                ld = sun + su * (r1 * np.cos(a1)) + sv * (r1 * np.sin(a1)); ld /= np.sqrt(ld @ ld)
                ndl = n @ ld
                col = np.zeros(3)
                if ndl > 0 and not _occluded(p + n * 1e-4, ld, A, B, rc, C, rs):
                    col += alb * sun_col * ndl
                    hv = ld - d; hv /= np.sqrt(hv @ hv)
                    col += sun_col * spec * (max(n @ hv, 0.0) ** (60.0 if kind == 2 else 18.0))
                # sky ambient with one AO ray (cosine weighted)
                nu, nv = _onb(n)
                r2 = np.random.random(); a2 = 2 * np.pi * np.random.random()
                sr = np.sqrt(r2)
                ad = nu * (sr * np.cos(a2)) + nv * (sr * np.sin(a2)) + n * np.sqrt(1 - r2)
                if not _occluded(p + n * 1e-4, ad, A, B, rc, C, rs):
                    col += alb * sky_col
                else:
                    col += alb * sky_col * 0.35
                # clear-coat sky reflection on beads
                if kind == 2:
                    rd = d - 2 * (d @ n) * n
                    f = 0.04 + 0.96 * (1 - abs(d @ n)) ** 5
                    col += f * sky_col * 1.4 * (0.6 + 0.4 * max(rd[2], 0.0))
                acc += col
            img[y, x, 0] = acc[0] / spp; img[y, x, 1] = acc[1] / spp; img[y, x, 2] = acc[2] / spp
            alpha[y, x] = cov / spp
    return img, alpha
