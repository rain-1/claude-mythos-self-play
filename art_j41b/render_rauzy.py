"""render_rauzy.py — 'Three Letters, One Shadow': the Rauzy fractal in pastel, hierarchy as palette.

Pigment = level-1 branch (which of the three subtiles), lightness = level-2 and level-3 branches
(smaller pieces darker), ink = boundaries of the pieces with width by level (outer thickest).
Ghost translates R + lambda (the lattice tiling) around the centre at low density, fading to
paper.  Coral: the three domain-exchange arrows (R_i + v_i tile R again).  Thin ink thread:
the first steps of the walk z_1, z_2, ... that generates the set.
"""
import numpy as np, sys, json, time
from scipy.ndimage import gaussian_filter, distance_transform_edt, binary_dilation
sys.path.insert(0, '.')
import rauzy as rz
from pastel import Sheet, PIG, polyline_density, discs_density, text_density, ink_from_distance, finish, absorb, text_width


def gen_points(K, k_lo, alpha, fn, chunk=800):
    """stream all admissible K-digit values in chunks; fn(z, addr) is called per chunk.
    addr: (N,3) level-1..3 branches from the low digits."""
    lo = rz.admissible_strings(k_lo)
    hi = rz.admissible_strings(K - k_lo)
    pw = alpha ** np.arange(K)
    z_lo = lo.astype(float) @ pw[:k_lo]
    z_hi = hi.astype(float) @ pw[k_lo:]
    addr_lo = rz.branch_address(lo, 3)
    l2, l1 = lo[:, -2].astype(bool), lo[:, -1].astype(bool)
    h0, h1 = hi[:, 0].astype(bool), hi[:, 1].astype(bool)
    total = 0
    for s in range(0, len(hi), chunk):
        e = min(len(hi), s + chunk)
        valid = ~((l2[:, None] & l1[:, None] & h0[None, s:e]) | (l1[:, None] & h0[None, s:e] & h1[None, s:e]))
        z = (z_lo[:, None] + z_hi[None, s:e])[valid]
        ad = np.broadcast_to(addr_lo[:, None, :], (len(lo), e - s, 3))[valid]
        total += len(z)
        fn(z, ad)
    return total


def render(FINAL=1024, SS=2, K=None, tag='proto_rauzy', caption=True, ghosts=True, thread=False, arrows=False,
           exchange=True, pig=('cornflower', 'mint', 'apricot'), l2=(0.80, 1.0, 1.32), l3=(0.92, 1.0, 1.12),
           base=0.95, ghost_d=0.36, fill=0.60, gran=0.16, ink_w=(1.7, 1.1, 0.65, 0.4), n_thread=300, rot=0.35,
           fade_r=(0.60, 0.55)):
    t0 = time.time()
    W = H = FINAL * SS
    rs = FINAL / 1024.0 * SS
    beta, alpha, v = rz.eig()
    if K is None:
        K = {1024: 27, 2560: 30, 4096: 31}[FINAL]
    k_lo = 14
    cert = dict(K=K, beta=beta, abs_alpha=abs(alpha))
    # bounding box from a coarse set
    coarse = rz.admissible_strings(22).astype(float) @ alpha ** np.arange(22)
    coarse = coarse * np.exp(1j * rot)
    cx0, cy0 = coarse.real.mean(), coarse.imag.mean()
    ext = max(np.ptp(coarse.real), np.ptp(coarse.imag))
    S = fill * W / ext
    cx, cy = 0.5 * W, 0.5 * H

    def xf(z):
        return cx + S * (z.real - cx0), cy - S * (z.imag - cy0)

    # accumulators: counts per (level-1 branch) and lightness-weighted counts, plus level-2 id counts
    cnt = np.zeros((3, H * W), np.float32)
    wcnt = np.zeros((3, H * W), np.float32)
    cnt2 = np.zeros((3, 3, H * W), np.uint16)
    cnt3 = np.zeros((3, H * W), np.uint16)     # level-3 branch counts, for the finest ink
    l2a = np.array(l2, np.float32); l3a = np.array(l3, np.float32)

    def fn(z, ad):
        x, y = xf(z * np.exp(1j * rot))
        ix = np.clip(np.floor(x).astype(np.int64), 0, W - 1); iy = np.clip(np.floor(y).astype(np.int64), 0, H - 1)
        idx = iy * W + ix
        wt = l2a[ad[:, 1] - 1] * l3a[ad[:, 2] - 1]
        for b in range(3):
            m = ad[:, 0] == b + 1
            if not m.any(): continue
            cnt[b] += np.bincount(idx[m], minlength=H * W).astype(np.float32)
            wcnt[b] += np.bincount(idx[m], weights=wt[m], minlength=H * W).astype(np.float32)
            for b2 in range(3):
                m2 = m & (ad[:, 1] == b2 + 1)
                if m2.any():
                    cnt2[b, b2] += np.minimum(np.bincount(idx[m2], minlength=H * W), 60000).astype(np.uint16)
        for b3 in range(3):
            m3 = ad[:, 2] == b3 + 1
            if m3.any():
                cnt3[b3] += np.minimum(np.bincount(idx[m3], minlength=H * W), 60000).astype(np.uint16)
    n_pts = gen_points(K, k_lo, alpha, fn)
    print(f'points {n_pts} in {time.time()-t0:.0f}s')
    cnt = cnt.reshape(3, H, W); wcnt = wcnt.reshape(3, H, W); cnt2 = cnt2.reshape(3, 3, H, W)
    id3 = np.argmax(cnt3.reshape(3, H, W), 0)
    del cnt3
    tot = cnt.sum(0)
    support = tot > 0
    mean_c = tot[support].mean()
    cert.update(n_points=int(n_pts), mean_points_per_px=float(mean_c), area_px=int(support.sum()))
    # areas of the three subtiles (pixel majority)
    id1 = np.argmax(cnt, 0)
    areas = [int(((id1 == b) & support).sum()) for b in range(3)]
    cert.update(subtile_area_px=areas, subtile_area_ratio=[a / areas[0] for a in areas],
                predicted_ratio_1_beta_inv_beta_inv2=[1, 1 / beta, 1 / beta ** 2])
    id2 = np.argmax(cnt2.reshape(9, H, W), 0)
    del cnt2
    # ---- sheet
    sheet = Sheet(W, H, seed=21)
    # unfinished-edge fade for the ghosts: radial from the centre
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    rr = np.hypot(xx - cx, yy - cy) / (0.5 * W)
    fade = np.clip(1 - (rr - fade_r[0]) / fade_r[1], 0, 1) ** 1.6
    # main fractal: density = base * lightness weight (≈ uniform count, so use the ratio)
    for b in range(3):
        d = base * (wcnt[b] / mean_c)
        d = np.clip(d, 0, 2.2)
        d = gaussian_filter(d, 0.7)
        sheet.wash(d, pig[b], granulate=gran, seed=40 + b)
    # ghosts: translates by the lattice
    lam_a, lam_b = (1 - v[2]), (v[1] - v[2])
    if ghosts:
        nbrs = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, -1), (-1, 1), (1, 1), (-1, -1), (2, -1), (-2, 1), (1, -2), (-1, 2)]
        overlap = {}
        cover = support.copy()
        for (a, b) in nbrs:
            lam = (a * lam_a + b * lam_b) * np.exp(1j * rot)
            dx, dy = int(round(S * lam.real)), int(round(-S * lam.imag))
            sh = np.roll(np.roll(tot, dy, 0), dx, 1)
            # zero the wrapped part
            if dy > 0: sh[:dy] = 0
            elif dy < 0: sh[dy:] = 0
            if dx > 0: sh[:, :dx] = 0
            elif dx < 0: sh[:, dx:] = 0
            m = sh > 0
            ov = (m & support).sum()
            overlap[f'{a},{b}'] = float(ov / support.sum())
            cover |= m
            for bb in range(3):
                ws = np.roll(np.roll(wcnt[bb], dy, 0), dx, 1)
                if dy > 0: ws[:dy] = 0
                elif dy < 0: ws[dy:] = 0
                if dx > 0: ws[:, :dx] = 0
                elif dx < 0: ws[:, dx:] = 0
                d = ghost_d * base * (ws / mean_c) * fade
                d = gaussian_filter(np.clip(d, 0, 2.2), 0.7)
                sheet.wash(d, pig[bb], granulate=gran, seed=50 + bb)
        # coverage certificate: fraction of a central disc (radius 0.45 W) covered by the 13 tiles
        disc = rr < 0.45
        cert.update(tiling_overlap_fraction=overlap, coverage_central_disc=float((cover & disc).sum() / disc.sum()))
        print('overlap', {k: round(x, 4) for k, x in overlap.items()}, 'coverage', cert['coverage_central_disc'])
    # ---- ink: boundaries by level
    ink = np.zeros((H, W), np.float32)
    dsup = distance_transform_edt(~support) + distance_transform_edt(support)
    ink += ink_from_distance(dsup - 0.5, ink_w[0] * rs) * 0.95
    edge1 = np.zeros((H, W), bool)
    edge1[:, 1:] |= (id1[:, 1:] != id1[:, :-1]); edge1[1:, :] |= (id1[1:, :] != id1[:-1, :])
    edge1 &= support & binary_dilation(support, iterations=1)
    ink += ink_from_distance(distance_transform_edt(~edge1), ink_w[1] * rs) * 0.8 * support
    edge2 = np.zeros((H, W), bool)
    edge2[:, 1:] |= (id2[:, 1:] != id2[:, :-1]); edge2[1:, :] |= (id2[1:, :] != id2[:-1, :])
    edge2 &= support
    ink += ink_from_distance(distance_transform_edt(~edge2), ink_w[2] * rs) * 0.55 * support
    # level 3: the boundaries of the level-3 pieces are where BOTH id2 is constant and id3 changes
    edge3 = np.zeros((H, W), bool)
    edge3[:, 1:] |= (id3[:, 1:] != id3[:, :-1]); edge3[1:, :] |= (id3[1:, :] != id3[:-1, :])
    edge3 &= support
    ink += ink_from_distance(distance_transform_edt(~edge3), ink_w[3] * rs) * 0.32 * support
    sheet.wash(np.clip(ink, 0, 1), 'ink')
    # ---- the domain exchange: R_i + v_i drawn as coral outlines; they must tile R again
    if exchange:
        cor = np.zeros((H, W), np.float32)
        outside = {}
        for b in range(3):
            m = (id1 == b) & support
            vv = v[b] * np.exp(1j * rot)
            dx, dy = int(round(S * vv.real)), int(round(-S * vv.imag))
            sh = np.roll(np.roll(m, dy, 0), dx, 1)
            if dy > 0: sh[:dy] = False
            elif dy < 0: sh[dy:] = False
            if dx > 0: sh[:, :dx] = False
            elif dx < 0: sh[:, dx:] = False
            outside[b + 1] = float((sh & ~support).sum() / max(1, sh.sum()))
            dd = distance_transform_edt(~sh) + distance_transform_edt(sh)
            cor += ink_from_distance(dd - 0.5, 1.05 * rs)
        sheet.wash(np.clip(cor, 0, 1) * 1.5, 'coral')
        cert.update(exchange_fraction_outside=outside)
        print('exchange outside fractions', outside)
    # ---- the walk thread
    if thread:
        u = rz.word(n_thread + 1)
        zs = np.concatenate([[0], np.cumsum(v[u[:n_thread] - 1])]) * np.exp(1j * rot)
        px = np.stack(xf(zs), 1)
        th = polyline_density(W, H, px, 0.55 * rs)
        th = gaussian_filter(th, 0.4 * rs)
        sheet.wash(np.clip(th, 0, 1) * 0.7, 'ink')
        # beads at the origin and at the three first images
        bx, by = xf(zs[:1])
        sheet.wash(discs_density(W, H, bx, by, [2.2 * rs], [1.0], sigma=0.5 * rs) * 1.4, 'coral')
    # ---- domain exchange arrows: centroid of R_i -> centroid of R_i + v_i
    if arrows:
        for b in range(3):
            m = (id1 == b) & support
            yc, xc = np.argwhere(m).mean(0)
            vv = v[b] * np.exp(1j * rot)
            dx, dy = S * vv.real, -S * vv.imag
            p0 = np.array([xc, yc]); p1 = p0 + np.array([dx, dy])
            seg = polyline_density(W, H, [p0, p1], 1.2 * rs)
            # arrow head
            dirv = (p1 - p0) / np.linalg.norm(p1 - p0); nrm = np.array([-dirv[1], dirv[0]])
            hd = 7 * rs
            head = polyline_density(W, H, [p1 - dirv * hd + nrm * hd * 0.5, p1, p1 - dirv * hd - nrm * hd * 0.5], 1.2 * rs)
            sheet.wash(gaussian_filter(np.clip(seg + head, 0, 1), 0.4 * rs) * 1.4, 'coral')
            sheet.wash(discs_density(W, H, [xc], [yc], [2.0 * rs], [1.0], sigma=0.5 * rs) * 1.4, 'coral')
    if caption:
        sheet.caption_strip(0.905, 0.985, f=0.55)
        title = 'Three Letters, One Shadow'
        sub = ("The word 1213121121312... walked in the plane; its closure is this tile. Pigment: which of three pieces; "
               "light and dark: the same split again. Coral: the pieces slid by their letters, tiling it anew.")
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
        k, val = a.split('=')
        try:
            val = eval(val)
        except Exception:
            pass
        kw[k] = val
    render(**kw)
