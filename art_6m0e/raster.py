"""Shared raster helpers: bilinear polyline splatting, tone mapping, palettes."""
import numpy as np

def splat_points(acc, xs, ys, ws, accv=None, vals=None):
    """Bilinear additive splat of weighted points into acc (H,W) float32.
    Optionally accumulate ws*vals into accv for a mean-value channel."""
    H, W = acc.shape
    x0 = np.floor(xs).astype(np.int64)
    y0 = np.floor(ys).astype(np.int64)
    fx = (xs - x0).astype(np.float32)
    fy = (ys - y0).astype(np.float32)
    ok = (x0 >= 0) & (x0 < W - 1) & (y0 >= 0) & (y0 < H - 1)
    x0, y0, fx, fy, ws = x0[ok], y0[ok], fx[ok], fy[ok], ws[ok]
    if vals is not None:
        vals = vals[ok]
    for dx, dy, wgt in ((0, 0, (1 - fx) * (1 - fy)), (1, 0, fx * (1 - fy)),
                        (0, 1, (1 - fx) * fy), (1, 1, fx * fy)):
        np.add.at(acc, (y0 + dy, x0 + dx), ws * wgt)
        if accv is not None:
            np.add.at(accv, (y0 + dy, x0 + dx), ws * wgt * vals)

def sample_polyline(pts, ds):
    """Resample a polyline (K,2) at spacing ds; returns (M,2) samples and per-sample
    mass ds (constant mass per unit length)."""
    seg = np.diff(pts, axis=0)
    L = np.hypot(seg[:, 0], seg[:, 1])
    keep = L > 1e-12
    seg, L, P0 = seg[keep], L[keep], pts[:-1][keep]
    out = []
    n = np.maximum(1, np.ceil(L / ds).astype(int))
    for i in range(len(L)):
        u = (np.arange(n[i]) + 0.5) / n[i]
        out.append(P0[i] + u[:, None] * seg[i])
    if not out:
        return np.zeros((0, 2)), np.zeros(0)
    S = np.concatenate(out)
    # mass: each segment carries L[i], split over n[i] samples
    m = np.concatenate([np.full(n[i], L[i] / n[i], dtype=np.float32) for i in range(len(L))])
    return S, m

def filmic(x, k):
    return 1.0 - np.exp(-k * x)

def palette3(v, c_neg, c_mid, c_pos):
    """v in [-1,1] -> 3-stop palette, bright at 0 (agreement), accents at +-1."""
    v = np.clip(v, -1, 1)
    out = np.zeros(v.shape + (3,), dtype=np.float32)
    a = np.clip(-v, 0, 1)[..., None]   # toward neg accent
    b = np.clip(v, 0, 1)[..., None]    # toward pos accent
    c_neg = np.asarray(c_neg, np.float32); c_mid = np.asarray(c_mid, np.float32)
    c_pos = np.asarray(c_pos, np.float32)
    out = c_mid * (1 - a - b) + c_neg * a + c_pos * b
    return np.clip(out, 0, 1)

def save_png(rgb, path):
    from PIL import Image
    img = (np.clip(rgb, 0, 1) * 255).astype(np.uint8)
    Image.fromarray(img).save(path)

def downscale(rgb, size):
    from PIL import Image
    img = Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8))
    return np.asarray(img.resize((size, size), Image.LANCZOS)).astype(np.float32) / 255.0
