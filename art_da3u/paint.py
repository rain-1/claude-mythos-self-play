import numpy as np
from PIL import Image, ImageDraw, ImageFont
from shutter import blade_field

def hexrgb(h): return np.array([int(h[i:i+2],16) for i in (1,3,5)])/255.
SORBET = {k: hexrgb(v) for k, v in dict(
    strawberry='#f7768e', coral='#ff8a73', peach='#ffb38a', butter='#ffe08a', lime='#c8ec8a',
    mint='#8fe3c0', sky='#8cc8f5', periwinkle='#9aa6f2', lilac='#c39af0', bubblegum='#f59ad8',
    rose='#f7a8b8', plum='#5c4d66').items()}
WHEEL = ['strawberry','peach','butter','lime','mint','sky','periwinkle','lilac','bubblegum']

def smooth_cov(s):
    gy, gx = np.gradient(s)
    g = np.hypot(gx, gy) + 1e-6
    d = s / g
    return np.clip(d + 0.5, 0, 1), d

def paint_pinwheel(img, X, Y, cx, cy, R, N, k, H, cols, phase=0.0, ink=1.6, curl=0.0, light=1.0, **kw):
    """composite a rolling-shutter pinwheel onto img (H,W,3 float) in place, region given by X,Y grids."""
    s, j, u, rr = blade_field(X, Y, cx, cy, R, N, k, H, phase=phase, curl=curl, **kw)
    cov, d = smooth_cov(s)
    base = np.stack([cols[i] for i in range(N)])[j]          # (...,3)
    # paper vane fold: one half lit, other half in soft shade; tip lighter
    fold = np.where(u > 0, 1.0, 0.84 + 0.10*np.abs(u))
    tipl = 0.9 + 0.18*rr
    c = base*fold[..., None]*tipl[..., None]
    c = 1 - (1 - np.clip(c, 0, 1))*light
    # crease highlight along centreline
    c = c + 0.10*np.exp(-(u/0.08)**2)[..., None]
    # thin ink rim
    rim = np.clip(1 - np.abs(d - ink*0.5)/ (ink*0.6), 0, 1)
    plum = SORBET['plum']
    c = c*(1 - 0.55*rim[..., None]) + plum*0.55*rim[..., None]
    a = cov[..., None]
    img[:] = img*(1 - a) + np.clip(c, 0, 1)*a
    return s

def paint_hub(img, X, Y, cx, cy, rad, col, ink=1.6):
    r = np.hypot(X - cx, Y - cy)
    d = rad - r
    a = np.clip(d + 0.5, 0, 1)[..., None]
    sh = 1 - 0.25*np.clip(((X - cx) + (Y - cy))/(rad*1.4), -1, 1)  # spherical button
    hl = np.exp(-(((X - cx + 0.35*rad)**2 + (Y - cy + 0.35*rad)**2)/(0.3*rad)**2))
    c = np.clip(col*sh[..., None]*0.95 + 0.35*hl[..., None], 0, 1)
    rim = np.clip(1 - np.abs(d - ink*0.5)/(ink*0.6), 0, 1)[..., None]
    c = c*(1 - 0.5*rim) + SORBET['plum']*0.5*rim
    img[:] = img*(1 - a) + c*a

FF = '/usr/share/fonts/truetype/freefont/'
def caption(im, x, y, lines, scale=1.0, ink=(92, 77, 102), align='left'):
    """lines: list of (text, style, size) with style in b/i/r; drawn on a PIL image."""
    d = ImageDraw.Draw(im)
    fn = {'b': 'FreeSerifBold.ttf', 'i': 'FreeSerifItalic.ttf', 'r': 'FreeSerif.ttf', 'm': 'FreeMono.ttf'}
    for text, st, sz in lines:
        f = ImageFont.truetype(FF + fn[st], int(sz*scale))
        w = d.textlength(text, font=f)
        xx = x - w/2 if align == 'center' else (x - w if align == 'right' else x)
        d.text((xx, y), text, font=f, fill=ink)
        y += int(sz*scale*1.32)
    return y
