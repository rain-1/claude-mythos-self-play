"""Compose the basin: mosaic floor glazed by the waves, caustic light, water, rim, paving."""
import sys, json, time
import numpy as np
from scipy.ndimage import map_coordinates, gaussian_filter
from PIL import Image
import pool

# glaze transmittance per wave (sorbet): strawberry, butter, mint, sky, lilac
BOATC = None
GLAZE = np.array([
    [1.00, 0.70, 0.76],
    [1.00, 0.89, 0.60],
    [0.68, 0.95, 0.80],
    [0.66, 0.83, 1.00],
    [0.86, 0.74, 1.00],
])


def _boatc():
    return [lin(c) for c in ([1.0, 0.62, 0.66], [1.0, 0.84, 0.46], [0.52, 0.88, 0.70], [0.55, 0.74, 1.0], [0.78, 0.64, 1.0])]


def srgb(x):
    x = np.clip(x, 0, 1)
    return np.where(x <= 0.0031308, 12.92 * x, 1.055 * x ** (1 / 2.4) - 0.055)


def lin(c):
    c = np.asarray(c, float)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def tonemap(x, white=1.35):
    return x * (1 + x / white ** 2) / (1 + x)


def mosaic(W, x0, x1, K, phi, a, ts, seed=7, glaze=GLAZE, dens=1.0):
    """floor albedo (linear) on the pixel grid: square tesserae, each glazed by every wave carrying its centre."""
    rng = np.random.default_rng(seed)
    px = (x1 - x0) / W
    c = x0 + (np.arange(W) + 0.5) * px
    X, Y = np.meshgrid(c, c)
    # slightly irregular tile grid: offset alternate rows by a random amount (hand-laid)
    row = np.floor(Y / ts).astype(np.int64)
    roff = (np.sin(row * 12.9898) * 43758.5453) % 1.0 * 0.35 * ts
    col = np.floor((X + roff) / ts).astype(np.int64)
    cx = (col + 0.5) * ts - roff
    cy = (row + 0.5) * ts
    # unique tiles -> weights at centres
    key = row * 100003 + col
    uk, inv = np.unique(key.ravel(), return_inverse=True)
    first = np.zeros(len(uk), np.int64)
    first[inv[::-1]] = np.arange(inv.size)[::-1]
    tcx = cx.ravel()[first]; tcy = cy.ravel()[first]
    w = np.zeros((len(uk), len(a)))
    tmp = np.empty(len(a))
    for t in range(len(uk)):
        pool.weights(tcx[t], tcy[t], K, phi, a, tmp)
        w[t] = tmp
    E = w > 0.5
    base = lin([0.985, 0.975, 0.955])
    alb = np.ones((len(uk), 3)) * base
    for k in range(len(a)):
        alb[E[:, k]] *= glaze[k] ** dens
    # hand-made variation
    alb *= (1 + rng.normal(0, 0.025, (len(uk), 1)))
    alb *= (1 + rng.normal(0, 0.012, (len(uk), 3)))
    A = alb[inv].reshape(W, W, 3)
    # grout: distance to tile edge
    fx = (X + roff) / ts - col
    fy = Y / ts - row
    d = np.minimum(np.minimum(fx, 1 - fx), np.minimum(fy, 1 - fy)) * ts / px  # px
    g = np.clip((d - 0.035 * ts / px) / (0.06 * ts / px + 1e-9), 0, 1)
    grout = lin([0.90, 0.88, 0.87])
    A = A * g[..., None] + grout * (1 - g[..., None])
    # tile bevel shading (tiny)
    bev = 0.93 + 0.07 * np.clip(d / (0.18 * ts / px), 0, 1)
    A *= bev[..., None]
    return A, E, inv.reshape(W, W)


def render(W=1024, ss=3, seed=3, lam=0.075, A=0.0042, depth=0.11, sun=(0.30, 0.55), R=0.5, cope=0.035,
           x0=-0.56, x1=0.56, ts=0.0085, out='proto.png', disp=(1.329, 1.334, 1.341), save=None,
           fan=None, spread=0.18, amb=0.62, sunk=0.70, absorb=(0.30, 0.09, 0.06), dens=1.0, floor='rings',
           probs=(0.4090311, 0.2646657, 0.1742928, 0.0984137, 0.0535967), icap=3.0, boats=True, glint=1.0, gsig=3e-4, bss=3):
    global BOATC
    t0 = time.time()
    BOATC = _boatc()
    K, phi, ang = pool.waves(seed, lam, spread, fan)
    a = pool.AMP
    el, az = sun  # sun direction: elevation from zenith (rad) and azimuth
    L = np.array([np.sin(el) * np.cos(az), np.sin(el) * np.sin(az), -np.cos(el)])
    # caustics per wavelength
    caus = []
    for c, n in enumerate(disp):
        caus.append(pool.caustic(W, x0, x1, K, phi, a, A, depth, L[0], L[1], L[2], 1.0 / n, ss, R, cope, 17 + c))
    caus = np.stack(caus, -1)
    print('caustics', time.time() - t0, caus.mean(), np.percentile(caus, [50, 99, 99.9]))
    fxy, fres, nrm, hgt = pool.view(W, x0, x1, K, phi, a, A, depth, 1.0 / 1.334, R)
    if floor == 'rings':
        cols = [lin([1.0, 0.78, 0.80]), lin([1.0, 0.91, 0.70]), lin([0.76, 0.95, 0.84]), lin([0.74, 0.86, 1.0]), lin([0.88, 0.80, 1.0])]
        alb = mosaic_rings(W, x0, x1, ts, probs, cols, R)
        E = None
    else:
        alb, E, tid = mosaic(W, x0, x1, K, phi, a, ts, dens=dens)
    px = (x1 - x0) / W
    u = (fxy[..., 0] - x0) / px - 0.5
    v = (fxy[..., 1] - x0) / px - 0.5
    seen = np.stack([map_coordinates(alb[..., c], [v, u], order=1, mode='nearest') for c in range(3)], -1)
    irr = np.stack([map_coordinates(caus[..., c], [v, u], order=1, mode='nearest') for c in range(3)], -1)
    irr = gaussian_filter(irr, (0.6, 0.6, 0))
    irr = irr / (1 + irr / icap)
    sky = lin([0.98, 0.96, 0.97])
    sunc = lin([1.0, 0.97, 0.90])
    amb = sky * amb
    light = amb + sunc * irr * sunk
    water = np.exp(-np.array(absorb) * 2 * depth / 0.11)  # pale aqua
    col = seen * light * water
    # surface: sky reflection, a touch brighter where tilted
    col = col * (1 - fres[..., None]) + fres[..., None] * sky * 1.2
    # sun glints: surface normal near the half vector of view (up) and sun
    Hv = np.array([-L[0], -L[1], 1 - L[2]]); Hv /= np.linalg.norm(Hv)
    ndh = nrm @ Hv
    gl = np.exp(-(1 - ndh) / gsig)
    col = col + glint * gl[..., None] * sunc * 3.0
    if boats:
        import boats as B
        bl = []
        for k in range(5):
            # boat k rides on its own sector, heading along its wave
            e = np.concatenate([[0], np.cumsum(probs)]); e /= e[-1]
            tm = np.pi / 2 + 2 * np.pi * (e[k] + e[k + 1]) / 2
            rad = 0.33 if k else 0.30
            bl.append((rad * np.cos(tm), rad * np.sin(tm), 0.13 * (0.6 + 0.4 * a[k] / a[0]), ang[k], BOATC[k]))
        bcol, balp, bwake = B.render_boats(W, x0, x1, bl, np.array([-L[0], -L[1]]), ss=bss)
        # shadow on the floor: footprint pushed away from the sun by depth*tan(elev), blurred
        hl = np.hypot(L[0], L[1]); sh_off = depth * hl / -L[2]
        from scipy.ndimage import shift as ndshift
        sh = ndshift(balp * 0.6, (L[1] / hl * sh_off / px, L[0] / hl * sh_off / px), order=1)
        sh = gaussian_filter(sh, 4.0 * W / 1024)
        shv = np.clip(map_coordinates(sh, [v, u], order=1), 0, 1)
        col = col * (1 - 0.45 * shv[..., None])
        # the boats themselves, lit by sky + sun
        blit = bcol * (sky * 0.55 + sunc * 0.62)
        col = col * (1 - balp[..., None]) + blit * balp[..., None]
        bw = gaussian_filter(bwake, 0.8 * W / 1024)
        col = col + 0.9 * bw[..., None] * (1 - balp[..., None])
    # outside the water: coping and paving
    c = x0 + (np.arange(W) + 0.5) * px
    X, Y = np.meshgrid(c, c)
    r = np.hypot(X, Y)
    rimw = 0.055
    # coping: rounded marble ring, with a pastel-pink cast
    tt = np.clip((r - R) / rimw, 0, 1)
    prof = np.sin(np.pi * tt)
    dprof = np.cos(np.pi * tt) * np.pi / rimw
    # normal of the rounded ring
    gxr = dprof * X / (r + 1e-9) * 0.012
    gyr = dprof * Y / (r + 1e-9) * 0.012
    nn = np.sqrt(gxr ** 2 + gyr ** 2 + 1)
    ndl = np.clip((-gxr * L[0] - gyr * L[1] - L[2]) / nn, 0, 1)
    marble = lin([0.97, 0.93, 0.92])
    thr = np.arctan2(Y, X)
    nrt = 96
    tr = np.floor((thr / (2 * np.pi) + 0.5) * nrt)
    marble = np.where(((tr % 2) == 0)[..., None], lin([0.99, 0.97, 0.96]), lin([1.0, 0.90, 0.88]))
    fs = ((thr / (2 * np.pi) + 0.5) * nrt) % 1.0
    jt = np.clip(np.minimum(fs, 1 - fs) * 2 * np.pi * r / nrt / px / 1.5, 0, 1)
    rimcol = marble * (sky * 0.50 + sunc * ndl[..., None] * 0.80)
    # glaze highlight on the rounded nose
    Hv2 = np.array([-L[0], -L[1], 1 - L[2]]); Hv2 /= np.linalg.norm(Hv2)
    ndh2 = (-gxr * Hv2[0] - gyr * Hv2[1] + Hv2[2]) / nn
    rimcol = rimcol + 0.6 * np.exp(-(1 - ndh2) / 0.004)[..., None] * sunc
    rimcol = rimcol * (0.82 + 0.18 * jt)[..., None]
    # paving outside: large pale peach slabs in radial rings
    pav = lin([0.96, 0.90, 0.84])
    rr = r - (R + rimw)
    ring = np.floor(rr / 0.07)
    th = np.arctan2(Y, X)
    nseg = np.maximum(12, np.round(2 * np.pi * (R + rimw + (ring + 0.5) * 0.07) / 0.09))
    seg = np.floor((th / (2 * np.pi) + 0.5 + ring * 0.37) * nseg)
    hsh = (np.sin(ring * 91.7 + seg * 13.3) * 43758.5) % 1.0
    pcol = pav * (0.96 + 0.05 * hsh)[..., None]
    fr = (rr / 0.07) % 1.0
    fs = ((th / (2 * np.pi) + 0.5 + ring * 0.37) * nseg) % 1.0
    dd = np.minimum(np.minimum(fr, 1 - fr) * 0.07, np.minimum(fs, 1 - fs) * 2 * np.pi * (R + rimw + rr) / nseg)
    gj = np.clip((dd - 0.0012) / 0.0015, 0, 1)
    pcol = pcol * gj[..., None] + lin([0.86, 0.82, 0.80]) * (1 - gj[..., None])
    # shadow of the coping on the paving (cast away from the sun) -- soft
    hl = np.hypot(L[0], L[1]); tan_e = hl / -L[2]
    sx = X - L[0] / hl * 0.02 * tan_e; sy = Y - L[1] / hl * 0.02 * tan_e
    sh = np.clip((np.hypot(sx, sy) - (R + rimw)) / 0.006, 0, 1)
    sh = gaussian_filter(sh, 2.0 * W / 1024)
    plit = pcol * (sky * 0.45 + sunc * 0.85 * (-L[2]) * (0.25 + 0.75 * sh))[..., None].squeeze() if False else \
        pcol * (sky * 0.45 + (sunc * 0.85 * (-L[2]))[None, None, :] * (0.25 + 0.75 * sh)[..., None])
    inside = np.clip((R - r) / px + 0.5, 0, 1)[..., None]
    onrim = np.clip((R + rimw - r) / px + 0.5, 0, 1)[..., None] * (1 - inside)
    outside = 1 - inside - onrim
    # inner lip shadow: water darkens near the wall on the sun side (wall shadow) handled by caustic; add AO near wall
    ao = 1 - 0.18 * np.exp(-(R - r).clip(0) / 0.012)
    img = col * inside * ao[..., None] + rimcol * onrim + plit * outside
    rgb = srgb(tonemap(img))
    rgb = rgb + np.random.default_rng(0).uniform(-0.5, 0.5, rgb.shape) / 255
    im = Image.fromarray((np.clip(rgb, 0, 1) * 255 + 0.5).astype(np.uint8))
    im.save(out)
    if save:
        np.savez_compressed(save, E=E)
    print('done', out, time.time() - t0)
    return im



def mosaic_rings(W, x0, x1, ts, probs, cols, R=0.5, seed=7, start=np.pi / 2, centre=0.06):
    """floor albedo: tesserae laid in concentric rings; ring tiles coloured by the sector whose
    angular share is probs[k] (the pie of the five probabilities, closing exactly once)."""
    rng = np.random.default_rng(seed)
    px = (x1 - x0) / W
    c = x0 + (np.arange(W) + 0.5) * px
    X, Y = np.meshgrid(c, c)
    r = np.hypot(X, Y)
    th = (np.arctan2(Y, X) - start) % (2 * np.pi)   # counter-clockwise from 'start'
    ring = np.floor((r - centre) / ts)
    rc = centre + (ring + 0.5) * ts
    ntile = np.maximum(6, np.round(2 * np.pi * rc / ts))
    off = (np.sin(ring * 12.9898) * 43758.5453) % 1.0
    u = th / (2 * np.pi) * ntile + off
    tile = np.floor(u)
    tc = ((tile + 0.5 - off) / ntile) % 1.0          # tile centre angle as a fraction of the turn
    edges = np.concatenate([[0], np.cumsum(probs)])
    edges = edges / edges[-1]
    sec = np.clip(np.searchsorted(edges, tc, side='right') - 1, 0, len(probs) - 1)
    cols = np.asarray(cols, float)
    A = cols[sec]
    # per-tile variation: lighter / deeper rows alternate, plus random jitter
    h = (np.sin(ring * 78.233 + tile * 12.9898) * 43758.5453) % 1.0
    shade = 1 + 0.035 * (h - 0.5) + 0.02 * ((ring % 2) - 0.5)
    A = A * shade[..., None]
    # centre medallion: white disc with a butter star of five petals
    inner = r < centre
    pet = 0.5 + 0.5 * np.cos(5 * (np.arctan2(Y, X) - start))
    flower = r < centre * (0.45 + 0.5 * pet ** 2)
    A[inner] = lin([0.985, 0.975, 0.955])
    A[inner & flower] = lin([1.0, 0.93, 0.70])
    A[r < centre * 0.22] = lin([1.0, 0.80, 0.70])
    # grout
    fr = (r - centre) / ts - ring
    fu = u - tile
    d = np.minimum(np.minimum(fr, 1 - fr) * ts, np.minimum(fu, 1 - fu) * 2 * np.pi * rc / ntile) / px
    d = np.where(inner, 99, d)
    gw = 0.06 * ts / px
    g = np.clip((d - gw) / (0.5 * gw + 1e-9), 0, 1)
    grout = lin([0.975, 0.965, 0.955])
    A = A * g[..., None] + grout * (1 - g[..., None])
    A *= (0.94 + 0.06 * np.clip(d / (0.2 * ts / px), 0, 1))[..., None]
    return A


if __name__ == '__main__':
    kw = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    render(**kw)
