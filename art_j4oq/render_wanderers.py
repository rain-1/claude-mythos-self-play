"""render_wanderers.py — THE CIRCLE EVERY WANDERER CARRIES.
Geocentric paths of the five naked-eye planets (JPL DE421), 2000–2030, Earth at the centre, stars fixed.
Strobe register: one bead per 6 hours, so dwell time is tone. Each planet one pigment family.
Coral: the Sun's yearly circle — the loop of every outer planet has exactly its radius (Ptolemy's shared epicycle,
Copernicus's clue). Radial scale: r_display ∝ log(1 + r / r0) so Mercury's whorl and Saturn's crown share a sheet."""
import numpy as np, sys, os, time
from scipy.ndimage import gaussian_filter
from pastel import *
from ephem import geo_path

FINAL = int(sys.argv[1]) if len(sys.argv) > 1 else 1024
SS = 2
W = H = FINAL * SS
rs = FINAL / 1024 * SS
out = sys.argv[2] if len(sys.argv) > 2 else f'cache/wanderers_{FINAL}.png'
Y0, Y1 = 2000, 2031
R0 = float(os.environ.get('R0', '1.0'))        # AU, log-warp scale
RMAXD = 0.455 * W
r_out = 11.2
WARP = os.environ.get('WARP', 'log')
def warp(r):
    if WARP == 'sqrt': return RMAXD * np.sqrt(r / r_out)
    if WARP == 'lin': return RMAXD * r / r_out
    return RMAXD * np.log1p(r / R0) / np.log1p(r_out / R0)
cx, cy = W / 2, H / 2 - 0.015 * H
PLAN = [('mercury', ('lemon', 'apricot'), 0.5), ('venus', ('apricot', 'blush'), 0.5), ('mars', ('orchid', 'lavender'), 1.0),
        ('jupiter', ('pistachio', 'mint'), 1.0), ('saturn', ('cornflower', 'aqua'), 1.0)]
yy_, xx_ = np.mgrid[0:H, 0:W]
sh = Sheet(W, H, seed=23)
t0 = time.time()
KNEE = float(os.environ.get('KNEE', '3.0'))
SIG = float(os.environ.get('SIG', '1.5'))
INSET = float(os.environ.get('INSET', '4.5'))       # magnification of the heart (r <= 2.2 AU) in the corner
icx, icy, irad = 0.20 * W, 0.735 * H, 0.165 * W
def place(name, x, y, mag=1.0, ox=cx, oy=cy):
    r = np.hypot(x, y); th = np.arctan2(y, x)
    rd = warp(r) * mag
    return ox + rd * np.cos(th), oy - rd * np.sin(th)
for name, (pa, pb), _ in PLAN + ([(n, p, 'inset') for n, p, _ in PLAN[:3]] if INSET > 0 else []):
    d = geo_path(name, Y0, Y1, 0.25)
    x, y = d['x'], d['y']
    inset = _ == 'inset'
    if inset:
        m = np.hypot(x, y) < 2.2
        x, y = x[m], y[m]
        px, py = place(name, x, y, INSET, icx, icy)
    else:
        px, py = place(name, x, y)
    yr = 2000.0 + (d['t'] - 2451545.0) / 365.25
    if inset: yr = yr[m]
    # pigment blend: by elongation family?  no — by TIME (history as palette) within the planet's pair
    f = (yr - Y0) / (Y1 - Y0)
    hgt = np.zeros((H, W), np.float32); hgt2 = np.zeros((H, W), np.float32)
    h0, _, _ = np.histogram2d(py, px, bins=[H, W], range=[[0, H], [0, W]], weights=1 - f)
    h1, _, _ = np.histogram2d(py, px, bins=[H, W], range=[[0, H], [0, W]], weights=f)
    h0 = gaussian_filter(h0.astype(np.float32), SIG * rs); h1 = gaussian_filter(h1.astype(np.float32), SIG * rs)
    both = h0 + h1
    ref = np.percentile(both[both > 0.03 * both.max()], 30)
    tone0 = 1 - np.exp(-h0 / (ref * KNEE)); tone1 = 1 - np.exp(-h1 / (ref * KNEE))
    if inset:   # the frame's disc: nothing outside
        tone0 *= (np.hypot(xx_ - icx, yy_ - icy) < irad); tone1 *= (np.hypot(xx_ - icx, yy_ - icy) < irad)
    sh.wash(1.2 * tone0, pa, granulate=0.1, seed=3); sh.wash(1.2 * tone1, pb, granulate=0.1, seed=4)
    print(name, 'ref', ref, 'max', both.max(), time.time() - t0)
# the Sun's circle in coral
yy, xx = yy_, xx_
rr = np.hypot(xx - cx, yy - cy)
ring = np.exp(-((rr - warp(1.0)) / (1.3 * rs)) ** 2)
sh.wash(0.9 * ring, 'coral')
sh.wash(discs_density(W, H, [cx], [cy], [3.0 * rs], [1.0], sigma=0.6 * rs) * 0.8, 'ink')
if INSET > 0:
    ri = np.hypot(xx - icx, yy - icy)
    sh.wash(0.9 * np.exp(-((ri - warp(1.0) * INSET) / (1.3 * rs)) ** 2) * (ri < irad), 'coral')
    sh.wash(discs_density(W, H, [icx], [icy], [3.0 * rs], [1.0], sigma=0.6 * rs) * 0.8, 'ink')
    sh.wash(0.5 * np.exp(-((ri - irad) / (0.9 * rs)) ** 2), 'ink')
    sh.wash(text_density(W, H, [(f'the heart, {INSET:g}× larger', icx, icy + irad + 8 * rs, 10 * rs, 'italic', 'mt')]) * 0.7, 'ink')
# radius scale ticks: 1, 2, 5, 10 AU as faint ink rings? keep air: labels only
items = []
for rv in [1, 2, 5, 10]:
    items.append((f'{rv} AU', cx + warp(rv) + 4 * rs, cy - 4 * rs, 9 * rs, 'italic', 'lm'))
sh.wash(text_density(W, H, items) * 0.6, 'ink')
sh.caption_strip(0.905, 0.985, 0.62)
items = [('The Circle Every Wanderer Carries', W / 2, 0.922 * H, 30 * rs, 'serif_bold', 'mm')]
sub = 'Mercury, Venus, Mars, Jupiter and Saturn around the Earth, 2000–2030, the stars held still, a bead every six hours, the radius drawn as its square root. Coral: the Sun’s yearly circle — in true scale every loop of Mars, Jupiter and Saturn is a copy of it.'
for i, ln in enumerate(wrap(sub, 13 * rs, 'italic', 0.84 * W)):
    items.append((ln, W / 2, 0.949 * H + i * 15.5 * rs, 13 * rs, 'italic', 'mm'))
sh.wash(text_density(W, H, items) * 0.95, 'ink')
finish(sh.develop(), (FINAL, FINAL), out)
print('done', time.time() - t0)
