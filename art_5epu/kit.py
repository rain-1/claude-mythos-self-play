"""Shared render kit — additive glowing splats, filmic tone map, fast bloom.
Reused across the triptych so palettes/registers stay cohesive.
"""
import numpy as np
from scipy.ndimage import gaussian_filter, zoom as ndzoom, grey_dilation


def fatten(ink, w):
    """Thicken thin stroke art to ~w px while KEEPING its brightness (grey
    dilation preserves peaks, unlike a mass-conserving blur), then soften a hair.
    Use to make point/line-splatted strokes survive a large downscale: route all
    strokes into a separate `ink` buffer and fatten with w ~ 1.0*SS*rs before
    compositing."""
    w = int(round(w))
    if w < 2:
        return ink
    out = grey_dilation(ink, size=(w, w, 1))
    return gaussian_filter(out, (0.6*w, 0.6*w, 0)) * 0.55 + out * 0.7


def splat(buf, xy, rgb, mass, S):
    """Bilinear (sub-pixel 4-neighbour) additive splat of points xy into buf(S,S,3).
    xy: (N,2) float pixel coords; rgb: (N,3) or (3,); mass: (N,) or scalar."""
    x = xy[:, 0]; y = xy[:, 1]
    m = np.broadcast_to(np.asarray(mass, float), (len(x),))
    rgb = np.asarray(rgb, float)
    if rgb.ndim == 1:
        rgb = np.broadcast_to(rgb, (len(x), 3))
    ok = (x >= 0) & (x < S - 1) & (y >= 0) & (y < S - 1)
    x, y, m, rgb = x[ok], y[ok], m[ok], rgb[ok]
    x0 = np.floor(x).astype(np.intp); y0 = np.floor(y).astype(np.intp)
    fx = x - x0; fy = y - y0
    for dx in (0, 1):
        for dy in (0, 1):
            w = (fx if dx else 1 - fx) * (fy if dy else 1 - fy) * m
            idx = (y0 + dy) * S + (x0 + dx)
            for c in range(3):
                np.add.at(buf.reshape(-1, 3)[:, c], idx, w * rgb[:, c])


def line_splat(buf, p0, p1, rgb, bright, S, nsamp=None):
    """Splat a line segment p0->p1 (pixel coords). `bright` is deposited PER PIXEL
    the line covers (sampling ~1 point/pixel), so brightness is independent of
    segment length."""
    p0 = np.asarray(p0, float); p1 = np.asarray(p1, float)
    L = np.hypot(*(p1 - p0))
    n = nsamp or max(2, int(L) + 1)
    t = np.linspace(0, 1, n)
    xy = p0[None, :] * (1 - t)[:, None] + p1[None, :] * t[:, None]
    splat(buf, xy, rgb, bright, S)


def fast_bloom(buf, sigma, ds=None):
    """Wide bloom via downsample->blur->upsample. Returns blurred copy."""
    if ds is None:
        ds = max(1, int(sigma / 6))
    small = buf[::ds, ::ds]
    small = gaussian_filter(small, (sigma / ds, sigma / ds, 0))
    up = ndzoom(small, (buf.shape[0] / small.shape[0],
                        buf.shape[1] / small.shape[1], 1), order=1)
    up = up[:buf.shape[0], :buf.shape[1]]
    return gaussian_filter(up, (1.2, 1.2, 0))


def tonemap(buf, k=1.0, gamma=0.85, gain=1.0):
    """Filmic 1-exp(-k x) then gamma lift. buf assumed >=0."""
    x = buf * gain
    x = 1.0 - np.exp(-k * x)
    x = np.clip(x, 0, 1) ** gamma
    return (np.clip(x, 0, 1) * 255).astype(np.uint8)


def downscale(rgb8, factor):
    from PIL import Image
    im = Image.fromarray(rgb8)
    w, h = im.size
    return im.resize((w // factor, h // factor), Image.LANCZOS)


# ---- curated palettes (cyclic / ramp) --------------------------------------
def lerp_ramp(stops, t):
    """stops: list of (pos, (r,g,b)) 0..1; t array -> (N,3)."""
    pos = np.array([s[0] for s in stops])
    cols = np.array([s[1] for s in stops], float)
    t = np.clip(t, 0, 1)
    out = np.empty((len(t), 3))
    for c in range(3):
        out[:, c] = np.interp(t, pos, cols[:, c])
    return out


# destiny ramp: cool slate (loose) -> teal -> gold -> rose-ember (tight, leash->1)
DESTINY = [
    (0.00, (0.10, 0.16, 0.34)),   # deep slate
    (0.35, (0.10, 0.45, 0.55)),   # teal
    (0.62, (0.85, 0.70, 0.28)),   # gold
    (0.85, (0.95, 0.42, 0.30)),   # ember
    (1.00, (1.00, 0.85, 0.72)),   # hot white-rose
]
