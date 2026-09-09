"""render_siegel.py — 'What Zero Draws': the golden-mean Siegel disk of z^2 + c in pastel.

Inside the disk: invariant curves (orbits of points on the segment from the fixed point toward 0),
pigment by conformal position (warm at the centre, cool at the rim).  Their preimages fill the
rest of the filled Julia set with smaller and smaller copies (constant mass per level, so the
small ones are darker: the pull-back of the same measure).  Outside: equipotential bands and
external rays in ink.  Coral: the orbit of the critical point 0 — its closure IS the boundary
of the disk (Douady–Herman: the boundary is a quasicircle through 0).
"""
import numpy as np, sys, json, time
from scipy.ndimage import gaussian_filter, distance_transform_edt
sys.path.insert(0, '.')
import siegel as sg
from pastel import Sheet, PIG, polyline_density, discs_density, text_density, ink_from_distance, finish, text_width

RAMP = ['apricot', 'lemon', 'pistachio', 'mint', 'aqua', 'cornflower', 'lavender', 'orchid', 'blush']


def render(FINAL=1024, SS=2, tag='proto_siegel', caption=True, n_curves=26, n_orb=None, levels=9, n_rays=48,
           fill=0.72, curve_d=3.0, sat_d=1.0, band_d=0.24, body_d=0.22, gran=0.14, ray_w=0.55, ray_d=0.75,
           crit_n=4000, t_min=0.06, t_pow=0.55, blur=0.6, ctr=None, band_per=2.0, w_ramp=(0.55, 1.25),
           blur_abs=False, edge_d=0.75, edge_w=0.8):
    t0 = time.time()
    W = H = FINAL * SS
    rs = FINAL / 1024.0 * SS
    th, lam, c, z0 = sg.params()
    cert = dict(theta=th, c=[c.real, c.imag], z0=[z0.real, z0.imag], multiplier_abs=float(abs(2 * z0)))
    if n_orb is None:
        n_orb = int(60000 * (W / 2048))
    # ---- frame from the filled Julia set at coarse resolution
    g = 400
    xs = np.linspace(-1.8, 1.8, g); X, Y = np.meshgrid(xs, xs)
    Gc = sg.green(X + 1j * Y, c, nmax=300)
    m = Gc == 0
    ys_, xs_ = np.nonzero(m)
    x0, x1 = xs[xs_.min()], xs[xs_.max()]; y0, y1 = xs[ys_.min()], xs[ys_.max()]
    if ctr is None:
        ctr = ((x0 + x1) / 2, (y0 + y1) / 2)
    ext = max(x1 - x0, y1 - y0)
    S = fill * W / ext
    cx, cy = 0.5 * W, 0.5 * H

    def xf(z):
        return cx + S * (z.real - ctr[0]), cy - S * (z.imag - ctr[1])

    # ---- Green's function on the full canvas (float32 grid, chunked)
    G = np.zeros((H, W), np.float32)
    xx = (np.arange(W) - cx) / S + ctr[0]
    for r0 in range(0, H, 256):
        r1 = min(H, r0 + 256)
        yy = ctr[1] - (np.arange(r0, r1) - cy) / S
        Z = xx[None, :] + 1j * yy[:, None]
        G[r0:r1] = sg.green(Z, c, nmax=500).astype(np.float32)
    inside = G == 0
    print(f'green {time.time()-t0:.0f}s, K fraction {inside.mean():.3f}')
    sheet = Sheet(W, H, seed=31)
    # ---- equipotential bands (one band per halving of G), fading far away
    lg = np.log2(np.maximum(G, 1e-30))
    band = 0.5 + 0.5 * np.cos(2 * np.pi * lg / band_per)
    band = gaussian_filter(band.astype(np.float32), 1.0 * rs)
    far = np.exp(-np.maximum(G, 0) / 0.25)
    sheet.wash(band_d * band * far * (~inside), 'lavender', granulate=gran, seed=61)
    # ---- body of K
    sheet.wash(body_d * gaussian_filter(inside.astype(np.float32), 1.0 * rs), 'paperpink', granulate=gran, seed=62)
    # ---- invariant curves: orbits of points on the segment z0 -> 0
    ts = t_min + (1 - t_min - 1e-3) * ((np.arange(n_curves) + 0.5) / n_curves) ** t_pow
    starts = z0 + ts * (0 - z0)
    O = sg.orbit(starts, c, n_orb)                   # (n_orb, n_curves)
    cert.update(n_curves=n_curves, n_orbit=n_orb, orbit_max_abs=float(np.abs(O).max()))
    # certificate: orbits stay away from the fixed point and from 0 in a t-ordered way (no crossing):
    rmin = np.abs(O - z0).min(0); rmax = np.abs(O - z0).max(0)
    cert.update(orbit_dist_to_z0_min=[float(x) for x in rmin], orbit_dist_to_z0_max=[float(x) for x in rmax],
                curves_nested=bool((rmax[:-1] < rmax[1:]).all()))
    # ---- pigment per curve
    pig_idx = (np.arange(n_curves) / max(1, n_curves - 1)) * (len(RAMP) - 1)
    acc = {p: np.zeros(H * W, np.float32) for p in RAMP}

    def splat(pts, cid, weight):
        x, y = xf(pts)
        ok = (x >= 0) & (x < W) & (y >= 0) & (y < H)
        idx = (np.floor(y[ok]).astype(np.int64) * W + np.floor(x[ok]).astype(np.int64))
        i0 = int(np.floor(pig_idx[cid])); tt = pig_idx[cid] - i0
        i1 = min(i0 + 1, len(RAMP) - 1)
        acc[RAMP[i0]] += np.bincount(idx, minlength=H * W).astype(np.float32) * weight * (1 - tt)
        if tt > 0:
            acc[RAMP[i1]] += np.bincount(idx, minlength=H * W).astype(np.float32) * weight * tt

    # mass normalisation: a curve of length L px with n_orb points -> n_orb/L points per px
    for ci in range(n_curves):
        P = O[:, ci]
        x, y = xf(P)
        Lpx = 2 * np.pi * np.abs(rmax[ci] + rmin[ci]) / 2 * S      # rough perimeter
        wgt = curve_d * Lpx / n_orb * (w_ramp[0] + (w_ramp[1] - w_ramp[0]) * ci / max(1, n_curves - 1))
        splat(P, ci, wgt)
        # preimages: subsample by 2 per level; constant total mass per level
        for k in range(1, levels + 1):
            sub = P[::2 ** k] if 2 ** k < n_orb else P[:8]
            PB = sg.pullback(sub, c, k)[-1]
            splat(PB, ci, sat_d * wgt)
    print(f'curves {time.time()-t0:.0f}s')
    for p in RAMP:
        d = acc[p].reshape(H, W)
        d = gaussian_filter(d, blur if blur_abs else blur * rs)
        d = 1.6 * np.tanh(d / 1.0)
        sheet.wash(d, p, granulate=gran * 0.5, seed=70 + RAMP.index(p))
    # ---- external rays
    ang = (np.arange(n_rays) + 0.5) / n_rays
    Rp = sg.rays(ang, c, R0=1e3, depth=40, sub=6)      # (levels, rays)
    ink = np.zeros((H, W), np.float32)
    n_bad = 0
    for j in range(n_rays):
        P = Rp[:, j]
        # keep the part inside the frame; drop if the ray jumped (large step late)
        stp = np.abs(np.diff(P))
        if (stp[-60:] > 0.05).any():
            n_bad += 1
        px = np.stack(xf(P), 1)
        ink += polyline_density(W, H, px, ray_w * rs)
    cert.update(n_rays=n_rays, rays_with_late_jumps=int(n_bad), ray_end_G=float(np.log(1e3) / 2 ** 40))
    ink = gaussian_filter(np.clip(ink, 0, 1), 0.4 * rs)
    sheet.wash(ink * ray_d, 'ink')
    # ---- Julia set outline in ink (EDT of K)
    d_in = distance_transform_edt(inside); d_out = distance_transform_edt(~inside)
    edge = ink_from_distance(np.where(inside, d_in, d_out) - 0.5, edge_w * rs)
    sheet.wash(edge * edge_d, 'ink')
    # ---- critical orbit in coral: the boundary of the disk is its closure
    C = sg.orbit(np.array([0j]), c, crit_n)[:, 0]
    x, y = xf(C)
    beads = discs_density(W, H, x, y, [1.1 * rs] * len(x), [1.0] * len(x), sigma=0.45 * rs)
    sheet.wash(np.clip(beads, 0, 1) * 1.3, 'coral')
    x0_, y0_ = xf(np.array([0j]))
    sheet.wash(discs_density(W, H, x0_, y0_, [3.0 * rs], [1.0], sigma=0.6 * rs) * 1.5, 'coral')
    # the fixed point: a small ink dot
    xz, yz = xf(np.array([z0]))
    sheet.wash(discs_density(W, H, xz, yz, [1.6 * rs], [1.0], sigma=0.5 * rs) * 1.2, 'ink')
    cert.update(critical_orbit_n=crit_n, critical_orbit_max_abs=float(np.abs(C).max()),
                critical_orbit_min_dist_to_z0=float(np.abs(C - z0).min()),
                innermost_curve_max_dist=float(rmax[0]), outermost_curve_max_dist=float(rmax[-1]))
    if caption:
        sheet.caption_strip(0.905, 0.985, f=0.55)
        title = 'What Zero Draws'
        sub = ("z -> z^2 + c at the golden rotation: every point inside turns forever on its own curve. "
               "Coral: the orbit of zero, whose closure is the rim. Outside: the potential and its rays.")
        fs = 0.0135 * H
        fs = min(fs, fs * 0.90 * W / max(1, text_width(sub, fs, 'italic')))
        items = [(title, 0.045 * W, 0.925 * H, 0.030 * H, 'serif_bold', 'ls'),
                 (sub, 0.045 * W, 0.962 * H, fs, 'italic', 'ls')]
        sheet.wash(text_density(W, H, items) * 1.9, 'ink')
    img = sheet.develop()
    finish(img, (FINAL, FINAL), f'{tag}_{FINAL}.png')
    json.dump(cert, open(f'{tag}_{FINAL}_cert.json', 'w'), indent=1)
    print(f'done {time.time()-t0:.0f}s')
    return cert


if __name__ == '__main__':
    kw = {}
    for a in sys.argv[1:]:
        k, val = a.split('=', 1)
        try:
            val = eval(val)
        except Exception:
            pass
        kw[k] = val
    render(**kw)
