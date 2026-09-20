"""render_fold.py — 'Folded Into Itself': a disc of tinted tissue paper folded along straight creases.
Every layer's tint is looked up exactly on the original sheet through its isometry; layers stack as
absorbance (tissue paper is Beer–Lambert); creases fold along with the paper. Coral: the unit circle
around the image of the centre — the congruent copy of the disc that always contains the folded figure.
"""
import sys, json, time
import numpy as np
from scipy.ndimage import map_coordinates, gaussian_filter, distance_transform_edt
from PIL import Image, ImageDraw
import fold
from pastel import Sheet, PIG, absorb, lowfreq, noise, ink_from_distance, polyline_density, \
    text_density, text_width, finish, wrap, draw_lines_density

SIZE = int(sys.argv[1]) if len(sys.argv) > 1 else 1024
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 3
K = int(sys.argv[3]) if len(sys.argv) > 3 else 10
OUT = sys.argv[4] if len(sys.argv) > 4 else f'fold_{SIZE}.png'
FLO = float(sys.argv[5]) if len(sys.argv) > 5 else 0.08
FHI = float(sys.argv[6]) if len(sys.argv) > 6 else 0.30
DENS0 = float(sys.argv[7]) if len(sys.argv) > 7 else 0.36
NDEEP = int(sys.argv[8]) if len(sys.argv) > 8 else 3
SS = 2
W = H = SIZE * SS
rs = SIZE / 1024.0 * SS      # reference scale: 1 rs = 1 px at 1024 final


def make_texture(T=2048, seed=11):
    """absorbance RGB on the original sheet, (u,v) in [-1.15,1.15]^2 (T x T)."""
    lin = np.linspace(-1.15, 1.15, T, dtype=np.float32)
    U, V = np.meshgrid(lin, lin)
    Rr = np.hypot(U, V)
    inside = (Rr <= 1.0).astype(np.float32)
    ang = np.arctan2(V, U)
    A = np.zeros((T, T, 3), np.float32)
    # ONE hue walk across the sheet (adjacent pigments only, so stacked layers never mix to mud):
    # aqua -> cornflower -> lavender -> orchid -> blush along the diagonal, drifting with a low-frequency field
    s = (U * 0.7 + V * 0.7)      # -1..1 along the diagonal
    m = lowfreq(T, T, 160, seed, 0.22)
    hpos = np.clip(0.5 + 0.5 * (s + m) / 1.15, 0, 0.999) * 4.0   # 0..4 over five pigments
    walk = ['aqua', 'cornflower', 'lavender', 'orchid', 'blush']
    i0 = np.floor(hpos).astype(int); tt = (hpos - i0)[..., None].astype(np.float32)
    AB = np.stack([absorb(PIG[p]) for p in walk])          # (5,3)
    tint = (1 - tt) * AB[i0] + tt * AB[np.minimum(i0 + 1, 4)]
    rad = np.clip(Rr, 0, 1)
    dens = DENS0 * (0.85 + 0.35 * rad ** 2)
    dens = dens * (1 + 0.10 * lowfreq(T, T, 40, seed + 5)) * inside
    A += dens[..., None] * tint
    # the sheet's own lines: faint concentric rings on the paper (they fold with it)
    ring = np.zeros_like(Rr)
    for r0 in (0.25, 0.5, 0.75):
        ring += np.exp(-((Rr - r0) / 0.006) ** 2)
    ring *= inside
    A += (0.30 * ring)[..., None] * absorb(PIG['ink'])[None, None]
    return A, lin[0], lin[-1]


def main():
    t0 = time.time()
    rng = np.random.default_rng(SEED)
    fig = fold.Folded(fold.disc_polygon(1440))
    sched = [(0.16, 0.26)] * NDEEP + [(FLO, FHI)] * (K - NDEEP)
    fold.random_fold_sequence(fig, K, rng, schedule=sched)
    pts = fig.hull_pts()
    c = fig.centre_img
    print('layers', len(fig.layers), 'creases', len(fig.creases), 'area/pi', fig.total_area() / np.pi)
    # composition: the coral unit circle around c fills the page; the stack sits inside it
    Rpx = 0.395 * H
    cx, cy = 0.5 * W, 0.428 * H
    def to_px(P):
        P = np.asarray(P, float)
        return np.c_[cx + (P[:, 0] - c[0]) * Rpx, cy - (P[:, 1] - c[1]) * Rpx]

    tex, lo, hi = make_texture()
    T = tex.shape[0]
    sheet = Sheet(W, H, seed=SEED)
    Acc = np.zeros((H, W, 3), np.float32)
    count = np.zeros((H, W), np.float32)
    edges = Image.new('F', (W, H), 0.0)
    dre = ImageDraw.Draw(edges)
    for li, (P, R, t) in enumerate(fig.layers):
        Q = to_px(P)
        x0, y0 = np.floor(Q.min(0)).astype(int) - 1
        x1, y1 = np.ceil(Q.max(0)).astype(int) + 1
        x0 = max(x0, 0); y0 = max(y0, 0); x1 = min(x1, W); y1 = min(y1, H)
        if x1 <= x0 or y1 <= y0:
            continue
        im = Image.new('L', (x1 - x0, y1 - y0), 0)
        ImageDraw.Draw(im).polygon([(q[0] - x0, q[1] - y0) for q in Q], fill=255)
        mask = np.asarray(im, np.float32) / 255.0
        if mask.sum() == 0:
            continue
        yy, xx = np.mgrid[y0:y1, x0:x1]
        # pixel -> current coords -> original coords
        px = c[0] + (xx - cx) / Rpx; py = c[1] - (yy - cy) / Rpx
        u = R[0, 0] * px + R[0, 1] * py + t[0]
        v = R[1, 0] * px + R[1, 1] * py + t[1]
        iu = (u - lo) / (hi - lo) * (T - 1); iv = (v - lo) / (hi - lo) * (T - 1)
        for ch in range(3):
            samp = map_coordinates(tex[..., ch], [iv, iu], order=1, mode='constant', cval=0.0)
            Acc[y0:y1, x0:x1, ch] += samp * mask
        count[y0:y1, x0:x1] += mask
        dre.polygon([tuple(q) for q in Q], outline=1.0, width=max(1, int(round(0.9 * rs))))
    print('layers painted', time.time() - t0)
    # tissue: absorbance stack, softened one hair
    cert_count_max = float(count.max()); del count
    for ch in range(3):
        sheet.A[..., ch] += gaussian_filter(Acc[..., ch], 0.6 * rs / 2) if rs > 1 else Acc[..., ch]
    del Acc
    # pooling at paper edges: darken where the layer count steps
    edge = np.asarray(edges, np.float32)
    sheet.wash(np.clip(edge, 0, 1) * 0.16, 'ink'); del edge, edges, dre
    # creases: ink, weight by how many layers were folded together
    segs = np.array([[x0, y0, x1, y1] for (x0, y0, x1, y1, w) in fig.creases])
    ws = np.array([w for (*_, w) in fig.creases])
    if len(segs):
        P0 = to_px(segs[:, :2]); P1 = to_px(segs[:, 2:])
        cr = draw_lines_density(W, H, np.c_[P0, P1], 1.4 * rs, weights=np.minimum(ws, 1.0) * 0.5)
        sheet.wash(np.clip(cr, 0, 1.6) * 0.42, 'ink')
    # the coral copy of the disc around the centre's image, and the centre itself
    th = np.linspace(0, 2 * np.pi, 2000)
    circ = np.c_[cx + Rpx * np.cos(th), cy - Rpx * np.sin(th)]
    cd = polyline_density(W, H, circ, 2.2 * rs, closed=True)
    sheet.wash(np.clip(cd, 0, 1) * 0.95, 'coral')
    halo = gaussian_filter(np.clip(cd, 0, 1), 6 * rs) * 0.12
    sheet.wash(halo, 'coral')
    dot = np.zeros((H, W), np.float32)
    pr = int(12 * rs); ys0, xs0 = int(cy) - pr, int(cx) - pr
    yy, xx = np.mgrid[ys0:ys0 + 2 * pr, xs0:xs0 + 2 * pr].astype(np.float32)
    dot[ys0:ys0 + 2 * pr, xs0:xs0 + 2 * pr] = np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / (3.5 * rs) ** 2))
    sheet.wash(dot * 0.9, 'coral'); del dot, yy, xx
    # ghost: the original disc (dashed) where it was before folding: centred at origin
    O = to_px(np.zeros((1, 2)))[0]
    im_d = Image.new('F', (W, H), 0.0); dd = ImageDraw.Draw(im_d)
    th2 = np.linspace(0, 2 * np.pi, 4000)
    P = np.c_[O[0] + Rpx * np.cos(th2), O[1] - Rpx * np.sin(th2)]
    for k in range(0, 4000, 4000 // 90):
        seg = P[k:k + 4000 // 180]
        if len(seg) > 1:
            dd.line([tuple(map(float, q)) for q in seg], fill=1.0, width=max(1, int(round(1.2 * rs))))
    dash = np.asarray(im_d, np.float32)
    sheet.wash(np.clip(dash, 0, 1) * 0.35, 'ink')
    # film strip: the states after each fold (ink outlines of every layer, the new crease in coral)
    ns = len(fig.snaps)
    cellw = min(0.075 * W, 0.90 * W / ns)
    x_start = 0.5 * W - 0.5 * cellw * ns
    ys = 0.865 * H
    sc = cellw * 0.44
    im_i = Image.new('F', (W, H), 0.0); di = ImageDraw.Draw(im_i)
    im_c = Image.new('F', (W, H), 0.0); dc = ImageDraw.Draw(im_c)
    for j, snap in enumerate(fig.snaps):
        ccx = x_start + (j + 0.5) * cellw
        for P in snap:
            Q = np.c_[ccx + P[:, 0] * sc, ys - P[:, 1] * sc]
            pl = [tuple(map(float, q)) for q in Q]; pl.append(pl[0])
            di.line(pl, fill=1.0, width=max(1, int(round(0.9 * rs))), joint='curve')
        if j >= 1:
            q, n = fig.snap_lines[j - 1]
            d = np.array([-n[1], n[0]])
            a = q - 1.3 * d; b = q + 1.3 * d
            dc.line([(ccx + a[0] * sc, ys - a[1] * sc), (ccx + b[0] * sc, ys - b[1] * sc)], fill=1.0,
                    width=max(1, int(round(1.1 * rs))))
    strip_ink = np.asarray(im_i, np.float32); strip_cor = np.asarray(im_c, np.float32)
    sheet.wash(np.clip(strip_ink, 0, 1) * 0.42, 'ink')
    sheet.wash(np.clip(strip_cor, 0, 1) * 0.75, 'coral')
    # caption
    sheet.caption_strip(0.895, 0.985, 0.5)
    title = 'Folded Into Itself'
    sub = (f'A disc of tissue paper folded {len(fig.lines)} times along straight creases ({len(fig.layers)} layers). '
           'Folding never increases a distance, so the folded figure always fits inside a copy of the disc (coral) — '
           'whether any other convex figure has this property is open (MathOverflow 7016).')
    lines = wrap(sub, 10.5 * rs, 'italic', 0.80 * W)
    items = [(title, W / 2, 0.915 * H, 26 * rs, 'serif_bold', 'mm')]
    for i, ln in enumerate(lines):
        items.append((ln, W / 2, 0.945 * H + i * 13.5 * rs, 10.5 * rs, 'italic', 'mm'))
    txt = text_density(W, H, items)
    sheet.wash(txt * 0.92, 'ink')
    img = sheet.develop()
    finish(img, (SIZE, SIZE), OUT)
    # certificate
    cert = dict(seed=SEED, folds=len(fig.lines), layers=len(fig.layers), area_over_pi=fig.total_area() / np.pi,
                max_dist_from_centre_image=float(np.linalg.norm(pts - c, axis=1).max()),
                lipschitz_excess=fig.check_lipschitz(np.random.default_rng(1))[0],
                count_max=cert_count_max)
    print(json.dumps(cert))
    json.dump(cert, open(OUT.replace('.png', '_cert.json'), 'w'), indent=1)
    print('done', time.time() - t0)


if __name__ == '__main__':
    main()
