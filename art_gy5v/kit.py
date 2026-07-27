"""Shared render kit: splats, bloom, tonemap, text."""
import numpy as np
from scipy.ndimage import gaussian_filter, grey_dilation, zoom as ndzoom
from PIL import Image, ImageDraw, ImageFont

def splat_points(buf, x, y, w, H, W):
    """bilinear point splat into buf[H,W]; x,y in pixel coords (float), w mass."""
    m = (x >= 0) & (x < W-1) & (y >= 0) & (y < H-1)
    x, y, w = x[m], y[m], (w[m] if np.ndim(w) else np.full(m.sum(), w))
    x0 = np.floor(x).astype(np.int64); y0 = np.floor(y).astype(np.int64)
    fx, fy = x - x0, y - y0
    for dx, dy, ww in ((0,0,(1-fx)*(1-fy)), (1,0,fx*(1-fy)), (0,1,(1-fx)*fy), (1,1,fx*fy)):
        np.add.at(buf, (y0+dy, x0+dx), w*ww)

def line_splat(buf, x0, y0, x1, y1, w, H, W, samples_per_px=1.2, mass_per_length=False):
    """splat line segments; arrays x0..y1 in px; w per-segment mass (spread along), or per-px if mass_per_length."""
    L = np.hypot(x1-x0, y1-y0)
    ns = np.maximum(2, (L*samples_per_px).astype(np.int64))
    # chunk by segments
    CH = 200000
    for i in range(0, len(x0), CH):
        sl = slice(i, min(i+CH, len(x0)))
        nn = ns[sl]; tot = nn.sum()
        seg = np.repeat(np.arange(sl.start, sl.stop), nn)
        # param t within each segment
        cum = np.concatenate([[0], np.cumsum(nn)])
        t = (np.arange(tot) - cum[seg - sl.start]) / (nn[seg - sl.start] - 1)
        xs = x0[seg] + (x1[seg]-x0[seg])*t
        ys = y0[seg] + (y1[seg]-y0[seg])*t
        if mass_per_length:
            ws = np.broadcast_to(w, (len(x0),))[seg] * (L[seg]/nn[seg - sl.start])
        else:
            ws = np.broadcast_to(w, (len(x0),))[seg] / nn[seg - sl.start]
        splat_points(buf, xs, ys, ws, H, W)

def wide_bloom(buf, sigma):
    """fast wide gaussian via downsample -> blur -> upsample."""
    if sigma <= 8: return gaussian_filter(buf, sigma)
    ds = max(1, int(sigma/6))
    H, W = buf.shape
    Hp, Wp = (H//ds)*ds, (W//ds)*ds
    small = buf[:Hp, :Wp].reshape(Hp//ds, ds, Wp//ds, ds).mean(axis=(1,3))
    sm = gaussian_filter(small, sigma/ds)
    up = np.array(Image.fromarray(sm.astype(np.float32)).resize((W, H), Image.BILINEAR))
    return gaussian_filter(up, 2.0)

def filmic(rgb, k=1.0, gamma=0.90):
    out = 1.0 - np.exp(-k*np.clip(rgb, 0, None))
    return np.clip(out, 0, 1)**gamma

def to_img(rgb):
    rng = np.random.default_rng(12345)
    d = (rng.random(rgb.shape) - 0.5)/255.0
    return Image.fromarray((np.clip(rgb + d, 0, 1)*255).astype(np.uint8))

FONT_PATHS = ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"]
def font(sz, mono=False, serif=False):
    p = FONT_PATHS[1] if mono else (FONT_PATHS[2] if serif else FONT_PATHS[0])
    return ImageFont.truetype(p, sz)

def text_layer(H, W, draws):
    """draws: list of (x, y, string, size, rgb, opts) -> float rgb layer.
    opts dict: mono, serif, anchor"""
    img = Image.new('RGB', (W, H), (0, 0, 0))
    d = ImageDraw.Draw(img)
    for (x, y, s, sz, col, *rest) in draws:
        opts = rest[0] if rest else {}
        f = font(sz, opts.get('mono', False), opts.get('serif', False))
        c = tuple(int(255*v) for v in col)
        d.text((x, y), s, font=f, fill=c, anchor=opts.get('anchor', 'la'))
    return np.asarray(img, dtype=np.float64)/255.0
