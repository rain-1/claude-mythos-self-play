"""Shared render toolkit — dark field, additive splats, filmic tone map."""
import numpy as np
from scipy.ndimage import gaussian_filter, zoom as ndzoom, grey_dilation

def line_splat(buf, x0, y0, x1, y1, w, npts=None):
    """Additive anti-aliased line: dense samples, bilinear splat. w = mass per unit length (scalar or per-line array)."""
    x0,y0,x1,y1 = (np.asarray(a, dtype=np.float64) for a in (x0,y0,x1,y1))
    L = np.hypot(x1-x0, y1-y0)
    n = np.maximum(2, (L*1.5).astype(int)) if npts is None else np.full(L.shape, npts, int)
    H,W = buf.shape[:2]
    for i in range(len(np.atleast_1d(x0))):
        t = np.linspace(0,1,n.flat[i])
        xs = x0.flat[i]+(x1.flat[i]-x0.flat[i])*t
        ys = y0.flat[i]+(y1.flat[i]-y0.flat[i])*t
        m = (np.atleast_1d(w)[i] if np.ndim(w)>0 else w) * L.flat[i]/n.flat[i]
        splat_pts(buf, xs, ys, m)

def splat_pts(buf, xs, ys, m):
    """bilinear point splat, m scalar or array"""
    H,W = buf.shape[:2]
    fx = np.floor(xs); fy = np.floor(ys)
    ax = xs-fx; ay = ys-fy
    for dx in (0,1):
        for dy in (0,1):
            wgt = (ax if dx else 1-ax)*(ay if dy else 1-ay)*m
            ix = (fx+dx).astype(int); iy = (fy+dy).astype(int)
            ok = (ix>=0)&(ix<W)&(iy>=0)&(iy<H)
            np.add.at(buf, (iy[ok], ix[ok]), wgt[ok] if np.ndim(wgt)>0 else wgt)

def wide_bloom(buf, sigma):
    """fast wide bloom: downsample -> blur -> upsample (craft note)"""
    if sigma <= 8: return gaussian_filter(buf, sigma)
    ds = max(2, int(sigma/6))
    small = buf[::ds, ::ds]
    sb = gaussian_filter(small, sigma/ds)
    up = ndzoom(sb, (buf.shape[0]/sb.shape[0], buf.shape[1]/sb.shape[1]), order=1)
    return np.clip(gaussian_filter(up[:buf.shape[0],:buf.shape[1]], 2), 0, None)

def filmic(x, k=1.0, gamma=0.85):
    y = 1-np.exp(-k*np.clip(x,0,None))
    return np.clip(y,0,1)**gamma

def to_img(rgb):
    from PIL import Image
    return Image.fromarray((np.clip(rgb,0,1)*255).astype(np.uint8))

def downscale(img, size):
    from PIL import Image
    return img.resize((size,size), Image.LANCZOS)

def nzpct(v, p):
    """percentile over non-negligible pixels (sparse-layer trap)"""
    nz = v[v > 0.02*v.max()] if v.max()>0 else v
    return np.percentile(nz, p) if nz.size else 1.0
