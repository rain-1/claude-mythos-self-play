"""Shared render kit — additive float32 canvas, bilinear splats, fast bloom,
filmic tonemap. Distilled from the memory branch's craft notes."""
import numpy as np
from scipy.ndimage import gaussian_filter, zoom as ndzoom


def canvas(S):
    return np.zeros((S, S, 3), np.float32)


def splat_points(img, px, py, w, color):
    """Bilinear additive splat. px,py float pixel coords; w scalar or array;
    color (3,) or (N,3)."""
    S = img.shape[0]
    x0 = np.floor(px).astype(np.int64)
    y0 = np.floor(py).astype(np.int64)
    fx = (px - x0).astype(np.float32)
    fy = (py - y0).astype(np.float32)
    w = np.asarray(w, np.float32)
    if w.ndim == 0:
        w = np.full(px.shape, float(w), np.float32)
    color = np.asarray(color, np.float32)
    flat = img.reshape(-1, 3)
    for dx, wx in ((0, 1 - fx), (1, fx)):
        for dy, wy in ((0, 1 - fy), (1, fy)):
            xi = x0 + dx
            yi = y0 + dy
            m = (xi >= 0) & (xi < S) & (yi >= 0) & (yi < S)
            if not m.any():
                continue
            idx = yi[m] * S + xi[m]
            ww = (w * wx * wy)[m]
            if color.ndim == 1:
                np.add.at(flat, idx, ww[:, None] * color[None, :])
            else:
                np.add.at(flat, idx, ww[:, None] * color[m])
    return img


def canvas_mono(S):
    return np.zeros(S * S, np.float32)


def splat_points_mono(mono, S, px, py, w):
    """Fast bilinear additive splat into a flat mono buffer (len S*S)."""
    x0 = np.floor(px).astype(np.int64)
    y0 = np.floor(py).astype(np.int64)
    fx = (px - x0).astype(np.float32)
    fy = (py - y0).astype(np.float32)
    w = np.asarray(w, np.float32)
    if w.ndim == 0:
        w = np.full(px.shape, float(w), np.float32)
    for dx, wx in ((0, 1 - fx), (1, fx)):
        for dy, wy in ((0, 1 - fy), (1, fy)):
            xi = x0 + dx
            yi = y0 + dy
            m = (xi >= 0) & (xi < S) & (yi >= 0) & (yi < S)
            if not m.any():
                continue
            np.add.at(mono, yi[m] * S + xi[m], (w * wx * wy)[m])
    return mono


def splat_segments_mono(mono, S, ax, ay, bx, by, w, samples_per_px=1.2, chunk=6_000_000):
    ax, ay, bx, by = (np.asarray(v, np.float32) for v in (ax, ay, bx, by))
    L = np.hypot(bx - ax, by - ay)
    nseg = len(ax)
    w = np.asarray(w, np.float32)
    if w.ndim == 0:
        w = np.full(nseg, float(w), np.float32)
    nsamp = np.maximum(2, (L * samples_per_px).astype(np.int64))
    csum = np.concatenate([[0], np.cumsum(nsamp)])
    i = 0
    while i < nseg:
        j = i
        while j < nseg and csum[j + 1] - csum[i] < chunk:
            j += 1
        j = max(j, i + 1)
        ns = nsamp[i:j]
        reps = np.repeat(np.arange(i, j), ns)
        offs = np.arange(len(reps)) - np.repeat(csum[i:j] - csum[i], ns)
        t = ((offs + 0.5) / np.repeat(ns, ns)).astype(np.float32)
        px = ax[reps] + (bx[reps] - ax[reps]) * t
        py = ay[reps] + (by[reps] - ay[reps]) * t
        ws = (w[reps] / np.repeat(ns, ns)).astype(np.float32)
        splat_points_mono(mono, S, px, py, ws)
        i = j
    return mono


def splat_segments(img, ax, ay, bx, by, w, color, samples_per_px=1.2, chunk=4_000_000):
    """Draw line segments additively with constant mass per unit length.
    ax..by are arrays of endpoints in pixel coords. w = mass per segment
    (scalar or per-segment array); mass is spread along the length."""
    S = img.shape[0]
    ax, ay, bx, by = (np.asarray(v, np.float32) for v in (ax, ay, bx, by))
    L = np.hypot(bx - ax, by - ay)
    nseg = len(ax)
    w = np.asarray(w, np.float32)
    if w.ndim == 0:
        w = np.full(nseg, float(w), np.float32)
    nsamp = np.maximum(2, (L * samples_per_px).astype(np.int64))
    color = np.asarray(color, np.float32)
    per_color = color.ndim == 2
    # process in chunks of total samples
    order = np.arange(nseg)
    tot = nsamp.sum()
    # build flat sample arrays segment-group by segment-group (by edges, not flat idx)
    start = 0
    csum = np.concatenate([[0], np.cumsum(nsamp)])
    i = 0
    while i < nseg:
        j = i
        while j < nseg and csum[j + 1] - csum[i] < chunk:
            j += 1
        j = max(j, i + 1)
        sl = slice(i, j)
        ns = nsamp[sl]
        reps = np.repeat(np.arange(i, j), ns)
        # param t in [0,1) per sample
        offs = np.arange(len(reps)) - np.repeat(csum[i:j] - csum[i], ns)
        t = (offs + 0.5) / np.repeat(ns, ns)
        px = ax[reps] + (bx[reps] - ax[reps]) * t
        py = ay[reps] + (by[reps] - ay[reps]) * t
        ws = (w[reps] / np.repeat(ns, ns)).astype(np.float32)
        col = color[reps] if per_color else color
        splat_points(img, px, py, ws, col)
        i = j
    return img


def wide_bloom(img, sigma, ds=None):
    """Fast wide gaussian bloom: downsample -> blur -> upsample (craft note)."""
    if ds is None:
        ds = max(1, int(sigma / 6))
    if ds == 1:
        return gaussian_filter(img, (sigma, sigma, 0))
    small = img[::ds, ::ds]
    b = gaussian_filter(small, (sigma / ds, sigma / ds, 0))
    out = ndzoom(b, (ds, ds, 1), order=1)
    return out[: img.shape[0], : img.shape[1]]


def bloom_add(img, tight=2.0, wide=40.0, t_amt=0.55, w_amt=0.35, thresh=None):
    src = img
    if thresh is not None:
        lum = img.mean(2)
        m = np.clip((lum - thresh) / max(thresh, 1e-6), 0, 1)[..., None]
        src = img * m
    out = img + t_amt * gaussian_filter(src, (tight, tight, 0))
    out = out + w_amt * wide_bloom(src, wide)
    return out


def tonemap(img, k=1.0, gamma=0.85, sat=1.0):
    x = 1.0 - np.exp(-k * np.clip(img, 0, None))
    if sat != 1.0:
        lum = x.mean(2, keepdims=True)
        x = lum + (x - lum) * sat
    x = np.clip(x, 0, 1) ** gamma
    return (x * 255).astype(np.uint8)


def save(arr_u8, path, downscale=None):
    from PIL import Image
    im = Image.fromarray(arr_u8)
    if downscale:
        im = im.resize((downscale, downscale), Image.LANCZOS)
    im.save(path)
    return path


def gauss_ring_line(img, pts_x, pts_y, w, color):
    """Thin curve from dense points: caller supplies dense samples."""
    splat_points(img, pts_x, pts_y, w, color)


# palette helpers -------------------------------------------------------------
def hex_rgb(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)], np.float32)


def lerp_palette(stops, t):
    """stops: list of (pos, rgb array). t array in [0,1] -> (N,3)."""
    t = np.clip(np.asarray(t, np.float32), 0, 1)
    pos = np.array([p for p, _ in stops], np.float32)
    cols = np.stack([c for _, c in stops])
    idx = np.clip(np.searchsorted(pos, t) - 1, 0, len(stops) - 2)
    t0 = pos[idx]; t1 = pos[idx + 1]
    f = ((t - t0) / np.maximum(t1 - t0, 1e-9))[:, None]
    return cols[idx] * (1 - f) + cols[idx + 1] * f
