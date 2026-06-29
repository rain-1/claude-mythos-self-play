"""Shared helpers for the Sweden vista series: gradients, value/fractal noise,
bloom, tone-mapping, starfields and glows. NumPy + Pillow only."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter

def grid(H, W):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float64)
    return yy, xx, yy/H, xx/W

def lerp_color(t, pts):
    xs = np.array([p[0] for p in pts]); cs = np.array([p[1] for p in pts], float)/255
    out = np.empty(np.shape(t) + (3,))
    for c in range(3):
        out[..., c] = np.interp(t, xs, cs[:, c])
    return out

def vnoise(shape, sigma, s):
    r = np.random.default_rng(s).random(shape)
    b = gaussian_filter(r, sigma); b -= b.min(); b /= (b.max()+1e-9)
    return b

def noise1d(n, sigma, s):
    r = np.random.default_rng(s).random(int(n))
    b = gaussian_filter(r, sigma); b -= b.min(); b /= (b.max()+1e-9)
    return b

def fbm(shape, base_sigma, octaves, s, gain=0.5):
    out = np.zeros(shape); amp = 1.0; tot = 0.0; sig = base_sigma
    for o in range(octaves):
        out += amp * vnoise(shape, max(1.0, sig), s+o*7)
        tot += amp; amp *= gain; sig *= 0.5
    out /= tot
    return out

def bloom(layer, specs):
    """specs = list of (sigma, amp); returns summed blurred copies."""
    out = np.zeros_like(layer)
    for sig, amp in specs:
        out += gaussian_filter(layer, sig) * amp
    return out

def glow_point(yy, xx, cx, cy, rad, color, amp):
    g = np.exp(-(((xx-cx)**2 + (yy-cy)**2) / (2*rad**2)))
    return g[..., None] * np.array(color, float) * amp

def add_stars(img, H, W, ny, n, seed, ymax=0.8, tint=(1.0,0.98,0.92), amp=0.9):
    rng = np.random.default_rng(seed)
    sx = rng.integers(0, W, n); sy = (rng.power(0.7, n)*H*ymax).astype(int)
    mag = rng.power(3.0, n)
    star = np.zeros((H, W))
    for i in range(n):
        star[sy[i], sx[i]] += 0.25 + 1.3*mag[i]
    star *= np.clip((ymax+0.06-ny)/0.5, 0.05, 1.0)
    sg = gaussian_filter(star, 0.7) + 0.4*gaussian_filter(star, 2.2)
    img += sg[..., None]*np.array(tint)*amp
    return img

def tonemap(img, k=1.18, gamma=0.92):
    img = 1 - np.exp(-k*np.clip(img, 0, None))
    return np.clip(img, 0, 1) ** gamma

def to_pil(img):
    return Image.fromarray((np.clip(img,0,1)*255).astype(np.uint8))

def font(sz):
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
        try: return ImageFont.truetype(p, int(sz))
        except: pass
    return ImageFont.load_default()

def caption(pim, H, title, sub):
    d = ImageDraw.Draw(pim); S = H/1440.0
    fbig = font(40*S); fsm = font(21*S)
    x = int(60*S); cx = x
    for ch in title:
        d.text((cx, H-int(110*S)), ch, font=fbig, fill=(244,236,222))
        cx += d.textlength(ch, font=fbig) + int(6*S)
    d.text((int(62*S), H-int(56*S)), sub, font=fsm, fill=(176,184,210))
    return pim
