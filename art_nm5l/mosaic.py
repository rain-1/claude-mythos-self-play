"""mosaic.py -- a small tesserae engine (Fable 5.2, day 4).

A picture is laid, not painted: every region supplies a pair of coordinates (u along the
row, v across the rows, both in pixels), `tess` cuts them into jittered tesserae, each
tessera takes ONE colour sampled at its centre, the colour is snapped to a limited box
of stones (with per-tile dither), and grout fills what is left.

  M = Mosaic(size, seed)
  T = tess(uu, v, h, key, ncols=None)      -> Tiles(id, edge, uc, vc, row, col)
  M.lay(mask, T, rgb, mat=0)               # rgb per pixel, constant on a tile
  M.cut(mask)                              # grout line along the boundary of a figure
  img = M.finish()
"""
import numpy as np
from scipy import ndimage as ndi
from PIL import Image, ImageDraw, ImageFont

def h32(a, b=0, c=0):
    a = np.asarray(a).astype(np.uint32); b = np.asarray(b).astype(np.uint32); c = np.asarray(c).astype(np.uint32)
    with np.errstate(over='ignore'):
        x = a*np.uint32(0x9E3779B1) ^ (b*np.uint32(0x85EBCA77) + np.uint32(0x165667B1)) ^ (c*np.uint32(0xC2B2AE3D) + np.uint32(0x27D4EB2F))
        x ^= x >> np.uint32(15); x = x*np.uint32(0x2C1B3C6D)
        x ^= x >> np.uint32(12); x = x*np.uint32(0x297A2D39)
        x ^= x >> np.uint32(15)
    return x
def rnd(a, b=0, c=0):
    return (h32(a, b, c) >> np.uint32(8)).astype(np.float32) / np.float32(1 << 24)

class Tiles:
    __slots__ = ("id", "edge", "uc", "vc", "row", "col")

def tess(uu, v, h, key, w=None, ncols=None, jit=0.5, inset=0.05, rho=0.2):
    """uu: along-row coordinate in TILE units (if w is given, uu is in pixels and divided by w);
    v across rows in pixels; h row height; ncols: per-pixel period for closed rings.
    Returns ids, edge distance (px, >0 inside the tessera), tile-centre coordinates."""
    wpx = w if w is not None else h
    if w is not None: uu = uu / w
    r = np.floor(v / h).astype(np.int32)
    uu = uu + rnd(r, key, 11) * 7.0
    if ncols is not None: uu = np.mod(uu, ncols)
    c0 = np.floor(uu).astype(np.int32)
    def cut(c):
        cm = np.mod(c, ncols).astype(np.int32) if ncols is not None else c
        return c + jit * (rnd(r, cm, key) - 0.5)
    k0 = cut(c0); k1 = cut(c0 + 1)
    lo = uu < k0; hi = uu >= k1
    c = c0 - lo.astype(np.int32) + hi.astype(np.int32)
    left = np.where(lo, cut(c0 - 1), np.where(hi, k1, k0))
    right = np.where(lo, k0, np.where(hi, cut(c0 + 2), k1))
    cm = np.mod(c, ncols).astype(np.int32) if ncols is not None else c
    tid = h32(r, cm, key + 7919)
    ins = inset * h
    # a slight skew of the side cuts, and uneven insets
    fv = v / h - r - 0.5
    sk = (rnd(tid, 3) - 0.5) * 0.16
    du = np.minimum(uu - left + sk * fv, right - uu - sk * fv) * wpx - ins * (0.3 + 1.4 * rnd(tid, 5))
    dv = np.minimum(v - r * h, (r + 1) * h - v) - ins * (0.3 + 1.4 * rnd(tid, 6))
    R = rho * h
    e = np.minimum(du, dv)
    corner = (du < R) & (dv < R)
    e = np.where(corner, R - np.hypot(R - du, R - dv), e)
    T = Tiles(); T.id = tid; T.edge = e.astype(np.float32)
    T.uc = ((left + right) * 0.5 - rnd(r, key, 11) * 7.0).astype(np.float32)   # tile units
    if w is not None: T.uc = T.uc * w
    T.vc = ((r + 0.5) * h).astype(np.float32); T.row = r; T.col = cm
    return T

def polar_tess(X, Y, cx, cy, h, key, w=None, r0=0.0, **kw):
    """concentric rows about (cx,cy); closed rings with an integer number of tiles.
    Returns Tiles and the tile-centre xy."""
    w = w or h
    rho = np.hypot(X - cx, Y - cy); th = np.arctan2(Y - cy, X - cx)
    v = rho - r0
    rr = (np.floor(v / h) + 0.5) * h + r0
    n = np.maximum(np.round(2 * np.pi * rr / w), 3.0)
    T = tess((th / (2 * np.pi) + 0.5) * n, v, h, key, ncols=n, **kw)
    thc = (T.uc / n - 0.5) * 2 * np.pi
    xc = cx + (T.vc + r0) * np.cos(thc); yc = cy + (T.vc + r0) * np.sin(thc)
    return T, xc, yc

STONES = {  # the box of stones: name -> sRGB
 # lapis / night blues
 "lap0": (22, 34, 82), "lap1": (30, 52, 118), "lap2": (44, 78, 150), "lap3": (66, 108, 176), "lap4": (98, 140, 196),
 # turquoise / sea
 "tur0": (14, 60, 78), "tur1": (20, 88, 104), "tur2": (36, 120, 130), "tur3": (70, 156, 158), "tur4": (120, 190, 184), "tur5": (170, 216, 206),
 # sky warm
 "sky0": (196, 222, 222), "apr0": (246, 226, 190), "apr1": (244, 204, 160), "apr2": (238, 176, 134), "ros0": (226, 150, 132), "ros1": (200, 122, 126), "mau0": (150, 112, 150), "mau1": (104, 92, 150),
 # marble
 "mar0": (250, 246, 234), "mar1": (236, 228, 208), "mar2": (214, 204, 182), "mar3": (184, 174, 154),
 # gold smalti
 "gol0": (255, 226, 130), "gol1": (240, 190, 70), "gol2": (212, 154, 40), "gol3": (166, 112, 28),
 # earth
 "och0": (206, 160, 96), "ter0": (178, 96, 62), "umb0": (112, 70, 48), "umb1": (66, 44, 36), "blk0": (30, 28, 34),
 # greens
 "grn0": (40, 92, 70), "grn1": (86, 138, 92), "grn2": (150, 180, 120),
 # the red
 "red0": (206, 44, 36), "red1": (156, 28, 30),
}
def C(name): return np.array(STONES[name], np.float32) / 255.0

class Mosaic:
    def __init__(self, size, seed=1, grout=(0.60, 0.57, 0.51)):
        self.n = size; self.S = size / 4096.0; self.seed = seed
        self.rgb = np.zeros((size, size, 3), np.float32)
        self.edge = np.full((size, size), -9.0, np.float32)
        self.tid = np.zeros((size, size), np.uint32)
        self.mat = np.zeros((size, size), np.uint8)       # 0 stone, 1 gold smalti, 2 glass, 9 = not mosaic
        self.figure = np.zeros((size, size), bool)
        self.grout = np.array(grout, np.float32)
        self.Y, self.X = np.mgrid[0:size, 0:size].astype(np.float32)
        self.X += 0.5; self.Y += 0.5
        self.palette = None

    def lay(self, mask, T, rgb, mat=0, sl=None):
        """mask, T fields and rgb live on the sub-window sl (a pair of slices) or the full canvas"""
        sl = sl or (slice(None), slice(None))
        self.rgb[sl][mask] = rgb[mask] if rgb.ndim == 3 else rgb
        self.edge[sl][mask] = T.edge[mask]; self.tid[sl][mask] = T.id[mask]
        m = self.mat[sl]; m[mask] = mat if np.isscalar(mat) else mat[mask]

    def cut(self, mask, width=None, sl=None):
        """a grout seam along the boundary of mask (inside and outside): figures are cut in"""
        sl = sl or (slice(None), slice(None))
        w = width or 1.6 * self.S + 0.6
        d = (ndi.distance_transform_edt(mask) + ndi.distance_transform_edt(~mask)).astype(np.float32) - 0.5
        e = self.edge[sl]; np.minimum(e, d - w * 0.5, out=e)

    def quantize(self, names=None, dither=0.055):
        names = names or list(STONES)
        P = np.array([STONES[k] for k in names], np.float32) / 255.0
        n = self.n; out = np.empty_like(self.rgb)
        for y0 in range(0, n, 512):
            c = self.rgb[y0:y0+512].copy(); t = self.tid[y0:y0+512]
            for k in range(3): c[..., k] += dither * (rnd(t, 21 + k) - 0.5) * 2
            best = np.full(c.shape[:2], 1e9, np.float32); idx = np.zeros(c.shape[:2], np.int32)
            for i, p in enumerate(P):
                d = ((c - p) ** 2 * np.array([0.9, 1.2, 0.8], np.float32)).sum(-1)
                m = d < best; best[m] = d[m]; idx[m] = i
            out[y0:y0+512] = P[idx]
        keep = self.mat == 9
        out[keep] = self.rgb[keep]; self.rgb = out

    def finish(self, quant=True, names=None, dither=0.055):
        if quant: self.quantize(names, dither)
        S = self.S; t = self.tid; rgb = self.rgb
        mosaic = self.mat != 9
        # per-tessera life: lightness, a little hue, gold glints
        l = 1.0 + 0.11 * (rnd(t, 31) - 0.5) * 2
        gold = self.mat == 1
        gl = rnd(t, 33)
        l = np.where(gold, 0.80 + 0.34 * gl + 0.55 * (gl > 0.93), l)
        l = np.where(self.mat == 2, 0.90 + 0.22 * gl + 0.35 * (gl > 0.96), l)
        tint = np.stack([1 + 0.035 * (rnd(t, 35) - .5) * 2, np.ones_like(l), 1 + 0.045 * (rnd(t, 36) - .5) * 2], -1)
        tile = rgb * l[..., None] * tint
        # shallow pillow: darker towards the cut edges, a lit top-left arris
        e = self.edge
        pil = np.clip(e / (5.0 * S + 1e-6), 0, 1)
        tile *= (0.86 + 0.14 * pil)[..., None]
        ey, ex = np.gradient(ndi.gaussian_filter(np.clip(e, -2 * S, 6 * S), 0.8 * S + 0.3))
        lit = np.clip((ex + ey) * 0.5, -1, 1)          # light from the top-left
        tile *= (1.0 + 0.16 * lit * (pil < 0.999))[..., None]
        # stone grain
        rs = np.random.RandomState(self.seed)
        g = ndi.gaussian_filter(rs.randn(self.n, self.n).astype(np.float32), 0.7 * S + 0.35)
        g /= g.std() + 1e-9
        tile *= (1 + 0.035 * g * (~gold))[..., None]
        # grout
        gr = self.grout * (1 + 0.06 * ndi.gaussian_filter(rs.randn(self.n, self.n).astype(np.float32), 0.6)[..., None] / 0.45)
        big = ndi.zoom(ndi.gaussian_filter(rs.randn(64, 64), 5), self.n / 64, order=1)[: self.n, : self.n]
        big = (big / (np.abs(big).max() + 1e-9)).astype(np.float32)
        gr = gr * (0.93 + 0.10 * big[..., None])
        a = np.clip(e / (0.9 * max(S, 0.35)) + 0.5, 0, 1)[..., None]
        # the tile casts a thin shadow into the joint on its lower-right
        out = tile * a + gr * (1 - a) * (0.80 + 0.20 * np.clip(-lit * 2 + 0.5, 0, 1))[..., None]
        # the floor is not perfectly flat or clean
        out *= (0.965 + 0.05 * big[..., None])
        res = np.where(mosaic[..., None], out, self.rgb)
        return np.clip(res, 0, 1)

def save(img, path, size=None):
    im = Image.fromarray((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8))
    if size and size != im.size[0]: im = im.resize((size, size), Image.LANCZOS)
    im.save(path, optimize=True); return im

FONT = "/usr/share/fonts/truetype/liberation/LiberationSerif-%s.ttf"
FALL = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
def text_mask(n, items):
    """items: (text, x_centre, y_baseline, px, style, tracking) -> float mask"""
    im = Image.new("L", (n, n), 0); d = ImageDraw.Draw(im)
    for text, xc, yb, px, style, track in items:
        f = ImageFont.truetype(FONT % style, int(px)); fb = ImageFont.truetype(FALL, int(px * 0.86))
        fs = [fb if ch in "⌊⌋φ≤≥·×√π²→" else f for ch in text]
        widths = [d.textlength(ch, font=g) for ch, g in zip(text, fs)]
        tot = sum(widths) + track * (len(text) - 1); x = xc - tot / 2
        for ch, wd, g in zip(text, widths, fs):
            d.text((x, yb), ch, font=g, fill=255, anchor="ls"); x += wd + track
    return np.asarray(im, np.float32) / 255.0

def marble(n, seed, base=(0.925, 0.905, 0.86)):
    """a honed marble slab for the surround"""
    rs = np.random.RandomState(seed)
    def fbm(oct0, octs):
        f = np.zeros((n, n), np.float32)
        for o in range(octs):
            k = oct0 * 2 ** o
            f += ndi.zoom(rs.randn(k + 3, k + 3), n / k, order=3)[:n, :n].astype(np.float32) / 2 ** o
        return f
    a = fbm(3, 5); b = fbm(2, 4)
    vein = np.exp(-np.abs(np.sin(3.2 * a + 2.0 * b)) * 9.0)
    m = np.array(base, np.float32) * (1 + 0.035 * a[..., None]) - vein[..., None] * np.array([0.035, 0.035, 0.03], np.float32)
    m += 0.012 * rs.randn(n, n, 1).astype(np.float32)
    return m

def incise(slab, mask, S, depth=0.55):
    """V-cut letters in stone, lit from the top-left"""
    m = ndi.gaussian_filter(mask, 0.6 * S + 0.3)
    gy, gx = np.gradient(ndi.gaussian_filter(mask, 1.6 * S + 0.4))
    sh = np.clip((gx + gy) * 6.0 / max(S, .3) ** 0, -1, 1)
    out = slab * (1 - depth * m[..., None]) * (1 - 0.35 * np.clip(sh, 0, 1) * 1.0)[..., None]
    out += 0.10 * np.clip(-sh, 0, 1)[..., None]
    return out
