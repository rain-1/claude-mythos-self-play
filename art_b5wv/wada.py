"""Piece C — 'To Decide' (Wada basins of three-disc chaotic scattering).

Three reflecting discs at the vertices of an equilateral triangle. A ray of
light (or a billiard particle) enters, bounces, and eventually escapes
through one of the three gaps. Colour = exit gap; brightness = dwell time
(number of bounces before escape). The three exit basins have the Wada
property: every point of any basin boundary borders ALL THREE basins.
At the place of change, all futures touch — Graham Priest's inconsistent
instant, drawn with a ray tracer.

Each pixel (x, y) launches one ray from that point aimed at the scattering
centre (plus its supersample siblings). Rays that never escape within the
bounce cap trace the chaotic saddle: they are painted white-hot.

Verification: statistical Wada check — for boundary pixels, every
epsilon-neighbourhood over a range of scales contains all three basins.
"""
import numpy as np
from scipy.ndimage import gaussian_filter
import argparse, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from artlib import filmic, bloom, ramp, save

# disc geometry: radius 1 discs, centres at distance d from origin
ANG = np.array([90.0, 210.0, 330.0]) * np.pi / 180


def trace(x0, y0, vx, vy, centers, R, max_bounce=120):
    """Vectorised three-disc pinball. Returns (exit_channel, bounces, alive).

    exit_channel in {0,1,2}: sector of the escape direction (the gap it
    leaves through, sectors centred on the gap directions 30/150/270 deg).
    alive=True marks rays still bouncing at the cap (chaotic saddle).
    """
    n = x0.size
    x = x0.copy(); y = y0.copy()
    vx = vx.copy(); vy = vy.copy()
    bounces = np.zeros(n, np.int32)
    plen = np.zeros(n, np.float32)
    done = np.zeros(n, bool)
    channel = np.full(n, -1, np.int8)
    Resc = 6.0

    idx = np.arange(n)
    for it in range(max_bounce):
        if idx.size == 0:
            break
        # nearest positive intersection with any disc
        tmin = np.full(idx.size, np.inf)
        hit_c = np.full(idx.size, -1, np.int8)
        for c in range(3):
            ox = x[idx] - centers[c, 0]
            oy = y[idx] - centers[c, 1]
            b = ox * vx[idx] + oy * vy[idx]
            disc = b * b - (ox * ox + oy * oy - R * R)
            ok = disc > 0
            sq = np.sqrt(np.where(ok, disc, 0))
            t = -b - sq
            ok &= t > 1e-9
            better = ok & (t < tmin)
            tmin[better] = t[better]
            hit_c[better] = c
        esc = hit_c < 0
        if esc.any():
            ei = idx[esc]
            th = np.arctan2(vy[ei], vx[ei])
            # gaps centred at 30, 150, 270 degrees
            channel[ei] = ((np.round((th - np.pi / 6) / (2 * np.pi / 3))
                            ).astype(np.int64) % 3).astype(np.int8)
            done[ei] = True
        keep = ~esc
        idx = idx[keep]
        if idx.size == 0:
            break
        t = tmin[keep]; hc = hit_c[keep]
        x[idx] += vx[idx] * t
        y[idx] += vy[idx] * t
        plen[idx] += t.astype(np.float32)
        # reflect at disc hc
        nx = (x[idx] - centers[hc, 0]) / R
        ny = (y[idx] - centers[hc, 1]) / R
        dot = vx[idx] * nx + vy[idx] * ny
        vx[idx] -= 2 * dot * nx
        vy[idx] -= 2 * dot * ny
        bounces[idx] += 1
    alive = ~done & (bounces >= 0)
    alive[channel >= 0] = False
    return channel, bounces, ~done, plen


def render(path, S=2560, ss=2, d=2.45, R=1.0, frame=2.9, max_bounce=120,
           k_tone=1.6, gamma=0.9, aim='swirl', chunk=4_000_000):
    W = S * ss
    centers = d * np.stack([np.cos(ANG), np.sin(ANG)], 1)

    # pixel grid → launch points; skip points inside discs
    lin = (np.arange(W) + 0.5) / W * 2 * frame - frame
    channel = np.full(W * W, -1, np.int8)
    nb = np.zeros(W * W, np.int32)
    plen_all = np.zeros(W * W, np.float32)
    saddle = np.zeros(W * W, bool)

    t0 = time.time()
    L0 = d + 1.35
    for a in range(0, W * W, chunk):
        b = min(a + chunk, W * W)
        ii = np.arange(a, b)
        px = lin[ii % W]
        py = -lin[ii // W]
        rr = np.hypot(px, py) + 1e-12
        if aim == 'chamber':
            # launch from inside the central chamber: x = point angle phi on a
            # small circle, y = absolute launch direction psi. Full torus.
            phi = (ii % W) / W * 2 * np.pi
            psi = (ii // W) / W * 2 * np.pi
            r0 = 0.55 * (d - 1.0)
            px = r0 * np.cos(phi); py = r0 * np.sin(phi)
            vx = np.cos(psi); vy = np.sin(psi)
        elif aim == 'phase':
            # phase-space chart: x = position angle phi on launch circle,
            # y = launch angle beta about the inward normal
            phi = (ii % W) / W * 2 * np.pi / 3 + np.pi / 2 - np.pi / 3
            beta = ((ii // W) / W - 0.5) * np.pi * 0.92
            px = L0 * np.cos(phi); py = L0 * np.sin(phi)
            ang = phi + np.pi + beta   # inward normal rotated by beta
            vx = np.cos(ang); vy = np.sin(ang)
        elif aim == 'center':
            vx = -px / rr; vy = -py / rr
        elif aim == 'swirl':
            # tangential launch: distinct angular momentum per pixel
            vx = -py / rr; vy = px / rr
        elif aim == 'swirl_in':
            # tangent blended with inward pull: spiralling rain of light
            ca, sa = np.cos(0.55), np.sin(0.55)
            tx, ty = -py / rr, px / rr
            nxx, nyy = -px / rr, -py / rr
            vx = ca * tx + sa * nxx; vy = ca * ty + sa * nyy
            vn = np.hypot(vx, vy); vx /= vn; vy /= vn
        # skip pixels inside a disc
        inside = np.zeros(b - a, bool)
        if aim != 'phase':
            for c in range(3):
                inside |= (px - centers[c, 0]) ** 2 + (py - centers[c, 1]) ** 2 < R * R
        ch, bo, al, pl = trace(px, py, vx, vy, centers, R, max_bounce)
        ch[inside] = -2
        channel[a:b] = ch
        nb[a:b] = bo
        plen_all[a:b] = pl
        saddle[a:b] = al & ~inside
        print(f'  traced {b}/{W*W} ({time.time()-t0:.0f}s)', flush=True)

    channel = channel.reshape(W, W)
    nb = nb.reshape(W, W).astype(np.float32)
    plen_all = plen_all.reshape(W, W)
    saddle = saddle.reshape(W, W)

    # --- Wada statistical check at render resolution
    basins = channel.copy()
    interior_px = (basins == -2)
    from scipy.ndimage import binary_erosion
    edge = np.zeros_like(saddle)
    for c in range(3):
        m = basins == c
        edge |= m & ~binary_erosion(m, iterations=2, border_value=1)
    # sample boundary pixels, check eps-balls contain all 3 basins
    rng = np.random.default_rng(0)
    ys, xs = np.where(edge)
    take = rng.choice(ys.size, size=min(4000, ys.size), replace=False)
    radii = [4, 8, 16, 32]
    wada_frac = []
    for rad in radii:
        okc = 0
        for i in take[:800]:
            yy0, xx0 = ys[i], xs[i]
            sl = basins[max(0, yy0 - rad):yy0 + rad + 1,
                        max(0, xx0 - rad):xx0 + rad + 1]
            if all(((sl == c).any()) for c in range(3)):
                okc += 1
        wada_frac.append(okc / 800)
    print('Wada check (fraction of boundary pixels whose eps-ball sees all 3 basins):')
    for rad, f in zip(radii, wada_frac):
        print(f'   eps = {rad}px: {f:.3f}')

    # --- colour composition
    # three basin hues (dark interiors, boundary filigree glows by dwell time)
    base = np.array([[0.98, 0.62, 0.12],    # gap 0 (right-up): amber
                     [0.16, 0.75, 0.72],    # gap 1 (left):     teal
                     [0.72, 0.30, 0.85]])   # gap 2 (down):     violet
    lp = np.log1p(plen_all / 3.0)
    lo = np.percentile(lp, 8); hi = np.percentile(lp, 99.85)
    dwell = np.clip((lp - lo) / max(hi - lo, 1e-9), 0, 1.0) ** 1.35
    # blend toward white where dwell is extreme (the chaotic saddle's skirt)
    wmix = np.clip((dwell - 0.72) / 0.28, 0, 1) ** 2
    rgb = np.zeros((W, W, 3), np.float32)
    for c in range(3):
        m = channel == c
        for k in range(3):
            colk = base[c, k] * (1 - wmix) + 1.0 * wmix
            rgb[..., k] += m * colk * (0.06 + 1.55 * dwell)
    # chaotic saddle: white-hot
    sad = gaussian_filter(saddle.astype(np.float32), 0.8 * ss)
    for k, tint in enumerate((1.0, 0.97, 0.90)):
        rgb[..., k] += sad * 2.6 * tint
    # disc interiors: near-black steel with a faint edge light
    disc_m = interior_px.astype(np.float32)
    edge_glow = gaussian_filter((nb > 0).astype(np.float32), 2.5 * ss)
    for k, tint in enumerate((0.055, 0.065, 0.085)):
        rgb[..., k] = np.where(interior_px, tint + 0.10 * edge_glow, rgb[..., k])

    rgb = filmic(rgb, k=k_tone, gamma=gamma)
    rgb = bloom(rgb, mask_lo=0.60, sigma=5 * ss, gain=0.55, tint=(1, 0.95, 0.85))
    save(rgb, path, down=ss)
    return wada_frac


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='variants/wada_proto.png')
    ap.add_argument('--size', type=int, default=1280)
    ap.add_argument('--ss', type=int, default=2)
    ap.add_argument('--d', type=float, default=2.45)
    ap.add_argument('--frame', type=float, default=2.9)
    ap.add_argument('--maxb', type=int, default=120)
    ap.add_argument('--aim', default='swirl')
    ap.add_argument('--ktone', type=float, default=1.0)
    args = ap.parse_args()
    render(args.out, S=args.size, ss=args.ss, d=args.d, frame=args.frame,
           max_bounce=args.maxb, k_tone=args.ktone, aim=args.aim)
