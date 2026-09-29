"""sorbet.py — Opus 5.5's render stack for this routine (started 2026-09-29).

A brighter cousin of the old subtractive pastel stack: everything is still pigment
density on a sheet (Beer–Lambert, so overlaps mix like glazes instead of adding to
white), but the sheet is a cool, luminous white, the pigments are 'sorbet' tints
(high value, clean chroma), and density is soft-capped low so nothing reaches mud.
Ink is a single plum-grey, used sparingly; one coral accent per piece.
"""
import numpy as np
from scipy.ndimage import gaussian_filter, zoom
from PIL import Image, ImageDraw, ImageFont

# linear-RGB transmission of each pigment at unit density
PIG = dict(
    strawberry=(1.00, 0.52, 0.62), coral=(1.00, 0.50, 0.42), peach=(1.00, 0.72, 0.52),
    butter=(1.00, 0.90, 0.45), honey=(1.00, 0.80, 0.38), lime=(0.78, 0.95, 0.46),
    mint=(0.52, 0.93, 0.74), sky=(0.52, 0.84, 1.00), periwinkle=(0.62, 0.66, 1.00),
    lilac=(0.80, 0.62, 1.00), bubblegum=(1.00, 0.60, 0.90), rose=(1.00, 0.70, 0.78),
    ink=(0.36, 0.30, 0.40), plum=(0.55, 0.40, 0.60))
WHEEL = ['strawberry', 'peach', 'butter', 'lime', 'mint', 'sky', 'periwinkle', 'lilac', 'bubblegum']

FONTS = dict(
    serif_bold='/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf',
    serif='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf',
    italic='/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf',
    sans='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    mono='/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf')


def absorb(tint):
    if isinstance(tint, str):
        tint = PIG[tint]
    return -np.log(np.clip(np.asarray(tint, np.float32), 1e-3, 1.0)).astype(np.float32)


def wheel_tint(h):
    """h in [0,1) -> transmission rgb, interpolating around WHEEL"""
    n = len(WHEEL)
    x = (h % 1.0) * n
    i = int(np.floor(x)) % n
    t = x - np.floor(x)
    a, b = np.array(PIG[WHEEL[i]]), np.array(PIG[WHEEL[(i + 1) % n]])
    return tuple(a ** (1 - t) * b ** t)


def lowfreq(H, W, cells, seed, amp=1.0):
    rng = np.random.default_rng(seed)
    h, w = max(2, H // cells), max(2, W // cells)
    n = gaussian_filter(rng.standard_normal((h, w)).astype(np.float32), 1.0)
    n = zoom(n, (H / h, W / w), order=3)[:H, :W]
    return amp * n / (np.abs(n).max() + 1e-9)


class Sheet:
    def __init__(self, W, H, seed=0, base=(0.992, 0.985, 0.975), drift=0.012, grain=0.010):
        self.W, self.H = W, H
        self.A = np.zeros((H, W, 3), np.float32)
        p = np.ones((H, W, 3), np.float32) * np.asarray(base, np.float32)
        g = np.random.default_rng(seed).standard_normal((H, W)).astype(np.float32)
        p *= (1 + lowfreq(H, W, max(16, W // 5), seed + 1, drift) + grain * gaussian_filter(g, 0.8) / 0.35)[..., None]
        self.paper = p

    def wash(self, density, tint, k=1.0):
        self.A += (k * np.clip(np.asarray(density, np.float32), 0, None))[..., None] * absorb(tint)[None, None, :]

    def wash_rgb(self, dens_rgb):
        """dens_rgb: (H,W,3) absorbance directly"""
        self.A += dens_rgb.astype(np.float32)

    def lighten(self, mask, f=0.6):
        self.A *= (1 - f * np.asarray(mask, np.float32))[..., None]

    def develop(self, dmax=1.6, glow=0.0):
        A = dmax * (1 - np.exp(-self.A / dmax))
        lin = np.clip(self.paper * np.exp(-A), 0, 1)
        if glow > 0:   # soft light bleed: pastel luminance haze
            s = max(1.0, self.W / 400)
            small = lin[::4, ::4]
            b = zoom(gaussian_filter(small, (s, s, 0)), (lin.shape[0] / small.shape[0], lin.shape[1] / small.shape[1], 1), order=1)
            lin = np.clip(1 - (1 - lin) * (1 - glow * b), 0, 1)   # screen
        srgb = np.where(lin <= 0.0031308, 12.92 * lin, 1.055 * np.power(lin, 1 / 2.4) - 0.055)
        srgb = srgb * 255 + np.random.default_rng(9).uniform(-0.5, 0.5, srgb.shape).astype(np.float32)
        return Image.fromarray(np.clip(srgb + 0.5, 0, 255).astype(np.uint8))


def lines(W, H, polylines, width, weights=None, sigma=None):
    """many polylines into one F density image (one ImageDraw, fast)."""
    im = Image.new('F', (W, H), 0.0)
    dr = ImageDraw.Draw(im)
    if weights is None:
        weights = [1.0] * len(polylines)
    for pts, wt in zip(polylines, weights):
        dr.line([tuple(map(float, q)) for q in pts], fill=float(wt), width=int(max(1, round(width))), joint='curve')
    a = np.asarray(im, np.float32).copy()
    return gaussian_filter(a, sigma) if sigma else a


def discs(W, H, xs, ys, rs, ws=None, sigma=None):
    im = Image.new('F', (W, H), 0.0)
    dr = ImageDraw.Draw(im)
    if ws is None:
        ws = np.ones(len(xs))
    for x, y, r, w in zip(xs, ys, rs, ws):
        dr.ellipse([x - r, y - r, x + r, y + r], fill=float(w))
    a = np.asarray(im, np.float32).copy()
    return gaussian_filter(a, sigma) if sigma else a


def text_mask(W, H, items):
    """items: (text, x, y, size, fontkey, anchor) -> (H,W) 0..1"""
    im = Image.new('L', (W, H), 0)
    dr = ImageDraw.Draw(im)
    for (txt, x, y, size, fk, anchor) in items:
        dr.text((x, y), txt, fill=255, font=ImageFont.truetype(FONTS[fk], int(size)), anchor=anchor)
    return np.asarray(im, np.float32) / 255.0


def text_w(txt, size, fk):
    return ImageFont.truetype(FONTS[fk], int(size)).getlength(txt)


def finish(img, size, path):
    if img.size[0] != size:
        img = img.resize((size, size * img.size[1] // img.size[0]), Image.LANCZOS)
    img.save(path, optimize=True)
    return img
