"""x^y = y^x as a three-drum risograph print.
h(t) = ln t / t ; phi = h(x) - h(y).  phi = 0 on y = x and on the friend curve
through (2,4); the two cross at the saddle (e, e).  Pink where x^y > y^x, aqua
where y^x > x^y, yellow on the curves where they trade places; the rational
pairs ((1+1/n)^n, (1+1/n)^(n+1)) as knocked-out discs marching into the saddle.
usage: python3 trade.py SIZE out.png [variant]
"""
import sys, math, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from riso import print_riso
from scipy.ndimage import gaussian_filter

S = int(sys.argv[1]); out = sys.argv[2]
V = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
lo, hi = V.get('lo', 1.0), V.get('hi', 7.4)
m0 = int(0.09 * S); m1 = int(0.09 * S)
top = int(0.07 * S); bot = int(0.80 * S)  # plot square: rows top..bot
side = bot - top
left = (S - side) // 2
y, x = np.mgrid[0:S, 0:S].astype(np.float64)
X = lo + (x - left) / side * (hi - lo)
Y = lo + (bot - y) / side * (hi - lo)
inside = (x >= left) & (x < left + side) & (y >= top) & (y < bot)
Xc = np.clip(X, 0.3, None); Yc = np.clip(Y, 0.3, None)
h = lambda t: np.log(t) / t
phi = h(Xc) - h(Yc)
# use a signed sqrt so bands are even on both sides of the saddle
q = np.sign(phi) * np.sqrt(np.abs(phi))
delta = V.get('delta', 0.042)
k = np.floor(q / delta)
fr = q / delta - k
band = np.abs(k).astype(int)
# stripes: alternate strong / pale, fading with distance from the zero set
strong, pale = V.get('strong', 0.78), V.get('pale', 0.26)
lev = np.where(band % 2 == 0, strong, pale)
# a soft gradient inside each band (riso posters love a halftone ramp)
ramp = V.get('ramp', 0.25)
lev = lev * (1 - ramp + ramp * np.where(k >= 0, fr, 1 - fr))
fade = np.clip(1.25 - 0.06 * band, 0.35, 1)
lev = lev * fade
pink = np.where((phi > 0) & inside, lev, 0)
aqua = np.where((phi < 0) & inside, lev, 0)
# pixel size in plot units
px = (hi - lo) / side
# distance to zero set ~ |phi| / |grad phi|
gx = (1 - np.log(Xc)) / Xc ** 2; gy = -(1 - np.log(Yc)) / Yc ** 2
dist = np.abs(phi) / np.sqrt(gx * gx + gy * gy + 1e-12)
lw = V.get('lw', 0.035)
yel = np.clip((lw - dist) / (1.2 * px) + 0.5, 0, 1) * inside
# white gutter either side of the yellow line
gut = np.clip((dist - lw * 1.9) / (1.2 * px) + 0.5, 0, 1)
pink *= gut; aqua *= gut
# rational pairs
pts = []
for n in range(1, 40):
    a = (1 + 1 / n) ** n; b = (1 + 1 / n) ** (n + 1)
    pts.append((a, b, n)); pts.append((b, a, n))
disc_knock = np.zeros_like(pink); disc_yel = np.zeros_like(pink); disc_pink = np.zeros_like(pink)
for a, b, n in pts:
    r = V.get('r0', 0.16) / n ** 0.55
    if r < 1.2 * px: continue
    d = np.sqrt((X - a) ** 2 + (Y - b) ** 2)
    ring = np.clip((r + 0.6 * lw - d) / (1.2 * px) + 0.5, 0, 1)
    core = np.clip((r - d) / (1.2 * px) + 0.5, 0, 1)
    disc_knock = np.maximum(disc_knock, ring)
    if n == 1:
        disc_pink = np.maximum(disc_pink, core * 0.9)
        disc_yel = np.maximum(disc_yel, core)
    else:
        disc_yel = np.maximum(disc_yel, core * 0.95)
pink = pink * (1 - disc_knock) + disc_pink
aqua = aqua * (1 - disc_knock)
yel = np.maximum(yel * (1 - disc_knock), disc_yel)
# the point (e, e) — a small aqua+pink target
d = np.sqrt((X - math.e) ** 2 + (Y - math.e) ** 2)
ee = np.clip((0.055 - d) / (1.2 * px) + 0.5, 0, 1)
pink = np.maximum(pink, ee * 0.0)

# ---- text drum (plum) : ticks, title, caption
txt = Image.new('L', (S, S), 0)
dr = ImageDraw.Draw(txt)
FB = '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'
FI = '/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf'
FR = '/usr/share/fonts/truetype/freefont/FreeSerif.ttf'
ft = ImageFont.truetype(FR, int(0.016 * S))
for t in range(int(math.ceil(lo)), int(hi) + 1):
    xp = left + (t - lo) / (hi - lo) * side
    yp = bot - (t - lo) / (hi - lo) * side
    dr.text((xp, bot + 0.012 * S), str(t), font=ft, fill=255, anchor='mt')
    dr.text((left - 0.012 * S, yp), str(t), font=ft, fill=255, anchor='rm')
fe = ImageFont.truetype(FI, int(0.018 * S))
xe = left + (math.e - lo) / (hi - lo) * side
dr.text((xe, bot + 0.012 * S), 'e', font=fe, fill=255, anchor='mt')
dr.text((left - 0.012 * S, bot - (math.e - lo) / (hi - lo) * side), 'e', font=fe, fill=255, anchor='rm')
f1 = ImageFont.truetype(FB, int(0.03 * S)); f2 = ImageFont.truetype(FI, int(0.0185 * S)); f3 = ImageFont.truetype(FR, int(0.0145 * S))
cy = bot + 0.055 * S
title = V.get('title', 'Two Who Trade Places')
dr.text((S / 2, cy), title, font=f1, fill=255, anchor='mt')
dr.text((S / 2, cy + 0.048 * S), V.get('l2', 'xʸ = yˣ off the diagonal: one whole pair, (2, 4), then the rational pairs x = (1+1/n)ⁿ, y = x·(1+1/n) marching into the saddle (e, e)'), font=f2, fill=255, anchor='mt')
dr.text((S / 2, cy + 0.08 * S), V.get('l3', 'pink: xʸ > yˣ   ·   aqua: yˣ > xʸ   ·   yellow: the two curves where they are equal   ·   stripes: level sets of ln x / x − ln y / y'), font=f3, fill=255, anchor='mt')
txt = np.asarray(txt).astype(np.float32) / 255

layers = [
    dict(ink='yellow', cov=yel, angle=0, cell=S / 340, density=0.95, mottle_sigma=S / 110),
    dict(ink='aqua', cov=aqua, angle=75, cell=S / 300, density=0.9, mottle_sigma=S / 100),
    dict(ink='fluo_pink', cov=pink, angle=15, cell=S / 300, density=0.85, mottle_sigma=S / 120),
    dict(ink='plum', cov=txt, angle=45, cell=S / 600, density=0.92, kind='grain'),
]
img = print_riso(layers, S, S, seed=V.get('seed', 4), misreg=S / 1400)
Image.fromarray((img * 255 + 0.5).astype(np.uint8)).save(out)
