"""Shared render toolkit — additive glow splats, filmic tone, palettes."""
import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image


def splat_segments(acc, x0, y0, x1, y1, w, color, samples_per_px=1.2, chunk=4_000_000):
    """Additively splat line segments into RGB accumulator `acc` (H,W,3).

    x*,y* : float arrays of segment endpoints in pixel coords.
    w     : per-segment weight (total mass ∝ w, spread along length).
    color : (N,3) or (3,) per-segment RGB.
    Bilinear sub-pixel deposition; samples per segment ∝ pixel length.
    """
    H, W = acc.shape[:2]
    x0 = np.asarray(x0, np.float64); y0 = np.asarray(y0, np.float64)
    x1 = np.asarray(x1, np.float64); y1 = np.asarray(y1, np.float64)
    w = np.broadcast_to(np.asarray(w, np.float64), x0.shape)
    color = np.asarray(color, np.float64)
    if color.ndim == 1:
        color = np.broadcast_to(color, (len(x0), 3))

    seglen = np.hypot(x1 - x0, y1 - y0)
    nsmp = np.maximum(1, np.ceil(seglen * samples_per_px).astype(np.int64))
    # weight per sample so total per-segment mass = w * seglen (mass ∝ length)
    wps = w * seglen / nsmp
    # chunk by edges
    csum = np.cumsum(nsmp)
    total = csum[-1]
    starts = np.searchsorted(csum, np.arange(0, total, chunk))
    starts = np.unique(np.append(starts, len(nsmp)))
    for i in range(len(starts) - 1):
        s, e = starts[i], starts[i + 1]
        if s >= e:
            continue
        n = nsmp[s:e]
        idx = np.repeat(np.arange(s, e), n)
        # param along each segment
        offs = np.arange(len(idx)) - np.repeat(np.concatenate([[0], np.cumsum(n)[:-1]]) , n)
        tpar = (offs + 0.5) / n[idx - s]
        xs = x0[idx] + (x1[idx] - x0[idx]) * tpar
        ys = y0[idx] + (y1[idx] - y0[idx]) * tpar
        ws = wps[idx]
        cs = color[idx]
        _bilinear_deposit(acc, xs, ys, ws, cs)


def splat_points(acc, xs, ys, w, color):
    color = np.asarray(color, np.float64)
    if color.ndim == 1:
        color = np.broadcast_to(color, (len(np.atleast_1d(xs)), 3))
    _bilinear_deposit(acc, np.asarray(xs, np.float64), np.asarray(ys, np.float64),
                      np.broadcast_to(np.asarray(w, np.float64), np.shape(xs)), color)


def _bilinear_deposit(acc, xs, ys, ws, cs):
    H, W = acc.shape[:2]
    ok = (xs > -1) & (xs < W) & (ys > -1) & (ys < H) & np.isfinite(xs) & np.isfinite(ys)
    if not ok.any():
        return
    xs, ys, ws, cs = xs[ok], ys[ok], ws[ok], cs[ok]
    fx = np.floor(xs); fy = np.floor(ys)
    dx = xs - fx; dy = ys - fy
    ix = fx.astype(np.int64); iy = fy.astype(np.int64)
    for ox, oy, wt in ((0, 0, (1 - dx) * (1 - dy)), (1, 0, dx * (1 - dy)),
                       (0, 1, (1 - dx) * dy), (1, 1, dx * dy)):
        gx = ix + ox; gy = iy + oy
        m = (gx >= 0) & (gx < W) & (gy >= 0) & (gy < H)
        if not m.any():
            continue
        flat = gy[m] * W + gx[m]
        wm = (ws * wt)[m]
        for c in range(3):
            np.add.at(acc[:, :, c].reshape(-1), flat, wm * cs[m, c])


def bloom(img, mask_lo=0.6, mask_hi=1.0, sigma=8.0, gain=0.6, tint=None):
    """Gaussian halo added back from the bright parts only."""
    lum = img @ np.array([0.2126, 0.7152, 0.0722])
    t = np.clip((lum - mask_lo) / max(mask_hi - mask_lo, 1e-9), 0, 1)
    t = t * t * (3 - 2 * t)
    src = img * t[..., None]
    hal = np.stack([gaussian_filter(src[..., c], sigma) for c in range(3)], -1)
    if tint is not None:
        hal = hal * np.asarray(tint)[None, None, :]
    return img + gain * hal


def filmic(acc, k=1.0, gamma=0.9):
    """1 - exp(-k x), then gamma. acc >= 0."""
    img = 1.0 - np.exp(-k * acc)
    return np.power(np.clip(img, 0, 1), gamma)


def save(img, path, downscale=1):
    im8 = (np.clip(img, 0, 1) * 255).astype(np.uint8)
    im = Image.fromarray(im8)
    if downscale > 1:
        im = im.resize((im.width // downscale, im.height // downscale), Image.LANCZOS)
    im.save(path)
    return path


def lerp_palette(t, stops):
    """t in [0,1] -> RGB via piecewise-linear stops [(pos, (r,g,b)), ...]."""
    t = np.clip(np.asarray(t, np.float64), 0, 1)
    pos = np.array([p for p, _ in stops])
    cols = np.array([c for _, c in stops])
    out = np.empty(t.shape + (3,))
    for c in range(3):
        out[..., c] = np.interp(t, pos, cols[:, c])
    return out
