"""batik.py — a small wax-resist dyeing engine (Fable 5.2, day 3 style).

The cloth is a reflectance image.  You draw WAX (masks in [0,1]) with a canting (lines, dots),
a brush (fills) or a stamp, then dip the cloth in a DYE bath: the bath multiplies the cloth by the
dye's transmittance wherever there is no wax.  Wax cracks, so every bath also leaks through a
network of hairline veins; every bath is a little uneven; edges bleed.  Baths accumulate, exactly
as on real cloth (indigo over soga gives the brown-black of Central Javanese sogan).

    C = Cloth(size, seed, ss=2)
    wax = C.mask(lambda d, S: d.ellipse(...))        # PIL drawing at working resolution
    C.dye(INDIGO, 0.8, wax, crackle=0.5)
    C.finish() -> PIL image
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy import ndimage as ndi
from scipy.spatial import cKDTree

# transmittance of a full-strength bath
INDIGO = np.array([0.10, 0.19, 0.42])
SOGA = np.array([0.56, 0.33, 0.15])     # soga brown
MENGKUDU = np.array([0.74, 0.13, 0.11])  # morinda red, the one red
KUNING = np.array([0.93, 0.74, 0.30])   # tegeran yellow
COTTON = np.array([0.945, 0.915, 0.845])

SERIF = "/usr/share/fonts/truetype/freefont/FreeSerif.ttf"
SERIF_I = "/usr/share/fonts/truetype/freefont/FreeSerifItalic.ttf"


def fbm(shape, scale, rng, octaves=4):
    """smooth noise in [0,1] by upsampling random lattices"""
    H, W = shape
    out = np.zeros(shape, np.float32); amp = 1.0; tot = 0.0
    for o in range(octaves):
        s = max(2, int(round(scale / 2 ** o)))
        g = rng.random((H // s + 3, W // s + 3)).astype(np.float32)
        im = Image.fromarray(g).resize((g.shape[1] * s, g.shape[0] * s), Image.BICUBIC)
        a = np.asarray(im, np.float32)
        oy, ox = rng.integers(0, s, 2)
        out += amp * a[oy:oy + H, ox:ox + W]; tot += amp; amp *= 0.5
    out /= tot
    return np.clip((out - 0.5) * 1.6 + 0.5, 0, 1)


class Cloth:
    def __init__(self, size, seed=0, ss=2, base=COTTON):
        self.size = size; self.ss = ss; self.W = size * ss
        self.rng = np.random.default_rng(seed)
        W = self.W
        self.S = W / 1000.0          # drawing unit: 1/1000 of the cloth side
        self.img = np.empty((W, W, 3), np.float32); self.img[:] = base
        self._crack_cache = {}

    # ---------- wax drawing ----------
    def mask(self, fn, blur=0.0):
        im = Image.new("L", (self.W, self.W), 0)
        fn(ImageDraw.Draw(im), self.S)
        if blur: im = im.filter(ImageFilter.GaussianBlur(blur * self.S))
        return np.asarray(im, np.float32) / 255.0

    def soften(self, m, r):
        return ndi.gaussian_filter(m, r * self.S)

    def canting(self, d, pts, width, wobble=0.6, blob=True, closed=False):
        """a hand-drawn wax line: constant-ish width, slight wander, a fat start"""
        S = self.S; rng = self.rng
        P = np.asarray(pts, float) * S
        if closed: P = np.vstack([P, P[:1]])
        n = len(P)
        if n < 2: return
        t = np.arange(n)
        off = ndi.gaussian_filter1d(rng.normal(size=(n, 2)), 6, mode="wrap" if closed else "nearest") * wobble * S * 2.2
        Q = P + off
        wv = width * S * (1 + 0.18 * ndi.gaussian_filter1d(rng.normal(size=n), 5, mode="nearest") * 2.5)
        d.line([tuple(q) for q in Q], fill=255, width=max(1, int(round(width * S))), joint="curve")
        step = max(1, int(n // 400) or 1)
        for i in range(0, n, step):
            r = max(0.5, wv[i] / 2)
            d.ellipse([Q[i, 0] - r, Q[i, 1] - r, Q[i, 0] + r, Q[i, 1] + r], fill=255)
        if blob and not closed:
            r = width * S * 0.85
            d.ellipse([Q[0, 0] - r, Q[0, 1] - r, Q[0, 0] + r, Q[0, 1] + r], fill=255)

    def cecek(self, d, pts, r, jitter=0.25):
        """wax dots (isen cecek): each a little different, some with a tail"""
        S = self.S; rng = self.rng
        for (x, y) in pts:
            rr = r * S * (1 + jitter * rng.normal() * 0.6)
            x = x * S + rng.normal() * r * S * 0.12; y = y * S + rng.normal() * r * S * 0.12
            e = 1 + 0.18 * rng.normal()
            d.ellipse([x - rr * e, y - rr / e, x + rr * e, y + rr / e], fill=255)

    # ---------- crackle ----------
    def crackle(self, cell, width=0.5, patch=0.5, seed=None):
        """hairline vein network: Voronoi edges of random points, alive only in patches. ~[0,1]"""
        key = (cell, width, patch, seed)
        if key in self._crack_cache: return self._crack_cache[key]
        rng = np.random.default_rng(self.rng.integers(1 << 30) if seed is None else seed)
        W = self.W; S = self.S
        f = 2 if W > 2400 else 1           # compute at half res for big cloths
        w = W // f
        n = int((1000.0 / cell) ** 2)
        P = rng.random((n, 2)) * w
        # anisotropy: cracks prefer one direction (the fold of the cloth)
        yy, xx = np.mgrid[0:w, 0:w].astype(np.float32)
        warp = fbm((w, w), 180 * S / f, rng, 2) * 40 * S / f
        q = np.stack([(xx + warp).ravel(), (yy * 0.72).ravel()], 1)
        tree = cKDTree(np.stack([P[:, 0], P[:, 1] * 0.72], 1))
        dd, _ = tree.query(q, k=2, workers=-1)
        e = (dd[:, 1] - dd[:, 0]).reshape(w, w)
        vein = np.exp(-(e / (width * S / f)) ** 2).astype(np.float32)
        alive = fbm((w, w), 90 * S / f, rng, 3)
        vein *= np.clip((alive - (1 - patch)) * 5, 0, 1)
        # veins fade in and out along their length
        vein *= 0.45 + 0.55 * fbm((w, w), 14 * S / f, rng, 2)
        if f > 1:
            vein = np.asarray(Image.fromarray(vein).resize((W, W), Image.BILINEAR), np.float32)
        self._crack_cache[key] = vein
        return vein

    # ---------- dyeing ----------
    def dye(self, colour, strength, wax=None, crackle=0.5, cell=26, uneven=0.12, bleed=0.5, seep=0.05):
        """one bath.  wax: mask in [0,1] or None.  crackle: how much the wax has cracked."""
        W = self.W; rng = self.rng
        if wax is None:
            open_ = np.ones((W, W), np.float32)
        else:
            wx = np.clip(wax, 0, 1)
            if bleed: wx = np.clip(ndi.gaussian_filter(wx, bleed * self.S) * 1.25 - 0.125, 0, 1)
            open_ = 1 - wx
            if crackle > 0:
                v = self.crackle(cell, 0.42, min(1.0, 0.35 + crackle * 0.5)) * crackle
                v2 = self.crackle(cell * 0.45, 0.3, 0.3) * crackle * 0.6
                open_ = np.maximum(open_, wx * np.clip(v + v2, 0, 1))
            if seep: open_ = np.maximum(open_, wx * seep * fbm((W, W), 60 * self.S, rng, 3))
        un = 1 - uneven * fbm((W, W), 260 * self.S, rng, 4) - uneven * 0.5 * fbm((W, W), 9 * self.S, rng, 2)
        amt = np.clip(strength * open_ * un, 0, 1)[..., None]
        self.img *= np.exp(amt * np.log(np.asarray(colour, np.float32)))   # Beer-Lambert: baths multiply

    def discharge(self, mask, amount=1.0, to=COTTON):
        """scrape / never dyed: push back towards bare cotton (use sparingly)"""
        m = (mask * amount)[..., None]
        self.img = self.img * (1 - m) + np.asarray(to, np.float32) * m

    # ---------- text ----------
    def text_mask(self, items):
        """items: (x, y, text, size, italic, anchor) in cloth units -> mask"""
        def fn(d, S):
            for (x, y, txt, sz, ital, anchor) in items:
                f = ImageFont.truetype(SERIF_I if ital else SERIF, int(sz * S))
                d.text((x * S, y * S), txt, font=f, fill=255, anchor=anchor)
        return self.mask(fn)

    # ---------- finish ----------
    def finish(self, weave=0.05, drape=0.05, vignette=0.06):
        W = self.W; rng = self.rng; S = self.S
        img = self.img
        # plain weave at the scale of two output pixels
        p = 2.0 * self.ss * max(1.0, self.size / 2048)
        yy, xx = np.mgrid[0:W, 0:W].astype(np.float32)
        slubx = ndi.gaussian_filter(rng.normal(size=(1, W)).astype(np.float32), (0, 0.6)) * 0.5
        sluby = ndi.gaussian_filter(rng.normal(size=(W, 1)).astype(np.float32), (0.6, 0)) * 0.5
        wv = (np.sin(2 * np.pi * xx / p) * np.sin(2 * np.pi * yy / p)) * 0.6 + slubx * 0.5 + sluby * 0.5
        img *= (1 + weave * wv)[..., None]
        # soft drape shading: long diagonal undulation
        dr = fbm((W, W), 420 * S, rng, 2) - 0.5
        img *= (1 + drape * 2 * dr)[..., None]
        r2 = ((xx / W - 0.5) ** 2 + (yy / W - 0.5) ** 2)
        img *= (1 - vignette * r2 * 2.2)[..., None]
        img += rng.normal(scale=0.006, size=img.shape).astype(np.float32)
        out = np.clip(img, 0, 1) ** (1 / 1.0)
        im = Image.fromarray((out * 255 + 0.5).astype(np.uint8))
        if self.ss > 1: im = im.resize((self.size, self.size), Image.LANCZOS)
        return im


def bands_from_field(F, levels):
    """band index of a scalar field for given increasing levels"""
    return np.digitize(F, levels).astype(np.int16)
