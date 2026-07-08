"""Shared render toolkit for the 'What the Edge Refuses' triptych.

Dark-field additive splatting, filmic tone map, curated palettes.
"""
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter


# ---------------------------------------------------------------- splatting

def splat_points(acc, x, y, w=1.0):
    """Additive bilinear splat of points (x, y) with weights w into acc (H, W).

    x, y in pixel coordinates (x → columns, y → rows). Out-of-frame samples
    are dropped. Weights may be scalar or per-point array.
    """
    H, W = acc.shape
    ok = (x >= 0) & (x < W - 1) & (y >= 0) & (y < H - 1)
    if not np.any(ok):
        return
    x = x[ok]; y = y[ok]
    if np.ndim(w):
        w = np.asarray(w)[ok]
    x0 = np.floor(x).astype(np.int64); y0 = np.floor(y).astype(np.int64)
    fx = x - x0; fy = y - y0
    for dx, dy, ww in ((0, 0, (1 - fx) * (1 - fy)), (1, 0, fx * (1 - fy)),
                       (0, 1, (1 - fx) * fy), (1, 1, fx * fy)):
        np.add.at(acc, (y0 + dy, x0 + dx), w * ww)


def splat_polyline(acc, px, py, w=1.0, samples_per_px=2.0, closed=False):
    """Splat a polyline (in pixel coords) with roughly uniform mass per arclength."""
    if closed:
        px = np.append(px, px[0]); py = np.append(py, py[0])
        if np.ndim(w):
            w = np.append(w, w[0])
    seg = np.hypot(np.diff(px), np.diff(py))
    n = np.maximum(1, np.ceil(seg * samples_per_px).astype(np.int64))
    idx = np.repeat(np.arange(len(seg)), n)
    # fractional position inside each segment
    t = (np.arange(idx.size) - np.repeat(np.concatenate(([0], np.cumsum(n)[:-1])), n)) \
        / np.repeat(n, n)
    x = px[idx] + (px[idx + 1] - px[idx]) * t
    y = py[idx] + (py[idx + 1] - py[idx]) * t
    if np.ndim(w):
        ww = (w[idx] + (w[idx + 1] - w[idx]) * t) / np.repeat(n, n)
    else:
        ww = w / np.repeat(n, n)
    splat_points(acc, x, y, ww)


# ---------------------------------------------------------------- tone / colour

def filmic(x, k=1.0, gamma=0.9):
    """Bounded filmic tone map: 1 - exp(-k x), then gamma lift. x >= 0."""
    y = 1.0 - np.exp(-k * np.maximum(x, 0))
    return np.power(y, gamma)


def bloom(rgb, mask_lo=0.6, mask_hi=1.0, sigma=6.0, gain=0.55, tint=(1, 1, 1)):
    """Add a soft halo around only the truly bright parts of an RGB field (0..1)."""
    lum = 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]
    t = np.clip((lum - mask_lo) / max(mask_hi - mask_lo, 1e-9), 0, 1)
    m = t * t * (3 - 2 * t)
    halo = np.stack([gaussian_filter(rgb[..., c] * m, sigma) * tint[c]
                     for c in range(3)], axis=-1)
    return rgb + gain * halo


def ramp(t, stops):
    """Piecewise-linear colour ramp. stops: list of (pos, (r,g,b)) with 0..1 colours."""
    t = np.clip(t, 0, 1)
    pos = np.array([p for p, _ in stops])
    cols = np.array([c for _, c in stops])
    out = np.empty(t.shape + (3,))
    for c in range(3):
        out[..., c] = np.interp(t, pos, cols[:, c])
    return out


def save(rgb, path, down=1):
    """Clip to [0,1], optional LANCZOS downscale by integer factor, save PNG."""
    img = np.clip(rgb, 0, 1)
    im = Image.fromarray((img * 255 + 0.5).astype(np.uint8))
    if down > 1:
        im = im.resize((im.width // down, im.height // down), Image.LANCZOS)
    im.save(path)
    print('wrote', path, im.size)
