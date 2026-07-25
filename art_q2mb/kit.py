"""Shared render kit: splats, lines, bloom, tonemap, text — numpy + PIL only."""
import numpy as np
from scipy.ndimage import gaussian_filter, grey_dilation, zoom as ndzoom

def canvas(S):
    return np.zeros((S, S, 3), dtype=np.float32)

def splat_points(buf, xs, ys, w, rgb, sigma=1.5):
    """additive gaussian splats via bincount grid + one blur at the end is NOT
    done here; this draws hard bilinear points into buf (call blur separately)."""
    S = buf.shape[0]
    xs = np.asarray(xs, dtype=np.float64); ys = np.asarray(ys, dtype=np.float64)
    w = np.broadcast_to(np.asarray(w, dtype=np.float64), xs.shape)
    x0 = np.floor(xs).astype(np.int64); y0 = np.floor(ys).astype(np.int64)
    fx = xs - x0; fy = ys - y0
    for dx in (0,1):
        for dy in (0,1):
            wx = fx if dx else 1-fx
            wy = fy if dy else 1-fy
            xi = x0+dx; yi = y0+dy
            m = (xi>=0)&(xi<S)&(yi>=0)&(yi<S)
            if not m.any(): continue
            ww = (w*wx*wy)[m]
            idx = yi[m]*S + xi[m]
            for c in range(3):
                acc = np.bincount(idx, weights=ww*rgb[c], minlength=S*S)
                buf[...,c] += acc.reshape(S,S).astype(np.float32)

def line_pts(x1,y1,x2,y2,n):
    t = np.linspace(0,1,n)
    return x1+(x2-x1)*t, y1+(y2-y1)*t

def bezier_pts(p0, p1, p2, n):
    t = np.linspace(0,1,n)[:,None]
    p = (1-t)**2*np.array(p0)+2*(1-t)*t*np.array(p1)+t**2*np.array(p2)
    return p[:,0], p[:,1]

def fat(layer, px):
    """grey-dilate a stroke layer to survive downscale"""
    if px <= 1: return layer
    k = int(round(px))
    return grey_dilation(layer, size=(k,k,1) if layer.ndim==3 else (k,k))

def bloom(buf, sigma, gain, thresh=0.0):
    """fast wide bloom: downsample -> blur -> upsample"""
    src = np.clip(buf - thresh, 0, None)
    if sigma > 12:
        ds = max(1, int(sigma//6))
        small = src[::ds, ::ds]
        bl = gaussian_filter(small, (sigma/ds, sigma/ds, 0))
        big = ndzoom(bl, (ds, ds, 1), order=1)
        big = big[:buf.shape[0], :buf.shape[1]]
        if big.shape[0] < buf.shape[0] or big.shape[1] < buf.shape[1]:
            pad = np.zeros_like(buf); pad[:big.shape[0], :big.shape[1]] = big; big = pad
        buf += gain * gaussian_filter(big, (2,2,0))
    else:
        buf += gain * gaussian_filter(src, (sigma, sigma, 0))
    return buf

def tonemap(buf, k=1.0, gamma=0.82):
    out = 1.0 - np.exp(-k*np.clip(buf,0,None))
    return np.power(out, gamma)

def save(buf, path, final=None):
    from PIL import Image
    img = (np.clip(buf,0,1)*255).astype(np.uint8)
    im = Image.fromarray(img)
    if final and final != buf.shape[0]:
        im = im.resize((final,final), Image.LANCZOS)
    im.save(path)
    return path

def draw_text(img_arr, xy, text, size, fill, anchor="la", font_path=None):
    """draw text onto a float [0,1] rgb array AFTER bloom; returns array"""
    from PIL import Image, ImageDraw, ImageFont
    im = Image.fromarray((np.clip(img_arr,0,1)*255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    fp = font_path or "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    try: font = ImageFont.truetype(fp, size)
    except Exception:
        font = ImageFont.load_default()
    d.text(xy, text, fill=tuple(int(c*255) for c in fill), font=font, anchor=anchor)
    return np.asarray(im).astype(np.float32)/255.0

def lerp(a, b, t):
    return tuple(a[i]+(b[i]-a[i])*t for i in range(3))

def ramp(stops, t):
    """t in [0,1] through list of rgb stops"""
    t = np.clip(t, 0, 1)
    n = len(stops)-1
    i = min(int(t*n), n-1)
    return lerp(stops[i], stops[i+1], t*n - i)
