"""pastel.py — subtractive watercolor render stack (run 2026-09-01).

Departure from the series' additive-on-black craft: here the canvas is warm
PAPER and every layer is pigment OPTICAL DENSITY.  Final image:

    rgb_linear = paper(x,y) * exp(-D_total(x,y))          (Beer-Lambert)

so overlapping washes multiply (glaze) instead of adding to white.  Airiness
is enforced by a filmic soft-knee IN DENSITY SPACE: D -> Dmax*(1-exp(-D/Dmax))
per channel, which lets arbitrarily deep data saturate to a chosen deepest
tone instead of crushing to black.  All math in linear RGB; sRGB at the end.
"""

import numpy as np
from PIL import Image

# ---------------------------------------------------------------- color space
def srgb_to_linear(c):
    c = np.asarray(c, np.float32)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4).astype(np.float32)

def linear_to_srgb(c):
    c = np.clip(c, 0.0, 1.0)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055)

def absorption(srgb_hex_or_tuple):
    """Absorption vector of a pigment whose UNIT-density glaze on white paper
    shows the given sRGB color.  density d -> color^d (linear space)."""
    if isinstance(srgb_hex_or_tuple, str):
        h = srgb_hex_or_tuple.lstrip('#')
        t = tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4))
    else:
        t = srgb_hex_or_tuple
    lin = srgb_to_linear(np.array(t, np.float32))
    lin = np.clip(lin, 1e-4, 1.0)
    return (-np.log(lin)).astype(np.float32)

# a curated pastel pigment box (unit-density colors, airy but not anemic)
PIGMENTS = {
    'rose':       absorption('#ef9fb2'),
    'peach':      absorption('#f5b58f'),
    'butter':     absorption('#ecd487'),
    'sage':       absorption('#a8c8a0'),
    'seafoam':    absorption('#8fd0bd'),
    'sky':        absorption('#92c1e0'),
    'periwinkle': absorption('#9fa8dc'),
    'lilac':      absorption('#c5a3d6'),
    'clay':       absorption('#d69c8a'),
    'graphite':   absorption('#8a8f98'),   # for fine ink lines (still soft)
    'ink':        absorption('#5a6070'),   # deepest accent allowed
}

# ---------------------------------------------------------------- paper
def _blur(a, sigma):
    from scipy.ndimage import gaussian_filter
    if sigma <= 8:
        return gaussian_filter(a, sigma)
    # ds -> blur -> us for big sigmas
    from scipy.ndimage import zoom
    ds = max(1, int(sigma / 6))
    small = a[::ds, ::ds].copy()
    small = gaussian_filter(small, sigma / ds)
    out = zoom(small, (a.shape[0] / small.shape[0], a.shape[1] / small.shape[1]), order=1)
    return out[:a.shape[0], :a.shape[1]].astype(a.dtype)

def make_paper(H, W, warm=1.0, seed=0):
    """Warm-white paper with low-frequency tone drift + fiber grain (linear RGB)."""
    rng = np.random.default_rng(seed)
    base = srgb_to_linear(np.array([0.988, 0.979, 0.960 - 0.006 * warm], np.float32))
    drift = _blur(rng.standard_normal((H, W)).astype(np.float32), min(H, W) / 6)
    drift = 0.012 * drift / (np.std(drift) + 1e-9)
    fib_h = _blur(rng.standard_normal((H, W)).astype(np.float32), 0.6)
    fib_h = np.diff(np.pad(fib_h, ((0, 0), (1, 0)), mode='edge'), axis=1)
    fib_v = _blur(rng.standard_normal((H, W)).astype(np.float32), 0.6)
    fib_v = np.diff(np.pad(fib_v, ((1, 0), (0, 0)), mode='edge'), axis=0)
    grain = 0.010 * (fib_h + fib_v) / (np.std(fib_h + fib_v) + 1e-9)
    tone = (1.0 + drift + grain)[..., None]
    return (base[None, None, :] * tone).astype(np.float32)

# ---------------------------------------------------------------- canvas
class Watercolor:
    def __init__(self, H, W, seed=0, warm=1.0):
        self.H, self.W = H, W
        self.paper = make_paper(H, W, warm=warm, seed=seed)
        self.D = np.zeros((H, W, 3), np.float32)
        self.rng = np.random.default_rng(seed + 1)

    def wash(self, field, pigment, strength=1.0, granulate=0.0, edge=0.0,
             edge_sigma=2.0):
        """Add a pigment wash. field: (H,W) >=0 density map (1.0 = unit glaze).
        granulate: multiplicative high-freq pigment settling.
        edge: extra density on the field's own gradient ridge (watercolor rim)."""
        f = np.asarray(field, np.float32)
        if granulate > 0:
            g = self.rng.standard_normal(f.shape).astype(np.float32)
            g = _blur(g, 1.0)
            f = f * (1.0 + granulate * g / (np.std(g) + 1e-9)).clip(0.3, 2.5)
        if edge > 0:
            from scipy.ndimage import gaussian_filter
            sm = gaussian_filter(f, edge_sigma)
            gy, gx = np.gradient(sm)
            rim = np.sqrt(gx * gx + gy * gy)
            m = rim.max() + 1e-9
            f = f + edge * f.max() * (rim / m) ** 1.2
        ab = PIGMENTS[pigment] if isinstance(pigment, str) else pigment
        self.D += (strength * f)[..., None] * ab[None, None, :]

    def develop(self, dmax=2.6, dither=True):
        """Soft-knee density compression, then paper * exp(-D), then sRGB."""
        D = dmax * (1.0 - np.exp(-self.D / dmax))
        rgb = self.paper * np.exp(-D)
        img = linear_to_srgb(rgb)
        if dither:
            img = img + (self.rng.random(img.shape).astype(np.float32) - 0.5) / 255.0
        return np.clip(img, 0, 1)

    def save(self, path, final_size=None, dmax=2.6):
        img = (self.develop(dmax=dmax) * 255).astype(np.uint8)
        im = Image.fromarray(img)
        if final_size is not None and final_size != (self.W, self.H):
            im = im.resize(final_size, Image.LANCZOS)
        im.save(path)
        return path

# ---------------------------------------------------------------- field tools
def splat_points(H, W, xs, ys, amps, rad):
    """Gaussian point splats -> density field (vectorized, local bboxes)."""
    fld = np.zeros((H, W), np.float32)
    r = int(max(2, 3 * rad))
    ax = np.arange(-r, r + 1, dtype=np.float32)
    gy, gx = np.meshgrid(ax, ax, indexing='ij')
    ker = np.exp(-(gx * gx + gy * gy) / (2 * rad * rad)).astype(np.float32)
    xs = np.asarray(xs); ys = np.asarray(ys); amps = np.asarray(amps, np.float32)
    for x, y, a in zip(xs, ys, amps):
        ix, iy = int(round(x)), int(round(y))
        x0, x1 = max(0, ix - r), min(W, ix + r + 1)
        y0, y1 = max(0, iy - r), min(H, iy + r + 1)
        if x0 >= x1 or y0 >= y1:
            continue
        fld[y0:y1, x0:x1] += a * ker[y0 - iy + r:y1 - iy + r, x0 - ix + r:x1 - ix + r]
    return fld

def stroke_polyline(fld, pts, width, amp=1.0):
    """Accumulate an anti-aliased soft stroke along pts [(x,y),...] into fld.
    Bilinear sub-pixel splatting of dense samples; width = gaussian sigma px."""
    H, W = fld.shape
    pts = np.asarray(pts, np.float32)
    if len(pts) < 2:
        return fld
    seg = np.diff(pts, axis=0)
    seglen = np.hypot(seg[:, 0], seg[:, 1])
    total = seglen.sum()
    n = max(8, int(total * 1.6))
    t = np.linspace(0, 1, n)
    cum = np.concatenate([[0], np.cumsum(seglen)]) / (total + 1e-12)
    x = np.interp(t, cum, pts[:, 0])
    y = np.interp(t, cum, pts[:, 1])
    # gaussian cross-section via per-sample random offsets (no ghost banding)
    rng = np.random.default_rng((int(pts[0, 0] * 7919) ^ int(pts[-1, 1] * 104729)) & 0x7fffffff)
    k = max(8, int(width * 8))
    w_each = amp * total * 1.6 / (n * k) * 10.0
    for _ in range(k):
        ox = rng.standard_normal(n).astype(np.float32) * width
        oy = rng.standard_normal(n).astype(np.float32) * width
        xi = x + ox; yi = y + oy
        x0 = np.floor(xi).astype(np.int64); y0 = np.floor(yi).astype(np.int64)
        fx = (xi - x0).astype(np.float32); fy = (yi - y0).astype(np.float32)
        for dx, wx in ((0, 1 - fx), (1, fx)):
            for dy, wy in ((0, 1 - fy), (1, fy)):
                xx = x0 + dx; yy = y0 + dy
                m = (xx >= 0) & (xx < W) & (yy >= 0) & (yy < H)
                np.add.at(fld, (yy[m], xx[m]), (w_each * wx * wy)[m])
    return fld
