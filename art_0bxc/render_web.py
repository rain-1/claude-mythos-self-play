"""render_web.py — 'Could the Universe Be a Neuron?' : the adhesion-model cosmic web on paper.

Voids are paper.  Every lower-hull facet is a lump of stuck mass at one Eulerian point; the picture is
those lumps as pigment (mass = density), the thin mist of still-free dust as the faintest wash,
ink beads on the heaviest knots, and one coral accent.
"""
import numpy as np, sys, json, time
from scipy.ndimage import gaussian_filter
from PIL import Image, ImageDraw
sys.path.insert(0, '.')
from pastel import Sheet, PIG, absorb, text_density, finish, text_width, discs_density, polyline_density
from adhesion import gaussian_potential, tile_field, lower_hull

RAMP = ['aqua', 'cornflower', 'lavender', 'orchid', 'blush']       # by log mass (mass mode)
EPOCH = ['apricot', 'lemon', 'pistachio', 'mint', 'aqua', 'cornflower', 'lavender', 'orchid']  # old -> young


def splat(H, W, x, y, w, sigma):
    ix = np.clip(np.floor(x).astype(np.int64), 0, W - 1)
    iy = np.clip(np.floor(y).astype(np.int64), 0, H - 1)
    f = np.bincount(iy * W + ix, weights=w, minlength=H * W).reshape(H, W).astype(np.float32)
    if sigma > 0:
        f = gaussian_filter(f, sigma)
    return f


def facet_adjacency(simp):
    """pairs (f1, f2) of facets sharing an edge."""
    F = len(simp)
    e = np.concatenate([simp[:, [0, 1]], simp[:, [1, 2]], simp[:, [2, 0]]], 0)
    e.sort(axis=1)
    fid = np.tile(np.arange(F), 3)
    key = e[:, 0].astype(np.int64) * (e.max() + 1) + e[:, 1]
    order = np.argsort(key, kind='stable')
    key, fid = key[order], fid[order]
    same = key[1:] == key[:-1]
    return np.stack([fid[:-1][same], fid[1:][same]], 1)


def lines_density(W, H, x0, y0, x1, y1, w, width, sigma):
    im = Image.new('F', (W, H), 0.0)
    dr = ImageDraw.Draw(im)
    wd = int(max(1, round(width)))
    for a, b, c, d_, e in zip(x0, y0, x1, y1, w):
        dr.line([(float(a), float(b)), (float(c), float(d_))], fill=float(e), width=wd)
    a = np.asarray(im, np.float32)
    return gaussian_filter(a, sigma) if sigma > 0 else a


def build(N, seed, T, n_index, k_cut, amp, epochs=0, margin=None):
    """hull at time T (+ optional ladder of earlier hulls for the collapse epoch of every particle)."""
    margin = margin or N // 6
    import os, pickle
    cache = f'cache_web_N{N}_s{seed}_T{T}_n{n_index}_e{epochs}.pkl'
    if os.path.exists(cache):
        print('cache hit', cache, flush=True)
        return pickle.load(open(cache, 'rb'))
    phi = gaussian_potential(N, seed=seed, n_index=n_index, k_cut=k_cut, amp=amp)
    q, P, inside = tile_field(phi, margin=margin)
    M = N + 2 * margin
    h = lower_hull(q, P, T)
    cell = (1.0 / N) ** 2
    out = dict(q=q, P=P, inside=inside, M=M, margin=margin, phi=phi, hull=h, cell=cell, T=T)
    if epochs:
        ts = T * np.geomspace(0.12, 1.0, epochs)
        tc = np.full(len(q), np.inf)           # absorption time per particle
        for k, t in enumerate(ts):
            hk = lower_hull(q, P, t)
            newly = (~hk['free']) & np.isinf(tc)
            tc[newly] = t
            print(f'  epoch {k} t={t:.3f} free {hk["free"][inside].mean():.3f}  ({hk["secs"]:.1f}s)', flush=True)
        tc[~h['free'] & np.isinf(tc)] = T
        out['tc'] = tc; out['ts'] = ts
        # per-facet mean epoch of the swallowed particles: rasterise facets (Lagrangian) into an id map
        simp = h['simplices']
        big = np.nonzero(h['mass'] / cell > 2.5)[0]
        idmap = Image.new('I', (M, M), -1)
        dr = ImageDraw.Draw(idmap)
        qi = (q * N + margin)                   # back to array index (float)
        for fi in big:
            tri = [(float(qi[v, 1]), float(qi[v, 0])) for v in simp[fi]]
            dr.polygon(tri, fill=int(fi))
        ids = np.asarray(idmap, np.int64).ravel()
        ok = (ids >= 0) & np.isfinite(tc)
        ssum = np.bincount(ids[ok], weights=np.log(tc[ok]), minlength=len(simp))
        cnt = np.bincount(ids[ok], minlength=len(simp))
        fe = np.full(len(simp), np.log(T))
        fe[cnt > 0] = ssum[cnt > 0] / cnt[cnt > 0]
        out['facet_epoch'] = fe   # log t_c averaged
    try:
        pickle.dump(out, open(cache, 'wb'), protocol=4)
    except Exception as e:
        print('cache write failed', e)
    return out


def render(FINAL=1024, SS=2, tag='proto_web', N=512, seed=1, T=1.0, n_index=-1.0, k_cut=None, amp=0.08,
           mode='mass', epochs=0, mist=0.12, mist_sigma=6.0, dens=1.0, knee=1.0, blur=0.8, bead_n=60,
           coral='attractor', caption=True, title='Could the Universe Be a Neuron?',
           sub='dust that moves in straight lines and sticks where it meets: every knot, wall and void is a face of one convex hull',
           gran=0.1, m0=2.5, window=None, data=None, mpow=0.5, edge_gain=1.0, line_w=1.0, knee_pct=60, halo_m=30.0, halo_r=1.6, halo_gain=1.0, halo_cap=14.0, edge_fade=0.10, roads_n=2500, roads_d=0.9):
    t0 = time.time()
    W = H = FINAL * SS
    rs = FINAL / 1024.0 * SS
    k_cut = k_cut or N / 6
    d = data or build(N, seed, T, n_index, k_cut, amp, epochs=(epochs if mode == 'epoch' else 0))
    h, cell = d['hull'], d['cell']
    x = np.mod(h['x'], 1.0)                      # periodic box
    m = h['mass'] / cell                          # in cells
    inside_f = np.all(d['inside'][h['simplices']], axis=1) | True   # keep all; the box is periodic
    # window: (x0, y0, size) in box units — a crop of the periodic box, tiled so edges wrap
    if window is None:
        window = (0.0, 0.0, 1.0)
    if window == 'auto':
        # put the heaviest knot at (0.38, 0.66) of the sheet, window 0.72 of the box
        g = int(np.argmax(m)); ws_ = 0.72
        window = (float(np.mod(x[g, 0] - 0.38 * ws_, 1.0)), float(np.mod(x[g, 1] - 0.66 * ws_, 1.0)), ws_)
    wx, wy, ws = window
    S = W / ws
    px = (np.mod(x[:, 0] - wx, 1.0)) * S
    py = (np.mod(x[:, 1] - wy, 1.0)) * S
    sheet = Sheet(W, H, seed=seed + 11)
    cert = dict(N=N, seed=seed, T=T, n_index=n_index, k_cut=k_cut, amp=amp, mode=mode, nfacets=int(len(m)),
                free_fraction=float(h['free'][d['inside']].mean()), mass_in_structures=float(m[m > m0].sum() / m.sum()),
                heaviest_cells=float(m.max()), window=list(window))
    # ---- mist: the still-free dust (tiny facets), heavily blurred, faint
    small = m <= m0
    f_mist = splat(H, W, px[small], py[small], m[small], mist_sigma * rs)
    f_mist /= (np.percentile(f_mist, 95) + 1e-9)
    sheet.wash(np.clip(f_mist, 0, 1.5) * mist, 'paperblue', granulate=gran)
    # ---- structures: facets > m0 cells; pigment by mode
    big = ~small
    lm = np.log10(m[big])
    if mode == 'mass':
        # ramp position over log mass from m0 to the 99.5th percentile
        lo, hi = np.log10(m0), np.percentile(lm, 99.7)
        u = np.clip((lm - lo) / (hi - lo), 0, 0.999) * (len(RAMP) - 1)
        names = RAMP
    else:
        fe = d['facet_epoch'][big]
        # mass-weighted percentile rank of the epoch among structure facets -> the palette spans by mass
        order = np.argsort(fe); cw = np.cumsum(m[big][order]); cw = cw / cw[-1]
        rank = np.empty(len(fe)); rank[order] = cw
        u = np.clip(rank, 0, 0.999) * (len(EPOCH) - 1)
        names = EPOCH
    i0 = np.floor(u).astype(int); tfrac = u - i0
    # density field per pigment: facet lumps (mass^p) + the hull edges between adjacent structure facets
    # drawn as segments (the filaments are chains of thin facets; their shared edges map to short
    # Eulerian segments between the lumps)
    bidx = np.nonzero(big)[0]
    mp = m ** mpow
    adj = facet_adjacency(h['simplices'])
    both = big[adj[:, 0]] & big[adj[:, 1]]
    adj = adj[both]
    dx = px[adj[:, 0]] - px[adj[:, 1]]; dy = py[adj[:, 0]] - py[adj[:, 1]]
    L = np.hypot(dx, dy)
    keep = L < 0.06 * W                    # never draw across the periodic seam
    adj = adj[keep]; L = L[keep]
    ufull = np.zeros(len(m)); ufull[bidx] = u
    uedge = 0.5 * (ufull[adj[:, 0]] + ufull[adj[:, 1]])
    wedge = 0.5 * (mp[adj[:, 0]] + mp[adj[:, 1]]) * edge_gain
    medge = 0.5 * (m[adj[:, 0]] + m[adj[:, 1]])
    wclass = np.clip(np.round(np.log10(medge / m0) * 1.5), 0, 4).astype(int)   # width class by mass
    fields = {}
    for j, name in enumerate(names):
        wj = np.where(i0 == j, 1 - tfrac, 0) + np.where(i0 + 1 == j, tfrac, 0)
        sel = wj > 0
        f = np.zeros((H, W), np.float32)
        if sel.any():
            f += splat(H, W, px[big][sel], py[big][sel], (mp[big] * wj)[sel], blur * rs)
            hs = sel & (m[big] > halo_m)
            if hs.any():
                rr = np.minimum(halo_r * rs * np.sqrt(m[big][hs] / halo_m), halo_cap * rs)
                f += halo_gain * discs_density(W, H, px[big][hs], py[big][hs], rr, (mp[big] * wj)[hs] / (rr / rs) ** 1.2,
                                               sigma=0.8 * rs)
        ej = np.abs(uedge - j) < 0.5
        if ej.any():
            for wc in np.unique(wclass[ej]):
                e2 = ej & (wclass == wc)
                f += lines_density(W, H, px[adj[e2, 0]], py[adj[e2, 0]], px[adj[e2, 1]], py[adj[e2, 1]], wedge[e2],
                                   line_w * rs * (1 + 0.5 * wc), blur * rs)
        if f.any():
            fields[name] = f
    tot = sum(fields.values())
    scale = np.percentile(tot[tot > 0], knee_pct) if (tot > 0).any() else 1.0
    for name, f in fields.items():
        dd = dens * np.tanh(f / (knee * scale)) * (f / (tot + 1e-12))
        sheet.wash(dd, name, granulate=gran)
    cert['n_edges_drawn'] = int(len(adj)); cert['scale'] = float(scale)
    # ---- ink beads on the heaviest knots (radius ~ sqrt mass)
    order = np.argsort(-m)[:bead_n]
    r = 0.55 * rs * np.sqrt(m[order] / m[order].min()) ** 0.5 * 1.6
    r = np.clip(r, 0.9 * rs, 5.5 * rs)
    ink = discs_density(W, H, px[order], py[order], r, np.full(len(order), 1.0), sigma=0.45 * rs)
    sheet.wash(np.clip(ink, 0, 1) * 1.05, 'ink')
    # ---- coral: the great attractor (heaviest knot) — a ring of its own size class and the straight
    # Zel'dovich roads of its catchment (a few of the particles it swallowed)
    if coral == 'attractor':
        g = int(np.argmax(m))
        cx, cy = px[g], py[g]
        cert['attractor'] = dict(mass_cells=float(m[g]), x=[float(cx / S + wx), float(cy / S + wy)])
        if True:
            # the heaviest knot in coral (its halo) and, around it, the thin circle whose area equals the
            # Lagrangian area it swallowed: the dust that used to fill that disc is now one point
            rr = np.sqrt(m[g] * cell / np.pi) * S
            rr_h = min(halo_cap * rs * 1.1, 0.42 * rr)
            halo = discs_density(W, H, [cx], [cy], [rr_h], [1.0], sigma=0.9 * rs)
            sheet.wash(np.clip(halo, 0, 1) * 1.5, 'coral')
            yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
            ring = np.exp(-((np.hypot(xx - cx, yy - cy) - rr) / (0.9 * rs)) ** 2)
            sheet.wash(ring * 1.1, 'coral')
            cert['attractor']['swallowed_disc_radius_box'] = float(rr / S)
    if edge_fade > 0:
        # painter's unfinished edge: pigment thins to paper in an irregular band along the border
        from pastel import lowfreq
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32) / W
        dd = np.minimum(np.minimum(xx, 1 - xx), np.minimum(yy, 1 - yy))
        wob = 1 + 0.5 * lowfreq(H, W, max(16, W // 5), seed + 5, 1.0)
        t_ = np.clip(dd / (edge_fade * wob), 0, 1)
        keep = t_ * t_ * (3 - 2 * t_)
        sheet.lighten(1 - keep, 1.0)
    if caption:
        ts_ = int(0.030 * H); ss = int(0.0135 * H)
        sheet.caption_strip(0.905, 0.985, f=0.62)
        items = [(title, int(0.045 * W), int(0.925 * H), ts_, 'serif_bold', 'ls')]
        if text_width(sub, ss, 'italic') > 0.9 * W:
            print('CAPTION OVERRUN', text_width(sub, ss, 'italic') / W)
        items.append((sub, int(0.045 * W), int(0.966 * H), ss, 'italic', 'ls'))
        sheet.wash(text_density(W, H, items) * 1.2, 'ink')
    img = sheet.develop()
    finish(img, (FINAL, FINAL), f'{tag}_{FINAL}.png')
    cert['secs'] = time.time() - t0
    json.dump(cert, open(f'{tag}_{FINAL}_cert.json', 'w'), indent=1)
    print(json.dumps(cert, indent=1))
    return d


if __name__ == '__main__':
    kw = {}
    for a in sys.argv[1:]:
        k, v = a.split('=', 1)
        try:
            v = json.loads(v)
        except Exception:
            pass
        kw[k] = v
    render(**kw)
