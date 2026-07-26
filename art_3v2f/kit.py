"""Shared render kit: tone map, bloom, splats, ramps, text."""
import numpy as np
from scipy.ndimage import gaussian_filter, grey_dilation
from PIL import Image, ImageDraw, ImageFont


def filmic(buf, k=1.0, gamma=1.0):
    """buf (H,W,3) float >=0 -> uint8 image, 1-exp tone map then gamma."""
    t = 1.0 - np.exp(-k * np.clip(buf, 0, None))
    t = np.clip(t, 0, 1) ** gamma
    return (t * 255).astype(np.uint8)


def fast_wide_blur(a, sigma):
    """downsample -> blur -> upsample; visually identical to giant gaussian."""
    if sigma <= 8:
        return gaussian_filter(a, sigma)
    ds = max(2, int(sigma / 6))
    small = a[::ds, ::ds]
    b = gaussian_filter(small, sigma / ds)
    out = np.array(Image.fromarray(b.astype(np.float32)).resize(
        (a.shape[1], a.shape[0]), Image.BILINEAR))
    return gaussian_filter(out, 2.0)


def bloom(buf, mask_thresh=0.7, sigma=30, gain=0.6, tint=(1.0, 0.9, 0.7)):
    lum = buf.mean(axis=2)
    lo, hi = mask_thresh * lum.max(), lum.max()
    m = np.clip((lum - lo) / max(hi - lo, 1e-9), 0, 1) ** 2
    halo = fast_wide_blur(lum * m, sigma)
    for c in range(3):
        buf[..., c] += gain * tint[c] * halo
    return buf


def splat_points(acc, xs, ys, w, rad, shape):
    """additive gaussian splats onto acc (H,W); xs,ys in pixel coords."""
    H, W = shape
    r = int(np.ceil(3 * rad))
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
    kern = np.exp(-(xx * xx + yy * yy) / (2 * rad * rad))
    ws = np.broadcast_to(np.atleast_1d(w), np.atleast_1d(xs).shape)
    for x, y, wi in zip(np.atleast_1d(xs), np.atleast_1d(ys), ws):
        ix, iy = int(round(x)), int(round(y))
        x0, x1 = max(0, ix - r), min(W, ix + r + 1)
        y0, y1 = max(0, iy - r), min(H, iy + r + 1)
        if x0 >= x1 or y0 >= y1:
            continue
        acc[y0:y1, x0:x1] += wi * kern[y0 - iy + r:y1 - iy + r, x0 - ix + r:x1 - ix + r]
    return acc


def line_splat(acc, x0, y0, x1, y1, w, n=None):
    """anti-aliased additive line via bilinear sub-pixel splatting."""
    H, W = acc.shape
    if n is None:
        n = int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 2
    t = np.linspace(0, 1, n)
    xs = x0 + (x1 - x0) * t
    ys = y0 + (y1 - y0) * t
    fx, fy = np.floor(xs).astype(int), np.floor(ys).astype(int)
    dx, dy = xs - fx, ys - fy
    for ox, oy, ww in ((0, 0, (1 - dx) * (1 - dy)), (1, 0, dx * (1 - dy)),
                       (0, 1, (1 - dx) * dy), (1, 1, dx * dy)):
        gx, gy = fx + ox, fy + oy
        m = (gx >= 0) & (gx < W) & (gy >= 0) & (gy < H)
        np.add.at(acc, (gy[m], gx[m]), w * ww[m] / n)
    return acc


def ramp(t, stops):
    """t in [0,1] (any shape) through color stops [(pos,(r,g,b)),...]."""
    t = np.clip(t, 0, 1)
    out = np.zeros(t.shape + (3,), np.float32)
    for (p0, c0), (p1, c1) in zip(stops[:-1], stops[1:]):
        m = (t >= p0) & (t <= p1)
        f = (t[m] - p0) / max(p1 - p0, 1e-9)
        for c in range(3):
            out[..., c][m] = c0[c] + (c1[c] - c0[c]) * f
    return out


def stamp_text(img_u8, texts, color=(210, 190, 140), fontsize=22, font=None):
    """texts = [(x, y, s, anchor)] ; draws AFTER tone map. Returns new array."""
    im = Image.fromarray(img_u8)
    d = ImageDraw.Draw(im)
    try:
        f = ImageFont.truetype(font or
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", fontsize)
    except Exception:
        f = ImageFont.load_default()
    for item in texts:
        x, y, s = item[:3]
        anchor = item[3] if len(item) > 3 else "mm"
        col = item[4] if len(item) > 4 else color
        d.text((x, y), s, fill=tuple(col), font=f, anchor=anchor)
    return np.array(im)
