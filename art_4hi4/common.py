"""Shared render kit for the Four Crossings suite (art_4hi4)."""
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter


def splat_lines(acc, x0, y0, x1, y1, w, samples_per_px=1.4):
    """Additively splat line segments into float32 accumulator `acc` (H,W).

    Bilinear sub-pixel splatting, constant mass per unit length * w.
    x*,y* in pixel coordinates (x = column, y = row). Vectorized over segments,
    chunked over sample index so memory stays flat.
    """
    H, W = acc.shape
    x0 = np.asarray(x0, np.float64); y0 = np.asarray(y0, np.float64)
    x1 = np.asarray(x1, np.float64); y1 = np.asarray(y1, np.float64)
    w = np.broadcast_to(np.asarray(w, np.float64), x0.shape)
    L = np.hypot(x1 - x0, y1 - y0)
    n = np.maximum(2, (L * samples_per_px).astype(np.int64) + 1)
    nmax = int(n.max())
    mass = w * L / n  # constant mass per sample => per unit length
    # process in strides over the sample axis to bound memory
    step = max(1, int(4e7 // max(1, len(x0))))
    for s0 in range(0, nmax, step):
        s1 = min(nmax, s0 + step)
        t = (np.arange(s0, s1, dtype=np.float64)[None, :] + 0.5)
        alive = t < n[:, None]
        tt = t / n[:, None]
        xs = x0[:, None] + (x1 - x0)[:, None] * tt
        ys = y0[:, None] + (y1 - y0)[:, None] * tt
        ms = np.broadcast_to(mass[:, None], xs.shape)
        xs = xs[alive]; ys = ys[alive]; ms = ms[alive]
        bilinear_splat(acc, xs, ys, ms)


def bilinear_splat(acc, xs, ys, ms):
    """Bilinear splat points (xs, ys) with masses ms into acc (H,W)."""
    H, W = acc.shape
    ok = (xs > -1) & (xs < W) & (ys > -1) & (ys < H)
    xs = xs[ok]; ys = ys[ok]; ms = ms[ok]
    xf = np.floor(xs); yf = np.floor(ys)
    fx = xs - xf; fy = ys - yf
    ix = xf.astype(np.int64); iy = yf.astype(np.int64)
    for dx, dy, wgt in ((0, 0, (1 - fx) * (1 - fy)), (1, 0, fx * (1 - fy)),
                        (0, 1, (1 - fx) * fy), (1, 1, fx * fy)):
        xi = ix + dx; yi = iy + dy
        good = (xi >= 0) & (xi < W) & (yi >= 0) & (yi < H)
        np.add.at(acc, (yi[good], xi[good]), (ms * wgt)[good].astype(acc.dtype))


def filmic(x, k=1.0, gamma=1.0):
    """Bounded filmic tone map: 1 - exp(-k x), then gamma lift."""
    y = 1.0 - np.exp(-k * np.maximum(x, 0))
    return y ** gamma if gamma != 1.0 else y


def bloom(rgb, mask_lo=0.72, mask_hi=1.0, sigma=6.0, strength=0.55, tint=None):
    """Bloom only the true foci: mask by luminance smoothstep, blur, add back."""
    lum = rgb @ np.array([0.2126, 0.7152, 0.0722])
    t = np.clip((lum - mask_lo) / max(1e-9, (mask_hi - mask_lo)), 0, 1)
    m = t * t * (3 - 2 * t)
    src = rgb * m[..., None]
    halo = np.stack([gaussian_filter(src[..., c], sigma) for c in range(3)], -1)
    if tint is not None:
        halo = halo * np.asarray(tint)[None, None, :]
    return rgb + strength * halo


def save_png(rgb, path):
    """rgb float in [0, ~1.2]; soft-clip, to uint8, save."""
    out = np.clip(rgb, 0, 1)
    Image.fromarray((out * 255 + 0.5).astype(np.uint8)).save(path)
    print("saved", path, out.shape)


def ramp(t, stops):
    """Piecewise-linear color ramp. stops = [(pos, (r,g,b)), ...] sorted."""
    t = np.clip(np.asarray(t, np.float64), 0, 1)
    pos = np.array([s[0] for s in stops])
    cols = np.array([s[1] for s in stops], np.float64)
    out = np.zeros(t.shape + (3,))
    idx = np.clip(np.searchsorted(pos, t) - 1, 0, len(stops) - 2)
    p0 = pos[idx]; p1 = pos[idx + 1]
    f = np.where(p1 > p0, (t - p0) / np.maximum(p1 - p0, 1e-12), 0.0)
    out = cols[idx] * (1 - f)[..., None] + cols[idx + 1] * f[..., None]
    return out
