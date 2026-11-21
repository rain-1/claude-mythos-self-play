"""chalk.py — chalk on a slate board.

The board has a tooth (a fixed fine noise field).  A stroke is a distance field, a width and a
pressure: chalk is left where the pressure beats the tooth, so light strokes skip and heavy ones
fill; every stroke also sheds a little dust around itself.  Rubbing out leaves a pale smear and a
ghost.  Nothing is anti-aliased by supersampling: all edges are analytic."""
import numpy as np
from scipy import ndimage as ndi
from PIL import Image, ImageDraw, ImageFont

def rgb(h):
    h = h.lstrip('#'); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32) / 255.0

F_I = "/usr/share/fonts/truetype/freefont/FreeSerifItalic.ttf"
F_R = "/usr/share/fonts/truetype/freefont/FreeSerif.ttf"
import os
for cand in ("/usr/share/fonts/truetype/freefont/FreeSerifItalic.ttf", "/usr/share/fonts/opentype/freefont/FreeSerifItalic.otf"):
    if os.path.exists(cand): F_I = cand
for cand in ("/usr/share/fonts/truetype/freefont/FreeSerif.ttf", "/usr/share/fonts/opentype/freefont/FreeSerif.otf"):
    if os.path.exists(cand): F_R = cand

CREAM = rgb('#f4eeda'); RED = rgb('#e2543f'); SLATE = rgb('#1a2233')

class Board:
    def __init__(self, S, seed=0, slate=SLATE):
        self.S = S; self.u = u = S / 4096.0; r = np.random.default_rng(seed); self.rng = r
        self.y, self.x = np.mgrid[0:S, 0:S].astype(np.float32)
        t = r.random((S, S)).astype(np.float32)
        t = ndi.gaussian_filter(t, 0.9 * max(1.0, 1.6 * u))
        t = (t - t.mean()) / t.std()
        # a little horizontal drag in the tooth, as on a board wiped sideways for years
        d = ndi.gaussian_filter(r.standard_normal((S, S)).astype(np.float32), (0.8 * max(1, u), 14 * u)); d /= d.std()
        self.tooth = (0.82 * t + 0.42 * d).astype(np.float32)           # ~N(0,1)
        self.dep = {}                                                    # colour name -> deposit
        self.cols = {}
        self.ground = np.zeros((S, S), np.float32)                       # smeared dust (cream)
        self.slate = slate

    # ---- strokes -------------------------------------------------------------------------
    def lay(self, dist, width, pressure=0.6, colour=CREAM, name='cream', dust=1.0, cov=None):
        """dist: distance to the stroke's centre line in px; width in px (or cov: a ready coverage mask)"""
        if cov is None:
            cov = np.clip(width / 2 - dist + 0.5, 0, 1)
            # chalk is fuller at the middle of the stroke than at its edges
            core = np.clip(1.0 - dist / (width / 2 + 1e-6), 0, 1)
        else: core = cov * 0.6
        g = np.clip((pressure * 2.6 - 0.75 + 0.7 * core - self.tooth) / 0.55, 0, 1)
        dpo = cov * g * (0.55 + 0.45 * np.minimum(1.0, pressure * 1.5))
        if name not in self.dep: self.dep[name] = np.zeros((self.S, self.S), np.float32); self.cols[name] = colour
        self.dep[name] = np.maximum(self.dep[name], dpo)
        if dust > 0:
            ys, xs = np.nonzero(cov > 0)
            if len(ys):
                pad = int(30 * self.u) + 2
                y0, y1, x0, x1 = max(ys.min() - pad, 0), min(ys.max() + pad, self.S), max(xs.min() - pad, 0), min(xs.max() + pad, self.S)
                self.ground[y0:y1, x0:x1] += 0.05 * dust * float(np.mean(pressure)) * ndi.gaussian_filter(cov[y0:y1, x0:x1], 7 * self.u)

    def seg_dist(self, ax, ay, bx, by):
        dx, dy = bx - ax, by - ay
        t = np.clip(((self.x - ax) * dx + (self.y - ay) * dy) / (dx * dx + dy * dy + 1e-9), 0, 1)
        return np.hypot(self.x - ax - t * dx, self.y - ay - t * dy)

    def line(self, a, b, width, pressure=0.6, dash=None, **kw):
        d = self.seg_dist(a[0], a[1], b[0], b[1])
        if dash:
            L = np.hypot(b[0] - a[0], b[1] - a[1]); t = ((self.x - a[0]) * (b[0] - a[0]) + (self.y - a[1]) * (b[1] - a[1])) / L
            d = np.where((t % (dash[0] + dash[1])) < dash[0], d, 1e6)
        self.lay(d, width, pressure, **kw)

    def circle(self, c, r, width, pressure=0.6, arc=None, wobble=0.0, **kw):
        ang = np.arctan2(self.y - c[1], self.x - c[0])
        rr = r * (1 + wobble * (np.sin(3 * ang + 1.0) * 0.5 + np.sin(7 * ang + 2.0) * 0.25)) if wobble else r
        d = np.abs(np.hypot(self.x - c[0], self.y - c[1]) - rr)
        if arc is not None:
            a0, a1 = arc; da = (ang - a0) % (2 * np.pi); d = np.where(da <= (a1 - a0) % (2 * np.pi), d, 1e6)
        # the hand presses unevenly round a circle
        pr = pressure * (1 + 0.22 * np.sin(ang * 1.0 + r * 0.01) + 0.10 * np.sin(ang * 2.3 + 1.7))
        self.lay(d, width, pr, **kw)

    def dot(self, c, r, pressure=0.9, **kw):
        self.lay(np.clip(np.hypot(self.x - c[0], self.y - c[1]) - r, 0, None) + 0.0, 2.0, pressure, **kw) if False else \
            self.lay(np.hypot(self.x - c[0], self.y - c[1]), 2 * r, pressure, **kw)

    def arrow(self, a, b, width, pressure=0.7, head=None, **kw):
        self.line(a, b, width, pressure, **kw)
        h = head or 7 * width; ang = np.arctan2(b[1] - a[1], b[0] - a[0])
        for s in (+1, -1):
            e = (b[0] - h * np.cos(ang + s * 0.42), b[1] - h * np.sin(ang + s * 0.42))
            self.line(e, b, width, pressure, **kw)

    def text(self, x, y, s, px, font=None, pressure=0.62, anchor='ls', jitter=1.0, width_boost=0.0, **kw):
        """written word by word, each a little off the line"""
        font = font or F_I; f = ImageFont.truetype(font, int(round(px))); r = self.rng
        im = Image.new('L', (self.S, self.S), 0); d = ImageDraw.Draw(im)
        total = d.textlength(s, font=f)
        cx = x - (total / 2 if anchor[0] == 'm' else total if anchor[0] == 'r' else 0)
        for wd in s.split(' '):
            if wd:
                w = d.textlength(wd, font=f); pad = int(px * 0.6)
                tile = Image.new('L', (int(w) + 2 * pad, int(px * 1.9) + 2 * pad), 0)
                ImageDraw.Draw(tile).text((pad, pad + px * 1.25), wd, font=f, fill=255, anchor='ls')
                tile = tile.rotate(float(r.normal(0, 1.1 * jitter)), resample=Image.BICUBIC)
                oy = r.normal(0, 0.035 * px * jitter)
                im.paste(Image.fromarray(np.maximum(np.asarray(tile), 0)), (int(cx - pad), int(y - px * 1.25 - pad + oy)), tile)
                cx += w
            cx += d.textlength(' ', font=f)
        m = np.asarray(im, np.float32) / 255.0
        if width_boost > 0: m = np.clip(ndi.gaussian_filter(m, width_boost) * 1.9, 0, 1)
        # a glyph is a filled shape: convert to a pseudo-distance so that lay() can grain it
        self.lay(None, 0, pressure, cov=m, **kw)

    def rub(self, cx, cy, rx, ry, strength=0.5, seed=0):
        """wipe an area with the felt: chalk mostly goes, a smear stays"""
        r = np.random.default_rng(seed)
        e = np.clip(1.2 - np.hypot((self.x - cx) / rx, (self.y - cy) / ry), 0, 1)
        n = ndi.gaussian_filter(r.standard_normal((self.S // 8 + 1, self.S // 8 + 1)).astype(np.float32), (2, 9)); n = ndi.zoom(n / n.std(), 8, order=1)[:self.S, :self.S]
        k = np.clip(e * 1.6 + 0.25 * n * (e > 0), 0, 1)
        gone = 0.0
        for nm in self.dep:
            lost = self.dep[nm] * k * 0.93; self.dep[nm] -= lost; gone = gone + lost
        sm = ndi.gaussian_filter(gone, (5 * self.u, 34 * self.u))
        self.ground += strength * (1.6 * sm + 0.055 * k * (0.6 + 0.4 * n))

    # ---- finishing ----------------------------------------------------------------------
    def render(self):
        S = self.S; u = self.u; r = np.random.default_rng(99)
        img = np.empty((S, S, 3), np.float32); img[:] = self.slate
        # years of wiping: broad pale swathes
        sw = ndi.gaussian_filter(r.standard_normal((S // 16 + 1, S // 16 + 1)).astype(np.float32), (3, 11)); sw = ndi.zoom(sw / sw.std(), 16, order=1)[:S, :S]
        sw2 = ndi.gaussian_filter(r.standard_normal((S // 16 + 1, S // 16 + 1)).astype(np.float32), (9, 4)); sw2 = ndi.zoom(sw2 / sw2.std(), 16, order=1)[:S, :S]
        haze = np.clip(0.030 + 0.020 * sw + 0.012 * sw2, 0, None) + np.clip(self.ground, 0, 0.5)
        haze = haze * (1.0 + 0.25 * np.clip(self.tooth, -2, 2))
        img = img + (CREAM - img) * np.clip(haze, 0, 0.6)[..., None]
        img *= (1.0 + 0.035 * np.clip(self.tooth, -2, 2))[..., None]
        for nm in sorted(self.dep, key=lambda k: k != 'cream'):
            a = np.clip(self.dep[nm], 0, 1)[..., None] * 0.93
            img = img * (1 - a) + self.cols[nm] * a
        return img
