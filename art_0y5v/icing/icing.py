# Flat-lay royal-icing cookies: a height-field renderer.
# Build a Plate (pixel canvas), add cookies (polygons), flood regions, piped lines and dots,
# then render with soft height-field shadows, glossy icing and sanding-sugar glints.
import numpy as np, numba as nb
from numba import njit, prange
from scipy import ndimage
from PIL import Image, ImageDraw

def lin(c):
    return (np.asarray(c, float) / 255.0) ** 2.2

@njit(parallel=True)
def shadow_march(h, lx, ly, tan_e, maxd, soft):
    H, W = h.shape
    out = np.ones((H, W), np.float32)
    for y in prange(H):
        for x in range(W):
            h0 = h[y, x]
            res = 1.0
            t = 1.0
            while t < maxd:
                xx = x + lx * t; yy = y + ly * t
                ix = int(xx); iy = int(yy)
                if ix < 0 or iy < 0 or ix >= W - 1 or iy >= H - 1:
                    break
                fx = xx - ix; fy = yy - iy
                hh = (h[iy, ix] * (1-fx) + h[iy, ix+1] * fx) * (1-fy) + (h[iy+1, ix] * (1-fx) + h[iy+1, ix+1] * fx) * fy
                dh = hh - (h0 + t * tan_e)
                if dh > 0:
                    r = 1.0 - dh / (soft * t * 0.05 + 1.0)
                    if r < res:
                        res = r
                    if res <= 0:
                        res = 0.0
                        break
                t += 1.0 + t * 0.02
            out[y, x] = max(res, 0.0)
    return out

class Plate:
    def __init__(self, W, H, bg=(232, 238, 250), seed=1):
        self.W, self.H = W, H
        self.rng = np.random.default_rng(seed)
        self.h = np.zeros((H, W), np.float32)
        self.col = np.zeros((H, W, 3), np.float32); self.col[:] = lin(bg)
        self.gloss = np.zeros((H, W), np.float32)     # 0 matte .. 1 glossy
        self.sugar = np.zeros((H, W), np.float32)     # sanding-sugar glint density
        self.bgcol = lin(bg)
        # linen / paper texture
        n = self._noise(6) * 0.5 + self._noise(40) * 0.5
        self.col *= (0.975 + 0.05 * n)[..., None]

    def _noise(self, scale):
        # smooth value noise of given cell size (pixels)
        gh = self.H // scale + 3; gw = self.W // scale + 3
        g = self.rng.random((gh, gw)).astype(np.float32)
        z = ndimage.zoom(g, scale, order=3)[: self.H, : self.W]
        z = (z - z.min()) / (np.ptp(z) + 1e-9)
        return z

    def mask_poly(self, polys, inset=0):
        im = Image.new('L', (self.W, self.H), 0)
        d = ImageDraw.Draw(im)
        for p in polys:
            d.polygon([tuple(map(float, q)) for q in p], fill=255)
        m = np.asarray(im) > 127
        if inset:
            dist = ndimage.distance_transform_edt(m)
            m = dist > inset
        return m

    def cookie(self, polys, thick=26.0, edge=34.0, dough=(244, 214, 168), bake=(222, 168, 110)):
        m = self.mask_poly(polys)
        d = ndimage.distance_transform_edt(m).astype(np.float32)
        prof = np.clip(d / edge, 0, 1)
        prof = 1 - (1 - prof) ** 2.2
        n = self._noise(5); n2 = self._noise(23)
        n3 = self._noise(3)
        hh = thick * prof + 0.5 * n3 + 0.6 * n + 1.4 * n2
        self.h = np.where(m, np.maximum(self.h, hh), self.h)
        # browned rim
        b = np.exp(-d / (edge * 0.7))[..., None]
        c = lin(dough) * (1 - 0.55 * b) + lin(bake) * 0.55 * b
        c = c * (0.94 + 0.10 * n2[..., None]) * (0.96 + 0.06 * n[..., None])
        self.col = np.where(m[..., None], c, self.col)
        self.gloss = np.where(m, 0.0, self.gloss)
        self.sugar = np.where(m, 0.6, self.sugar)
        self.cookie_mask = m if not hasattr(self, 'cookie_mask') else (self.cookie_mask | m)
        return m

    def flood(self, polys, colour, inset=6.0, thick=12.0, dome=5.0, under=None):
        m = self.mask_poly(polys)
        if under is not None:
            m &= under
        d = ndimage.distance_transform_edt(m).astype(np.float32)
        m2 = d > inset
        d2 = np.clip(d - inset, 0, None)
        prof = 1 - np.exp(-d2 / dome)
        # slight self-levelling wobble
        n = self._noise(31)
        base = ndimage.gaussian_filter(self.h, 12)
        hh = np.maximum(self.h, base + thick * prof * (0.985 + 0.03 * n) + 0.4)
        self.h = np.where(m2, hh, self.h)
        c = lin(colour) * (0.985 + 0.03 * n[..., None])
        self.col = np.where(m2[..., None], c, self.col)
        self.gloss = np.where(m2, 1.0, self.gloss)
        self.sugar = np.where(m2, 0.0, self.sugar)
        return m2

    def lines(self, segs, colour, radius=7.0, wobble=0.6, lift=None):
        """segs: list of ((x0,y0),(x1,y1)). tube profile over the current surface."""
        im = Image.new('L', (self.W, self.H), 0)
        dr = ImageDraw.Draw(im)
        for (a, b) in segs:
            dr.line([tuple(a), tuple(b)], fill=255, width=1)
        sk = np.asarray(im) > 0
        d, ind = ndimage.distance_transform_edt(~sk, return_indices=True)
        r = radius * (1 + wobble * 0.08 * (self._noise(17) - 0.5))
        m = d < r
        tube = np.sqrt(np.clip(r ** 2 - d ** 2, 0, None)) * 0.85
        # sit the tube on the local surface under its spine
        base = self.h[ind[0], ind[1]] if lift is None else lift
        hh = base + tube
        upd = m & (hh > self.h - 0.5)
        self.h = np.where(upd, np.maximum(self.h, hh), self.h)
        self.col = np.where(upd[..., None], lin(colour), self.col)
        self.gloss = np.where(upd, 0.8, self.gloss)
        self.sugar = np.where(upd, 0.0, self.sugar)
        return upd

    def dots(self, pts, colours, radius=8.0, gloss=1.0, pearl=False):
        pts = np.asarray(pts, float)
        im = np.zeros((self.H, self.W), np.int32)
        idx = np.full((self.H, self.W), -1, np.int64)
        for i, (x, y) in enumerate(pts):
            ix, iy = int(round(x)), int(round(y))
            if 0 <= ix < self.W and 0 <= iy < self.H:
                im[iy, ix] = 1; idx[iy, ix] = i
        d, ind = ndimage.distance_transform_edt(im == 0, return_indices=True)
        nearest = idx[ind[0], ind[1]]
        rr = np.asarray(radius, float)
        rad = rr[nearest] if rr.ndim else rr
        m = d < rad
        cap = np.sqrt(np.clip(rad ** 2 - d ** 2, 0, None))
        base = self.h[ind[0], ind[1]]
        hh = base + cap
        upd = m & (hh > self.h)
        self.h = np.where(upd, hh, self.h)
        cols = lin(np.asarray(colours))
        c = cols[nearest] if cols.ndim == 2 else np.broadcast_to(cols, (self.H, self.W, 3))
        if pearl:
            # pearlescent sheen: tint shifts with the facing
            pass
        self.col = np.where(upd[..., None], c, self.col)
        self.gloss = np.where(upd, gloss, self.gloss)
        self.sugar = np.where(upd, 0.0, self.sugar)
        return upd

    def render(self, light=(-0.6, -0.55, 0.58), sky=(1.0, 0.97, 0.99), exposure=1.0, shadow_tint=(0.80, 0.80, 0.95), soft=12.0):
        L = np.array(light, float); L /= np.linalg.norm(L)
        h = self.h
        gy, gx = np.gradient(h)
        nx = -gx; ny = -gy; nz = np.ones_like(h)
        nl = np.sqrt(nx * nx + ny * ny + nz * nz)
        nx /= nl; ny /= nl; nz /= nl
        ndl = np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, None)
        lxy = np.hypot(L[0], L[1])
        sh = shadow_march(h.astype(np.float32), L[0] / lxy, L[1] / lxy, L[2] / lxy, 600.0, soft)
        sh = ndimage.gaussian_filter(sh, 1.2)
        # ambient occlusion from blurred height
        hb = ndimage.gaussian_filter(h, 18)
        ao = np.clip(1 - 0.018 * np.clip(hb - h, 0, None), 0.6, 1)
        self.sh = sh
        st = np.array(shadow_tint)
        amb = 0.40 * (0.6 + 0.4 * nz)
        key = 0.78 * ndl * sh
        lit = self.col * (key[..., None] + amb[..., None] * ao[..., None] * (st + (1 - st) * sh[..., None]))
        # glossy icing: Blinn highlight + broad sheen
        V = np.array([0, 0, 1.0]); Hv = L + V; Hv /= np.linalg.norm(Hv)
        nh = np.clip(nx * Hv[0] + ny * Hv[1] + nz * Hv[2], 0, None)
        spec = (0.55 * nh ** 90 + 0.10 * nh ** 12) * self.gloss * (0.3 + 0.7 * sh)
        # rim-light env reflection for glossy (tilted normals catch a window)
        fres = (1 - nz) ** 3 * 0.35 * self.gloss
        lit += (spec + fres)[..., None] * np.array(sky)
        # sanding sugar glints on the bare cookie
        g = self.rng.random(h.shape) < 0.0018 * self.sugar
        gl = ndimage.gaussian_filter(g.astype(np.float32), 0.7) * 6.0 * (0.4 + 0.6 * sh)
        lit += gl[..., None] * np.array([1.0, 0.97, 0.92])
        lit *= exposure
        y = lit / (1 + 0.10 * lit) * 1.10
        y = np.clip(y, 0, 1)
        srgb = np.where(y <= 0.0031308, 12.92 * y, 1.055 * np.power(y, 1 / 2.4) - 0.055)
        return (srgb * 255 + 0.5).clip(0, 255).astype(np.uint8)
