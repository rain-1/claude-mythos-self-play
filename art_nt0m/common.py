"""Shared render toolkit: bilinear splat via bincount, filmic tonemap, bloom, save."""
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter


def splat_rgb(acc, xs, ys, w_rgb, W, H):
    """Bilinear-splat points into acc (H,W,3) float32.
    xs, ys: float pixel coords. w_rgb: (N,3) weights.
    Clamped-index bug avoided: weights from UNCLIPPED floor."""
    x0f = np.floor(xs)
    y0f = np.floor(ys)
    fx = (xs - x0f).astype(np.float32)
    fy = (ys - y0f).astype(np.float32)
    x0 = x0f.astype(np.int64)
    y0 = y0f.astype(np.int64)
    flat = acc.reshape(-1, 3)
    for dx, wx in ((0, 1.0 - fx), (1, fx)):
        for dy, wy in ((0, 1.0 - fy), (1, fy)):
            xi = x0 + dx
            yi = y0 + dy
            m = (xi >= 0) & (xi < W) & (yi >= 0) & (yi < H)
            idx = yi[m] * W + xi[m]
            ww = (wx[m] * wy[m])
            for c in range(3):
                flat[:, c] += np.bincount(idx, weights=ww * w_rgb[m, c],
                                          minlength=H * W).astype(np.float32)


def filmic(acc, k=1.0, gamma=0.9):
    """Bounded filmic tone map 1-exp(-k x), then gamma lift. acc >= 0."""
    t = 1.0 - np.exp(-k * acc)
    return np.power(np.clip(t, 0, 1), gamma)


def bloom(img, sigma_tight=2.0, sigma_wide=12.0, amt_tight=0.35, amt_wide=0.25,
          thresh=0.55):
    """Add halo around bright regions only (mask by smoothstep on luminance)."""
    lum = img @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    t = np.clip((lum - thresh) / (1.0 - thresh), 0, 1)
    mask = (t * t * (3 - 2 * t))[..., None] * img
    out = img.copy()
    for s, a in ((sigma_tight, amt_tight), (sigma_wide, amt_wide)):
        b = np.stack([gaussian_filter(mask[..., c], s) for c in range(3)], axis=-1)
        out += a * b
    return out


def save(img, path, down=1):
    """img float 0..~1.2 (H,W,3) -> PNG, optional LANCZOS downscale by 'down'."""
    im8 = (np.clip(img, 0, 1) * 255).astype(np.uint8)
    pil = Image.fromarray(im8)
    if down > 1:
        pil = pil.resize((pil.width // down, pil.height // down), Image.LANCZOS)
    pil.save(path)
    print("saved", path, pil.size)


def lerp_palette(t, stops):
    """t in [0,1] (N,), stops: list of (pos, (r,g,b)). Piecewise-linear. Returns (N,3)."""
    t = np.clip(t, 0, 1)
    pos = np.array([s[0] for s in stops], dtype=np.float32)
    col = np.array([s[1] for s in stops], dtype=np.float32)
    out = np.empty(t.shape + (3,), dtype=np.float32)
    idx = np.clip(np.searchsorted(pos, t) - 1, 0, len(stops) - 2)
    f = (t - pos[idx]) / (pos[idx + 1] - pos[idx] + 1e-12)
    out = col[idx] + f[..., None] * (col[idx + 1] - col[idx])
    return out
