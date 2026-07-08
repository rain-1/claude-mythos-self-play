"""Shared render kit: additive line splatting, bloom, filmic tone map."""
import numpy as np
from scipy.ndimage import gaussian_filter


def splat_points(acc, xs, ys, w):
    """Bilinear-splat points (xs, ys in pixel coords) with weights w into acc (H,W)."""
    H, W = acc.shape
    x0f = np.floor(xs); y0f = np.floor(ys)
    fx = xs - x0f; fy = ys - y0f
    x0 = x0f.astype(np.int64); y0 = y0f.astype(np.int64)
    for dx, dy, ww in ((0, 0, (1 - fx) * (1 - fy)), (1, 0, fx * (1 - fy)),
                       (0, 1, (1 - fx) * fy), (1, 1, fx * fy)):
        xi = x0 + dx; yi = y0 + dy
        m = (xi >= 0) & (xi < W) & (yi >= 0) & (yi < H)
        np.add.at(acc, (yi[m], xi[m]), (w * ww)[m])


def splat_segments(acc, x1, y1, x2, y2, w, samples_per_px=1.4, max_chunk=6_000_000):
    """Additively draw line segments; per-segment mass = w (spread along length)."""
    L = np.hypot(x2 - x1, y2 - y1)
    n = np.maximum(2, np.ceil(L * samples_per_px).astype(np.int64))
    order = np.argsort(n)
    x1, y1, x2, y2, w, L, n = (a[order] for a in (x1, y1, x2, y2, w, L, n))
    i = 0
    N = len(n)
    while i < N:
        j = i
        tot = 0
        nn = n[i]
        while j < N and n[j] == nn and tot < max_chunk:
            tot += nn; j += 1
        t = np.linspace(0.0, 1.0, nn)[None, :]
        xs = (x1[i:j, None] * (1 - t) + x2[i:j, None] * t).ravel()
        ys = (y1[i:j, None] * (1 - t) + y2[i:j, None] * t).ravel()
        ws = np.repeat(w[i:j] / nn, nn)
        splat_points(acc, xs, ys, ws)
        i = j


def splat_quad_bezier(acc, x1, y1, cx, cy, x2, y2, w, samples_per_px=1.4,
                      max_chunk=6_000_000):
    """Additive quadratic bezier strokes; mass w spread along the stroke."""
    # chord length as a cheap arc-length proxy
    L = np.hypot(x2 - x1, y2 - y1) + 0.5 * (np.hypot(cx - 0.5 * (x1 + x2),
                                                     cy - 0.5 * (y1 + y2)))
    n = np.maximum(3, np.ceil(L * samples_per_px).astype(np.int64))
    order = np.argsort(n)
    x1, y1, cx, cy, x2, y2, w, n = (a[order] for a in (x1, y1, cx, cy, x2, y2, w, n))
    i = 0
    N = len(n)
    while i < N:
        j = i
        tot = 0
        nn = n[i]
        while j < N and n[j] == nn and tot < max_chunk:
            tot += nn; j += 1
        t = np.linspace(0.0, 1.0, nn)[None, :]
        omt = 1 - t
        xs = (omt * omt * x1[i:j, None] + 2 * omt * t * cx[i:j, None]
              + t * t * x2[i:j, None]).ravel()
        ys = (omt * omt * y1[i:j, None] + 2 * omt * t * cy[i:j, None]
              + t * t * y2[i:j, None]).ravel()
        ws = np.repeat(w[i:j] / nn, nn)
        splat_points(acc, xs, ys, ws)
        i = j


def bloom(rgb, sigma=6.0, amount=0.35, thresh=0.6):
    """Bloom only the true foci: threshold on luminance, blur, add back."""
    lum = 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]
    t0, t1 = thresh, min(1.0, thresh + 0.28)
    m = np.clip((lum - t0) / (t1 - t0), 0, 1)
    m = m * m * (3 - 2 * m)
    src = rgb * m[..., None]
    out = rgb.copy()
    for s, a in ((sigma, amount), (sigma * 3.0, amount * 0.5)):
        for c in range(3):
            out[..., c] += a * gaussian_filter(src[..., c], s)
    return out


def filmic(rgb, k=1.0, gamma=0.90):
    x = 1.0 - np.exp(-k * np.clip(rgb, 0, None))
    return np.clip(x, 0, 1) ** gamma


def save(rgb, path, down=1):
    from PIL import Image
    img = (np.clip(rgb, 0, 1) * 255).astype(np.uint8)
    im = Image.fromarray(img)
    if down > 1:
        im = im.resize((img.shape[1] // down, img.shape[0] // down),
                       Image.LANCZOS)
    im.save(path)
    return path


def lerp_palette(t, stops):
    """t in [0,1] -> RGB via linear ramp through given (t_i, (r,g,b)) stops."""
    t = np.clip(t, 0, 1)
    ts = np.array([s[0] for s in stops])
    cs = np.array([s[1] for s in stops], dtype=np.float64)
    out = np.empty(t.shape + (3,))
    for c in range(3):
        out[..., c] = np.interp(t, ts, cs[:, c])
    return out
