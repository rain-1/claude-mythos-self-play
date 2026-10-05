"""render_veils.py — two veils of random lines with the same chance (MO 499477).

Three circles in a row, tangent: red (radius 1), green (r), black (r²) — green in the middle.
Veil 1: lines through A on red and B on green.  Veil 2: lines through two points B, C on green.
The question: why does each veil pierce the black pearl equally often?  Every line is drawn edge
to edge as a thin glaze; lines that pierce the pearl carry full colour, misses are a breath.

usage: render_veils.py W H out.png [key=val ...]
"""
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter

ARG = dict(a.split('=', 1) for a in sys.argv[4:] if '=' in a)
def P(k, d): return type(d)(ARG.get(k, d))

WARM = [(1.00, 0.50, 0.60), (1.00, 0.62, 0.52), (1.00, 0.76, 0.48), (1.00, 0.88, 0.50), (1.00, 0.62, 0.82)]
COOL = [(0.50, 0.90, 0.74), (0.50, 0.82, 1.00), (0.62, 0.66, 1.00), (0.78, 0.60, 1.00), (0.52, 0.92, 0.90)]
def ramp(stops, h):
    h = np.asarray(h) % 1.0; n = len(stops); x = h * n; i = np.floor(x).astype(int) % n; t = (x - np.floor(x))[..., None]
    a = np.array(stops)[i]; b = np.array(stops)[(i + 1) % n]
    return a ** (1 - t) * b ** t


def geometry(r):
    R = dict(red=1.0, green=r, black=r * r)
    C = dict(red=np.array([0.0, 0.0]), green=np.array([1 + r, 0.0]), black=np.array([1 + 2 * r + r * r, 0.0]))
    return R, C


def hits(Pt, Q, c, R):
    d = Q - Pt; t = np.einsum('ij,ij->i', c - Pt, d) / np.einsum('ij,ij->i', d, d)
    F = Pt + t[:, None] * d
    return np.linalg.norm(F - c, axis=1) < R


def panel(W, H, lines_p, lines_q, hit, hue, stops, view, Rg, Cg):
    """accumulate absorbance of full lines (clipped to view) into an (H,W,3) float array"""
    x0, x1, y0, y1 = view
    SS = P('ss', 2); Ws, Hs = W * SS, H * SS
    A = np.zeros((Hs * Ws, 3), np.float32)
    ab = -np.log(ramp(stops, hue)).astype(np.float32)
    wt = np.where(hit, 1.0, P('miss', 0.16)).astype(np.float32)
    L = np.hypot(x1 - x0, y1 - y0) * 1.05
    step = (x1 - x0) / Ws * 0.5
    ts = np.arange(-L, L, step)
    for i0 in range(0, len(lines_p), 64):
        p = lines_p[i0:i0 + 64]; q = lines_q[i0:i0 + 64]
        d = q - p; d /= np.linalg.norm(d, axis=1, keepdims=True)
        mid = (p + q) / 2
        # project mid to the view centre along the line so the sample range covers the window
        c = np.array([(x0 + x1) / 2, (y0 + y1) / 2])
        s = np.einsum('ij,ij->i', c - mid, d)
        base = mid + s[:, None] * d
        X = base[:, None, 0] + ts[None] * d[:, None, 0]
        Y = base[:, None, 1] + ts[None] * d[:, None, 1]
        px = ((X - x0) / (x1 - x0) * Ws).astype(np.int64); py = ((y1 - Y) / (y1 - y0) * Hs).astype(np.int64)
        ok = (px >= 0) & (px < Ws) & (py >= 0) & (py < Hs)
        idx = (py * Ws + px)[ok]
        w = np.broadcast_to(wt[i0:i0 + 64, None], X.shape)[ok]
        for ch in range(3):
            cw = np.broadcast_to((ab[i0:i0 + 64, ch] * wt[i0:i0 + 64])[:, None], X.shape)[ok]
            A[:, ch] += np.bincount(idx, cw, minlength=Hs * Ws).astype(np.float32)
    A = A.reshape(Hs, Ws, 3) * 0.5 * P('k', 0.25)
    A = A.reshape(H, SS, W, SS, 3).mean((1, 3))
    return A


def main():
    W, H, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    r = P('r', 0.62); N = P('N', 6000)
    R, C = geometry(r)
    rng = np.random.default_rng(P('seed', 3))
    a = rng.uniform(0, 2 * np.pi, N); b = rng.uniform(0, 2 * np.pi, N); c = rng.uniform(0, 2 * np.pi, N)
    A_ = C['red'] + R['red'] * np.stack([np.cos(a), np.sin(a)], 1)
    B_ = C['green'] + R['green'] * np.stack([np.cos(b), np.sin(b)], 1)
    C_ = C['green'] + R['green'] * np.stack([np.cos(c), np.sin(c)], 1)
    h1 = hits(A_, B_, C['black'], R['black']); h2 = hits(B_, C_, C['black'], R['black'])
    print('fractions', h1.mean(), h2.mean())
    gap = P('gap', 0.03); cap = P('cap', 0.12)
    ph = int(H * (1 - cap - gap) / 2)
    cxm = P('cx', 1.25); span = P('span', 5.6)
    view = (cxm - span / 2, cxm + span / 2, -span / 2 * ph / W, span / 2 * ph / W)
    paper = np.array([0.993, 0.986, 0.978], np.float32)
    img = np.ones((H, W, 3), np.float32) * paper
    panels = [(A_, B_, h1, (a / (2 * np.pi)) * P('hs', 0.8), WARM), (B_, C_, h2, (b / (2 * np.pi)) * P('hs', 0.8) + 0.5, COOL)]
    tops = [int(H * 0.02), int(H * 0.02) + ph + int(H * gap)]
    for (p, q, hit, hue, st), top in zip(panels, tops):
        Ab = panel(W, ph, p, q, hit, hue, st, view, R, C)
        Am = P('amax', 2.2)
        Ab = Am * (1 - np.exp(-Ab * P('gain', 0.9) / Am))
        fy = np.minimum(np.arange(ph), ph - 1 - np.arange(ph)) / (P('feather', 0.10) * ph)
        fx = np.minimum(np.arange(W), W - 1 - np.arange(W)) / (P('feather', 0.10) * ph)
        win = np.clip(fy, 0, 1)[:, None] * np.clip(fx, 0, 1)[None, :]
        win = win * win * (3 - 2 * win)
        img[top:top + ph] = paper * np.exp(-Ab * win[..., None])
    # circles: ink rims + the black pearl
    S = P('ink_ss', 3)
    big = Image.fromarray((np.clip(img, 0, 1) ** (1 / 2.2) * 255).astype(np.uint8)).resize((W * S, H * S), Image.BICUBIC)
    dr = ImageDraw.Draw(big, 'RGBA')
    def topix(x, y, top):
        return ((x - view[0]) / (view[1] - view[0]) * W * S, top * S + (view[3] - y) / (view[3] - view[2]) * ph * S)
    for top in tops:
        for name, colr in [('red', (232, 92, 112, 235)), ('green', (70, 180, 140, 235))]:
            cx, cy = topix(*C[name], top); rr = R[name] / (view[1] - view[0]) * W * S
            lw = int(P('lw', 3.2) * S)
            dr.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=colr, width=lw)
    big = big.resize((W, H), Image.LANCZOS)
    arr = np.asarray(big).astype(np.float32) / 255
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    base = np.array(P('pearl', '0.62,0.50,0.74').split(','), float)
    for top in tops:
        cx, cy = topix(*C['black'], top); cx /= S; cy /= S; rr = R['black'] / (view[1] - view[0]) * W
        # soft shadow
        sh = np.exp(-(((xx - cx - 0.12 * rr) ** 2 + (yy - cy - 0.18 * rr) ** 2) / (1.15 * rr) ** 2) ** 2)
        arr *= (1 - 0.18 * sh)[..., None]
        dx, dy = (xx - cx) / rr, (yy - cy) / rr; q = dx * dx + dy * dy
        inside = np.clip((1 - np.sqrt(q)) * rr, 0, 1)
        nz = np.sqrt(np.clip(1 - q, 0, 1))
        L = np.array([-0.45, -0.55, 0.70]); L /= np.linalg.norm(L)
        lam = np.clip(dx * L[0] + dy * L[1] + nz * L[2], 0, 1)
        Hh = L + np.array([0, 0, 1.0]); Hh /= np.linalg.norm(Hh)
        sp = np.clip(dx * Hh[0] + dy * Hh[1] + nz * Hh[2], 0, 1) ** 140
        rim = (1 - nz) ** 3
        col = base * (0.55 + 0.55 * lam[..., None]) + 0.55 * sp[..., None] + 0.25 * rim[..., None] * np.array([1.0, 0.55, 0.5])
        arr = arr * (1 - inside[..., None]) + np.clip(col, 0, 1) * inside[..., None]
    big = Image.fromarray((np.clip(arr, 0, 1) * 255 + 0.5).astype(np.uint8))
    from caption import caption, font
    fs = int(W * 0.0125)
    labels = ['a line through a point on the red circle and a point on the green',
              'a line through two points on the green circle']
    for (p, q, hit, hue, st), top, lab in zip(panels, tops, labels):
        d = ImageDraw.Draw(big)
        d.text((int(W * 0.03), top + int(ph * 0.04)), lab, font=font('i', fs), fill=(92, 77, 102))
        d.text((int(W * 0.03), top + int(ph * 0.04) + int(fs * 1.4)),
               f'{hit.sum():,} of {len(hit):,} drawn lines pierce the pearl  ({100 * hit.mean():.1f} %)',
               font=font('m', int(fs * 0.85)), fill=(120, 105, 130))
    caption(big, int(W * 0.96), tops[1] + ph + int(H * 0.012), P('title', 'Two Veils, One Chance'),
            [(f'circles in a row, radii 1 : r : r\u00b2 with r = {P("r", 0.62)}; both kinds of random line pierce the pearl with probability {P("pexact", 0.3047):.4f}', 'i', 0.62),
             ('MathOverflow 499477  \u00b7  warm: red\u2013green lines   cool: green\u2013green chords   full colour = the line meets the pearl', 'r', 0.5)],
            int(W * 0.03), align='right')
    big.save(out)
    np.save(out.replace('.png', '_frac.npy'), np.array([h1.mean(), h2.mean()]))


if __name__ == '__main__':
    main()
