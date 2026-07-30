"""THE FREEZE  (panel 2, 2560x2560)

Why 2^^inf exists at all: mod every window n the tower 2^^k stops moving
after finitely many floors.  One column per window n = 2..385, floors
k = 1..12 stacked upward, cell hue = the residue 2^^k mod n.  Cells burn
while the residue is still in flight and dim to glacier-ice the moment
it reaches the value it will keep forever; the gold coastline is the
freeze boundary.  Pale-gold ringed cells are FALSE ARRIVALS: floors
where the tower already touches its final value, leaves again, and only
later comes home for good (n = 7 does this on floor 1).  The upper field
is 2^^inf itself, one hue per window.  Frozen values = OEIS A245970
(10000/10000 exact); freeze heights verified to lambda-chain depth + 3.
"""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_common import *
from scipy.ndimage import gaussian_filter
from PIL import Image, ImageDraw

PROTO = int(os.environ.get('PROTO', '0'))
FINAL = 1200 if PROTO else 2560
SS = 2
S = FINAL * SS
rs = S / 2400.0

d = np.load(SC + 'freeze_data.npz')
trajs, k0s, tvals = d['trajs'], d['k0s'], d['tvals']
NMIN, NMAX = 2, 385
ns = np.arange(NMIN, NMAX + 1)
NC = len(ns)
K = 12

STOPS = np.array([
    [0.10, 0.08, 0.38], [0.05, 0.42, 0.55], [0.10, 0.62, 0.36],
    [0.85, 0.62, 0.12], [0.85, 0.25, 0.30], [0.42, 0.16, 0.55],
    [0.10, 0.08, 0.38],
], dtype=np.float32)
def cmap(x):
    t = (np.asarray(x, dtype=np.float64) % 1.0) * (len(STOPS) - 1)
    i = np.minimum(t.astype(int), len(STOPS) - 2)
    fr = (t - i)[..., None].astype(np.float32)
    return (STOPS[i] * (1 - fr) + STOPS[i + 1] * fr).astype(np.float32)

GLACIER = np.array([0.42, 0.60, 0.82], np.float32)
GOLD = np.array([1.0, 0.78, 0.28], np.float32)

MX = int(0.028 * S)
FOOT = int(0.078 * S)
TOPM = int(0.026 * S)
wrow = np.array([4.2, 4.2, 4.6, 5.0, 5.0, 4.6, 3.6, 2.8, 2.2, 1.8, 1.5, 1.3])
ICE_FRACT = 0.30
usable = S - FOOT - TOPM - int(0.012 * S)
row_h = (wrow / wrow.sum() * (1 - ICE_FRACT) * usable).astype(int)
ice_h = usable - row_h.sum()
y_bot = S - FOOT - int(0.012 * S)
ybounds = [y_bot]
for k in range(K):
    ybounds.append(ybounds[-1] - row_h[k])
y_ice_top = ybounds[-1] - ice_h
colw = (S - 2 * MX) / NC

img = np.zeros((S, S, 3), dtype=np.float32)
x_edges = (MX + np.arange(NC + 1) * colw).astype(int)
gapx = max(1, int(round(1.0 * rs)))
gapy = max(1, int(round(1.2 * rs)))

glint = np.zeros((S, S), dtype=np.float32)   # false-arrival rims
coast = np.zeros((S, S), dtype=np.float32)

for j in range(NC):
    n = ns[j]
    x0, x1 = x_edges[j] + gapx, x_edges[j + 1] - gapx
    if x1 <= x0: x1 = x0 + 1
    k0 = int(k0s[n]); tv = int(tvals[n])
    for k in range(1, min(k0, K + 1)):
        v = int(trajs[n, k - 1])
        ytop, ybotk = ybounds[k] + gapy, ybounds[k - 1] - gapy
        c = cmap(v / n) * 1.30
        img[ytop:ybotk, x0:x1] += c * 0.95
        if v == tv:   # false arrival: touches destiny, will leave again
            img[ytop:ybotk, x0:x1] += np.array([0.55, 0.50, 0.34], np.float32)
            glint[ytop:ybotk, x0 - gapx:x0] = 1.0
            glint[ytop:ybotk, x1:x1 + gapx] = 1.0
            glint[ytop - gapy:ytop, x0:x1] = 1.0
            glint[ybotk:ybotk + gapy, x0:x1] = 1.0
    # from the coast upward: one continuous ice thread, hue = destiny
    c = cmap(tv / n)
    g = c.mean()
    cice = (0.52 * c + 0.48 * GLACIER * (0.28 + 0.72 * g))
    y_coast = ybounds[k0 - 1]
    xpad = max(1, int(round(0.7 * rs)))
    xa, xb = x0 + xpad, max(x0 + xpad + 1, x1 - xpad)
    n_ice = y_coast - y_ice_top
    prof = (0.88 - 0.64 * np.linspace(1.0, 0.0, n_ice) ** 2.0)[:, None, None]  # bright at coast, fade at top
    img[y_ice_top:y_coast, xa:xb] += cice * prof
    # coastline segment (bottom edge of first frozen floor)
    yy = ybounds[k0 - 1]
    hw = max(1, int(round(1.6 * rs)))
    coast[yy - hw:yy + hw, x_edges[j]:x_edges[j + 1]] = 1.0
    # vertical connector to the next column's coast level
    if j + 1 < NC:
        yy2 = ybounds[int(k0s[ns[j + 1]]) - 1]
        if yy2 != yy:
            ya, yb = sorted((yy, yy2))
            coast[ya - hw:yb + hw, x_edges[j + 1] - hw:x_edges[j + 1] + hw] = 1.0

img += gaussian_filter(coast, 1.6 * rs)[..., None] * GOLD * 1.25
img += gaussian_filter(coast, 8 * rs)[..., None] * GOLD * 0.32
img += gaussian_filter(glint, 1.0 * rs)[..., None] * np.array([1.0, 0.92, 0.60], np.float32) * 0.85

img = tonemap(img, k=1.5, gamma=0.88)

im = Image.fromarray((img * 255).astype(np.uint8))
dr = ImageDraw.Draw(im)
f1 = font(int(0.019 * S), bold=True)
f2 = font(int(0.0112 * S))
f3 = font(int(0.0095 * S))
ty = S - FOOT + int(0.011 * S)
dr.text((MX, ty), "THE FREEZE", font=f1, fill=(232, 224, 206))
dr.text((MX, ty + int(0.027 * S)),
        "2↑↑k mod n · floors k = 1…12, one column per window n = 2…385 · burning cells: residues still in flight ·  "
        "threads above the gold coast: 2↑↑∞ itself, frozen forever",
        font=f2, fill=(152, 150, 160))
dr.text((MX, ty + int(0.0445 * S)),
        "gold-washed cells: false arrivals — the tower touches its final value, leaves, and later comes home for good · "
        "frozen values = OEIS A245970: 10000/10000 exact",
        font=f2, fill=(122, 120, 132))
for k in [1, 2, 3, 4, 5, 6, 8, 12]:
    ymid = (ybounds[k] + ybounds[k - 1]) // 2
    dr.text((int(0.005 * S), ymid - int(0.005 * S)), f"k={k}", font=f3, fill=(115, 117, 133))
dr.text((int(0.005 * S), (y_ice_top + ybounds[K]) // 2), "2↑↑∞", font=f3, fill=(130, 134, 150))

if im.size != (FINAL, FINAL):
    im = im.resize((FINAL, FINAL), Image.LANCZOS)
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'freeze_proto.png' if PROTO else 'freeze.png')
im.save(out, optimize=True)
print("saved", out, im.size)
