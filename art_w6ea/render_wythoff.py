"""render_wythoff.py — the Grundy field of Wythoff's game.

Two piles (m, n).  A move takes any positive number from ONE pile, or the same
positive number from BOTH.  Every position already has a value: G(m,n), the
mex of its options.  G = 0 means the player to move has already lost, and those
squares are exactly the Beatty pairs (floor k*phi, floor k*phi^2).

The pigment is  R = G(m,n) / (m+n) : deep where the position is nearly lost,
pale where it is richly winning.  Coral = the squares you cannot win from.
"""
import sys, json, time
import numpy as np
from scipy.ndimage import zoom, gaussian_filter
import pastel as P

PHI = (1 + 5 ** 0.5) / 2
WALK = ['aqua', 'cornflower', 'lavender', 'orchid', 'blush', 'apricot', 'lemon']


def walk_tint(s):
    x = np.clip(s, 0, 1) * (len(WALK) - 1)
    i = min(int(np.floor(x)), len(WALK) - 2)
    return P.mix_tint(WALK[i], WALK[i + 1], float(x - i))


def load(N):
    return np.fromfile(f'wy{N}.bin', np.int32).reshape(N, N)


def build(S, N=2048, nbins=24, seed=11, out='wy.png', final=None, caption=True,
          dlo=0.30, dhi=2.15, pw=1.35):
    t0 = time.time()
    G = load(N)
    W = H = S
    rs = S / 4096.0
    sh = P.Sheet(W, H, seed=seed)

    X0, X1 = 0.058 * W, 0.972 * W
    Y0, Y1 = 0.040 * H, 0.812 * H
    BW, BH = X1 - X0, Y1 - Y0

    mm = np.arange(N, dtype=np.float32)[:, None]
    nn = np.arange(N, dtype=np.float32)[None, :]
    R = G.astype(np.float32) / (mm + nn + 1.0)          # R[m, n]
    R = np.clip(R, 0.0, 1.0)
    # R is heavily skewed (median 0.78): spread it through its own distribution
    # so the pigment walk uses its whole range.  eq = a blend of R and CDF(R).
    qs = np.quantile(R[::3, ::3].ravel().astype(np.float64), np.linspace(0, 1, 513))
    qs = np.maximum.accumulate(qs)
    Rq = np.interp(R, qs, np.linspace(0, 1, 513)).astype(np.float32)
    Rs = (0.30 * R + 0.70 * Rq).astype(np.float32)

    # board -> canvas: m across, n up.  Rows of the canvas are n descending.
    k = BW / N
    def putfield(field):
        """board array [m,n] -> (H,W) canvas density inside the plot rect"""
        f = np.ascontiguousarray(field.T[::-1])          # rows = n desc, cols = m
        z = zoom(f, (BH / N, BW / N), order=0)
        out = np.zeros((H, W), np.float32)
        h2, w2 = z.shape
        out[int(Y0):int(Y0) + h2, int(X0):int(X0) + w2] = z
        return out

    edges = np.linspace(0.0, 1.0, nbins + 1)
    for kb in range(nbins):
        lo, hi = edges[kb], edges[kb + 1]
        msk = (Rs >= lo) & (Rs < hi) if kb < nbins - 1 else (Rs >= lo)
        if not msk.any():
            continue
        s = 0.5 * (lo + hi)
        dens = (dlo + (dhi - dlo) * (1.0 - s) ** pw) * msk.astype(np.float32)
        d = putfield(dens)
        d = gaussian_filter(d, 0.45 * rs + 0.3)
        sh.wash(d, walk_tint(s), granulate=0.13, seed=200 + kb)
        del d, dens, msk
    print(f'  field {time.time()-t0:.0f}s', flush=True)

    # ---- the two golden lines, in ink ------------------------------------
    def bx(m):
        return X0 + (m + 0.5) * BW / N
    def by(n):
        return Y1 - (n + 0.5) * BH / N

    # ---- coral: the squares you cannot win from (G = 0) -------------------
    zm, zn = np.where(G == 0)
    xs, ys = bx(zm.astype(np.float64)), by(zn.astype(np.float64))
    rr = np.full(len(xs), 2.7 * rs + 1.0)
    d = P.discs_density(W, H, xs, ys, rr, np.ones(len(xs)), sigma=1.5 * rs + 0.5)
    sh.lighten(np.clip(gaussian_filter(d, 3.0 * rs + 1.0) * 2.2, 0, 1), 0.86)
    sh.wash(d * 1.95, 'coral')
    sh.wash(gaussian_filter(d, 13 * rs + 3) * 0.70, 'coral')
    del d

    # ---- axes + labels ----------------------------------------------------
    items = []
    segs = []
    for v in range(0, N + 1, N // 8):
        vv = min(v, N - 1)
        x = float(bx(vv)); y = float(by(vv))
        segs.append((x, Y1, x, Y1 + 11 * rs))
        items.append((f'{v:,}', x, Y1 + 20 * rs, 27 * rs, 'mono', 'ma'))
        segs.append((X0 - 11 * rs, y, X0, y))
        items.append((f'{v:,}', X0 - 17 * rs, y, 27 * rs, 'mono', 'rm'))
    d = P.draw_lines_density(W, H, segs, max(1, int(round(2 * rs))), sigma=0.6)
    sh.wash(d * 0.85, 'ink')
    del d
    items.append(('first pile   m', (X0 + X1) / 2, Y1 + 50 * rs, 33 * rs, 'italic', 'ma'))
    items.append(('n = φm', float(bx(N / PHI)) - 12 * rs, float(by(N - 1)) + 26 * rs,
                  33 * rs, 'italic', 'rm'))
    items.append(('m = φn', float(bx(N - 1)) - 10 * rs, float(by((N - 1) / PHI)) + 4 * rs,
                  33 * rs, 'italic', 'rm'))
    sh.wash(P.text_density(W, H, items) * 1.25, 'ink')

    # vertical axis label
    from PIL import Image as _I, ImageDraw as _D, ImageFont as _F
    txt = 'second pile   n'
    wv = int(P.text_width(txt, 33 * rs, 'italic') * 1.15) + 8
    im = _I.new('L', (wv, int(60 * rs)), 0)
    _D.Draw(im).text((wv / 2, 30 * rs), txt, fill=255,
                     font=_F.truetype(P.FONTS['italic'], int(33 * rs)), anchor='mm')
    im = im.rotate(90, expand=True)
    can = _I.new('L', (W, H), 0)
    can.paste(im, (int(X0 - 108 * rs), int((Y0 + Y1) / 2 - im.size[1] / 2)))
    sh.wash(np.asarray(can, np.float32) / 255.0 * 1.25, 'ink')

    if caption:
        sh.caption_strip(0.828, 0.995, 0.72)
        it = [('Every Square Already Knows', W / 2, 0.858 * H, 106 * rs, 'serif_bold', 'ma')]
        for j, ln in enumerate(P.wrap(
                'Wythoff’s game: take any amount from one pile, or the same amount from both. '
                'Nobody needs to play it — every square already holds its verdict. The deep rays are the '
                'positions worth least, and the coral beads, the only squares whose owner cannot win, '
                'lie on the two golden lines.',
                40 * rs, 'italic', 0.82 * W)):
            it.append((ln, W / 2, (0.903 + 0.0168 * j) * H, 40 * rs, 'italic', 'ma'))
        it.append((f'{N:,} × {N:,} positions · pigment = G(m,n)/(m+n) · '
                   f'{int((G==0).sum()):,} losing squares, all of them Beatty pairs '
                   f'⌊kφ⌋, ⌊kφ²⌋',
                   W / 2, 0.968 * H, 29 * rs, 'mono', 'ma'))
        pairs = ' '.join(f'({int(k*PHI)},{int(k*PHI*PHI)})' for k in range(1, 13))
        it.append(('the first twelve:  ' + pairs, W / 2, 0.988 * H, 27 * rs, 'mono', 'ma'))
        sh.wash(P.text_density(W, H, it) * 1.28, 'ink')

    img = sh.develop(dmax=2.75)
    P.finish(img, final or (S, S), out)
    print(f'{out}  {time.time()-t0:.0f}s', flush=True)


if __name__ == '__main__':
    S = int(sys.argv[1]) if len(sys.argv) > 1 else 1500
    N = int(sys.argv[2]) if len(sys.argv) > 2 else 1024
    build(S, N=N, out=f'proto_wy_{S}.png')
