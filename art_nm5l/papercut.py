"""papercut.py — a cut-paper shadow box.

A Box is a stack of opaque paper sheets.  Each sheet is a mask at a height z (in sheet-gaps).
Laying a sheet (1) casts its shadow on whatever is already there — offset and blur grow with the
gap between the sheet and the surface under it, (2) glues the sheet on with its own fibre texture,
a pale cut edge towards the light and a dark one away from it.  Nothing is transparent and
nothing glows: all colour is paper stock, all depth is shadow.
"""
import numpy as np
from scipy import ndimage as ndi
from PIL import Image, ImageDraw, ImageFont

def rgb(h):
    h = h.lstrip('#'); return np.array([int(h[i:i+2], 16) for i in (0, 2, 4)], np.float32) / 255.0

def mix(a, b, t):
    return np.asarray(a, np.float32) * (1 - t) + np.asarray(b, np.float32) * t

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"

def _blur(a, s):
    """gaussian blur; large sigmas are done at reduced resolution"""
    if s < 0.3: return a
    if s <= 6: return ndi.gaussian_filter(a, s, mode='nearest')
    f = int(min(8, max(2, s // 3)))
    h, w = a.shape; H, W = (h // f) * f, (w // f) * f
    small = a[:H, :W].reshape(H // f, f, W // f, f).mean((1, 3))
    small = ndi.gaussian_filter(small, s / f, mode='nearest')
    out = ndi.zoom(small, f, order=1, mode='nearest', grid_mode=True)
    if out.shape != a.shape:
        o = np.empty_like(a); o[:] = 0
        hh, ww = min(h, out.shape[0]), min(w, out.shape[1]); o[:hh, :ww] = out[:hh, :ww]
        if hh < h: o[hh:, :] = o[hh - 1:hh, :]
        if ww < w: o[:, ww:] = o[:, ww - 1:ww]
        out = o
    return out

def _shift(a, dx, dy):
    return ndi.shift(a, (dy, dx), order=1, mode='constant', cval=0.0, prefilter=False)

class Box:
    def __init__(self, size, seed=0, base='#f3efe4', light=(-0.62, -0.78)):
        self.S = size; self.u = size / 4096.0          # u: pixels per design unit
        self.rng = np.random.default_rng(seed)
        self.img = np.empty((size, size, 3), np.float32); self.img[:] = rgb(base)
        self.z = np.zeros((size, size), np.float32)
        l = np.array(light, np.float32); self.light = l / np.linalg.norm(l)   # direction TO the light (x, y)
        self._fib = {}

    # ---- textures -------------------------------------------------------------------------
    def fibre(self, strength=1.0, k=0):
        """multiplicative paper texture ~1: fine tooth + soft cloudiness + a few long fibres"""
        key = k % 5
        if key not in self._fib:
            S = self.S; r = np.random.default_rng(1000 + key)
            fine = r.standard_normal((S, S)).astype(np.float32)
            fine = ndi.gaussian_filter(fine, 0.7 * max(1, self.u)) * 1.6
            cloud = ndi.zoom(r.standard_normal((S // 32 + 2, S // 32 + 2)).astype(np.float32), 32, order=3)[:S, :S]
            lng = r.standard_normal((S, S)).astype(np.float32)
            lng = ndi.gaussian_filter(lng, (0.6 * max(1, self.u), 9 * self.u)) * 3.0
            self._fib[key] = (0.030 * fine + 0.022 * cloud + 0.018 * lng).astype(np.float32)
        return 1.0 + strength * self._fib[key]

    # ---- laying a sheet -------------------------------------------------------------------
    def lay(self, mask, colour, z, shadow=0.55, reach=9.0, soft=3.0, edge=1.0, tex=1.0, k=0, contact=0.25, ao=0.0, ao_soft=14.0):
        """mask: float32 [0,1] (S,S); colour: (3,) or (S,S,3); z: height of this sheet.
        reach/soft: shadow offset and blur in design px per unit gap."""
        u = self.u; mask = np.clip(mask, 0, 1).astype(np.float32)
        ys, xs = np.nonzero(mask > 0.002)
        if len(ys) == 0: return
        if shadow > 0:
            gap = np.clip(z - self.z, 0, None)
            levels = [g for g in (1.0, 2.5, 6.0, 14.0) if g <= max(1.0, float(gap.max()) * 1.6)] or [1.0]
            sh = np.zeros_like(mask); 
            lg = np.log(np.clip(gap, levels[0], levels[-1]))
            for i, g in enumerate(levels):
                dx, dy = -self.light[0] * reach * g * u, -self.light[1] * reach * g * u
                s = _blur(_shift(mask, dx, dy), soft * g ** 0.8 * u)
                if len(levels) == 1: wgt = 1.0
                else:
                    c = np.log(g)
                    lo = np.log(levels[i - 1]) if i > 0 else None; hi = np.log(levels[i + 1]) if i < len(levels) - 1 else None
                    wgt = np.ones_like(mask)
                    if lo is not None: wgt = np.where(lg < c, np.clip((lg - lo) / (c - lo), 0, 1), wgt)
                    if hi is not None: wgt = np.where(lg >= c, np.clip((hi - lg) / (hi - c), 0, 1), wgt)
                    if lo is None: wgt = np.where(lg < c, 1.0, wgt)
                    if hi is None: wgt = np.where(lg >= c, 1.0, wgt)
                sh += wgt * s
            sh *= (gap > 0.01)
            if contact > 0:   # tight contact shadow hugging the edge
                sh = np.maximum(sh, contact / max(shadow, 1e-6) * _blur(_shift(mask, -self.light[0] * 2.5 * u, -self.light[1] * 2.5 * u), 2.0 * u) * (gap > 0.01))
            if ao > 0:        # ambient occlusion: the sheet behind is dimmer close to the edge of the sheet in front
                sh = np.maximum(sh, ao / max(shadow, 1e-6) * _blur(mask, ao_soft * u) * (gap > 0.01))
            dark = 1.0 - shadow * np.clip(sh, 0, 1)
            # shadows on paper are slightly cool
            self.img *= np.stack([dark, dark ** 0.96, dark ** 0.90], -1)
        col = np.asarray(colour, np.float32)
        sheet = np.broadcast_to(col, self.img.shape).copy() if col.ndim == 1 else col.copy()
        if tex > 0: sheet *= self.fibre(tex, k)[..., None]
        if edge > 0:
            # bevel: the cut edge catches light on the side facing the lamp and is dark on the other
            b = _blur(mask, 1.6 * u)
            gy, gx = np.gradient(b)
            d = -(gx * self.light[0] + gy * self.light[1]) * 1.6 * u   # >0 on edges facing the light
            lit = np.clip(d, 0, 1) * 1.3 * edge; drk = np.clip(-d, 0, 1) * 0.9 * edge
            sheet = sheet + (1.0 - sheet) * (0.55 * lit)[..., None]
            sheet = sheet * (1.0 - 0.45 * drk)[..., None]
        a = mask[..., None]
        self.img = self.img * (1 - a) + sheet * a
        self.z = np.where(mask > 0.5, z, self.z).astype(np.float32)

    # ---- helpers --------------------------------------------------------------------------
    def grid(self):
        y, x = np.mgrid[0:self.S, 0:self.S].astype(np.float32)
        return x, y

    def rect(self, x0, y0, x1, y1):
        """antialiased rectangle mask, coordinates in pixels"""
        S = self.S
        cx = np.clip(np.minimum(np.arange(S) + 1, x1) - np.maximum(np.arange(S), x0), 0, 1).astype(np.float32)
        cy = np.clip(np.minimum(np.arange(S) + 1, y1) - np.maximum(np.arange(S), y0), 0, 1).astype(np.float32)
        return cy[:, None] * cx[None, :]

    def disc(self, cx, cy, r):
        x, y = self.grid()
        return np.clip(r - np.hypot(x - cx, y - cy) + 0.5, 0, 1)

    def poly(self, pts, ss=2):
        im = Image.new('L', (self.S * ss, self.S * ss), 0)
        ImageDraw.Draw(im).polygon([(float(x) * ss, float(y) * ss) for x, y in pts], fill=255)
        if ss > 1: im = im.resize((self.S, self.S), Image.LANCZOS)
        return np.asarray(im, np.float32) / 255.0

    def text_mask(self, items):
        """items: list of (x, y, text, font_path, px, anchor)"""
        im = Image.new('L', (self.S, self.S), 0); d = ImageDraw.Draw(im)
        for x, y, t, fp, px, anchor in items:
            d.text((x, y), t, font=ImageFont.truetype(fp, int(round(px))), fill=255, anchor=anchor)
        return np.asarray(im, np.float32) / 255.0

    def ink(self, mask, colour, strength=0.85):
        """pencil / print on the surface (no height)"""
        a = (np.clip(mask, 0, 1) * strength)[..., None]
        self.img = self.img * (1 - a) + rgb(colour) * a if isinstance(colour, str) else self.img * (1 - a) + np.asarray(colour) * a

    def mat(self, x0, y0, x1, y1, colour='#f4f0e6', z=60, k=4):
        """a window mat lying on top of everything: deep shadow into the box"""
        m = 1.0 - self.rect(x0, y0, x1, y1)
        self.lay(m, rgb(colour), z, shadow=0.62, reach=1.6, soft=1.1, edge=1.0, tex=0.8, k=k, contact=0.3)

    def save(self, path, vignette=0.0):
        out = np.clip(self.img, 0, 1)
        out = out ** (1 / 1.0)
        Image.fromarray((out * 255 + 0.5).astype(np.uint8)).save(path)
