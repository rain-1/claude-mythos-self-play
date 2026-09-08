"""render_mush.py — 'Is Happiness a Trap?' : Bunimovich's mushroom billiard in pastel.

String-art register: every chord is one thin line of pigment; the caustic circle of a
trapped orbit appears by itself as the envelope of its chords.  Trapped orbits (caustic
radius rho >= r) in the cool family, pigment by rho (mint next to the theorem's circle,
lavender at the rim).  'Sticky' orbits — launched in the cap with rho just BELOW r, free by
the theorem — in the warm family (blush closest to r, apricot farther): they circle for a
long time imitating a trapped orbit and then fall into the stem.  Coral: the circle rho = r
and the two mouth corners.
"""
import numpy as np, sys, json, time
from scipy.ndimage import gaussian_filter
sys.path.insert(0, '.')
import mushroom as mb
from pastel import Sheet, PIG, polyline_density, discs_density, text_density, finish

R, r, h = 1.0, 0.5, 1.0


def launch_with_rho(rng, rho, side=None):
    """start on the arc, chord tangent to the circle of radius rho, heading inward"""
    n = len(rho)
    phi = rng.uniform(0.05, np.pi - 0.05, n)
    P = np.stack([R * np.cos(phi), R * np.sin(phi)], 1)
    if side is None:
        side = rng.choice([-1, 1], n)
    ang = phi + np.pi - side * np.arcsin(rho / R)
    V = np.stack([np.cos(ang), np.sin(ang)], 1)
    inward = (P * V).sum(1) < 0
    V[~inward] *= -1
    P = P + 1e-9 * V
    assert np.allclose(mb.caustic_radius(P, V), rho, atol=1e-7)
    return P, V


def render(FINAL=1024, SS=2, n_tr=28, nb_tr=260, n_st=7, nb_st=3000, n_fr=2, nb_fr=1200, tag='proto_mush',
           caption=True, amp=1.0, seed=3, rho_pow=1.4, gran=0.18, line=1.0, knee=0.9, eps_min=2e-3, eps_max=0.12,
           stem_w=0.45, cool_dark=1.0, warm_dark=1.0, layout='centre', phase_tries=64, blur=0.9):
    t0 = time.time()
    W = H = FINAL * SS
    rs = FINAL / 1024.0 * SS
    rng = np.random.default_rng(seed)
    S = 0.76 * W / (2 * R)
    cx, cy = 0.5 * W, 0.43 * H

    def xf(x, y):
        return cx + S * x, cy - S * y

    cert = {}
    # ---------- trapped orbits: rho in (r, R), spaced, biased toward r
    u = ((np.arange(n_tr) + 0.5) / n_tr) ** rho_pow
    rho_tr = np.clip(r + (R - r) * u, r + 2e-3, R - 4e-3)
    P, V = launch_with_rho(rng, rho_tr)
    segs_tr, incap_tr = mb.propagate(P, V, nb_tr, R, r, h)
    assert incap_tr.all(), 'a trapped orbit left the cap'
    L_tr = np.hypot(segs_tr[..., 2] - segs_tr[..., 0], segs_tr[..., 3] - segs_tr[..., 1])
    rho_after = np.abs(segs_tr[-1, :, 0] * (segs_tr[-1, :, 3] - segs_tr[-1, :, 1]) - segs_tr[-1, :, 1] * (segs_tr[-1, :, 2] - segs_tr[-1, :, 0])) / L_tr[-1]
    cert.update(n_trapped=n_tr, chords_per_trapped=nb_tr, rho_trapped=[float(x) for x in rho_tr],
                rho_drift_max=float(np.abs(rho_after - rho_tr).max()), all_trapped_stayed=True)
    # ---------- sticky orbits: rho = r(1 - eps), free by the theorem
    eps = np.geomspace(eps_min, eps_max, n_st)
    rho_st = r * (1 - eps)
    # phase search: for each eps try `phase_tries` launch phases and keep the longest first sojourn
    tries = phase_tries
    rho_rep = np.repeat(rho_st, tries)
    Pc, Vc = launch_with_rho(rng, rho_rep)
    sc, ic = mb.propagate(Pc, Vc, nb_st, R, r, h)
    fe = np.where((~ic).any(0), np.argmin(ic, 0), nb_st).reshape(n_st, tries)
    best = np.argmax(fe, 1)
    idx = np.arange(n_st) * tries + best
    P, V = Pc[idx], Vc[idx]
    segs_st, incap_st = sc[:, idx], ic[:, idx]
    del sc, ic
    L_st = np.hypot(segs_st[..., 2] - segs_st[..., 0], segs_st[..., 3] - segs_st[..., 1])
    # first exit chord index and the length of the first sojourn
    first_exit = np.array([int(np.argmin(incap_st[:, i])) if (~incap_st[:, i]).any() else -1 for i in range(n_st)])
    first_len = np.array([L_st[:k, i].sum() if k >= 0 else L_st[:, i].sum() for i, k in enumerate(first_exit)])
    cert.update(n_sticky=n_st, chords_per_sticky=nb_st, eps_sticky=[float(x) for x in eps],
                first_exit_chord=[int(x) for x in first_exit], first_sojourn_length=[float(x) for x in first_len])
    print('sticky first exits (chords):', first_exit, 'lengths', np.round(first_len, 1))
    # ---------- a couple of free orbits from the stem (the stem's own web)
    P = np.stack([rng.uniform(-r, r, n_fr), rng.uniform(-h, 0, n_fr)], 1)
    a = rng.uniform(0, 2 * np.pi, n_fr); V = np.stack([np.cos(a), np.sin(a)], 1)
    segs_fr, incap_fr = mb.propagate(P, V, nb_fr, R, r, h)
    print(f'orbits {time.time()-t0:.1f}s')
    # ---------- rasterise: weight = chord length in px => ~1 unit of mass per pixel along the line
    def wpx(segs):
        x0, y0 = xf(segs[..., 0], segs[..., 1]); x1, y1 = xf(segs[..., 2], segs[..., 3])
        return np.hypot(x1 - x0, y1 - y0)
    acc = {}
    bands_tr = ['mint', 'aqua', 'cornflower', 'lavender']
    tb = (rho_tr - r) / (R - r)
    w_tr = wpx(segs_tr)
    for bi, name in enumerate(bands_tr):
        c = (bi + 0.5) / len(bands_tr)
        wb = np.clip(1 - np.abs(tb - c) * len(bands_tr), 0, 1)
        ww = (w_tr * wb[None, :]).reshape(-1); m = ww > 0
        if m.any():
            acc[name] = mb.raster(segs_tr.reshape(-1, 4)[m], ww[m], W, H, xf, step=0.7).reshape(H, W)
    # sticky: blush for the closest to r, apricot for the farthest (log scale in eps); stem chords lighter
    te = (np.log(eps) - np.log(eps_min)) / (np.log(eps_max) - np.log(eps_min))
    w_st = wpx(segs_st) * np.where(incap_st, 1.0, stem_w)
    for name, wb in (('blush', 1 - te), ('apricot', te)):
        ww = (w_st * wb[None, :]).reshape(-1); m = ww > 0
        if m.any():
            acc[name] = acc.get(name, 0) + mb.raster(segs_st.reshape(-1, 4)[m], ww[m], W, H, xf, step=0.7).reshape(H, W)
    w_fr = wpx(segs_fr) * stem_w
    acc['apricot'] = acc.get('apricot', 0) + mb.raster(segs_fr.reshape(-1, 4), w_fr.reshape(-1), W, H, xf, step=0.7).reshape(H, W)
    print(f'raster {time.time()-t0:.1f}s')
    # ---------- sheet
    sheet = Sheet(W, H, seed=11)
    for i, name in enumerate(bands_tr + ['blush', 'apricot']):
        if name not in acc: continue
        dark = cool_dark if name in bands_tr else warm_dark
        d = amp * dark * 1.5 * np.tanh(acc[name] * knee / line)
        d = gaussian_filter(d.astype(np.float32), blur)   # absolute blur: threads stay threads at any size
        sheet.wash(d, name, granulate=gran, seed=30 + i)
    # ---------- ink outline + coral theorem circle + mouth beads
    th = np.linspace(0, np.pi, 720)
    arc = np.stack(xf(R * np.cos(th), R * np.sin(th)), 1)
    outline = [arc, np.array([xf(-R, 0), xf(-r, 0)]).reshape(2, 2), np.array([xf(r, 0), xf(R, 0)]).reshape(2, 2),
               np.array([xf(-r, 0), xf(-r, -h), xf(r, -h), xf(r, 0)]).reshape(4, 2)]
    ink = np.zeros((H, W), np.float32)
    for pl in outline:
        ink += polyline_density(W, H, pl, 1.5 * rs)
    ink = np.clip(gaussian_filter(ink, 0.5 * rs), 0, 1)
    sheet.wash(ink * 0.8, 'ink')
    th2 = np.linspace(0, np.pi, 500)
    cor = polyline_density(W, H, np.stack(xf(r * np.cos(th2), r * np.sin(th2)), 1), 1.2 * rs)
    cor = gaussian_filter(cor, 0.5 * rs)
    sheet.wash(np.clip(cor, 0, 1) * 1.3, 'coral')
    bx, by = xf(np.array([-r, r]), np.array([0.0, 0.0]))
    beads = discs_density(W, H, bx, by, [3.2 * rs] * 2, [1.0] * 2, sigma=0.6 * rs)
    sheet.wash(np.clip(beads, 0, 1) * 1.5, 'coral')
    if caption:
        sheet.caption_strip(0.905, 0.985, f=0.55)
        title = 'Is Happiness a Trap?'
        sub = ("Bunimovich's mushroom. Cool: orbits whose caustic circle clears the mouth (rho >= r) — they never leave. "
               "Warm: rho just under r — they circle for ages, then fall.")
        items = [(title, 0.045 * W, 0.925 * H, 0.030 * H, 'serif_bold', 'ls'),
                 (sub, 0.045 * W, 0.962 * H, 0.0135 * H, 'italic', 'ls')]
        sheet.wash(text_density(W, H, items) * 1.9, 'ink')
    img = sheet.develop()
    finish(img, (FINAL, FINAL), f'{tag}_{FINAL}.png')
    json.dump(cert, open(f'{tag}_{FINAL}_cert.json', 'w'), indent=1)
    print(f'done {time.time()-t0:.0f}s')
    return cert


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--final', type=int, default=1024)
    ap.add_argument('--ss', type=int, default=2)
    ap.add_argument('--ntr', type=int, default=28)
    ap.add_argument('--nbtr', type=int, default=260)
    ap.add_argument('--nst', type=int, default=7)
    ap.add_argument('--nbst', type=int, default=3000)
    ap.add_argument('--nfr', type=int, default=2)
    ap.add_argument('--nbfr', type=int, default=1200)
    ap.add_argument('--amp', type=float, default=1.0)
    ap.add_argument('--rhopow', type=float, default=1.4)
    ap.add_argument('--gran', type=float, default=0.18)
    ap.add_argument('--line', type=float, default=1.0)
    ap.add_argument('--knee', type=float, default=0.9)
    ap.add_argument('--epsmin', type=float, default=2e-3)
    ap.add_argument('--epsmax', type=float, default=0.12)
    ap.add_argument('--stemw', type=float, default=0.45)
    ap.add_argument('--seed', type=int, default=3)
    ap.add_argument('--tries', type=int, default=64)
    ap.add_argument('--blur', type=float, default=0.9)
    ap.add_argument('--tag', default='proto_mush')
    ap.add_argument('--nocap', action='store_true')
    a = ap.parse_args()
    render(FINAL=a.final, SS=a.ss, n_tr=a.ntr, nb_tr=a.nbtr, n_st=a.nst, nb_st=a.nbst, n_fr=a.nfr, nb_fr=a.nbfr, tag=a.tag,
           caption=not a.nocap, amp=a.amp, seed=a.seed, rho_pow=a.rhopow, gran=a.gran, line=a.line, knee=a.knee,
           eps_min=a.epsmin, eps_max=a.epsmax, stem_w=a.stemw, phase_tries=a.tries, blur=a.blur)
