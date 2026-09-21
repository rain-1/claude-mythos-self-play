"""render_sub.py — hero: the submarine bombing game as a spacetime sheaf.

mode 'vel'    : horizontal u = log10 t, vertical v = x/t  (the mean velocity an
                observer would infer) -- every submarine (a,b) is the curve
                v = b + a/t, so the sea combs itself into integer strata.
mode 'symlog' : horizontal u = log10 t, vertical y = sign(x) log10(1+|x|) -- a
                double fan, one ray per velocity.

Either way a thread is drawn only while it is ALIVE, i.e. for t <= T(a,b), and
the pigment is the submarine's velocity: warm going right, cool going left.
"""
import sys, json, time
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter
import pastel as P
from submarine import Hunt, live_radius

WARM = ['lemon', 'apricot', 'blush']
COOL = ['aqua', 'cornflower', 'lavender']


def ramp_tint(names, s):
    x = np.clip(s, 0, 1) * (len(names) - 1)
    i = min(int(np.floor(x)), len(names) - 2)
    return P.mix_tint(names[i], names[i + 1], float(x - i))


def bloom(d, sig):
    """cheap wide blur: decimate, blur, put back"""
    from scipy.ndimage import zoom as _z
    k = 6
    sm = d[::k, ::k]
    sm = gaussian_filter(sm, sig / k)
    return _z(sm, (d.shape[0] / sm.shape[0], d.shape[1] / sm.shape[1]), order=1)[:d.shape[0], :d.shape[1]]


def vtext(W, H, txt, cx, cy, size, fk):
    """vertical (rotated 90 deg CCW) text as a density mask"""
    w = int(P.text_width(txt, size, fk) * 1.15) + 8
    hgt = int(size * 1.8)
    im = Image.new('L', (w, hgt), 0)
    dr = ImageDraw.Draw(im)
    from PIL import ImageFont
    dr.text((w / 2, hgt / 2), txt, fill=255, font=ImageFont.truetype(P.FONTS[fk], int(size)), anchor='mm')
    im = im.rotate(90, expand=True)
    out = Image.new('L', (W, H), 0)
    out.paste(im, (int(cx - im.size[0] / 2), int(cy - im.size[1] / 2)))
    return np.asarray(out, np.float32) / 255.0


def vel_tint(b, M):
    if b > 0:
        return ramp_tint(WARM, b / M)
    if b < 0:
        return ramp_tint(COOL, -b / M)
    return P.PIG['sepia']


def build(S, M=50, order='shell', mode='vel', nbins=40, seed=5,
          coral=(43, -31), lw=None, wt=0.62, out='sub.png', final=None,
          caption=True, tmax_frac=1.0, fadelen=0.045, bl=0.35, bombw=0.30):
    t0 = time.time()
    h = Hunt(M, order)
    N = int(h.N * tmax_frac)
    W = H = S
    sh = P.Sheet(W, H, seed=seed)
    rs = S / 4096.0

    X0, X1 = 0.098 * W, 0.972 * W
    Y0, Y1 = 0.048 * H, 0.828 * H
    LN = np.log10(N)

    def px(t):
        return X0 + (np.log10(np.maximum(t, 1.0)) / LN) * (X1 - X0)

    if mode == 'vel':
        Vmax = M + 0.55

        def yv(a, b, t):
            return b + a / t
    else:
        Vmax = np.log10(1.0 + M + M * N) * 1.02

        def yv(a, b, t):
            x = a + b * t
            return np.sign(x) * np.log10(1.0 + np.abs(x))

    def py(v):
        return Y0 + ((Vmax - v) / (2 * Vmax)) * (Y1 - Y0)

    if lw is None:
        lw = max(1, int(round(S / 1650.0)))

    # painter's unfinished edge on the left (all threads start at t=1 -> a wall)
    xx = np.arange(W, dtype=np.float32)
    u = (xx - X0) / (X1 - X0)
    fade = np.clip(u / fadelen, 0, 1) ** 0.85 * np.clip((1.004 - u) / 0.010, 0, 1)
    yy = np.arange(H, dtype=np.float32)
    vclip = np.clip((yy - Y0) / (4.0 * rs + 1), 0, 1) * np.clip((Y1 - yy) / (4.0 * rs + 1), 0, 1)
    fade = fade[None, :] * vclip[:, None]

    a = h.seq[:, 0].astype(np.float64)
    b = h.seq[:, 1].astype(np.float64)
    T = np.minimum(np.arange(1, h.N + 1, dtype=np.float64), N)
    keepthread = np.arange(1, h.N + 1) <= N
    binid = np.clip(((b + M) / (2 * M) * nbins).astype(int), 0, nbins - 1)

    NS = 170
    frac = np.linspace(0.0, 1.0, NS)
    YLIM = 4.0 * H
    edges = np.linspace(-M, M, nbins + 1)

    for k in range(nbins):
        sel = np.where((binid == k) & keepthread)[0]
        if len(sel) == 0:
            continue
        im = Image.new('F', (W, H), 0.0)
        dr = ImageDraw.Draw(im)
        for i in sel:
            Ti = T[i]
            if Ti <= 1.0:
                continue
            tt = 10.0 ** (frac * np.log10(Ti))
            xs = px(tt)
            ys = np.clip(py(yv(a[i], b[i], tt)), -YLIM, YLIM)
            dr.line([(float(x), float(y)) for x, y in zip(xs, ys)],
                    fill=float(wt), width=lw, joint='curve')
        d = np.asarray(im, np.float32)
        del im, dr
        d = gaussian_filter(d, 0.55 * rs + 0.35) * fade
        bmid = 0.5 * (edges[k] + edges[k + 1])
        tint = vel_tint(bmid, M)
        sh.wash(d, tint, granulate=0.12, seed=100 + k)
        sh.wash(bloom(d, 30 * rs + 3) * bl * fade, tint)
        del d
    print(f'  threads {time.time()-t0:.0f}s', flush=True)

    # ---- the bombs: every thread ends where one bomb fell -----------------
    aa, bb, TT = a[keepthread], b[keepthread], T[keepthread]
    ve = bb + aa / TT
    ex, ey = px(TT), py(ve)
    ok = (ey > Y0) & (ey < Y1)
    rr = np.full(ok.sum(), 2.1 * rs + 0.8)
    d = P.discs_density(W, H, ex[ok], ey[ok], rr, np.ones(ok.sum()), sigma=1.5 * rs + 0.6)
    sh.wash(d * bombw * fade, 'ink')
    del d

    # ---- the shoreline: a stratum is intact only while max(|a|,|b|) >= r(t) ----
    if mode == 'vel':
        tt = np.logspace(0, LN, 900)
        r = live_radius(tt)
        keep = r <= Vmax
        for sgn in (+1, -1):
            d = P.polyline_density(W, H, list(zip(px(tt[keep]), py(sgn * r[keep]))),
                                   max(1, int(round(2.2 * rs))), 1.0, sigma=0.8)
            sh.wash(d * 0.72, 'ink')
            del d

    # ---- the one submarine that was really there -------------------------
    a0, b0 = coral
    T0 = min(h.capture_time(a0, b0), N)
    tt = 10.0 ** (np.linspace(0, 1, 1600) * np.log10(max(T0, 2)))
    xs = px(tt)
    ys = np.clip(py(yv(a0, b0, tt)), -YLIM, YLIM)
    d = P.polyline_density(W, H, list(zip(xs, ys)), max(2, int(round(3.2 * rs))), 1.0,
                           sigma=0.9 * rs + 0.3)
    sh.wash(d * 1.85 * fade, 'coral', granulate=0.08, seed=41)
    xk, yk = float(px(T0)), float(py(yv(a0, b0, T0)))
    rb = 26 * rs
    sh.wash(P.discs_density(W, H, [xk], [yk], [rb], [1.0], sigma=rb * 0.30) * 1.05, 'coral')
    sh.wash(P.discs_density(W, H, [xk], [yk], [rb * 1.2], [1.0], sigma=rb * 2.8) * 0.60, 'coral')
    del d

    # ---- axes ------------------------------------------------------------
    items = []
    segs = []
    for t in [1, 10, 100, 1000, 10000]:
        if t > N:
            continue
        x = float(px(t))
        segs.append((x, Y1, x, Y1 + 11 * rs))
        items.append((f't = {t:,}', x, Y1 + 20 * rs, 27 * rs, 'mono', 'ma'))
    if mode == 'vel':
        for v in range(-M, M + 1):
            if v % 10:
                continue
            y = float(py(v))
            segs.append((X0 - 11 * rs, y, X0, y))
            items.append((f'{v:+d}' if v else '0', X0 - 17 * rs, y, 27 * rs, 'mono', 'rm'))
        sh.wash(vtext(W, H, 'mean velocity   x / t', X0 - 78 * rs, (Y0 + Y1) / 2, 34 * rs, 'italic') * 1.25, 'ink')
        items.append(('|b| = (√t − 1) / 2', float(px(N)) - 16 * rs,
                      float(py(live_radius(N))) - 14 * rs, 31 * rs, 'italic', 'rd'))
    else:
        for e in range(0, 7):
            for sgn in (+1, -1):
                y = float(py(sgn * e))
                if not (Y0 <= y <= Y1):
                    continue
                segs.append((X0 - 11 * rs, y, X0, y))
                items.append((('0' if e == 0 else f'{"+" if sgn>0 else "−"}10^{e}'),
                              X0 - 17 * rs, y, 27 * rs, 'mono', 'rm'))
        sh.wash(vtext(W, H, 'position   x', X0 - 78 * rs, (Y0 + Y1) / 2, 34 * rs, 'italic') * 1.25, 'ink')
    items.append(('the submarine that was there', xk - 24 * rs, yk + 6 * rs, 32 * rs, 'italic', 'rm'))

    d = P.draw_lines_density(W, H, segs, max(1, int(round(2 * rs))), sigma=0.6)
    sh.wash(d * 0.85, 'ink')
    del d

    naive = h.certify()['naive_hunter_hit_fraction']
    if caption:
        sh.caption_strip(0.845, 0.995, 0.70)
        items.append(('Already on the List', W / 2, 0.874 * H, 106 * rs, 'serif_bold', 'ma'))
        for j, ln in enumerate(P.wrap(
                'A submarine starts at an unknown integer and moves at an unknown integer speed. '
                'One bomb a turn is enough: number the pairs, and on turn n bomb where pair n would be. '
                'Every thread is a submarine that might exist, drawn until the turn that destroys it.',
                40 * rs, 'italic', 0.82 * W)):
            items.append((ln, W / 2, (0.920 + 0.0168 * j) * H, 40 * rs, 'italic', 'ma'))
        items.append((f'{h.N:,} candidate submarines · all destroyed by turn {h.N:,} '
                      f'· a hunter who bombs 0, −1, +1, −2, … instead reaches {naive*100:.1f} %',
                      W / 2, 0.974 * H, 29 * rs, 'mono', 'ma'))

    t_ = P.text_density(W, H, items)
    sh.wash(t_ * 1.30, 'ink')
    del t_

    img = sh.develop(dmax=2.90)
    P.finish(img, final or (S, S), out)
    print(f'{out}  {time.time()-t0:.0f}s', flush=True)
    return h


if __name__ == '__main__':
    S = int(sys.argv[1]) if len(sys.argv) > 1 else 1100
    md = sys.argv[2] if len(sys.argv) > 2 else 'vel'
    build(S, mode=md, out=f'proto_sub_{md}_{S}.png')
