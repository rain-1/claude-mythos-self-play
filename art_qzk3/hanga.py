"""hanga.py -- a small procedural woodblock-print (mokuhanga) engine.

A print is a sheet of paper and an ordered list of BLOCKS.  A block is a coverage
mask (what the carver left standing), one transparent water-based ink, and the way
the printer wiped it: flat, or graded (bokashi).  Inks multiply (subtractive), every
block carries its own wood grain and baren speckle, is registered a pixel or two off,
and pools a little at its edges.

    S = Sheet(size, seed)
    m = S.mask(lambda d: d.polygon(S.px(pts), fill=255))      # PIL drawing, supersampled
    S.block(m, INK['indigo'], bokashi=S.grad_y(0.0, 0.2))     # graded wipe
    S.key(m_lines)                                            # sumi key block
    S.save('x.png')
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy import ndimage as ndi

INK = dict(
    sumi=(0.150, 0.140, 0.190), indigo=(0.105, 0.225, 0.430), prussian=(0.130, 0.330, 0.560),
    aqua=(0.560, 0.790, 0.820), sky=(0.700, 0.850, 0.880), celadon=(0.640, 0.800, 0.690),
    moss=(0.560, 0.690, 0.380), pine=(0.120, 0.330, 0.290), ochre=(0.900, 0.740, 0.420),
    sand=(0.945, 0.860, 0.640), vermilion=(0.850, 0.230, 0.140), rose=(0.950, 0.600, 0.520),
    peach=(0.980, 0.760, 0.560), plum=(0.470, 0.300, 0.450), slate=(0.430, 0.540, 0.640),
    straw=(0.960, 0.880, 0.560), wood=(0.720, 0.470, 0.280), grey=(0.620, 0.630, 0.640),
)
PAPER = (0.957, 0.925, 0.846)
SERIF_B = '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'
SERIF = '/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf'
SERIF_I = '/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf'


def fbm(H, W, rng, base=4, octaves=5, aspect=1.0, gain=0.5):
    """value noise in [0,1]; aspect>1 stretches features along x."""
    out = np.zeros((H, W), np.float32); amp = 1.0; tot = 0.0
    for o in range(octaves):
        gy = max(2, int(base * 2 ** o)); gx = max(2, int(base * 2 ** o / aspect))
        g = rng.random((gy + 3, gx + 3)).astype(np.float32)
        z = ndi.zoom(g, (H / gy, W / gx), order=1)[:H, :W]
        if z.shape != (H, W):
            z = np.pad(z, ((0, H - z.shape[0]), (0, W - z.shape[1])), mode='edge')
        out += amp * z; tot += amp; amp *= gain
    return out / tot


class Sheet:
    def __init__(self, size, seed=0, ss=2, paper=PAPER):
        self.W = self.H = size; self.ss = ss; self.rng = np.random.default_rng(seed)
        H = W = size; rng = self.rng
        self.img = np.empty((H, W, 3), np.float32); self.img[:] = paper
        # washi: soft mottling, long fibres, a few flecks
        mott = fbm(H, W, rng, base=6, octaves=4) - 0.5
        fine = fbm(H, W, rng, base=size // 6, octaves=2) - 0.5
        fib = Image.new('L', (W, H), 0); d = ImageDraw.Draw(fib)
        for _ in range(int(2600 * (size / 1024) ** 2 / 4)):
            x, y = rng.random(2) * size; a = rng.random() * np.pi; L = size * rng.uniform(.01, .05)
            c = rng.uniform(-.5, .5); pts = []
            for t in np.linspace(0, 1, 7):
                pts.append((x + L * t * np.cos(a + c * t), y + L * t * np.sin(a + c * t)))
            d.line(pts, fill=int(rng.uniform(60, 200)), width=1)
        fib = np.asarray(fib.filter(ImageFilter.GaussianBlur(0.6)), np.float32) / 255
        tone = 1 + 0.045 * mott + 0.030 * fine
        self.img *= tone[..., None]
        self.img *= 1 - fib[..., None] * np.array([0.045, 0.060, 0.090], np.float32)
        self.fibre = fib
        # one plank of grain per sheet family; blocks pick shifted/rotated versions
        self._grain_cache = {}
        self.tooth = fbm(H, W, rng, base=size // 3, octaves=2)        # paper tooth for speckle

    # ---------- geometry helpers ----------
    def px(self, pts):
        s = self.W * self.ss
        return [(float(x) * s, float(y) * s) for x, y in pts]

    def mask(self, draw_fn, blur=0.0):
        """draw_fn(ImageDraw) paints white on black at ss-times resolution -> float mask"""
        s = self.W * self.ss
        im = Image.new('L', (s, s), 0); draw_fn(ImageDraw.Draw(im))
        if self.ss > 1: im = im.reduce(self.ss)
        if blur: im = im.filter(ImageFilter.GaussianBlur(blur * self.W / 1024))
        return np.asarray(im, np.float32) / 255

    def grad_y(self, y0, y1, power=1.0):
        """1 at y0 fading to 0 at y1 (normalised coords)"""
        y = np.linspace(0, 1, self.H, dtype=np.float32)[:, None]
        t = np.clip((y - y1) / (y0 - y1), 0, 1) ** power
        return np.broadcast_to(t * t * (3 - 2 * t), (self.H, self.W))

    def grad_r(self, cx, cy, r0, r1, power=1.0):
        y, x = np.mgrid[0:self.H, 0:self.W].astype(np.float32) / self.W
        r = np.hypot(x - cx, y - cy)
        t = np.clip((r - r1) / (r0 - r1), 0, 1) ** power
        return t * t * (3 - 2 * t)

    def grain(self, k=0):
        """wood grain 0..1, mostly horizontal, different per block index"""
        if k in self._grain_cache: return self._grain_cache[k]
        rng = np.random.default_rng(1000 + k); H, W = self.H, self.W
        warp = fbm(H, W, rng, base=3, octaves=4, aspect=6.0)
        y = np.linspace(0, 1, H, dtype=np.float32)[:, None]
        f = rng.uniform(26, 44)
        g = 0.5 + 0.5 * np.sin(2 * np.pi * (f * y * 0.35 + 9.0 * warp))
        g = g ** 1.6
        streak = fbm(H, W, rng, base=self.W // 10, octaves=1, aspect=14.0)
        g = 0.75 * g + 0.25 * streak
        self._grain_cache[k] = g.astype(np.float32)
        if len(self._grain_cache) > 4: self._grain_cache.pop(next(iter(self._grain_cache)))
        return self._grain_cache[k]

    # ---------- printing ----------
    def block(self, mask, ink, strength=1.0, bokashi=None, grain=0.16, speckle=0.10,
              rim=0.18, misreg=1.0, k=None, wobble=True):
        """print one colour block."""
        rng = self.rng; sc = self.W / 1024
        m = mask
        if wobble:   # hand-cut edge: threshold the soft mask against fine noise
            pass
        if misreg:
            dx, dy = rng.normal(0, misreg * sc * 0.9, 2)
            m = ndi.shift(m, (dy, dx), order=1, mode='constant')
        dens = m.copy()
        if rim:      # ink pools at the edge of the block
            inner = ndi.gaussian_filter(m, 2.2 * sc)
            dens *= 1 + rim * np.clip(m - inner, 0, 1) * 2.2
        if bokashi is not None: dens = dens * bokashi
        if grain:
            g = self.grain(int(rng.integers(0, 6)) if k is None else k)
            dens *= 1 - grain * g
        if speckle:  # goma-zuri: the baren misses the valleys of the paper
            n = rng.random(m.shape, dtype=np.float32)
            n = ndi.gaussian_filter(n, 0.7 * sc)
            n = (n - n.mean()) / (n.std() + 1e-6)
            dens *= 1 - speckle * np.clip(0.5 + 0.5 * n + 1.4 * (self.tooth - 0.5), 0, 1.4)
            dens *= 1 - 0.35 * self.fibre * speckle * 4
        dens = np.clip(dens * strength, 0, 1.25)
        ink = np.asarray(ink, np.float32)
        self.img *= 1 - dens[..., None] * (1 - ink)

    def key(self, mask, ink=INK['sumi'], strength=0.96, rough=0.5):
        """key block: crisp lines, slightly broken where the block is worn"""
        rng = self.rng; sc = self.W / 1024
        n = ndi.gaussian_filter(rng.random(mask.shape, dtype=np.float32), 1.1 * sc)
        n = (n - n.mean()) / (n.std() + 1e-6)
        m = np.clip(mask * (1.0 + 0.18 * rough * n) - 0.10 * rough * np.clip(n, 0, 3), 0, 1)
        self.block(m, ink, strength=strength, grain=0.06, speckle=0.05, rim=0.0, misreg=0.0)

    def lift(self, mask, amount=1.0):
        """leave paper: used by masks before printing (returns complement helper)"""
        return 1 - np.clip(mask * amount, 0, 1)

    # ---------- text ----------
    def text_mask(self, items):
        """items: (x, y, string, font_path, size_norm, anchor)"""
        def f(d):
            s = self.W * self.ss
            for x, y, t, fp, sz, anc in items:
                d.text((x * s, y * s), t, font=ImageFont.truetype(fp, int(sz * s)), fill=255, anchor=anc)
        return self.mask(f)

    def save(self, path, sat=1.0):
        a = np.clip(self.img, 0, 1)
        if sat != 1.0:
            l = a.mean(2, keepdims=True); a = np.clip(l + (a - l) * sat, 0, 1)
        Image.fromarray((a * 255 + 0.5).astype(np.uint8)).save(path, optimize=True)


def stroke(d, pts, width, fill=255):
    """round-capped polyline with per-point width (pts in pixels)"""
    pts = np.asarray(pts, float); w = np.broadcast_to(np.asarray(width, float), (len(pts),))
    for i in range(len(pts) - 1):
        d.line([tuple(pts[i]), tuple(pts[i + 1])], fill=fill, width=max(1, int(round((w[i] + w[i + 1]) / 2))))
    for (x, y), r in zip(pts, w / 2):
        d.ellipse([x - r, y - r, x + r, y + r], fill=fill)


def bezier(p0, p1, p2, n=60):
    t = np.linspace(0, 1, n)[:, None]
    return (1 - t) ** 2 * np.asarray(p0) + 2 * t * (1 - t) * np.asarray(p1) + t ** 2 * np.asarray(p2)
