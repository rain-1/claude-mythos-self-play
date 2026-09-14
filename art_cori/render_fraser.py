"""render_fraser.py — CIRCLES YOU READ AS A SPIRAL.
The Fraser twisted-cord illusion, generated: concentric circles drawn as two-strand cords whose every dash is tilted
by alpha from the circle's tangent, on a checkerboard of arcs.  The eye integrates the local tilt into a spiral.
Certificate in coral: the curve whose tangent is everywhere tilted by alpha from the circle through it is the
logarithmic spiral r = r0·exp(theta·tan alpha) — that is the spiral you see; the ink is circles.

usage: python3 render_fraser.py FINAL alpha_deg out_prefix [nrings] [spiral 0/1]
"""
import sys, json, time
import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image, ImageDraw
import pastel as P

FINAL = int(sys.argv[1]); ALPHA = float(sys.argv[2]); OUT = sys.argv[3]
NR = int(sys.argv[4]) if len(sys.argv) > 4 else 13
SPIRAL = int(sys.argv[5]) if len(sys.argv) > 5 else 1
SS = 2; W = H = FINAL * SS; rs = FINAL / 1024.0 * SS
al = np.radians(ALPHA); t0 = time.time()
cx, cy = W / 2, 0.47 * H
R0, R1 = 0.045 * H, 0.42 * H
radii = R0 + (R1 - R0) * (np.arange(NR + 1) / NR) ** 1.0
SEC = 36                                             # checkerboard sectors

sheet = P.Sheet(W, H, seed=31)
yy, xx = np.mgrid[:H, :W]
rr = np.hypot(xx - cx, yy - cy); ph = np.arctan2(yy - cy, xx - cx)
# ---- checkerboard of arcs: ring band j × sector i, alternate aqua / paper, shifted by half a sector each band
band = np.searchsorted(radii, rr) - 1
sec = np.floor((ph + np.pi) / (2 * np.pi) * SEC + 0.5 * (band % 2)).astype(int)
inside = (rr >= radii[0]) & (rr < radii[-1])
check = ((sec + band) % 2 == 0) & inside
check = gaussian_filter(check.astype(np.float32), 0.6 * rs)
sheet.wash(1.05 * check, 'aqua', granulate=0.10, seed=2)
sheet.wash(0.10 * (1 - check) * inside, 'blush', granulate=0.10, seed=3)

# ---- twisted cords: in an annulus of width wc around every ring, dark/light stripes tilted by alpha from the tangent
# (barber-pole / rope): phase u = arc-length - radial offset / tan(alpha); dark where sin(2*pi*u/lam) > 0
wc = 4.2 * rs; lam = 9.0 * rs
dark_a = np.zeros((H, W), np.float32); light_a = np.zeros((H, W), np.float32)
for k, r in enumerate(radii):
    band_m = np.abs(rr - r) < wc / 2
    s_arc = r * ph
    u = s_arc - (rr - r) / np.tan(al)
    stripe = np.sin(2 * np.pi * u / lam)
    soft = np.clip(stripe / 0.35, -1, 1)                  # soft-edged stripes
    dark_a[band_m] = np.clip(soft[band_m], 0, 1)
    light_a[band_m] = np.clip(-soft[band_m], 0, 1)
dark_a = gaussian_filter(dark_a, 0.35 * rs); light_a = gaussian_filter(light_a, 0.35 * rs)
sheet.lighten(np.clip(light_a, 0, 1), 0.95)            # the light strand is paper
sheet.wash(1.25 * np.clip(dark_a, 0, 1), 'ink')

# ---- certificate: the log spiral the eye reads (tangent tilted by alpha from every circle it crosses)
if SPIRAL:
    th = np.linspace(0, np.log(R1 / R0) / np.tan(al), 4000)
    r_s = R0 * np.exp(th * np.tan(al))
    pts = [(cx + r_ * np.cos(t_ + np.pi / 2), cy + r_ * np.sin(t_ + np.pi / 2)) for r_, t_ in zip(r_s, th)]
    sp = P.polyline_density(W, H, pts, 1.3 * rs, sigma=0.4 * rs)
    sheet.wash(0.75 * np.clip(sp, 0, 1), 'coral')
    # and its mirror image, fainter: the tilt has a sign; the other spiral is what a mirrored cord would give
    pts2 = [(cx + r_ * np.cos(-t_ + np.pi / 2), cy + r_ * np.sin(-t_ + np.pi / 2)) for r_, t_ in zip(r_s, th)]
    sp2 = P.polyline_density(W, H, pts2, 1.0 * rs, sigma=0.4 * rs)
    sheet.wash(0.22 * np.clip(sp2, 0, 1), 'coral')
turns = np.log(R1 / R0) / np.tan(al) / (2 * np.pi)

title = 'Circles You Read as a Spiral'
sub = (f'{NR + 1} concentric circles, each drawn as a twisted cord whose strands lean {ALPHA:g}° off the circle, on a checkerboard of arcs. '
       'Nothing here spirals: follow any cord with a finger and it closes. The coral curve is what the eye makes of a constant lean — '
       f'the logarithmic spiral r = r₀·e^(θ·tan {ALPHA:g}°), which needs {turns:.1f} turns to cross the rings the cords close in one.')
fs_t = int(0.036 * H); fs_s = int(0.0125 * H)
sheet.caption_strip(0.905, 0.995, 0.6)
items = [(title, 0.05 * W, 0.935 * H, fs_t, 'serif_bold', 'ls')]
for j_, line in enumerate(P.wrap(sub, fs_s, 'italic', 0.90 * W)):
    items.append((line, 0.05 * W, (0.958 + 0.018 * j_) * H, fs_s, 'italic', 'ls'))
sheet.wash(0.95 * P.text_density(W, H, items), 'ink')
img = sheet.develop()
P.finish(img, (FINAL, FINAL), OUT + f'_{FINAL}.png')
json.dump(dict(alpha_deg=ALPHA, nrings=NR + 1, sectors=SEC, spiral_turns_R0_to_R1=float(turns), seconds=time.time() - t0),
          open(OUT + f'_{FINAL}_cert.json', 'w'), indent=1)
print('done [%.0fs]' % (time.time() - t0))
