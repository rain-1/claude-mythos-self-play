"""pastel.py — Fable 5.1's subtractive watercolor stack (third pastel run).

Everything is pigment DENSITY on warm paper (Beer–Lambert): the sheet accumulates
absorbance A = sum_i density_i * (-log tint_i); the print is paper * exp(-knee(A)).
Black is unreachable by construction (soft knee at dmax).
"""
import numpy as np
from scipy.ndimage import gaussian_filter, zoom
from PIL import Image, ImageDraw, ImageFont

# bright pigment box (linear RGB transmission at unit density)
PIG = dict(
    coral=(1.00, 0.55, 0.50), apricot=(1.00, 0.74, 0.46), lemon=(1.00, 0.93, 0.48),
    pistachio=(0.73, 0.88, 0.50), mint=(0.55, 0.90, 0.72), aqua=(0.50, 0.85, 0.93),
    cornflower=(0.55, 0.68, 0.96), lavender=(0.73, 0.63, 0.96), orchid=(0.89, 0.58, 0.91),
    blush=(0.99, 0.72, 0.82), ink=(0.34, 0.31, 0.36), sepia=(0.58, 0.46, 0.36),
    paperblue=(0.80, 0.86, 0.95), paperpink=(0.98, 0.88, 0.90))
CYCLE = ['coral', 'apricot', 'lemon', 'pistachio', 'mint', 'aqua', 'cornflower', 'lavender', 'orchid', 'blush']

FONTS = dict(
    serif_bold='/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf',
    serif='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf',
    italic='/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf',
    mono='/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf')


def absorb(tint):
    return -np.log(np.clip(np.asarray(tint, np.float32), 1e-3, 1.0)).astype(np.float32)


def noise(H, W, sigma, seed):
    rng = np.random.default_rng(seed)
    n = rng.standard_normal((H, W)).astype(np.float32)
    if sigma > 0:
        n = gaussian_filter(n, sigma)
    n /= (n.std() + 1e-9)
    return n


def lowfreq(H, W, cells, seed, amp=1.0):
    """smooth field: coarse noise upsampled (cheap, no giant blur)"""
    rng = np.random.default_rng(seed)
    h, w = max(2, H // cells), max(2, W // cells)
    n = rng.standard_normal((h, w)).astype(np.float32)
    n = gaussian_filter(n, 1.0)
    n = zoom(n, (H / h, W / w), order=3)[:H, :W]
    n /= (np.abs(n).max() + 1e-9)
    return amp * n


class Sheet:
    def __init__(self, W, H, seed=0, base=(0.985, 0.975, 0.950), drift=0.025, fiber=0.030):
        self.W, self.H = W, H
        self.A = np.zeros((H, W, 3), np.float32)
        p = np.ones((H, W, 3), np.float32) * np.asarray(base, np.float32)
        d = lowfreq(H, W, max(16, W // 6), seed + 1, drift)
        f = noise(H, W, 0.7, seed + 2) * fiber
        p *= (1 + d + f)[..., None]
        self.paper = p

    def wash(self, density, tint, granulate=0.0, edge=0.0, seed=7):
        """density: (H,W) float; tint: name or rgb"""
        if isinstance(tint, str):
            tint = PIG[tint]
        d = np.asarray(density, np.float32)
        if granulate > 0:
            g = noise(self.H, self.W, 1.6, seed)
            d = d * (1 + granulate * g)
        if edge > 0:
            b = gaussian_filter(d, 1.5)
            gy, gx = np.gradient(b)
            d = d + edge * np.hypot(gx, gy) * 4.0
        d = np.clip(d, 0, None)
        self.A += d[..., None] * absorb(tint)[None, None, :]

    def lighten(self, mask, f=0.6):
        """lift pigment under a mask (a caption strip): absorbance *= (1 - f*mask)"""
        self.A *= (1 - f * np.asarray(mask, np.float32))[..., None]

    def caption_strip(self, y0, y1, f=0.62):
        """soft lightened band between rows y0..y1 (fractions of H)"""
        yy = np.arange(self.H, dtype=np.float32) / self.H
        band = np.clip((yy - y0) / 0.012, 0, 1) * np.clip((y1 - yy) / 0.012, 0, 1)
        self.lighten(np.repeat(band[:, None], self.W, axis=1), f)

    def develop(self, dmax=2.4):
        A = dmax * (1 - np.exp(-self.A / dmax))
        lin = self.paper * np.exp(-A)
        lin = np.clip(lin, 0, 1)
        srgb = np.where(lin <= 0.0031308, 12.92 * lin, 1.055 * lin ** (1 / 2.4) - 0.055)
        rng = np.random.default_rng(99)
        srgb = srgb * 255 + rng.uniform(-0.5, 0.5, srgb.shape).astype(np.float32)
        return Image.fromarray(np.clip(srgb + 0.5, 0, 255).astype(np.uint8))


def ink_from_distance(d, w):
    """crisp ink line: density exp(-(d/w)^2)"""
    return np.exp(-(np.asarray(d, np.float32) / w) ** 2).astype(np.float32)


def draw_lines_density(W, H, segs, width, weights=None, sigma=None):
    """segs: (N,4) x0,y0,x1,y1 in pixel coords. Returns density (H,W) float in [0,1]-ish.
    Draws with PIL into an 'F' image then blurs slightly for softness."""
    im = Image.new('F', (W, H), 0.0)
    dr = ImageDraw.Draw(im)
    segs = np.asarray(segs, np.float64)
    if weights is None:
        weights = np.ones(len(segs))
    for (x0, y0, x1, y1), wt in zip(segs, weights):
        dr.line([(x0, y0), (x1, y1)], fill=float(wt), width=int(max(1, round(width))))
    a = np.asarray(im, np.float32)
    if sigma:
        a = gaussian_filter(a, sigma)
    return a


def polyline_density(W, H, pts, width, weight=1.0, sigma=None, closed=False):
    im = Image.new('F', (W, H), 0.0)
    dr = ImageDraw.Draw(im)
    p = [tuple(map(float, q)) for q in pts]
    if closed:
        p.append(p[0])
    dr.line(p, fill=float(weight), width=int(max(1, round(width))), joint='curve')
    a = np.asarray(im, np.float32)
    if sigma:
        a = gaussian_filter(a, sigma)
    return a


def discs_density(W, H, xs, ys, rs, ws, sigma=None):
    """soft pastel beads: hard discs drawn in an F image, then blurred."""
    im = Image.new('F', (W, H), 0.0)
    dr = ImageDraw.Draw(im)
    for x, y, r, w in zip(xs, ys, rs, ws):
        dr.ellipse([x - r, y - r, x + r, y + r], fill=float(w))
    a = np.asarray(im, np.float32)
    if sigma:
        a = gaussian_filter(a, sigma)
    return a


def text_density(W, H, items):
    """items: list of (text, x, y, size, fontkey, anchor). Returns (H,W) float mask 0..1."""
    im = Image.new('L', (W, H), 0)
    dr = ImageDraw.Draw(im)
    for (txt, x, y, size, fk, anchor) in items:
        try:
            f = ImageFont.truetype(FONTS[fk], int(size))
        except Exception as e:
            print('FONT FAIL', fk, e)
            f = ImageFont.load_default()
        dr.text((x, y), txt, fill=255, font=f, anchor=anchor)
    return np.asarray(im, np.float32) / 255.0


def text_width(txt, size, fk):
    f = ImageFont.truetype(FONTS[fk], int(size))
    l, t, r, b = f.getbbox(txt)
    return r - l


def finish(img, final_size, path):
    if img.size[0] != final_size[0]:
        img = img.resize(final_size, Image.LANCZOS)
    img.save(path, optimize=True)
    print('saved', path, img.size)
    return img


def hue_to_pigments(h):
    """cyclic hue h in [0,1) -> (idx0, idx1, t) over CYCLE (10 pigments)"""
    h = np.mod(h, 1.0) * len(CYCLE)
    i0 = np.floor(h).astype(int) % len(CYCLE)
    i1 = (i0 + 1) % len(CYCLE)
    t = (h - np.floor(h)).astype(np.float32)
    return i0, i1, t


def mix_tint(a, b, t):
    """mix two tints in absorbance space (never through grey)"""
    Aa, Ab = absorb(PIG[a]), absorb(PIG[b])
    return np.exp(-((1 - t) * Aa + t * Ab))
