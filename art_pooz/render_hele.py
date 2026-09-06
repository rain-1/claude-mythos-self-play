"""render_hele.py — 'The Fluid Leaves Before the Model Does' : Hele-Shaw suction to the cusp.

Nested tinted strips = the fluid removed in each time slice (warm early → cool late),
thin ink on the strip rims, coral on the boundary at the cusp instant, a pale wash on
the fluid that is still there when the theory ends, faint ink for the non-univalent
continuation of the same equations (what the map says after the fluid can no longer follow).
"""
import numpy as np, sys, json, time
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter
sys.path.insert(0, '.')
import hele
from pastel import Sheet, PIG, CYCLE, absorb, polyline_density, text_density, finish, ink_from_distance

def build(seed=27, K=7, Q=-1.0, dt=0.002, ghost=0.09):
    rng = np.random.default_rng(seed)
    a0 = np.zeros(K, complex); a0[0] = 1
    for k in range(2, K + 1):
        a0[k - 1] = rng.uniform(0.02, 0.16) / k * np.exp(1j * rng.uniform(0, 2 * np.pi))
    out, tc, resid = hele.integrate(a0, Q=Q, dt=dt, ghost=ghost)
    return a0, out, tc, resid

def render(FINAL=2560, SS=2, seed=27, nstrips=28, fine=10, tag='hele', caption=True):
    t0 = time.time()
    a0, out, tc, resid = build(seed=seed)
    ts = np.array([t for t, a in out])
    ic = int(np.argmin(np.abs(ts - tc)))          # index of the cusp state
    print(f'cusp t={tc:.5f}, removed {1-hele.area(out[ic][1])/hele.area(a0):.3f}, PG resid {resid:.1e}')
    # Richardson moment certificate
    M0 = hele.moments(a0, 6); Mc = hele.moments(out[ic][1], 6)
    drift = np.abs(Mc[1:] - M0[1:]).max()
    area_err = abs(hele.area(out[ic][1]) - (hele.area(a0) - tc)) if False else abs(hele.area(out[ic][1]) - (hele.area(a0) + (-1.0) * tc))
    print(f'moment drift {drift:.2e}, area law error {area_err:.2e}')
    W = H = FINAL * SS
    rs = FINAL / 1024.0 * SS      # stroke scale: every width/radius in units of the 1024-proto pixel
    K = len(a0); ks = np.arange(1, K + 1)
    # geometry: fit initial shape
    b0 = hele.boundary(a0, 4096)
    rad = np.abs(b0).max()
    scale = 0.40 * W / rad
    cx, cy = W * 0.5, H * 0.455
    def to_px(z):
        return np.stack([cx + scale * z.real, cy - scale * z.imag], 1)
    # fine survival-count field: number of Ω(t_j) (t_j ≤ tc, fine sampling) containing the pixel
    nf = nstrips * fine
    tf = np.linspace(0, tc, nf + 1)
    cnt = np.zeros((H, W), np.float32)
    for j, t in enumerate(tf):
        k = int(np.argmin(np.abs(ts - t)))
        b = hele.boundary(out[k][1], 3000)
        im = Image.new('L', (W, H), 0)
        ImageDraw.Draw(im).polygon([tuple(p) for p in to_px(b)], fill=255)
        cnt += (np.asarray(im, np.float32) > 0)
        if j % 50 == 0: print(f'  mask {j}/{nf}  {time.time()-t0:.0f}s', flush=True)
    # cnt in 0..nf+1 ; interior (still fluid at tc) = nf+1
    Lf = np.clip(cnt - 1, 0, nf) / fine            # continuous layer coordinate 0..nstrips (nstrips = interior)
    strip = np.floor(Lf).astype(int)
    frac = Lf - strip
    inside0 = cnt > 0
    interior = cnt >= nf + 1
    band = inside0 & ~interior
    sheet = Sheet(W, H, seed=seed)
    # pigment ramp warm -> cool over the strips
    ramp = ['lemon', 'apricot', 'blush', 'orchid', 'lavender', 'cornflower', 'aqua']
    pos = np.clip(Lf / nstrips, 0, 0.999) * (len(ramp) - 1)
    i0 = np.floor(pos).astype(int); tmix = (pos - i0).astype(np.float32); i1 = np.minimum(i0 + 1, len(ramp) - 1)
    # pooling toward the inner rim of each strip (pigment gathers where the wash stops)
    pool = (0.50 + 0.95 * frac ** 2.0).astype(np.float32)
    base = 1.6
    dens = np.where(band, base * pool, 0).astype(np.float32)
    # slight fading of the outermost strips (the edge of the paper's attention)
    dens *= (0.75 + 0.25 * np.clip(Lf / 6, 0, 1))
    for i, name in enumerate(ramp):
        w = np.where(i0 == i, 1 - tmix, 0) + np.where(i1 == i, tmix, 0)
        d = dens * w
        if d.max() > 0:
            sheet.wash(d, name, granulate=0.22, seed=11 + i)
    del dens
    # interior: the fluid the theory can no longer describe — pale mint wash with grain
    sheet.wash(interior.astype(np.float32) * 0.34, 'mint', granulate=0.40, edge=0.0, seed=41)
    # strip rims in ink
    inkw = 1.1 * rs
    rim = np.zeros((H, W), np.float32)
    for j in range(nstrips + 1):
        t = tc * j / nstrips
        k = int(np.argmin(np.abs(ts - t)))
        b = hele.boundary(out[k][1], 3000)
        wt = 0.42 if j % 4 else 0.7
        rim += polyline_density(W, H, to_px(b), inkw, weight=wt, closed=True)
    rim = np.clip(gaussian_filter(rim, 0.6 * rs), 0, 1)
    sheet.wash(rim * 0.85, 'ink')
    # the cusp instant in coral, twice
    bc = hele.boundary(out[ic][1], 6000)
    cusp_line = polyline_density(W, H, to_px(bc), 2.6 * rs, weight=1.0, closed=True)
    cusp_line = gaussian_filter(cusp_line, 0.7 * rs)
    sheet.wash(cusp_line * 1.5, 'coral')
    # ghost continuation past the cusp (non-univalent): faint ink, denser near tc
    gh = np.zeros((H, W), np.float32)
    tg = [t for t, a in out if t > tc + 1e-9]
    if tg:
        sel = np.linspace(0, len(tg) - 1, 14).astype(int)
        for si, s in enumerate(sel):
            k = ic + 1 + s
            b = hele.boundary(out[k][1], 4000)
            gh += polyline_density(W, H, to_px(b), 1.0 * rs, weight=0.7 - 0.5 * si / len(sel), closed=True)
        gh = np.clip(gaussian_filter(gh, 0.6 * rs), 0, 1)
        sheet.wash(gh * 0.6, 'ink')
    # streamlines of the flow at the cusp instant: images of the radii of the disc under f(·,t_c)
    # (pressure p ∝ log|ζ|, so fluid moves along these; speed ∝ 1/|f'(ζ)| — infinite at a cusp)
    from pastel import draw_lines_density
    ac = out[ic][1]
    nray, nr = 120, 160
    rr_ = np.linspace(0.045, 0.9985, nr + 1)
    segs, wts = [], []
    for j in range(nray):
        ph = 2 * np.pi * (j + 0.5) / nray
        zeta = rr_ * np.exp(1j * ph)
        pts = to_px(np.sum(ac[None, :] * zeta[:, None] ** ks[None, :], axis=1))
        fp = np.abs(np.sum((ks * ac)[None, :] * zeta[:, None] ** (ks - 1)[None, :], axis=1))
        speed = 1.0 / np.maximum(fp, 1e-3)
        w = 0.30 + 0.70 * np.clip((speed - 0.9) / 2.5, 0, 1) ** 0.7      # brighter where the fluid races
        w *= np.clip((rr_ - 0.045) / 0.25, 0, 1) ** 0.7                    # fade into the sink
        for i in range(nr):
            segs.append([pts[i, 0], pts[i, 1], pts[i + 1, 0], pts[i + 1, 1]]); wts.append(w[i])
    web = draw_lines_density(W, H, np.array(segs), 1.15 * rs, weights=np.array(wts))
    web = np.clip(gaussian_filter(web, 0.55 * rs), 0, 1) * interior
    sheet.wash(web * 0.95, 'ink')
    # equipotentials (images of circles) — a few, fainter
    eq = np.zeros((H, W), np.float32)
    for r_ in [0.25, 0.4, 0.55, 0.7, 0.85]:
        zeta = r_ * np.exp(1j * np.linspace(0, 2 * np.pi, 1500))
        pts = to_px(np.sum(ac[None, :] * zeta[:, None] ** ks[None, :], axis=1))
        eq += polyline_density(W, H, pts, 1.0 * rs, weight=0.5, closed=True)
    sheet.wash(np.clip(gaussian_filter(eq, 0.5 * rs), 0, 1) * 0.7, 'ink')
    # the sink
    yy, xx = np.ogrid[:H, :W]
    r = np.hypot(xx - cx, yy - cy)
    sheet.wash(np.exp(-(r / (5 * rs)) ** 2).astype(np.float32) * 1.4, 'coral')
    sheet.wash(np.clip(1 - np.abs(r - 11 * rs) / (1.4 * rs), 0, 1).astype(np.float32) * 0.9, 'ink')
    # cusp points: small coral beads at f(root) for the roots of f' on the circle
    rts = hele.fprime_roots(out[ic][1])
    ncusp = 0
    for z in rts:
        if abs(abs(z) - 1) < 0.02:
            zc = z / abs(z)
            p = np.sum(out[ic][1] * zc ** ks)
            px = to_px(np.array([p]))[0]
            rr = np.hypot(xx - px[0], yy - px[1])
            sheet.wash(np.clip(1 - np.abs(rr - 16 * rs) / (1.8 * rs), 0, 1).astype(np.float32) * 1.3, 'coral')
            ncusp += 1
    if caption:
        sheet.caption_strip(0.900, 0.985, 0.5)
        ts_ = 0.030 * W; is_ = 0.0125 * W
        items = [('The Fluid Leaves Before the Model Does', W * 0.5, H * 0.922, ts_, 'serif_bold', 'mm'),
                 (f'Hele-Shaw suction with no surface tension, one sink: each strip is the fluid removed in one slice of time. The rim sharpens into {ncusp} cusps '
                  f'after only {100*(1-hele.area(out[ic][1])/hele.area(a0)):.0f}% has left.', W * 0.5, H * 0.952, is_, 'italic', 'mm'),
                 ('Coral: the instant the equations stop describing anything.  Faint ink: what they go on to say.', W * 0.5, H * 0.971, is_, 'italic', 'mm')]
        sheet.wash(text_density(W, H, items) * 1.9, 'ink')
    img = sheet.develop()
    finish(img, (FINAL, FINAL), f'{tag}_{FINAL}.png')
    cert = dict(seed=seed, K=K, a0=[[float(c.real), float(c.imag)] for c in a0], Q=-1.0, cusp_time=float(tc),
                area0=float(hele.area(a0)), area_cusp=float(hele.area(out[ic][1])),
                fraction_removed=float(1 - hele.area(out[ic][1]) / hele.area(a0)),
                richardson_moment_drift_max=float(drift), area_law_error=float(area_err), PG_residual=float(resid),
                fprime_roots_abs_at_cusp=[float(abs(z)) for z in rts], cusps_on_circle=ncusp)
    json.dump(cert, open(f'{tag}_{FINAL}_cert.json', 'w'), indent=1)
    print(json.dumps(cert, indent=1)); print(f'done {time.time()-t0:.0f}s')

if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--final', type=int, default=1024)
    ap.add_argument('--ss', type=int, default=2)
    ap.add_argument('--seed', type=int, default=27)
    ap.add_argument('--tag', default='proto_hele')
    a = ap.parse_args()
    render(FINAL=a.final, SS=a.ss, seed=a.seed, tag=a.tag)
