"""render_lipo.py — the book without sevens (MO 515601).

d(n) deletes every digit 7 from n (d(2798) = 298, d(7) = 0).  Every n that contains a 7 sends an arc down to
d(n).  Arcs are glazed onto paper; colour = how many sevens were deleted, the axis is log10(n+1) so every
decade gets the same room and the self-similarity (block a7b -> ab, at every scale) shows.

usage: render_lipo.py W H out.png [key=val ...]
"""
import sys, numpy as np
from PIL import Image, ImageDraw

ARG = dict(a.split('=', 1) for a in sys.argv[4:] if '=' in a)
def P(k, d): return type(d)(ARG.get(k, d))

TINT = {0: (1.00, 0.72, 0.50), 1: (0.54, 0.90, 0.72), 2: (0.52, 0.76, 1.00), 3: (0.78, 0.60, 1.00),
        4: (1.00, 0.56, 0.74), 5: (1.00, 0.84, 0.46)}


def d7(n):
    s = str(n).replace('7', '')
    return int(s) if s else 0


def main():
    W, H, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    Nmax = P('N', 100000)
    mode = P('mode', 'log')
    ns = np.array([n for n in range(1, Nmax + 1) if '7' in str(n)])
    ds = np.array([d7(n) for n in ns]); k7 = np.array([len(str(n)) - 1 - str(n).index('7') for n in ns])
    print('arcs', len(ns))
    if mode == 'log':
        X = lambda v: np.log10(np.asarray(v, float) + 1) / np.log10(Nmax + 1)
    else:
        X = lambda v: np.asarray(v, float) / Nmax
    ml, mr = P('ml', 0.05), P('mr', 0.05)
    base = P('base', 0.62)            # axis height (fraction of H)
    SS = 2; Ws, Hs = W * SS, H * SS
    A = np.zeros((Hs * Ws, 3), np.float32)
    x0 = (ml + (1 - ml - mr) * X(ds)) * Ws; x1 = (ml + (1 - ml - mr) * X(ns)) * Ws
    c = (x0 + x1) / 2; r = (x1 - x0) / 2
    hscale = P('hs', 1.0)
    ab = -np.log(np.array([TINT[min(k, 5)] for k in k7], np.float32))
    wt = P('k', 0.35) / np.maximum(1, (np.log(1 + r / SS)) ** P('rpow', 0.0))
    for i0 in range(0, len(ns), 256):
        cc, rr = c[i0:i0 + 256], r[i0:i0 + 256]
        L = np.pi * rr * max(hscale, 1)
        m = int(max(8, L.max() * 1.2))
        t = np.linspace(0, np.pi, m)
        X_ = cc[:, None] - rr[:, None] * np.cos(t)[None]
        Y_ = base * Hs - hscale * rr[:, None] * np.sin(t)[None]
        # sample density per pixel ~ 1 per arc-length pixel
        step = (np.pi * rr * max(hscale, 1)) / m
        px = X_.astype(np.int64); py = Y_.astype(np.int64)
        ok = (px >= 0) & (px < Ws) & (py >= 0) & (py < Hs)
        idx = (py * Ws + px)[ok]
        w = np.broadcast_to((step * (wt[i0:i0 + 256] if np.ndim(wt) else wt))[:, None], X_.shape)
        for ch in range(3):
            cw = (w * ab[i0:i0 + 256, ch][:, None])[ok]
            A[:, ch] += np.bincount(idx, cw, minlength=Hs * Ws).astype(np.float32)
    A = A.reshape(Hs, Ws, 3).reshape(H, SS, W, SS, 3).mean((1, 3))
    Am = P('amax', 2.0); A = Am * (1 - np.exp(-A * P('gain', 1.0) / Am))
    paper = np.array([0.993, 0.986, 0.978], np.float32)
    img = paper * np.exp(-A)
    # reflection below the axis, faint
    if P('mirror', 1):
        b = int(base * H); h2 = min(H - b, b)
        refl = A[b - h2:b][::-1] * P('mir', 0.22)
        fade = np.linspace(1, 0, h2)[:, None, None] ** 1.5
        img[b:b + h2] = paper * np.exp(-refl * fade)
    im = Image.fromarray((np.clip(img, 0, 1) ** (1 / 2.2) * 255 + 0.5).astype(np.uint8))
    sys.path.insert(0, '.')
    from caption import caption, font
    d = ImageDraw.Draw(im)
    yb = int(base * H)
    d.line([(int(ml * W), yb), (int((1 - mr) * W), yb)], fill=(150, 135, 160), width=max(1, W // 1600))
    fs = int(W * 0.011)
    if mode == 'log':
        for p in range(0, int(np.log10(Nmax)) + 1):
            v = 10 ** p
            xx = (ml + (1 - ml - mr) * X(v)) * W
            d.line([(xx, yb - 6), (xx, yb + 6)], fill=(150, 135, 160), width=2)
            lab = f'{v:,}'
            f = font('m', fs); w = d.textlength(lab, font=f)
            d.text((xx - w / 2, yb + 14), lab, font=f, fill=(130, 115, 140))
    caption(im, int(W * (1 - mr)), int(H * P('capy', 0.83)), P('title', 'The Book Without Sevens'),
            [(f'every n ≤ {Nmax:,} that contains a 7 sends an arc down to the number left when its sevens are crossed out', 'i', 0.55),
             ('peach = one seven, strawberry = two, lilac = three, periwinkle = four, teal = five  ·  log axis: every decade the same width', 'r', 0.44),
             ('MathOverflow 515601: can this map be built from + × − 1/g and the floor function?', 'r', 0.44)],
            int(W * 0.03), align='right')
    im.save(out)


if __name__ == '__main__':
    main()
