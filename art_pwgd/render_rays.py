"""render_rays.py — what each marble does to light: exact ray portraits of the three lenses.

  LUNEBURG (waking)   a parallel bundle is gathered to ONE point of the far rim, then fans out
  FISH-EYE (dreaming) every ray leaving a rim point meets again at its antipode
  EATON  (deep sleep) every ray of a bundle turns round the centre and goes home

All arcs are exact (harmonic ellipses, Maxwell circles, Kepler half-ellipses) from grin.lens_map /
beam.inside_arc.  Rays are drawn alpha-over (thin pastel threads stay clean where they cross); the
glass is a radial glaze proportional to n(r) − 1.

usage: render_rays.py W H out.png [key=val]
"""
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter
from grin import lens_map, nrm
from beam import inside_arc

ARG = dict(a.split('=', 1) for a in sys.argv[4:] if '=' in a)
def P(k, d): return type(d)(ARG.get(k, d))
W, H, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
SS = 2; WW, HH = W * SS, H * SS

WHEEL = [(1.00, 0.52, 0.62), (1.00, 0.70, 0.52), (1.00, 0.86, 0.46), (0.76, 0.93, 0.50), (0.52, 0.90, 0.76),
         (0.52, 0.80, 1.00), (0.64, 0.66, 1.00), (0.80, 0.60, 1.00), (1.00, 0.60, 0.90)]
def wheel(h, span=1.0):
    x = (h % 1.0) * (len(WHEEL) - 1) * span; i = int(x) % len(WHEEL); t = x - int(x)
    a, b = np.array(WHEEL[i]), np.array(WHEEL[(i + 1) % len(WHEEL)])
    return a ** (1 - t) * b ** t

paper = np.array([0.993, 0.986, 0.976])
img = np.ones((HH, WW, 3), np.float32) * paper
g = gaussian_filter(np.random.default_rng(2).standard_normal((HH // 4, WW // 4)).astype(np.float32), 1.0)
img *= (1 + 0.010 * np.kron(g, np.ones((4, 4)))[:HH, :WW] / (np.abs(g).max() + 1e-9))[..., None]

panels = [dict(kind='lune', tint=(1.0, 0.86, 0.50)), dict(kind='fish', tint=(0.80, 0.66, 1.0)), dict(kind='eaton', tint=(0.60, 0.82, 1.0))]
band_top, band_h = P('top', 0.05) * HH, P('bh', 0.255) * HH
Rpx = P('R', 0.15) * WW
yy, xx = np.mgrid[0:HH, 0:WW].astype(np.float32)
centres = []
for pi, pn in enumerate(panels):
    cx, cy = WW * P('cx', 0.5), band_top + band_h * (pi + 0.5)
    centres.append((cx, cy))
    r = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / Rpx
    rr = np.clip(r, 1e-3, 1)
    n = {'lune': np.sqrt(2 - rr ** 2), 'fish': 2 / (1 + rr ** 2), 'eaton': np.sqrt(np.clip(2 / rr - 1, 0, 9))}[pn['kind']]
    dens = np.where(r < 1, np.clip(n - 1, 0, 1.6), 0) * P('gdens', 0.55)
    dens = gaussian_filter(dens.astype(np.float32), 1.0 * SS)
    img *= np.exp(-dens[..., None] * -np.log(np.array(pn['tint']))[None, None])
    # rim
    rim = np.exp(-((r - 1) * Rpx / (1.4 * SS)) ** 2)
    img *= np.exp(-0.35 * rim[..., None] * -np.log(np.array(pn['tint']) * 0.8))

canvas = Image.fromarray((np.clip(img, 0, 1) ** (1 / 2.2) * 255).astype(np.uint8)).convert('RGBA')
layer = None; dr = None
lw = max(1, int(round(P('lw', 0.0009) * WW)))
alpha = P('alpha', 120)

def line(pts, col, a, w=lw):
    rgb = tuple(int(255 * v ** (1 / 2.2)) for v in col)
    dr.line([tuple(map(float, p)) for p in pts], fill=rgb + (int(a),), width=w, joint='curve')

def to_px(p, c):
    return np.stack([c[0] + p[..., 0] * Rpx, c[1] - p[..., 1] * Rpx], -1)

coral_pts = []
far = P('far', 3.3)
for pi, pn in enumerate(panels):
    c = centres[pi]; kind = pn['kind']
    layer = canvas.copy(); dr = ImageDraw.Draw(layer, 'RGBA')
    rays = []
    if kind == 'lune':
        nb = P('nl', 140)
        for th_in, fade in ((0.0, 1.0), (P('obl', 0.62), P('oblf', 0.30)), (-P('obl', 0.62), P('oblf', 0.30))):
            d = np.array([np.cos(th_in), np.sin(th_in), 0.0])
            for i, b in enumerate(np.linspace(-0.995, 0.995, nb)):
                perp = np.array([-d[1], d[0], 0.0])
                P0 = -np.sqrt(1 - b * b) * d + b * perp
                rays.append((P0, d, i / (nb - 1), fade))
        coral_pts.append(to_px(np.array([1.0, 0.0]), c))
        for th in (P('obl', 0.62), -P('obl', 0.62)):
            coral_pts.append(to_px(np.array([np.cos(th), np.sin(th)]), c) )
    elif kind == 'fish':
        nb = P('nf', 120)
        for sgn in (1.0, -1.0):
            P0 = np.array([-sgn, 0.0, 0.0])
            for i, a in enumerate(np.linspace(-np.pi / 2 + 0.02, np.pi / 2 - 0.02, nb)):
                d = np.array([sgn * np.cos(a), np.sin(a), 0.0])
                h = i / (nb - 1) if sgn > 0 else 1 - i / (nb - 1)
                rays.append((P0, d, h, 1.0 if sgn > 0 else P('f2', 0.8)))
        coral_pts.append(to_px(np.array([-1.0, 0.0]), c)); coral_pts.append(to_px(np.array([1.0, 0.0]), c))
    else:
        nb = P('ne', 120)
        d = np.array([1.0, 0.0, 0.0])
        for i, b in enumerate(np.linspace(0.006, 0.995, nb)):
            P0 = np.array([-np.sqrt(1 - b * b), b, 0.0])
            rays.append((P0, d, i / (nb - 1), 1.0))
        coral_pts.append(to_px(np.array([0.0, 0.0]), c))
    for P0, d, h, fade in rays:
        col = wheel(P('h0', 0.0) + h * P('hspan', 0.88), 1.0)
        arc = inside_arc(kind, P0, d, n=120)
        Xe, De, L = lens_map(kind, P0[None], d[None])
        # incoming segment (from the panel's left edge), the arc, and the outgoing ray
        if kind != 'fish':
            t_in = np.linspace(far, 0, 30)
            pin = P0[None, :2] - t_in[:, None] * d[None, :2]
            line(to_px(pin, c), col, alpha * 0.55 * fade)
        line(to_px(arc[:, :2], c), col, alpha * fade)
        t_out = np.linspace(0, far, 40)
        pout = Xe[0, None, :2] + t_out[:, None] * De[0, None, :2]
        # fade the outgoing ray in segments
        for s in range(0, 39, 3):
            line(to_px(pout[s:s + 4], c), col, alpha * 0.55 * fade * (1 - s / 40) ** 1.2)
    # soft vertical window around the band, then composite
    la = np.asarray(layer).astype(np.float32); lc = np.asarray(canvas).astype(np.float32)
    yb = (np.arange(HH) - c[1]) / (band_h * 0.5)
    win = (np.clip((1.0 - np.abs(yb)) / 0.22, 0, 1) ** 1.5)[:, None, None]
    canvas = Image.fromarray((lc * (1 - win) + la * win + 0.5).astype(np.uint8))

img = np.asarray(canvas.convert('RGB')).astype(np.float32) / 255
img = img ** 2.2
# coral beads
R = P('kr', 0.0085) * WW
for (px, py) in coral_pts:
    x0b, x1b, y0b, y1b = int(px - 2 * R), int(px + 2 * R), int(py - 2 * R), int(py + 2 * R)
    X_, Y_ = xx[y0b:y1b, x0b:x1b] - px, yy[y0b:y1b, x0b:x1b] - py
    rr = np.sqrt(X_ ** 2 + Y_ ** 2) / R
    a = np.clip((1 - rr) * R * 0.7, 0, 1)[..., None]
    halo = np.exp(-(rr / 1.6) ** 2)[..., None] * 0.35
    z = np.sqrt(np.clip(1 - rr ** 2, 0, 1))
    base = np.array([0.98, 0.45, 0.40])
    shade = base * (0.72 + 0.28 * np.clip(-0.4 * X_ / R - 0.5 * Y_ / R + 0.75 * z, 0, 1))[..., None]
    shade = shade + 0.6 * np.exp(-((X_ / R + 0.35) ** 2 + (Y_ / R + 0.4) ** 2) / 0.03)[..., None]
    sub = img[y0b:y1b, x0b:x1b]
    sub = sub * (1 - halo) + halo * 1.0
    img[y0b:y1b, x0b:x1b] = sub * (1 - a) + a * np.clip(shade, 0, 1)
srgb = np.where(img <= 0.0031308, 12.92 * img, 1.055 * np.power(np.clip(img, 0, 1), 1 / 2.4) - 0.055)
pim = Image.fromarray((np.clip(srgb, 0, 1) * 255 + 0.5).astype(np.uint8)).resize((W, H), Image.LANCZOS)
dr = ImageDraw.Draw(pim)
FD = '/usr/share/fonts/truetype/liberation/'
INKc = (92, 77, 102)
if P('title', ''):
    tb = ImageFont.truetype(FD + 'LiberationSerif-Bold.ttf', int(0.030 * W))
    ti = ImageFont.truetype(FD + 'LiberationSerif-Italic.ttf', int(0.0155 * W))
    tr_ = ImageFont.truetype(FD + 'LiberationSerif-Regular.ttf', int(0.0128 * W))
    x, y = 0.07 * W, P('ty', 0.86) * H
    dr.text((x, y), P('title', ''), font=tb, fill=INKc); y += int(0.030 * W * 1.35)
    for line_, f_ in ((P('l1', ''), ti), (P('l2', ''), tr_), (P('l3', ''), tr_), (P('l4', ''), tr_)):
        if line_:
            dr.text((x, y), line_, font=f_, fill=INKc); y += int(f_.size * 1.4)
# small labels beside each lens
sl = ImageFont.truetype(FD + 'LiberationSerif-Italic.ttf', int(0.0125 * W))
for (cx, cy), t in zip(centres, P('labels', 'waking|dreaming|deep sleep').split('|')):
    dr.text((cx / SS, (cy + Rpx * 1.04) / SS), t, font=sl, fill=INKc, anchor='mt')
pim.save(out)
np.save(out.replace('.png', '_centres.npy'), np.array(centres) / SS)
print('saved', out)
