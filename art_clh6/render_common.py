"""Shared render kit: dark-field additive canvas, splats, filmic tonemap."""
import numpy as np
from scipy.ndimage import gaussian_filter, grey_dilation
from PIL import Image, ImageDraw, ImageFont

SC = '/tmp/claude-0/-home-user-claude-mythos-self-play/df482f23-d1ae-562a-8002-f98face66e54/scratchpad/'

def canvas(w, h):
    return np.zeros((h, w, 3), dtype=np.float32)

def splat_points(buf, xs, ys, rgb, amp, sigma):
    """Additive Gaussian splats, each windowed to +-4 sigma (bbox-local)."""
    H, W, _ = buf.shape
    R = max(2, int(4 * sigma))
    for x, y, a in zip(np.atleast_1d(xs), np.atleast_1d(ys), np.broadcast_to(amp, (len(np.atleast_1d(xs)),))):
        xi, yi = int(round(x)), int(round(y))
        x0, x1 = max(0, xi - R), min(W, xi + R + 1)
        y0, y1 = max(0, yi - R), min(H, yi + R + 1)
        if x0 >= x1 or y0 >= y1:
            continue
        gy = np.arange(y0, y1)[:, None] - y
        gx = np.arange(x0, x1)[None, :] - x
        g = np.exp(-(gx * gx + gy * gy) / (2 * sigma * sigma)).astype(np.float32)
        for c in range(3):
            buf[y0:y1, x0:x1, c] += a * rgb[c] * g

def vline(buf, x, y0, y1, rgb, amp, width):
    """Additive vertical soft bar from y0(bottom,larger) up to y1(top,smaller);
    amp may be scalar or per-row array of length |y0-y1|."""
    H, W, _ = buf.shape
    ylo, yhi = int(min(y0, y1)), int(max(y0, y1))
    ylo, yhi = max(0, ylo), min(H, yhi)
    if ylo >= yhi:
        return
    hw = width / 2.0
    x0, x1 = max(0, int(np.floor(x - hw - 2))), min(W, int(np.ceil(x + hw + 3)))
    if x0 >= x1:
        return
    gx = np.arange(x0, x1)[None, :] - x
    prof = np.exp(-0.5 * (gx / (hw * 0.6 + 1e-9)) ** 4).astype(np.float32)  # soft-edged bar
    a = np.asarray(amp, dtype=np.float32)
    if a.ndim == 0:
        a = np.full(yhi - ylo, float(a), dtype=np.float32)
    elif len(a) != yhi - ylo:
        a = np.interp(np.linspace(0, 1, yhi - ylo),
                      np.linspace(0, 1, max(2, len(a))),
                      a if len(a) >= 2 else np.repeat(a, 2)).astype(np.float32)
    col = a[:, None] * prof
    for c in range(3):
        buf[ylo:yhi, x0:x1, c] += rgb[c] * col

def bloom(buf, sigma, gain, thresh=0.55):
    lum = 0.2126 * buf[..., 0] + 0.7152 * buf[..., 1] + 0.0722 * buf[..., 2]
    m = np.clip((lum - thresh) / max(1e-9, lum.max() - thresh), 0, 1) ** 1.5
    src = buf * m[..., None]
    if sigma > 8:
        ds = max(1, int(sigma / 6))
        small = src[::ds, ::ds]
        bl = gaussian_filter(small, (sigma / ds, sigma / ds, 0))
        big = np.kron(bl, np.ones((ds, ds, 1), dtype=np.float32))[:buf.shape[0], :buf.shape[1]]
        pady, padx = buf.shape[0] - big.shape[0], buf.shape[1] - big.shape[1]
        if pady or padx:
            big = np.pad(big, ((0, pady), (0, padx), (0, 0)), mode='edge')
        bl = gaussian_filter(big, (2, 2, 0))
    else:
        bl = gaussian_filter(src, (sigma, sigma, 0))
    return buf + gain * bl

def tonemap(buf, k=1.0, gamma=0.86, dither=True):
    img = 1.0 - np.exp(-k * np.clip(buf, 0, None))
    img = np.clip(img, 0, 1) ** gamma
    if dither:
        img = img + (np.random.default_rng(7).random(img.shape).astype(np.float32) - 0.5) / 255.0
    return np.clip(img, 0, 1)

def save(img01, path, final_size=None):
    im = Image.fromarray((img01 * 255).astype(np.uint8))
    if final_size and im.size != (final_size, final_size):
        im = im.resize((final_size, final_size), Image.LANCZOS)
    im.save(path, optimize=True)
    return im.size

def font(sz, bold=False):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    for p in ("/usr/share/fonts/truetype/dejavu/", "/usr/share/fonts/dejavu/"):
        try:
            return ImageFont.truetype(p + name, sz)
        except OSError:
            continue
    return ImageFont.load_default()

def lerp(c1, c2, t):
    t = np.clip(t, 0, 1)
    return tuple(a + (b - a) * t for a, b in zip(c1, c2))

def ramp(stops, t):
    """stops: list of rgb; t in [0,1] -> piecewise-linear color."""
    t = float(np.clip(t, 0, 1)) * (len(stops) - 1)
    i = min(int(t), len(stops) - 2)
    return lerp(stops[i], stops[i + 1], t - i)
