"""Shared render kit: dark field, additive splats, filmic tonemap, dither."""
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, grey_dilation

def filmic(x, k=1.0):
    return 1.0 - np.exp(-k*np.maximum(x, 0))

def to_img(rgb, gamma=1.0, dither=True):
    v = np.clip(rgb, 0, 1)
    if gamma != 1.0: v = v**gamma
    if dither: v = v + (np.random.default_rng(1).uniform(-1,1,v.shape)/255.0)
    return Image.fromarray((np.clip(v,0,1)*255).astype(np.uint8))

def downscale(img, size):
    return img.resize((size,size), Image.LANCZOS)

def wide_bloom(buf, sigma):
    """downsample -> blur -> upsample (fast wide bloom)."""
    ds = max(1, int(sigma/6))
    if ds > 1:
        from scipy.ndimage import zoom
        small = buf[::ds, ::ds]
        b = gaussian_filter(small, sigma/ds)
        out = np.kron(b, np.ones((ds,ds)))[:buf.shape[0],:buf.shape[1]]
        h,w = out.shape
        if h < buf.shape[0] or w < buf.shape[1]:
            out = np.pad(out, ((0,buf.shape[0]-h),(0,buf.shape[1]-w)), mode='edge')
        return gaussian_filter(out, 2.0)
    return gaussian_filter(buf, sigma)

def splat_points(buf, xs, ys, w, S):
    """bilinear additive splat; xs,ys in pixel coords."""
    ok = (xs >= 0) & (xs < S-1) & (ys >= 0) & (ys < S-1)
    xs, ys = xs[ok], ys[ok]
    if np.isscalar(w): w = np.full(xs.shape, float(w))
    else: w = w[ok]
    x0 = np.floor(xs).astype(np.int64); y0 = np.floor(ys).astype(np.int64)
    fx = xs - x0; fy = ys - y0
    for dx, dy, ww in ((0,0,(1-fx)*(1-fy)), (1,0,fx*(1-fy)), (0,1,(1-fx)*fy), (1,1,fx*fy)):
        np.add.at(buf, (y0+dy, x0+dx), w*ww)

def line_splat(buf, x0, y0, x1, y1, w, S, step=0.7):
    """splat a batch of segments; scalar or per-seg w."""
    x0,y0,x1,y1 = map(np.asarray, (x0,y0,x1,y1))
    L = np.hypot(x1-x0, y1-y0)
    n = np.maximum(2, (L/step).astype(int))
    if np.isscalar(w): w = np.full(x0.shape, float(w))
    for i in range(len(x0)):
        t = np.linspace(0,1,n[i])
        splat_points(buf, x0[i]+(x1[i]-x0[i])*t, y0[i]+(y1[i]-y0[i])*t,
                     (w[i]/n[i])*np.ones(n[i]), S)

def hist_eq(v, bins=4096):
    """histogram-equalize positive values, zeros stay zero."""
    out = np.zeros_like(v)
    m = v > 0
    if m.sum() == 0: return out
    vals = v[m]
    h, edges = np.histogram(vals, bins=bins)
    cdf = np.cumsum(h).astype(np.float64); cdf /= cdf[-1]
    out[m] = np.interp(vals, edges[1:], cdf)
    return out
