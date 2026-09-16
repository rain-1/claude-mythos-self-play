"""render_sky.py — THE LAST LIGHT: the microwave sky as a pastel Mollweide ellipse.

Temperature above the mean -> warm family (lemon -> apricot -> blush), below -> cool (mint -> aqua -> cornflower),
density by |dT| with a soft knee.  Ink: nothing but the ellipse's own edge.  Coral: one circle of the
first acoustic peak's angular size, drawn at the ellipse's centre — the loudest note, about a degree wide.
    python3 render_sky.py <nside> <final_w>
"""
import sys, json
import numpy as np
import healpy as hp
from scipy.ndimage import gaussian_filter
from pastel import *
from sky import mollweide, gnomonic

nside = int(sys.argv[1]) if len(sys.argv) > 1 else 1024
FW = int(sys.argv[2]) if len(sys.argv) > 2 else 2048
FH = int(FW * 0.86)               # ellipse on top, patch + caption below
SS = 1 if FW >= 2048 else 2
W, H = FW * SS, FH * SS
rs = FW / 2048 * SS * 2
m = hp.read_map('cache/sky_%d.fits' % nside)
cert = json.load(open('cache/sky_cert.json'))
sigma = m.std()
# ellipse occupies the top part: width 0.94 W
EW = int(0.92 * W)
EH = EW // 2
ell, inside = mollweide(m, EW, EH)
print('projected', ell.shape, 'rms', sigma)
# map temperature to two families
x = np.nan_to_num(ell / sigma, nan=0.0)
warm = np.clip(x, 0, None)
cool = np.clip(-x, 0, None)
def knee(v, k=2.0):
    return (1 - np.exp(-v / k)) * k
dw = knee(warm); dc = knee(cool)
# family drift with amplitude: 0..1 sigma lemon/mint, 1..2 apricot/aqua, >2 blush/cornflower
def split(d, fam):
    out = {}
    u = np.clip(d / 2.2, 0, 1)
    h = u * (len(fam) - 1)
    i0 = np.floor(h).astype(int); i1 = np.minimum(i0 + 1, len(fam) - 1); fr = h - i0
    for k, name in enumerate(fam):
        wgt = np.where(i0 == k, 1 - fr, 0) + np.where(i1 == k, fr, 0)
        out[name] = d * wgt
    return out
sheet = Sheet(W, H, seed=21)
ox, oy = (W - EW) // 2, int(0.03 * H)
full = np.zeros((H, W), np.float32)
gain = 1.5
for fam, d in ((['lemon', 'apricot', 'blush'], dw), (['mint', 'aqua', 'cornflower'], dc)):
    for name, dens in split(d, fam).items():
        f = np.zeros((H, W), np.float32)
        f[oy:oy + EH, ox:ox + EW] = dens
        sheet.wash(f * gain, name, granulate=0.08, seed=3)
# the ellipse's edge in ink (hairline), and the painter's leaves the outside as paper
edge = np.zeros((H, W), np.float32)
edge[oy:oy + EH, ox:ox + EW] = inside.astype(np.float32)
from scipy.ndimage import distance_transform_edt
dist = distance_transform_edt(edge > 0.5)
rim = np.exp(-((dist - 0.0) / (1.4 * rs)) ** 2) * (edge > 0.5)
sheet.wash(rim * 0.7, 'ink')
# the magnified patch: a 14-degree tangent-plane window, drawn below the ellipse at the left,
# and the coral circle of the first peak's angular size inside it (the loudest note)
fov = 14.0
PW = int(0.30 * W); PH = PW
patch = gnomonic(m, PW, PH, fov, lon0=np.radians(40.0), lat0=np.radians(-20.0))
xp = patch / sigma
pw_ = knee(np.clip(xp, 0, None)); pc_ = knee(np.clip(-xp, 0, None))
px0 = int(0.04 * W); py0 = oy + EH + int(0.035 * H)
for fam, d in ((['lemon', 'apricot', 'blush'], pw_), (['mint', 'aqua', 'cornflower'], pc_)):
    for name, dens in split(d, fam).items():
        f = np.zeros((H, W), np.float32)
        f[py0:py0 + PH, px0:px0 + PW] = dens
        sheet.wash(f * gain, name, granulate=0.08, seed=4)
# the window's frame (hairline) and its footprint on the ellipse (hairline circle)
frame = np.zeros((H, W), np.float32); frame[py0:py0 + PH, px0:px0 + PW] = 1
dist2 = distance_transform_edt(frame > 0.5)
sheet.wash(np.exp(-(dist2 / (1.4 * rs)) ** 2) * (frame > 0.5) * 0.7, 'ink')
deg = cert['peak_deg']
px_per_deg = PW / fov
rad = 0.5 * deg * px_per_deg
cxx, cyy = px0 + PW / 2, py0 + PH / 2
theta = np.linspace(0, 2 * np.pi, 400)
ring = polyline_density(W, H, list(zip(cxx + rad * np.cos(theta), cyy + rad * np.sin(theta))), max(1.0, 2.0 * rs), closed=True)
sheet.wash(gaussian_filter(ring, 0.4 * rs) * 1.3, 'coral')
# footprint of the window on the ellipse: Mollweide position of (lon 40, lat -20)
R = EW / (2 * np.sqrt(2))
lat0 = np.radians(-20.0); lon0 = np.radians(40.0)
th_ = lat0
for _ in range(50):
    th_ = th_ - (2 * th_ + np.sin(2 * th_) - np.pi * np.sin(lat0)) / (2 + 2 * np.cos(2 * th_))
fx = ox + EW / 2 + (2 * np.sqrt(2) / np.pi) * R * lon0 * np.cos(th_)
fy = oy + EH / 2 - np.sqrt(2) * R * np.sin(th_)
fr_ = 0.5 * fov * (2 * np.sqrt(2) * R / np.pi) * (np.pi / 180) * np.cos(th_)
foot = polyline_density(W, H, list(zip(fx + fr_ * np.cos(theta), fy + fr_ * np.sin(theta))), max(1.0, 1.4 * rs), closed=True)
sheet.wash(gaussian_filter(foot, 0.4 * rs) * 0.8, 'ink')
print('peak deg', deg, 'ring radius px', rad, 'footprint', fx, fy, fr_)
# caption
title = 'The Last Light'
sub = ('The microwave sky at 380,000 years, drawn from the Planck spectrum: the plasma ended here and everything '
       'we can see began. Below, a window of %d degrees; the coral circle is the loudest note, %.1f degrees across.' % (int(fov), deg))
size_t = int(30 * rs); size_s = int(15.5 * rs)
tx = px0 + PW + 0.05 * W
ty = py0 + 0.30 * PH
items = [(title, tx, ty, size_t, 'serif_bold', 'lm')]
lines = wrap(sub, size_s, 'italic', W - tx - 0.05 * W)
for i, ln in enumerate(lines):
    items.append((ln, tx, ty + (0.11 + 0.075 * i) * PH, size_s, 'italic', 'lm'))
sheet.wash(text_density(W, H, items), 'ink')
img = sheet.develop()
finish(img, (FW, FH), 'cache/sky_%d_%d.png' % (nside, FW))
