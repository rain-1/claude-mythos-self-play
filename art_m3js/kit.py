"""Shared render kit — dark-field additive splats, filmic tone map."""
import numpy as np
from scipy.ndimage import gaussian_filter, grey_dilation
from PIL import Image

def splat(buf, x, y, w):
    """Bilinear-splat points (x,y) with weights w into 2-D buf (y down)."""
    H, W = buf.shape
    x = np.asarray(x, np.float64); y = np.asarray(y, np.float64)
    w = np.broadcast_to(np.asarray(w, np.float64), x.shape)
    m = (x >= 0) & (x < W-1) & (y >= 0) & (y < H-1)
    x, y, w = x[m], y[m], w[m]
    x0 = np.floor(x).astype(np.int64); y0 = np.floor(y).astype(np.int64)
    fx, fy = x - x0, y - y0
    for dx, dy, ww in ((0,0,(1-fx)*(1-fy)), (1,0,fx*(1-fy)),
                       (0,1,(1-fx)*fy),     (1,1,fx*fy)):
        np.add.at(buf, (y0+dy, x0+dx), w*ww)

def draw_polyline(buf, xs, ys, mass, seg_per_px=1.6):
    """Sample a polyline densely and splat; total mass distributed evenly."""
    xs = np.asarray(xs); ys = np.asarray(ys)
    d = np.hypot(np.diff(xs), np.diff(ys))
    L = d.sum()
    if L < 1e-9: return
    n = max(8, int(L * seg_per_px))
    t = np.concatenate([[0], np.cumsum(d)]) / L
    u = np.linspace(0, 1, n)
    splat(buf, np.interp(u, t, xs), np.interp(u, t, ys), mass / n)

def wide_bloom(buf, sigma):
    """Fast wide bloom: downsample -> blur -> upsample (craft note)."""
    if sigma <= 8: return gaussian_filter(buf, sigma)
    ds = max(2, int(sigma / 6))
    H, W = buf.shape
    h2, w2 = H // ds, W // ds
    small = buf[:h2*ds, :w2*ds].reshape(h2, ds, w2, ds).mean(axis=(1, 3))
    small = gaussian_filter(small, sigma / ds)
    big = np.array(Image.fromarray(small.astype(np.float32)).resize((W, H), Image.BILINEAR))
    return gaussian_filter(big, 2.0)

def typ(buf, q=70):
    v = buf[buf > 0.02 * buf.max()] if buf.max() > 0 else np.array([1.0])
    return np.percentile(v, q) if len(v) else 1.0

def fatten(buf, px):
    """Grey-dilate strokes so they survive the SS downscale (peak-preserving)."""
    k = max(1, int(round(px)))
    return grey_dilation(buf, size=(k, k))

def tonemap(rgb, k=1.0, gamma=0.86):
    out = 1.0 - np.exp(-k * np.clip(rgb, 0, None))
    return np.clip(out, 0, 1) ** gamma

def save(rgb, path, final_size=None):
    img = (np.clip(rgb, 0, 1) * 255).astype(np.uint8)
    im = Image.fromarray(img)
    if final_size and final_size != img.shape[0]:
        im = im.resize((final_size, final_size), Image.LANCZOS)
    im.save(path)
    print("saved", path, im.size)

def ramp(stops, t):
    """Piecewise-linear color ramp; stops = list of (pos, (r,g,b)); t in [0,1]."""
    t = np.clip(np.asarray(t, np.float64), 0, 1)
    ps = np.array([s[0] for s in stops]); cs = np.array([s[1] for s in stops], float)
    out = np.empty(t.shape + (3,))
    for c in range(3):
        out[..., c] = np.interp(t, ps, cs[:, c])
    return out
