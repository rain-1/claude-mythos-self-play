"""render_search.py — Koopman's optimal search, drawn as a sea.

Two glazes over one landscape:
  cool  = the belief you are LEFT with after searching optimally and finding
          nothing, which is min(prior, c): your prior with every peak shaved to
          one height;
  warm  = the effort you SPENT, phi = log(p/c)_+ , a dome over each island.
The coral curve is p = c, the exact edge of where you looked.  The bead is the
thing itself, sitting in water you never looked at.
"""
import sys, json, time
import numpy as np
from scipy.ndimage import gaussian_filter, zoom
import pastel as P
from search import make_prior, solve, uniform_compare, proportional_compare

COOL = ['mint', 'aqua', 'cornflower', 'lavender']
WARM = ['lemon', 'apricot', 'blush', 'orchid']


def ramp(names, s):
    x = np.clip(s, 0, 1) * (len(names) - 1)
    i = min(int(np.floor(x)), len(names) - 2)
    return P.mix_tint(names[i], names[i + 1], float(x - i))


def build(S, G=900, seed=13, out='search.png', final=None, caption=True,
          Bfrac=0.10, nb=22, truth=(0.905, 0.560)):
    t0 = time.time()
    W = H = S
    rs = S / 4096.0
    sh = P.Sheet(W, H, seed=seed)

    X0, X1 = 0.050 * W, 0.950 * W
    Y0, Y1 = 0.052 * H, 0.782 * H
    BW, BH = X1 - X0, Y1 - Y0

    p = make_prior(G, G)
    sol = solve(p, 1.0, Bfrac * p.size)
    c = sol['c']
    post = np.minimum(p, c)
    phi = np.maximum(np.log(p / c), 0.0)

    def putf(f, order=3):
        z = zoom(f.astype(np.float32), (BH / G, BW / G), order=order)
        o = np.zeros((H, W), np.float32)
        h2, w2 = z.shape
        o[int(Y0):int(Y0) + h2, int(X0):int(X0) + w2] = z
        return o

    # ---- glaze 1: the belief you are left with (cool) ---------------------
    b = post / post.max()
    for k in range(nb):
        lo, hi = k / nb, (k + 1) / nb
        m = ((b >= lo) & (b < hi)) if k < nb - 1 else (b >= lo)
        if not m.any():
            continue
        d = putf(m.astype(np.float32), order=1)
        d = gaussian_filter(d, 0.8 * rs + 0.6)
        sh.wash(d * (0.045 + 1.05 * (0.5 * (lo + hi)) ** 1.25),
                ramp(COOL, 0.5 * (lo + hi)), granulate=0.12, seed=300 + k)
        del d, m

    # ---- glaze 2: the effort you spent (warm), only inside the islands ----
    e = phi / max(phi.max(), 1e-9)
    for k in range(nb):
        lo, hi = k / nb, (k + 1) / nb
        m = ((e >= lo) & (e < hi)) if k < nb - 1 else (e >= lo)
        m = m & (phi > 0)
        if not m.any():
            continue
        d = putf(m.astype(np.float32), order=1)
        d = gaussian_filter(d, 0.8 * rs + 0.6)
        sh.wash(d * (0.14 + 1.75 * (0.5 * (lo + hi)) ** 0.85),
                ramp(WARM, 0.5 * (lo + hi)), granulate=0.12, seed=400 + k)
        del d, m
    print(f'  glazes {time.time()-t0:.0f}s', flush=True)

    # ---- relief: the shaved peaks are FLAT, so hillshade shows the cut ----
    surf = gaussian_filter(post / post.max(), 1.2)
    gy, gx = np.gradient(surf)
    lx, ly, lz = -0.62, -0.55, 0.56
    nrm = np.sqrt(gx * gx + gy * gy + 1e-9)
    shade = np.clip(-(gx * lx + gy * ly) / (40 * nrm + 1e-9), 0, 1)
    shade = np.clip(shade * np.clip(nrm * 260, 0, 1), 0, 1)
    sh.wash(putf(shade) * 0.42, 'sepia')

    # ---- contours of the prior, in ink; the level c in coral --------------
    def contour(field, level, width, sigma=0.8):
        a = (field > level).astype(np.float32)
        a = zoom(a, (BH / G, BW / G), order=1)
        g1, g2 = np.gradient(gaussian_filter(a, 1.0))
        e2 = np.hypot(g1, g2)
        o = np.zeros((H, W), np.float32)
        h2, w2 = e2.shape
        o[int(Y0):int(Y0) + h2, int(X0):int(X0) + w2] = e2
        o = o / (o.max() + 1e-9)
        return gaussian_filter(o ** 0.55, sigma * rs + 0.5)

    levels = np.exp(np.linspace(np.log(p.min() * 1.25), np.log(c * 0.985), 15))
    for L in levels:
        sh.wash(contour(p, L, 1) * 0.26, 'ink')
    # the archipelago at four budgets: thin coral ghosts, then the real shore
    for bf, w in [(0.02, 0.20), (0.045, 0.24), (0.30, 0.26), (0.75, 0.28)]:
        cc = solve(p, 1.0, bf * p.size)['c']
        sh.wash(contour(p, cc, 1, 1.0) * w, 'coral')
    shore = contour(p, c, 1, 1.9)
    sh.lighten(np.clip(shore * 1.6, 0, 1), 0.55)
    sh.wash(shore * 1.9, 'coral')
    print(f'  contours {time.time()-t0:.0f}s', flush=True)

    # ---- the thing itself -------------------------------------------------
    tx = X0 + truth[0] * BW
    ty = Y0 + truth[1] * BH
    gi, gj = int(truth[1] * G), int(truth[0] * G)
    inside = bool(p[gi, gj] > c)
    rb = 22 * rs
    sh.lighten(P.discs_density(W, H, [tx], [ty], [rb * 3.4], [1.0], sigma=rb * 1.4) * 0.9, 0.55)
    sh.wash(P.discs_density(W, H, [tx], [ty], [rb], [1.0], sigma=rb * 0.32) * 1.35, 'coral')
    sh.wash(P.discs_density(W, H, [tx], [ty], [rb * 1.3], [1.0], sigma=rb * 2.9) * 0.70, 'coral')

    items = [('it was here', tx + 26 * rs, ty, 34 * rs, 'italic', 'lm'),
             ('the edge of where you looked', X0 + 0.055 * BW, Y0 + 0.055 * BH,
              33 * rs, 'italic', 'ls')]
    if caption:
        sh.caption_strip(0.800, 0.995, 0.70)
        items.append(('Where You Have Not Looked', W / 2, 0.828 * H, 106 * rs, 'serif_bold', 'ma'))
        for j, ln in enumerate(P.wrap(
                'Spend a fixed amount of looking to maximise the chance of finding something. '
                'The best plan searches only the islands where your belief stands above one water level, '
                'and what it leaves you is your own prior with every peak shaved flat to that line.',
                40 * rs, 'italic', 0.80 * W)):
            items.append((ln, W / 2, (0.874 + 0.0168 * j) * H, 40 * rs, 'italic', 'ma'))
        pu = uniform_compare(p, 1.0, Bfrac * p.size)
        pr = proportional_compare(p, 1.0, Bfrac * p.size)
        items.append((f'Koopman water-filling · {sol["searched_fraction"]*100:.1f} % of the sea searched '
                      f'· found with probability {sol["pdetect"]*100:.1f} % '
                      f'(spread evenly: {pu*100:.1f} %; in proportion to belief: {pr*100:.1f} %)',
                      W / 2, 0.955 * H, 29 * rs, 'mono', 'ma'))
        items.append(('warm = the effort spent   ·   cool = the belief it leaves behind   ·   '
                      'coral = the level  p = c', W / 2, 0.980 * H, 28 * rs, 'mono', 'ma'))
    sh.wash(P.text_density(W, H, items) * 1.28, 'ink')

    img = sh.develop(dmax=2.80)
    P.finish(img, final or (S, S), out)
    cert = dict(grid=G, budget_per_cell=Bfrac, water_level=float(c),
                searched_fraction=float(sol['searched_fraction']),
                P_detect_optimal=float(sol['pdetect']),
                P_detect_uniform=float(uniform_compare(p, 1.0, Bfrac * p.size)),
                P_detect_proportional=float(proportional_compare(p, 1.0, Bfrac * p.size)),
                truth_inside_searched_set=inside,
                posterior_is_capped_prior=bool(np.allclose(np.minimum(p, c), post)))
    print(json.dumps(cert, indent=1))
    print(f'{out}  {time.time()-t0:.0f}s', flush=True)
    return cert


if __name__ == '__main__':
    S = int(sys.argv[1]) if len(sys.argv) > 1 else 1400
    build(S, out=f'proto_search_{S}.png')
