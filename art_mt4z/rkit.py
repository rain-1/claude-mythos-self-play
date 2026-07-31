"""Small render kit: additive float buffers, line splats, bloom, filmic tonemap."""
import numpy as np
from scipy.ndimage import gaussian_filter, grey_dilation


def line_splat(buf, x0, y0, x1, y1, w, npts=None):
    """Additive anti-aliased polyline segments into 2-D float buffer.
    x,y in pixel coords; w = mass per segment (scalar or per-seg array)."""
    H, W = buf.shape
    x0 = np.asarray(x0, float); y0 = np.asarray(y0, float)
    x1 = np.asarray(x1, float); y1 = np.asarray(y1, float)
    L = np.hypot(x1 - x0, y1 - y0)
    if npts is None:
        npts = int(np.clip(np.median(L) * 1.5, 2, 4000))
    t = np.linspace(0, 1, npts)
    xs = x0[:, None] + (x1 - x0)[:, None] * t
    ys = y0[:, None] + (y1 - y0)[:, None] * t
    ws = (np.broadcast_to(np.asarray(w, float)[..., None] if np.ndim(w) else
          np.full(x0.shape + (1,), float(w)), xs.shape) / npts)
    _bilin(buf, xs.ravel(), ys.ravel(), ws.ravel())


def _bilin(buf, x, y, w):
    H, W = buf.shape
    xf = np.floor(x); yf = np.floor(y)
    fx = x - xf; fy = y - yf
    for dx in (0, 1):
        for dy in (0, 1):
            xi = (xf + dx).astype(np.int64)
            yi = (yf + dy).astype(np.int64)
            m = (xi >= 0) & (xi < W) & (yi >= 0) & (yi < H)
            wt = w * (fx if dx else 1 - fx) * (fy if dy else 1 - fy)
            np.add.at(buf, (yi[m], xi[m]), wt[m])


def splat_points(buf, x, y, w):
    _bilin(buf, np.asarray(x, float), np.asarray(y, float),
           np.broadcast_to(np.asarray(w, float), np.shape(x)).astype(float))


def bloom(rgb, sigma, gain, mask_thresh=0.55):
    lum = rgb.max(axis=2)
    m = np.clip((lum - mask_thresh) / (1 - mask_thresh), 0, 1) ** 1.5
    src = rgb * m[..., None]
    ds = max(1, int(sigma / 6))
    small = src[::ds, ::ds]
    bl = np.stack([gaussian_filter(small[..., c], sigma / ds) for c in range(3)], axis=2)
    if ds > 1:
        from scipy.ndimage import zoom
        bl = zoom(bl, (rgb.shape[0] / bl.shape[0], rgb.shape[1] / bl.shape[1], 1),
                  order=1)
        bl = bl[:rgb.shape[0], :rgb.shape[1]]
    return rgb + gain * bl


def filmic(rgb, k=1.0, gamma=0.88):
    out = 1 - np.exp(-k * np.clip(rgb, 0, None))
    return np.clip(out, 0, 1) ** gamma


def caption(img_rgb, lines, margin=28, size=13, color=(210, 215, 225), title_color=(255, 230, 170), pos='bottom'):
    """Draw caption lines (list of str; first = title) bottom-left. img in [0,1]."""
    from PIL import Image, ImageDraw, ImageFont
    S = img_rgb.shape[0]
    sc = S / 1024.0
    im = Image.fromarray((np.clip(img_rgb, 0, 1) * 255).astype(np.uint8))
    dr = ImageDraw.Draw(im)
    try:
        ft = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', int(size * sc))
        ftb = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', int((size + 3) * sc))
    except OSError:
        ft = ftb = ImageFont.load_default()
    y = int(margin * sc) if pos == 'top' else S - int(margin * sc) - int((len(lines) + 1.6) * size * 1.55 * sc)
    for i, ln in enumerate(lines):
        f = ftb if i == 0 else ft
        col = title_color if i == 0 else color
        dr.text((int(margin * sc), y), ln, font=f, fill=col)
        y += int(size * 1.55 * sc * (1.6 if i == 0 else 1.0))
    return np.asarray(im).astype(np.float64) / 255.0


def to_img(rgb, path, dither=True):
    from PIL import Image
    a = np.clip(rgb, 0, 1)
    if dither:
        a = a + (np.random.default_rng(1).random(a.shape) - 0.5) / 255.0
    Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).save(path)


def downscale(rgb, S):
    from PIL import Image
    im = Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8))
    im = im.resize((S, S), Image.LANCZOS)
    return np.asarray(im).astype(np.float64) / 255.0


def ramp(stops, t):
    """Multi-stop color ramp. stops: list of (pos, (r,g,b)). t in [0,1] array."""
    t = np.clip(np.asarray(t, float), 0, 1)
    out = np.zeros(t.shape + (3,))
    ps = [s[0] for s in stops]
    cs = [np.array(s[1]) for s in stops]
    for i in range(len(stops) - 1):
        m = (t >= ps[i]) & (t <= ps[i + 1])
        u = np.where(m, (t - ps[i]) / max(ps[i + 1] - ps[i], 1e-9), 0)
        out += m[..., None] * (cs[i] * (1 - u[..., None]) + cs[i + 1] * u[..., None])
    return out
