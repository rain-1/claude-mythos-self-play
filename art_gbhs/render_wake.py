"""render_wake.py — 'The Angle Every Boat Shares' : the Kelvin ship-wave pattern in pastel.

Crests warm (apricot -> blush as the wave turns from transverse to diverging), troughs cool
(aqua -> cornflower), density = wave amplitude with a soft knee; Kelvin's closed-form crest
curves ride the ridges as thin ink (one fitted phase per branch); coral beads at the cusps of
the crest curves, which lie on the two straight lines at arcsin(1/3) from the course.
"""
import numpy as np, sys, json, time
from scipy.ndimage import map_coordinates, gaussian_filter, zoom
sys.path.insert(0, '.')
import wake
from pastel import Sheet, PIG, polyline_density, discs_density, text_density, text_width, finish


def fit_branch(eta, x0, y0, dx, mask_fn, nmin=3, nmax=30, nt=500):
    t = np.linspace(-1.25, 1.25, nt)
    tm = t[mask_fn(t)]
    best = None
    for c in np.linspace(0, 2 * np.pi, 240, endpoint=False):
        s = 0.0; w = 0
        for n in range(nmin, nmax + 1):
            xw, yw = wake.crest_curve(2 * np.pi * n - c, tm)
            col, row = wake.to_grid(xw, yw, x0, y0, 0.0, dx, dx)
            v = wake.sample(eta, col, row); s += v.sum(); w += len(v)
        if best is None or s / w > best[1]:
            best = (c, s / w)
    c = best[0]
    rms = 0.0; cnt = 0
    for n in range(nmin, nmax + 1):
        for sh in np.linspace(-np.pi, np.pi, 24, endpoint=False):
            xw, yw = wake.crest_curve(2 * np.pi * n - c + sh, tm)
            col, row = wake.to_grid(xw, yw, x0, y0, 0.0, dx, dx)
            v = wake.sample(eta, col, row); rms += (v ** 2).sum(); cnt += len(v)
    return c, best[1] / np.sqrt(rms / cnt)


def render(FINAL=1024, SS=2, a=1.0, mu=0.012, L=230.0, alpha_deg=27.0, src=(0.10, 0.17),
           tag='wake', caption=True, gain_pow=0.35, ink_on=True, nfield=None, variant='dir', dens_amp=2.1, knee=1.0, ink_every=3, boats=None, body=0.0):
    """L = wave-units across the canvas width; alpha_deg = heading of the wake on the canvas
    (negative = trailing down-right, image y down); src = source position (fractions of canvas)."""
    t0 = time.time()
    W = H = FINAL * SS
    rs = FINAL / 1024.0 * SS
    # ---- field on a long axis-aligned box, resolution = canvas px (before supersampling)
    nf = nfield or FINAL
    dx = L / nf                                    # wave units per canvas pixel (pre-SS)
    Lx = 3.2 * L; Ly = 1.6 * L
    Nx = int(round(Lx / dx)); Ny = int(round(Ly / dx))
    eta, (x0, y0) = wake.solve(Nx, Lx, a=a, mu=mu, src=(0.08, 0.5), Ny=Ny, Ly=Ly)
    print(f'field {Nx}x{Ny} ({time.time()-t0:.1f}s) |eta|max {np.abs(eta).max():.3g}')
    # ---- certificates on the axis-aligned field
    psis, prof = wake.angle_profile(eta, x0, y0, 0.0, dx, dx, 0.35 * L, 0.9 * L)
    peak, edge, sm = wake.wedge_from_profile(psis, prof)
    tc = np.arctan(1 / np.sqrt(2))
    cT, kT = fit_branch(eta, x0, y0, dx, lambda t: np.abs(t) < tc)
    cD, kD = fit_branch(eta, x0, y0, dx, lambda t: (np.abs(t) > tc) & (np.abs(t) < 0.95))
    cert = dict(a=a, Fr=float(1 / np.sqrt(a)), mu=mu, L=L, Nx=Nx, Ny=Ny,
                peak_angle_deg=float(peak), half_amplitude_edge_deg=float(edge),
                kelvin_deg=float(wake.KELVIN_DEG),
                rms_at=dict((str(p), float(np.interp(p, psis, prof))) for p in (0, 10, 15, 19.47, 22, 25, 30)),
                phase_transverse=float(cT), contrast_transverse=float(kT),
                phase_diverging=float(cD), contrast_diverging=float(kD))
    print(json.dumps(cert, indent=1))
    # ---- sample the field onto the rotated canvas (SS resolution), one boat per (scale, pos, amp)
    al = np.radians(alpha_deg)
    if boats is None:
        boats = [(1.0, src[0], src[1], 1.0)]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    field = np.zeros((H, W), np.float32)
    for (sc, bx, by, bamp) in boats:
        sx, sy = bx * W, by * H
        px = (xx - sx) / SS; py = (yy - sy) / SS
        uu = (px * np.cos(al) + py * np.sin(al)) / sc
        vv = (-px * np.sin(al) + py * np.cos(al)) / sc
        col = x0 / dx + uu; row = y0 / dx + vv
        fb = map_coordinates(eta, [row, col], order=3, mode='constant', cval=0.0).astype(np.float32)
        gain_b = np.clip(uu / (0.25 * L / dx), 0.3, None) ** gain_pow
        field += bamp * fb * gain_b
        if sc == boats[0][0]:
            u, v = uu, vv
        del px, py, uu, vv, col, row, fb, gain_b
    del xx, yy
    sx, sy = boats[0][1] * W, boats[0][2] * H
    # local wave direction (for the transverse/diverging pigment split)
    gy, gx = np.gradient(gaussian_filter(field, 1.0 * rs))
    gu = gx * np.cos(al) + gy * np.sin(al); gv = -gx * np.sin(al) + gy * np.cos(al)
    theta = np.abs(np.arctan2(gv, gu)); theta = np.minimum(theta, np.pi - theta)   # 0..pi/2
    del gx, gy, gu, gv
    dirw = np.clip((theta - 0.25) / 0.75, 0, 1).astype(np.float32)   # 0 transverse .. 1 diverging
    del theta
    # ---- density: amplitude with a mild downstream gain (the honest x^-1/2 decay, softened)
    far = (u > 0.25 * L / dx) & (u < 0.9 * L / dx) & (np.abs(v) < u * np.tan(np.radians(19.6)))
    s = np.percentile(np.abs(field[far]), 96) if far.any() else np.abs(field).max()
    amp = np.abs(field) / s
    dens = dens_amp * np.tanh(amp * knee).astype(np.float32)
    del amp
    # fade at the upstream side of the source (the pressure patch itself is not a wave)
    near = np.exp(-np.maximum(0, -u) ** 2 / (2 * (0.6 * a / dx) ** 2 + 1e-9))
    pos = field > 0
    sheet = Sheet(W, H, seed=7)
    if variant == 'dir':
        pigs = [('apricot', pos, 1 - dirw), ('blush', pos, dirw), ('aqua', ~pos, 1 - dirw), ('cornflower', ~pos, dirw)]
    else:
        pigs = [('apricot', pos, 1.0), ('cornflower', ~pos, 1.0)]
    for i, (name, m, wgt) in enumerate(pigs):
        d = dens * m * wgt
        sheet.wash(d, name, granulate=0.25, seed=21 + i)
    del dens, dirw
    if body > 0:
        env = gaussian_filter(np.abs(field) / s, 4 * rs)
        sheet.wash(np.clip(env * 1.5, 0, 1).astype(np.float32) * body, 'mint', granulate=0.3, seed=5)
        del env
    # ---- ink: Kelvin's crest curves, per branch with its fitted phase; coral cusp beads + lines
    alive_all = np.clip(gaussian_filter(np.abs(field) / s, 3 * rs) * 2.2, 0, 1)
    ink = np.zeros((H, W), np.float32); beads = np.zeros((H, W), np.float32); line = np.zeros((H, W), np.float32)
    for (sc, bx, by, bamp) in boats:
      sx, sy = bx * W, by * H
      def to_canvas(xw, yw, sc=sc, sx=sx, sy=sy):
        X = sx + SS * sc * (xw * np.cos(al) - yw * np.sin(al)) / dx
        Y = sy + SS * sc * (xw * np.sin(al) + yw * np.cos(al)) / dx
        return np.stack([X, Y], 1)
      if ink_on:
        tt = np.linspace(-1.3, 1.3, 900)
        nmax = int(0.95 * 1.6 * L / (2 * np.pi))
        for n in range(1, nmax + 1):
            if n % max(ink_every, int(round(ink_every / sc))): continue
            for c, msk, wt in ((cT, np.abs(tt) < tc, 0.6), (cD, (np.abs(tt) > tc) & (np.abs(tt) < 1.0), 0.8)):
                A = 2 * np.pi * n - c
                if A <= 0: continue
                for sign in (1, -1):
                    sel = msk & (sign * tt >= 0)
                    xw, yw = wake.crest_curve(A, tt[sel])
                    keep = (xw < 1.6 * L) & (xw > 0)
                    if keep.sum() < 3: continue
                    ink += polyline_density(W, H, to_canvas(xw[keep], yw[keep]), 0.9 * rs * sc ** 0.3, weight=wt * sc ** 0.5)
      xs, ys, rr, ws = [], [], [], []
      nmax = int(0.95 * 1.6 * L / (2 * np.pi))
      for n in range(1, nmax + 1):
        A = 2 * np.pi * n - cD
        for sign in (1, -1):
            xw, yw = wake.crest_curve(A, sign * tc)
            if xw > 1.6 * L or xw <= 0: continue
            p = to_canvas(np.array([xw]), np.array([yw]))[0]
            if 0 <= p[0] < W and 0 <= p[1] < H:
                xs.append(p[0]); ys.append(p[1]); rr.append(2.2 * rs * sc ** 0.5); ws.append(1.0)
      beads += discs_density(W, H, xs, ys, rr, ws, sigma=0.5 * rs)
      for sign in (1, -1):
        xw = np.linspace(0, 1.6 * L, 400); yw = sign * xw * np.tan(np.radians(wake.KELVIN_DEG))
        line += polyline_density(W, H, to_canvas(xw, yw), 0.7 * rs, weight=sc ** 0.5)
    ink = np.clip(gaussian_filter(ink, 0.45 * rs), 0, 1)
    sheet.wash(ink * 0.62 * alive_all, 'ink')
    alive = np.clip(alive_all * 1.4, 0.15, 1)
    sheet.wash(np.clip(beads, 0, 1) * 1.4 * alive, 'coral')
    line = gaussian_filter(line, 0.5 * rs)
    sheet.wash(line * 0.45 * alive, 'coral')
    del line, beads, alive, alive_all, ink, field
    # ---- caption
    if caption:
        sheet.caption_strip(0.905, 0.985, f=0.55)
        title = 'The Angle Every Boat Shares'
        sub = (f'Three boats, three speeds, one wedge: arcsin(1/3) = 19.47°. Linear deep-water theory, one Fourier transform; '
               f'the wedge is measured from the field ({edge:.1f}° at half amplitude), never drawn.')
        items = [(title, 0.045 * W, 0.925 * H, 0.030 * H, 'serif_bold', 'ls'),
                 (sub, 0.045 * W, 0.962 * H, 0.0135 * H, 'italic', 'ls')]
        sheet.wash(text_density(W, H, items) * 1.9, 'ink')
    img = sheet.develop()
    out = f'{tag}_{FINAL}.png'
    finish(img, (FINAL, FINAL), out)
    json.dump(cert, open(f'{tag}_{FINAL}_cert.json', 'w'), indent=1)
    print(f'done {time.time()-t0:.0f}s')
    return cert


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--final', type=int, default=1024)
    ap.add_argument('--ss', type=int, default=2)
    ap.add_argument('--a', type=float, default=1.0)
    ap.add_argument('--mu', type=float, default=0.02)
    ap.add_argument('--L', type=float, default=240.0)
    ap.add_argument('--alpha', type=float, default=27.0)
    ap.add_argument('--dens', type=float, default=2.1)
    ap.add_argument('--knee', type=float, default=1.0)
    ap.add_argument('--inkevery', type=int, default=3)
    ap.add_argument('--srcx', type=float, default=0.10)
    ap.add_argument('--srcy', type=float, default=0.17)
    ap.add_argument('--boats', default='')
    ap.add_argument('--body', type=float, default=0.0)
    ap.add_argument('--tag', default='proto_wake')
    ap.add_argument('--variant', default='dir')
    ap.add_argument('--noink', action='store_true')
    ap.add_argument('--nocap', action='store_true')
    ap.add_argument('--gain', type=float, default=0.35)
    ap.add_argument('--nfield', type=int, default=None)
    args = ap.parse_args()
    render(FINAL=args.final, SS=args.ss, a=args.a, mu=args.mu, L=args.L, alpha_deg=args.alpha,
           tag=args.tag, variant=args.variant, ink_on=not args.noink, caption=not args.nocap,
           gain_pow=args.gain, nfield=args.nfield, dens_amp=args.dens, knee=args.knee, ink_every=args.inkevery, src=(args.srcx, args.srcy), body=args.body,
           boats=[tuple(map(float, b.split(','))) for b in args.boats.split(';')] if args.boats else None)
