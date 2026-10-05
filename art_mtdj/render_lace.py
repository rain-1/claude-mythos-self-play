"""render_lace.py — Narayana parity as a lace doily (MO 515413).

C_n(t) = sum_k N(n,k+1) t^k.  Row n of the parity triangle (coefficients mod 2) is laid on a triangular lattice
with its apex at the centre; six copies make a hexagonal doily.  Each odd coefficient is a stitch, neighbouring
stitches are tied by thread, and the hue changes with the power-of-two band 2^m <= n < 2^(m+1) — the bands
the OP's identity f(2^m + k) = f(k)(1 + t^(2^m)) is about.

usage: render_lace.py S out.png [key=val ...]
"""
import sys, numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter
sys.path.insert(0, '.')
from caption import caption, font
from narayana import table

ARG = dict(a.split('=', 1) for a in sys.argv[3:] if '=' in a)
def P(k, d): return type(d)(ARG.get(k, d))

BAND = [(250, 150, 160), (252, 176, 130), (250, 206, 110), (170, 220, 130), (110, 210, 180),
        (120, 180, 245), (165, 150, 245), (225, 145, 225)]


HP = 0.6
def hue(n, R):
    t = ((max(n, 1) - 1) / (R - 1)) ** HP * (len(BAND) - 1)
    i = min(int(t), len(BAND) - 2); f = t - i
    a, b = np.array(BAND[i], float), np.array(BAND[i + 1], float)
    return tuple(int(x) for x in a ** (1 - f) * b ** f)


def main():
    S, out = int(sys.argv[1]), sys.argv[2]
    H = P('H', S)
    R = P('R', 128)
    T = table(R)
    SS = 3
    im = Image.new('RGB', (S * SS, H * SS), (253, 251, 249))
    lace = Image.new('L', (S * SS, H * SS), 0)            # coverage mask for the shadow
    col = Image.new('RGB', (S * SS, H * SS), (0, 0, 0))
    dl = ImageDraw.Draw(lace); dc = ImageDraw.Draw(col)
    cx, cy = S * SS / 2, H * SS * P('cy', 0.46)
    rad = P('rad', 0.385) * S * SS
    h = rad / (R - 1)                                            # row spacing (apex to edge = R rows)
    sp = h * 2 / np.sqrt(3)                                # lattice spacing along a row
    pts = {}
    for w in range(6):
        ang = -np.pi / 2 + w * np.pi / 3                   # wedge axis direction
        u = np.array([np.cos(ang), np.sin(ang)]); v = np.array([-u[1], u[0]])
        for n in range(1, R + 1):
            for k in range(n - 1 if n > 1 else 1):       # the last stitch of a row belongs to the next wedge
                if T[n, k] and not (n == 1 and w > 0):
                    p = np.array([cx, cy]) + u * (n - 1) * h + v * (k - (n - 1) / 2) * sp
                    pts[(w, n, k)] = p
    tw = max(1, int(P('tw', 0.22) * sp))
    for (w, n, k), p in pts.items():
        c = hue(n, R)
        nb = [(w, n, k + 1), (w, n + 1, k), (w, n + 1, k + 1)]
        if k == n - 2: nb[0] = ((w + 1) % 6, n, 0)
        if k == n - 2: nb.append(((w + 1) % 6, n + 1, 0))
        if n == 1: nb = [(ww, 2, 0) for ww in range(6)]
        for q in nb:
            if q in pts:
                a, b = tuple(p), tuple(pts[q])
                dl.line([a, b], fill=255, width=tw); dc.line([a, b], fill=c, width=tw)
    rr = P('ring', 0.30) * sp
    for (w, n, k), p in pts.items():
        c = hue(n, R)
        box = [p[0] - rr, p[1] - rr, p[0] + rr, p[1] + rr]
        dl.ellipse(box, fill=255); dc.ellipse(box, fill=c)
    # downsample
    lace = np.asarray(lace.resize((S, H), Image.LANCZOS)).astype(np.float32) / 255
    col = np.asarray(col.resize((S, H), Image.LANCZOS)).astype(np.float32) / 255
    paper = np.array([0.993, 0.986, 0.978], np.float32)
    # ground: a soft round linen cloth under the doily
    yy, xx = np.mgrid[0:H, 0:S].astype(np.float32)
    shadow = gaussian_filter(lace, P('blur', 3.0))
    shadow = np.roll(np.roll(shadow, int(P('sdy', 4)), 0), int(P('sdx', 3)), 1)
    img = np.broadcast_to(paper, (H, S, 3)).copy()
    if P('plate', 1):
        pr = P('plater', 0.47) * S; d0 = np.hypot(xx - cx / SS, yy - cy / SS)
        pl = np.clip((pr - d0) / 2.0, 0, 1)[..., None]
        ptint = np.array([float(v) for v in P('ptint', '0.985,0.955,0.93').split(',')])
        psh = gaussian_filter((d0 < pr).astype(np.float32), 10)
        psh = np.roll(np.roll(psh, 10, 0), 7, 1)[..., None]
        img = img * (1 - 0.10 * psh * (1 - pl))
        rim = np.exp(-((d0 - pr * 0.96) / (0.006 * S)) ** 2)[..., None]
        img = img * (1 - pl) + (ptint * (1 - 0.03 * rim)) * pl
    img = img * (1 - P('shd', 0.28) * shadow[..., None])
    tint = col / np.maximum(lace[..., None], 1e-3)
    # lace body: tint, lightened toward its top-left (a thread highlight)
    gy, gx = np.gradient(gaussian_filter(lace, 0.8))
    hl = np.clip(-(gx + gy) * P('hl', 3.0), 0, 0.6)[..., None]
    body = tint * (0.92) + (1 - tint * 0.92) * hl
    img = img * (1 - lace[..., None]) + body * lace[..., None]
    out_im = Image.fromarray((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8))
    fs = int(S * 0.024)
    caption(out_im, int(S * 0.955), int(H * P('capy', 0.885)), P('title', 'Six Copies of an Odd Triangle'),
            [(f'Narayana polynomials C_n(t) for n ≤ {R}: every odd coefficient is a stitch, six copies of the parity triangle make the doily', 'i', 0.5),
             ('hue walks outward with n; the OP’s identity f(2^m + k) = f(k)(1 + t^(2^m)) makes rows 2^m to 2^(m+1) two copies of everything before them', 'r', 0.40),
             ('MathOverflow 515413  ·  identity checked for every n ≤ 512', 'r', 0.40)],
            fs, align='right')
    out_im.save(out)


if __name__ == '__main__':
    main()
