"""Shared rendering helpers for the 'What Comes Home' set."""
import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image


def filmic(x, k=1.0):
    """Bounded filmic tone map; never clips to white."""
    return 1.0 - np.exp(-k * np.maximum(x, 0.0))


def gamma(x, g=1.0 / 1.8):
    return np.clip(x, 0, 1) ** g


def bloom(rgb, sigmas=(2.0, 8.0, 24.0), amps=(0.5, 0.3, 0.18)):
    """Additive multi-scale glow. rgb in [0,inf), HxWx3 float32."""
    out = rgb.copy()
    for s, a in zip(sigmas, amps):
        b = np.empty_like(rgb)
        for c in range(3):
            b[..., c] = gaussian_filter(rgb[..., c], s)
        out += a * b
    return out


def save(rgb01, path):
    """rgb01 in [0,1] HxWx3 -> 8-bit PNG."""
    img = np.clip(rgb01 * 255.0 + 0.5, 0, 255).astype(np.uint8)
    Image.fromarray(img, "RGB").save(path)
    return path


def downscale(rgb01, factor):
    """LANCZOS downscale of a [0,1] float image by integer factor."""
    h, w = rgb01.shape[:2]
    img = Image.fromarray(np.clip(rgb01 * 255 + 0.5, 0, 255).astype(np.uint8), "RGB")
    img = img.resize((w // factor, h // factor), Image.LANCZOS)
    return np.asarray(img, np.float32) / 255.0


def splat_add(canvas, xs, ys, rgb, radius, intensity):
    """Additive disk splats with a soft gaussian falloff into an HxWx3 buffer.
    xs,ys pixel coords (float), rgb (N,3) or (3,), radius px, intensity scalar/array."""
    H, W = canvas.shape[:2]
    rgb = np.asarray(rgb, np.float32)
    if rgb.ndim == 1:
        rgb = np.broadcast_to(rgb, (len(xs), 3))
    inten = np.broadcast_to(np.asarray(intensity, np.float32), (len(xs),))
    r = int(np.ceil(radius * 3))
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
    ker = np.exp(-(xx * xx + yy * yy) / (2 * radius * radius)).astype(np.float32)
    ix = np.round(xs).astype(int)
    iy = np.round(ys).astype(int)
    for k in range(len(xs)):
        cx, cy = ix[k], iy[k]
        x0, x1 = cx - r, cx + r + 1
        y0, y1 = cy - r, cy + r + 1
        if x1 <= 0 or y1 <= 0 or x0 >= W or y0 >= H:
            continue
        kx0 = max(0, -x0); ky0 = max(0, -y0)
        kx1 = ker.shape[1] - max(0, x1 - W); ky1 = ker.shape[0] - max(0, y1 - H)
        cx0 = max(0, x0); cy0 = max(0, y0)
        cx1 = min(W, x1); cy1 = min(H, y1)
        sub = ker[ky0:ky1, kx0:kx1, None] * (rgb[k] * inten[k])[None, None, :]
        canvas[cy0:cy1, cx0:cx1] += sub
    return canvas
