"""Paper-quilling renderer: strips of paper glued on edge onto a card.

The scene is a world height map H (pixels; walls are ~2-4 px thick, Hw tall) with an albedo
map.  An orthographic camera tilted by `tilt` from vertical ray-marches the height field; a low
sun casts shadows through the strips, which are translucent: every wall a shadow ray crosses
tints it by that strip's colour, so shadows are pools of coloured light.

build helpers:
  stroke(H, A, segs, width, height, col)    walls along polyline segments
  coil(H, A, mask, pitch, width, height, col, pole=None)   loose spiral coil filling a region
"""
import numpy as np
from numba import njit, prange
from scipy import ndimage as ndi


# ------------------------------------------------------------------ geometry → height
@njit(parallel=True, cache=True)
def _seg_dist(segs, h, w, x0, y0, x1, y1, out):
    for yy in prange(y0, y1):
        for xx in range(x0, x1):
            px = xx + 0.5
            py = yy + 0.5
            best = out[yy, xx]
            for k in range(segs.shape[0]):
                ax, ay, bx, by = segs[k, 0], segs[k, 1], segs[k, 2], segs[k, 3]
                dx, dy = bx - ax, by - ay
                L2 = dx * dx + dy * dy
                t = 0.0
                if L2 > 0:
                    t = ((px - ax) * dx + (py - ay) * dy) / L2
                    t = min(1.0, max(0.0, t))
                qx = ax + t * dx - px
                qy = ay + t * dy - py
                d = (qx * qx + qy * qy) ** 0.5
                if d < best:
                    best = d
            out[yy, xx] = best


def seg_dist(segs, shape, pad=8):
    """distance from each pixel centre to the nearest segment (inf far outside the bbox)."""
    segs = np.asarray(segs, np.float64).reshape(-1, 4)
    h, w = shape
    out = np.full(shape, 1e9)
    x0 = max(0, int(np.floor(min(segs[:, 0].min(), segs[:, 2].min()) - pad)))
    x1 = min(w, int(np.ceil(max(segs[:, 0].max(), segs[:, 2].max()) + pad)))
    y0 = max(0, int(np.floor(min(segs[:, 1].min(), segs[:, 3].min()) - pad)))
    y1 = min(h, int(np.ceil(max(segs[:, 1].max(), segs[:, 3].max()) + pad)))
    _seg_dist(segs, h, w, x0, y0, x1, y1, out)
    return out


def poly_segs(pts, closed=True):
    pts = np.asarray(pts, float)
    q = np.roll(pts, -1, 0) if closed else pts[1:]
    p = pts if closed else pts[:-1]
    return np.hstack([p, q])


def wall_profile(d, width):
    """0..1 cross-section of a strip of thickness `width` (soft 1px edges, slightly rounded top)."""
    a = np.clip(width / 2 + 0.5 - d, 0, 1)
    return a


def put(H, A, prof, height, col, top_round=0.1):
    """merge a wall (profile 0..1) into the scene; taller/later wins where they overlap."""
    hh = height * prof * (1 - top_round + top_round * prof)
    m = hh > H
    H[m] = hh[m]
    a = np.clip(prof * 1.6, 0, 1)[..., None]
    sel = (prof > 0.02)[..., None]
    A[:] = np.where(sel & m[..., None], A * (1 - a) + np.asarray(col) * a, A)


def stroke(H, A, segs, width, height, col):
    d = seg_dist(segs, H.shape, pad=width + 4)
    put(H, A, wall_profile(d, width), height, col)
    return d


def coil(H, A, mask, pitch, width, height, col, pole=None, ecc=0.0, ecc_dir=0.0, hue_fn=None,
         rim_gap=1.5, centre_gap=0.0, smooth=0.0):
    """Fill a boolean region with a spiral coil whose turns follow the region's distance contours.

    u = d/pitch + θ/2π is continuous (θ's 2π jump changes u by exactly 1), so walls at
    frac(u) ≈ 0 trace one spiral.  `ecc` pulls the turns toward one side like a loose coil
    that was pinched (0 = centred)."""
    if mask.sum() < 20:
        return
    d = ndi.distance_transform_edt(mask)
    if pole is None:
        k = np.argmax(d)
        pole = (k % mask.shape[1], k // mask.shape[1])
    dmax = d.max()
    yy, xx = np.nonzero(mask)
    y0, y1, x0, x1 = yy.min(), yy.max() + 1, xx.min(), xx.max() + 1
    sub = d[y0:y1, x0:x1]
    msub = mask[y0:y1, x0:x1]
    gy, gx = np.mgrid[y0:y1, x0:x1].astype(float)
    th = np.arctan2(gy + 0.5 - pole[1], gx + 0.5 - pole[0])
    # loose-coil eccentricity: compress pitch on one side of the pole
    if smooth > 0:
        sub = ndi.gaussian_filter(sub, smooth) * msub
    dd = sub - rim_gap
    s = dd / dmax
    if ecc:
        dd = dd * (1 + ecc * np.cos(th - ecc_dir) * np.clip(s, 0, 1) * (1 - np.clip(s, 0, 1)) * 4)
    u = dd / pitch + th / (2 * np.pi)
    f = u - np.floor(u)
    dist = np.minimum(f, 1 - f) * pitch
    prof = wall_profile(dist, width) * (dd > 0) * msub
    if centre_gap > 0:
        prof *= np.clip((dmax - sub - centre_gap) / 2, 0, 1)
    # the innermost tight centre: a little solid dot of rolled paper
    Hs = H[y0:y1, x0:x1]
    As = A[y0:y1, x0:x1]
    c = col if hue_fn is None else hue_fn(s)
    put(Hs, As, prof, height, c)
    return pole


# ------------------------------------------------------------------ renderer
@njit(parallel=True, cache=True, fastmath=True)
def _render(H, A, NX, NY, NZ, AO, out, scale, ys0, tilt, L, sun, amb, hmax, spp, trans, seed, G, gcol):
    Hh, Hw = H.shape
    So, Wo = out.shape[0], out.shape[1]
    ta = np.tan(tilt)
    ca = np.cos(tilt)
    for Y in prange(So):
        rs = np.uint64(seed + Y * 7919)
        for X in range(Wo):
            acc0 = 0.0
            acc1 = 0.0
            acc2 = 0.0
            for s in range(spp):
                # jitter (LCG)
                rs = rs * np.uint64(6364136223846793005) + np.uint64(1442695040888963407)
                jx = ((rs >> np.uint64(33)) & np.uint64(0xFFFFFF)) / 16777216.0
                rs = rs * np.uint64(6364136223846793005) + np.uint64(1442695040888963407)
                jy = ((rs >> np.uint64(33)) & np.uint64(0xFFFFFF)) / 16777216.0
                x = (X + jx) * scale
                y0 = ((Y + jy) * scale) / ca + ys0
                # march from z=hmax down to 0; ray at height z sits at y0 + z*ta
                nst = int(hmax * ta / 0.35) + 2
                hz = hmax
                hitz = -1.0
                hx = x
                hy = y0
                for i in range(nst + 1):
                    z = hmax * (1.0 - i / nst)
                    yy = y0 + z * ta
                    # bilinear height
                    fx = x - 0.5
                    fy = yy - 0.5
                    ix = int(np.floor(fx))
                    iy = int(np.floor(fy))
                    if ix < 0 or iy < 0 or ix >= Hw - 1 or iy >= Hh - 1:
                        continue
                    ax = fx - ix
                    ay = fy - iy
                    h = (H[iy, ix] * (1 - ax) * (1 - ay) + H[iy, ix + 1] * ax * (1 - ay)
                         + H[iy + 1, ix] * (1 - ax) * ay + H[iy + 1, ix + 1] * ax * ay)
                    if z <= h:
                        hitz = h if (h - z) < hmax / nst * 1.01 and i > 0 else z
                        if i == 0:
                            hitz = h
                        hitz = min(h, z + hmax / nst) if i > 0 else h
                        hx = x
                        hy = yy
                        break
                if hitz < 0:
                    hitz = 0.0
                    hx = x
                    hy = y0
                ix = min(max(int(hx), 0), Hw - 1)
                iy = min(max(int(hy), 0), Hh - 1)
                nx = NX[iy, ix]
                ny = NY[iy, ix]
                nz = NZ[iy, ix]
                # is this a side face?  (hit well below the local top)
                htop = H[iy, ix]
                side = (htop - hitz) > 1.0
                if side:
                    # side faces: horizontal normal, flip to face the camera (+y)
                    ln = (nx * nx + ny * ny) ** 0.5
                    if ln < 1e-3:
                        nx, ny = 0.0, 1.0
                    else:
                        nx /= ln
                        ny /= ln
                    if ny < 0:
                        ny = -ny
                    nz = 0.0
                    tot = (nx * nx + ny * ny) ** 0.5
                    nx /= tot
                    ny /= tot
                r = A[iy, ix, 0]
                g = A[iy, ix, 1]
                b = A[iy, ix, 2]
                if not side:
                    gw = G[iy, ix]
                    if gw > 0:
                        r = r * (1 - gw) + gcol[0] * gw
                        g = g * (1 - gw) + gcol[1] * gw
                        b = b * (1 - gw) + gcol[2] * gw
                # shadow ray with coloured transmittance
                T0 = 1.0
                T1 = 1.0
                T2 = 1.0
                px = hx
                py = hy
                pz = hitz + 0.6
                step = 0.5
                inside = False
                for k in range(4000):
                    px += L[0] * step
                    py += L[1] * step
                    pz += L[2] * step
                    if pz > hmax or px < 0 or py < 0 or px >= Hw - 1 or py >= Hh - 1:
                        break
                    jx2 = int(px)
                    jy2 = int(py)
                    hh2 = H[jy2, jx2]
                    if pz < hh2:
                        if not inside:
                            inside = True
                            T0 *= trans * (0.25 + 0.75 * A[jy2, jx2, 0])
                            T1 *= trans * (0.25 + 0.75 * A[jy2, jx2, 1])
                            T2 *= trans * (0.25 + 0.75 * A[jy2, jx2, 2])
                            if T0 + T1 + T2 < 0.02:
                                break
                    else:
                        inside = False
                ndl = nx * L[0] + ny * L[1] + nz * L[2]
                ao = AO[iy, ix]
                if side:
                    ao = ao * (0.55 + 0.45 * min(1.0, hitz / (htop + 1e-6)) ** 0.7)
                dif = max(ndl, 0.0)
                back = max(-ndl, 0.0) * 0.32 if side else 0.0   # light glowing through the paper
                if not side and G[iy, ix] > 0.3:
                    # metallic gild: a broad warm sheen toward the viewer-ish half vector
                    hz = nz * 0.8 + 0.6
                    dif = dif + 0.55 * G[iy, ix] * hz * T0
                c0 = r * (amb[0] * ao + sun[0] * (dif * T0 + back))
                c1 = g * (amb[1] * ao + sun[1] * (dif * T1 + back))
                c2 = b * (amb[2] * ao + sun[2] * (dif * T2 + back))
                acc0 += c0
                acc1 += c1
                acc2 += c2
            out[Y, X, 0] = acc0 / spp
            out[Y, X, 1] = acc1 / spp
            out[Y, X, 2] = acc2 / spp


def normals(H, sigma=0.9):
    Hb = ndi.gaussian_filter(H, sigma)
    gy, gx = np.gradient(Hb)
    nx, ny, nz = -gx, -gy, np.ones_like(H) * 0.6
    n = np.sqrt(nx * nx + ny * ny + nz * nz)
    return (nx / n).astype(np.float32), (ny / n).astype(np.float32), (nz / n).astype(np.float32)


def ambient_occlusion(H, hmax):
    ao = np.ones_like(H)
    for s, wgt in ((3, 0.45), (9, 0.35), (24, 0.2)):
        Hb = ndi.uniform_filter(H, int(2 * s + 1))
        occ = np.clip((Hb - H) / hmax, 0, 1)
        ao -= wgt * occ * 1.6
    return np.clip(ao, 0.35, 1).astype(np.float32)


def render(H, A, tilt_deg=32, light=(-0.55, -0.62, 0.56), sun=(1.02, 0.97, 0.9),
           amb=(0.50, 0.50, 0.58), out_w=None, spp=4, trans=0.62, ys0=None, out_h=None, seed=1, G=None,
           gcol=(1.0, 0.86, 0.58)):
    if G is None:
        G = np.zeros(H.shape, np.float32)
    H = np.ascontiguousarray(H, np.float32)
    A = np.ascontiguousarray(A, np.float32)
    hmax = float(H.max()) + 1
    tilt = np.radians(tilt_deg)
    NX, NY, NZ = normals(H)
    AO = ambient_occlusion(H, hmax)
    L = np.array(light, float)
    L /= np.linalg.norm(L)
    scale = 1.0 if out_w is None else H.shape[1] / out_w
    Wo = int(round(H.shape[1] / scale))
    if ys0 is None:
        ys0 = 0.0
    if out_h is None:
        out_h = int((H.shape[0] - ys0) * np.cos(tilt) / scale)
    out = np.zeros((out_h, Wo, 3), np.float32)
    _render(H, A, NX, NY, NZ, AO, out, scale, ys0, tilt, L, np.array(sun, float),
            np.array(amb, float), hmax, spp, trans, seed, np.ascontiguousarray(G, np.float32),
            np.array(gcol, float))
    return out


def tonemap(img, white=1.0, sat=1.0):
    x = np.clip(img / white, 0, None)
    x = x / (1 + 0.12 * x)            # gentle shoulder
    x = x / (1 / 1.12)
    if sat != 1.0:
        m = x.mean(-1, keepdims=True)
        x = m + (x - m) * sat
    x = np.clip(x, 0, 1)
    return (255 * x ** (1 / 1.0) + 0.5).astype(np.uint8)
