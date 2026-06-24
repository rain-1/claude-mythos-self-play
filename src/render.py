"""Shared rendering helpers — tone mapping, palettes, save.

Craft notes carried from memory:
- filmic tone map 1 - exp(-k x) + gamma lift; cache the raw field.
- never clip to white; curated cyclic palettes beat raw HSV.
- supersample then LANCZOS down.
"""
import numpy as np
from PIL import Image


def filmic(x, k=2.2, gamma=0.85):
    """Bounded filmic tone map on a non-negative field, returns [0,1]."""
    x = np.asarray(x, dtype=np.float64)
    x = x / (x.max() + 1e-12)
    y = 1.0 - np.exp(-k * x)
    y = y / (1.0 - np.exp(-k))
    return np.clip(y, 0, 1) ** gamma


def palette_lut(stops, n=1024):
    """stops: list of (t, (r,g,b)) with t in [0,1] and rgb in [0,1].
    Returns (n,3) float LUT."""
    stops = sorted(stops, key=lambda s: s[0])
    ts = np.array([s[0] for s in stops])
    cs = np.array([s[1] for s in stops], dtype=np.float64)
    x = np.linspace(0, 1, n)
    out = np.empty((n, 3))
    for c in range(3):
        out[:, c] = np.interp(x, ts, cs[:, c])
    return out


def apply_lut(field01, lut):
    """field01 in [0,1] -> (H,W,3) uint8 via LUT."""
    idx = np.clip((field01 * (len(lut) - 1)).astype(np.int64), 0, len(lut) - 1)
    rgb = lut[idx]
    return rgb


def to_uint8(rgb01):
    return np.clip(rgb01 * 255.0 + 0.5, 0, 255).astype(np.uint8)


def save(rgb01, path, downscale_to=None):
    """rgb01: (H,W,3) in [0,1]. Optionally LANCZOS-downscale to a size."""
    img = Image.fromarray(to_uint8(rgb01), "RGB")
    if downscale_to is not None and img.size[0] != downscale_to:
        img = img.resize((downscale_to, downscale_to), Image.LANCZOS)
    img.save(path)
    return path


# A few curated palettes (t, rgb in 0..1)
PAL_EMBER = [
    (0.00, (0.01, 0.00, 0.03)),
    (0.30, (0.20, 0.03, 0.18)),
    (0.55, (0.70, 0.16, 0.18)),
    (0.78, (0.98, 0.62, 0.18)),
    (1.00, (1.00, 0.97, 0.86)),
]
PAL_ICE = [
    (0.00, (0.01, 0.01, 0.04)),
    (0.28, (0.04, 0.10, 0.30)),
    (0.55, (0.10, 0.45, 0.62)),
    (0.80, (0.40, 0.82, 0.86)),
    (1.00, (0.93, 0.99, 1.00)),
]
PAL_VIRID = [
    (0.00, (0.02, 0.01, 0.07)),
    (0.25, (0.18, 0.06, 0.36)),
    (0.50, (0.18, 0.40, 0.55)),
    (0.72, (0.20, 0.69, 0.47)),
    (0.90, (0.62, 0.85, 0.20)),
    (1.00, (0.99, 0.98, 0.62)),
]
