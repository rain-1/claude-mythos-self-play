"""Shared render toolkit — What Reaches Us (3x3 grid).

Conventions: work in float32 luminance/RGB fields in [0, inf), tone-map at the
end (filmic 1-exp(-k x) then gamma), supersample x2 and LANCZOS-downscale.
numpy 2.x: use np.ptp / np.trapezoid (methods removed).
"""
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter


def filmic(x, k=1.0, gamma=1.0):
    """Bounded tone map: never clips to white."""
    y = 1.0 - np.exp(-k * np.maximum(x, 0.0))
    if gamma != 1.0:
        y = y ** gamma
    return y


def norm_percentile(x, lo=0.0, hi=99.7):
    a = np.percentile(x, lo)
    b = np.percentile(x, hi)
    return np.clip((x - a) / max(b - a, 1e-12), 0, None)


def bloom(rgb, threshold=0.72, sigmas=(3, 9, 27), weights=(0.5, 0.3, 0.2), gain=0.6):
    """Bloom only the true foci: mask = smoothstep above threshold."""
    lum = rgb @ np.array([0.2126, 0.7152, 0.0722], dtype=rgb.dtype)
    t = np.clip((lum - threshold) / (1 - threshold), 0, 1)
    t = t * t * (3 - 2 * t)
    src = rgb * t[..., None]
    halo = np.zeros_like(rgb)
    for s, w in zip(sigmas, weights):
        for c in range(3):
            halo[..., c] += w * gaussian_filter(src[..., c], s)
    return rgb + gain * halo


def to_image(rgb, out_size=None):
    """rgb float in [0,1] -> PIL image, optional LANCZOS downscale."""
    img = Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8))
    if out_size is not None and img.size != (out_size, out_size):
        img = img.resize((out_size, out_size), Image.LANCZOS)
    return img


def lerp_palette(t, stops):
    """t in [0,1] (any shape) -> rgb via piecewise-linear colour stops.
    stops: list of (pos, (r,g,b)) with pos ascending in [0,1], rgb in [0,1]."""
    t = np.clip(t, 0, 1)
    pos = np.array([p for p, _ in stops], dtype=np.float32)
    cols = np.array([c for _, c in stops], dtype=np.float32)
    idx = np.clip(np.searchsorted(pos, t) - 1, 0, len(stops) - 2)
    p0, p1 = pos[idx], pos[idx + 1]
    f = ((t - p0) / np.maximum(p1 - p0, 1e-9))[..., None]
    return cols[idx] * (1 - f) + cols[idx + 1] * f


# Row hue identities (columns share treatment; rows share hue family).
PAL_EMBER = [  # row A — tomography: ember/amber over deep teal-black
    (0.00, (0.010, 0.012, 0.020)),
    (0.25, (0.075, 0.060, 0.085)),
    (0.50, (0.45, 0.16, 0.08)),
    (0.75, (0.92, 0.55, 0.18)),
    (0.92, (1.00, 0.86, 0.55)),
    (1.00, (1.00, 0.97, 0.88)),
]
PAL_IRIS = [  # row B — diffraction: violet/cyan iris
    (0.00, (0.008, 0.010, 0.022)),
    (0.28, (0.10, 0.06, 0.24)),
    (0.55, (0.24, 0.22, 0.66)),
    (0.78, (0.25, 0.62, 0.88)),
    (0.93, (0.72, 0.92, 0.98)),
    (1.00, (0.96, 1.00, 1.00)),
]
PAL_VERDIGRIS = [  # row C — drums: verdigris/gold membrane
    (0.00, (0.008, 0.014, 0.012)),
    (0.30, (0.03, 0.12, 0.10)),
    (0.58, (0.10, 0.44, 0.34)),
    (0.80, (0.55, 0.78, 0.42)),
    (0.94, (0.97, 0.90, 0.55)),
    (1.00, (1.00, 0.99, 0.90)),
]
