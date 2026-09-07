"""render_kac.py — 'The Ring That Only Slept' : Kac's ring as a polar carpet.

Angle = site on the ring, radius = time (t = 0 at the inner rim, t = 2N at the outer rim).
A white ball is paper; a black ball is pigment, its hue = how many markers the ball has
crossed so far (the ball's experience), stepping through the box every two crossings.
Coral ticks at the rims = the markers (the only things that ever change a colour).
Below: Kac's greyness G(t) as ink, the ensemble exponential (1-2mu)^t as coral, and the
exact return at 2N.
"""
import numpy as np, sys, json, time
from scipy.ndimage import gaussian_filter, distance_transform_edt
sys.path.insert(0, '.')
import kac
from pastel import Sheet, PIG, polyline_density, discs_density, text_density, text_width, finish, ink_from_distance

RAMP = ['apricot', 'lemon', 'pistachio', 'mint', 'aqua', 'cornflower', 'lavender', 'orchid', 'blush']


def render(FINAL=1024, SS=2, N=720, M=37, kind='random', seed=3, tag='kac', caption=True,
           r0=0.085, R=0.355, cy=0.415, dens=1.35, edge=0.35):
    t0 = time.time()
    W = H = FINAL * SS
    rs = FINAL / 1024.0 * SS
    m = kac.markers(N, M, kind, seed=seed)
    M = int(m.sum())
    T = 2 * N
    C, F = kac.colour_field(m, T)
    B = kac.simulate(m, T)
    assert np.array_equal(C, B), 'closed form != brute force'
    G = kac.greyness(C)
    mu = M / N
    cert = dict(N=N, M=M, mu=mu, kind=kind, seed=seed, closed_form_equals_brute_force=True,
                recurrence_2N=bool(np.array_equal(C[T], C[0])), anti_recurrence_N=bool(np.array_equal(C[N], 1 - C[0])),
                G_first=[float(x) for x in G[:8]], kac_mean_first=[float((1 - 2 * mu) ** t) for t in range(8)],
                G_N=float(G[N]), G_2N=float(G[T]), G_min_abs_window=float(np.abs(G[20:N - 20]).max()))
    print(json.dumps(cert, indent=1))
    # ---- polar lookup
    cx, cyy = 0.5 * W, cy * H
    Rin, Rout = r0 * W, R * W
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    dxp, dyp = xx - cx, yy - cyy
    rr = np.hypot(dxp, dyp); th = np.arctan2(-dyp, dxp) % (2 * np.pi)
    del xx, yy
    inside = (rr >= Rin) & (rr <= Rout)
    ti = np.clip(((rr - Rin) / (Rout - Rin) * T).astype(int), 0, T)
    ii = (th / (2 * np.pi) * N).astype(int) % N
    K = F[ti, ii]                                   # flips so far
    black = (K % 2 == 1) & inside
    # pigment index by experience
    pidx = ((K - 1) // 2) % len(RAMP)
    sheet = Sheet(W, H, seed=seed)
    for p, name in enumerate(RAMP):
        d = (black & (pidx == p)).astype(np.float32) * dens
        if d.any():
            sheet.wash(d, name, granulate=0.22, edge=edge, seed=30 + p)
    # ---- ink: cell boundaries of the black regions (thin), the two rims
    bnd = black.astype(np.float32)
    edt_in = distance_transform_edt(bnd); edt_out = distance_transform_edt(1 - bnd)
    dist = np.where(bnd > 0, edt_in - 0.5, edt_out - 0.5)
    ink = ink_from_distance(np.abs(dist), 0.55 * rs) * inside
    sheet.wash(ink * 0.35, 'ink')
    del edt_in, edt_out, dist, ink
    ring = np.abs(rr - Rin); ring2 = np.abs(rr - Rout)
    sheet.wash((ink_from_distance(ring, 0.8 * rs) + ink_from_distance(ring2, 0.8 * rs)) * 0.7, 'ink')
    # ---- coral: marker ticks on both rims (marker on edge j sits between site j and j+1)
    tick = np.zeros((H, W), np.float32)
    for j in np.nonzero(m)[0]:
        a = 2 * np.pi * (j + 1) / N
        for (ra, rb) in ((Rin - 9 * rs, Rin - 1.5 * rs), (Rout + 1.5 * rs, Rout + 9 * rs)):
            pts = np.array([[cx + ra * np.cos(a), cyy - ra * np.sin(a)], [cx + rb * np.cos(a), cyy - rb * np.sin(a)]])
            tick += polyline_density(W, H, pts, 1.6 * rs, weight=1.0)
    sheet.wash(np.clip(gaussian_filter(tick, 0.4 * rs), 0, 1) * 1.5, 'coral')
    # the anti-recurrence ring t = N (everything flipped) as a coral hairline
    rN = Rin + (Rout - Rin) * 0.5
    sheet.wash(ink_from_distance(np.abs(rr - rN), 0.6 * rs) * 0.9, 'coral')
    del rr, th, dxp, dyp
    # ---- greyness chart below the ring
    x0, x1 = 0.10 * W, 0.90 * W
    y0, y1 = (cy + R + 0.035) * H, (cy + R + 0.035) * H + 0.075 * H  # chart band (y down)
    ts = np.arange(T + 1)
    T1 = 80; xb = x0 + 0.30 * (x1 - x0)           # magnified first 80 steps, then the rest (broken axis)
    X = np.where(ts <= T1, x0 + (xb - x0) * ts / T1, xb + (x1 - xb) * (ts - T1) / (T - T1))
    Y = y1 - (y1 - y0) * (G + 1) / 2
    ch = polyline_density(W, H, np.stack([X, Y], 1), 1.3 * rs, weight=1.0)
    axis = polyline_density(W, H, np.array([[x0, y1 - (y1 - y0) / 2], [x1, y1 - (y1 - y0) / 2]]), 0.8 * rs, weight=0.5)
    axis = axis + polyline_density(W, H, np.array([[xb - 3 * rs, y1 + 4 * rs], [xb + 3 * rs, y0 - 4 * rs]]), 0.8 * rs, weight=0.5)
    sheet.wash(np.clip(gaussian_filter(ch + axis, 0.4 * rs), 0, 1) * 0.95, 'ink')
    Yk = y1 - (y1 - y0) * ((1 - 2 * mu) ** ts + 1) / 2
    ck = polyline_density(W, H, np.stack([X[:T1 + 1], Yk[:T1 + 1]], 1), 1.6 * rs, weight=1.0)
    sheet.wash(np.clip(gaussian_filter(ck, 0.5 * rs), 0, 1) * 1.3, 'coral')
    # ---- caption
    if caption:
        title = 'The Ring That Only Slept'
        sub = (f'Kac’s ring, {N} balls, {M} markers. It greys in a dozen steps as if dying; at t = N every ball is flipped; at t = 2N it is exactly what it was.')
        items = [(title, 0.10 * W, (y1 / H + 0.045) * H, 0.030 * H, 'serif_bold', 'ls'),
                 (sub, 0.10 * W, (y1 / H + 0.08) * H, 0.0135 * H, 'italic', 'ls')]
        sheet.wash(text_density(W, H, items) * 1.9, 'ink')
        lab = [('t = 0', x0, y1 + 0.012 * H, 0.012 * H, 'italic', 'ls'), ('t = 80', xb, y1 + 0.012 * H, 0.012 * H, 'italic', 'ms'), ('t = N', float(X[N]), y1 + 0.012 * H, 0.012 * H, 'italic', 'ms'),
               ('t = 2N', x1, y1 + 0.012 * H, 0.012 * H, 'italic', 'rs')]
        sheet.wash(text_density(W, H, lab) * 1.5, 'ink')
    img = sheet.develop()
    out = f'{tag}_{FINAL}.png'
    finish(img, (FINAL, FINAL), out)
    json.dump(cert, open(f'{tag}_{FINAL}_cert.json', 'w'), indent=1)
    print(f'done {time.time()-t0:.0f}s')


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--final', type=int, default=1024)
    ap.add_argument('--ss', type=int, default=2)
    ap.add_argument('--N', type=int, default=720)
    ap.add_argument('--M', type=int, default=37)
    ap.add_argument('--kind', default='random')
    ap.add_argument('--seed', type=int, default=3)
    ap.add_argument('--tag', default='proto_kac')
    ap.add_argument('--nocap', action='store_true')
    ap.add_argument('--dens', type=float, default=1.35)
    ap.add_argument('--edge', type=float, default=0.35)
    a = ap.parse_args()
    render(FINAL=a.final, SS=a.ss, N=a.N, M=a.M, kind=a.kind, seed=a.seed, tag=a.tag, caption=not a.nocap, dens=a.dens, edge=a.edge)
