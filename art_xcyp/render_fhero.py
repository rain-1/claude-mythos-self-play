#!/usr/bin/env python3
"""THE CEILING TOUCHED TWICE — MO 514772, f(n) census to n = 8192.

f(n) = the most lattice points a circle can carry on its rim while holding
EXACTLY n lattice points inside. The parity bound floor(2+sqrt(8n+4)) is a
straight line in the sqrt(n) chart; the census (every circle through >= 3
lattice points, translation-deduped, exact integer arithmetic) shows reality
touches that ceiling exactly twice — n = 0 and n = 4 — and then departs
forever: the true growth is n^(Theta(1)/loglog n), and every record is set
by a half-integer-center circle whose 4r^2 climbs the split-prime tower
2, 10, 50, 130, 650, 2210, 8450 (= 2 x {1, 5, 25, 65, 325, 1105, 4225}).

Registers: main sky = (sqrt n, k) chart: parity ceiling exiting the frame,
population fog of all 1.49M k>=4 circle classes, the achieved f(n) as warm
dust, records as gold stars, the unique void n = 6 as an ice needle, the 14
f(n)=3 stragglers as embers, census shoreline at n = 8192, and the next
tower rung — f >= 48 at n = 8660, direct count, NOT proven maximal — as a
beacon in the dark sea beyond. Bottom: the seven record circles as domes
rising at TRUE common scale from one baseline, rim beads = lattice points
on the rim, each dome under its record star.
"""
import numpy as np, sys, math
import scipy.ndimage as ndi
from PIL import Image, ImageDraw, ImageFont

PROTO = len(sys.argv) > 1 and sys.argv[1] == "proto"
SIZE = 1024 if PROTO else 4096
SS = 2
S = SIZE * SS
rs = SIZE / 1024.0

# ---------------- data
best = {}; wit = {}
pop = []
for line in open("fcensus_8192.txt"):
    p = line.split()
    if p[0] == "F":
        n = int(p[1]); best[n] = int(p[2]); wit[n] = tuple(map(int, p[3:]))
    else:
        pop.append((int(p[1]), int(p[2]), int(p[3])))
NMAX = max(best)
RECS = [(0, 4), (4, 8), (32, 12), (96, 16), (500, 24), (1716, 32), (6624, 36)]
STRAG = sorted(n for n in best if best[n] == 3)
VOID = 6
BEACON = (8660, 48)          # exact direct count; lower bound, not proven max

# ---------------- chart frame
XL = math.log(60001.0)       # x = ln(n+1); both beacons fit in the sea
KMAX = 52.0
x0f, x1f = 0.045, 0.975
y_sky0, y_sky1 = 0.700, 0.055
def X(n):  return (x0f + (x1f - x0f) * math.log(n + 1) / XL) * S
def Xv(n): return (x0f + (x1f - x0f) * np.log(n + 1) / XL) * S
def Y(k):  return (y_sky0 + (y_sky1 - y_sky0) * k / KMAX) * S
SHORE_X = X(NMAX + 0.5)

img = np.zeros((S, S, 3), dtype=np.float32)
AMPF = rs ** 0.9

def splat_pts(xs_, ys_, amp, sig, col, buf=None):
    """Gaussian splats via bincount at quarter res then upsample (craft)."""
    if buf is None: buf = img
    H = np.zeros((S, S), dtype=np.float32)
    xi = np.clip(xs_.astype(int), 0, S - 1)
    yi = np.clip(ys_.astype(int), 0, S - 1)
    np.add.at(H.ravel(), yi * S + xi, amp.astype(np.float32))
    H = ndi.gaussian_filter(H, sig)
    for ch in range(3):
        buf[..., ch] += H * col[ch]
    return buf

def draw_line(p0, p1, w, col, amp=1.0):
    n = int(max(abs(p1[0]-p0[0]), abs(p1[1]-p0[1])) / 1.5) + 2
    t = np.linspace(0, 1, n)
    xs_ = p0[0] + (p1[0]-p0[0]) * t
    ys_ = p0[1] + (p1[1]-p0[1]) * t
    splat_pts(xs_, ys_, np.full(n, AMPF * amp * 1.5 / n * max(abs(p1[0]-p0[0]), abs(p1[1]-p0[1])) / 40), w, col)

def star(x, y, amp, sig, col):
    yy, xx = np.ogrid[max(0,int(y-6*sig)):min(S,int(y+6*sig)),
                      max(0,int(x-6*sig)):min(S,int(x+6*sig))]
    g = np.exp(-((xx-x)**2 + (yy-y)**2) / (2*sig*sig)).astype(np.float32) * amp
    for ch in range(3):
        img[max(0,int(y-6*sig)):min(S,int(y+6*sig)),
            max(0,int(x-6*sig)):min(S,int(x+6*sig)), ch] += g * col[ch]

# ---------------- 1. population fog (steel blue, count is the measure)
FOG = np.zeros((S, S), dtype=np.float32)
for n, k, c in pop:
    x = X(n); y = Y(k)
    xi, yi = int(x), int(y)
    if 0 <= xi < S and 0 <= yi < S:
        FOG[yi, xi] += c
FOG = ndi.gaussian_filter(FOG, (1.5 * SS * rs, 5.0 * SS * rs))
famp = np.power(FOG / max(FOG.max(), 1e-9), 0.42)
for ch, v in enumerate((0.30, 0.44, 0.62)):
    img[..., ch] += famp * v * 0.85
del FOG

# ---------------- 2. achieved f(n): warm dust on the frontier
ns_ = np.array([n for n in sorted(best) if best[n] >= 4], float)
ks_ = np.array([best[n] for n in sorted(best) if best[n] >= 4], float)
splat_pts(Xv(ns_), Y(ks_), np.full(len(ns_), 0.030 * AMPF), 1.5 * SS * rs, (1.0, 0.72, 0.38))

# running-max staircase (thin gold thread)
runmax = []
run = 0
for n in range(NMAX + 1):
    run = max(run, best[n]); runmax.append(run)
nnn = np.arange(0, NMAX + 1, 0.25); pts_x = Xv(nnn); pts_y = Y(np.array(runmax, float)[nnn.astype(int)])
splat_pts(pts_x, pts_y, np.full(len(pts_x), 0.012 * AMPF), 1.1 * SS * rs, (1.0, 0.85, 0.45))

# ---------------- 3. the parity ceiling: a line that leaves the frame
nn_ = np.concatenate([np.linspace(0, 8, 1600), np.geomspace(8, 400, 10400)])
ky = 2 + np.sqrt(8 * nn_ + 4)
m = ky <= KMAX + 2
splat_pts(Xv(nn_[m]), Y(ky[m]), np.full(m.sum(), 0.026 * AMPF), 1.3 * SS * rs, (0.95, 0.80, 0.42))
# tight points blaze ON the line
for n, k in [(0, 4), (4, 8)]:
    star(X(n), Y(k), 2.2, 3.6 * SS * rs, (1.15, 0.95, 0.55))

# ---------------- 4. record stars + connection threads to domes (later)
for n, k in RECS:
    star(X(n), Y(k), 2.0, 4.0 * SS * rs, (1.2, 0.98, 0.5))
    star(X(n), Y(k), 0.9, 1.6 * SS * rs, (1.3, 1.15, 0.8))

# ---------------- 5. the void n=6: ice needle
xv = X(VOID)
vv = np.linspace(Y(1.0), Y(14.0), 500)
splat_pts(np.full(500, xv), vv, np.full(500, 0.050 * AMPF), 1.5 * SS * rs, (0.45, 0.85, 1.05))
star(xv, Y(1.0), 1.5, 2.8 * SS * rs, (0.5, 0.9, 1.15))

# ---------------- 6. stragglers f=3: crimson embers
for n in STRAG:
    star(X(n), Y(3.0), 0.75, 2.6 * SS * rs, (1.05, 0.30, 0.22))

# ---------------- 7. shoreline + the dark sea + beacon
xs_line = np.full(500, SHORE_X)
ys_line = np.linspace(Y(KMAX), Y(0), 500)
splat_pts(xs_line, ys_line, np.full(500, 0.008 * AMPF), 2.2 * SS * rs, (0.55, 0.65, 0.75))
# sea shading: subtle cold gradient right of shore
gx = np.arange(S, dtype=np.float32)[None, :]
sea = np.clip((gx - SHORE_X) / (S - SHORE_X), 0, 1) ** 1.5
gyv = np.arange(S, dtype=np.float32)[:, None]
seamask = np.clip((0.74 * S - gyv) / (0.04 * S), 0, 1)
img[..., 2] += sea * seamask * 0.028; img[..., 1] += sea * seamask * 0.012
star(X(8660), Y(48), 1.6, 3.6 * SS * rs, (0.8, 1.0, 1.1))
star(X(8660), Y(48), 0.7, 1.5 * SS * rs, (1.0, 1.15, 1.2))
# the f>=64 beacon leaves the frame at the top: half-cropped star at the edge
star(X(50304), 0.020 * S, 1.4, 3.4 * SS * rs, (0.8, 1.0, 1.1))

# ---------------- 8. domes: record circles at TRUE common scale
UPX = 0.00425 * S              # px per lattice unit (biggest dome ~ 0.195 S)
BASE_Y = 0.982 * S
ground_amp = 0.05
# lattice ground: dim stars on integer grid across dome band
gx0, gx1 = int(0.02 * S), int(0.98 * S)
gxs, gys = [], []
band_h = int(50 * UPX)
for yy in range(0, int(band_h / UPX) + 1):
    y = BASE_Y - yy * UPX
    if y < 0.72 * S: break
    for xx in range(gx0, gx1, max(2, int(UPX))):
        gxs.append(xx + (yy % 2) * UPX * 0.5)  # offset alternate rows? no — keep square
gxs = []  # (skip textured ground; keep it clean — domes carry the lattice)

def circle_pts(A, G, F, num):
    """lattice points on and strictly inside the circle, relative to center."""
    cx = -G / (2 * A); cy = -F / (2 * A)
    r = math.sqrt(num) / (2 * A)
    on, inside = [], []
    for x in range(int(cx - r) - 2, int(cx + r) + 3):
        for y in range(int(cy - r) - 2, int(cy + r) + 3):
            v = A * (x * x + y * y) + G * x + F * y
            if v == 0: on.append((x - cx, y - cy))
            elif v < 0: inside.append((x - cx, y - cy))
    return r, on, inside

dome_font_pts = []
dome_xcur = 0.028 * S
for n, k in RECS:
    A, G, F, num = wit[n]
    r, on, inside = circle_pts(A, G, F, num)
    dx = dome_xcur + r * UPX
    dome_xcur = dx + r * UPX + 0.0145 * S
    # dome arc (upper half): center on the baseline
    th = np.linspace(0, math.pi, max(60, int(r * UPX)))
    ax = dx + r * UPX * np.cos(th)
    ay = BASE_Y - r * UPX * np.sin(th)
    mvis = ay > 0.70 * S
    splat_pts(ax[mvis], ay[mvis], np.full(mvis.sum(), 0.030 * AMPF), 1.4 * SS * rs, (0.75, 0.78, 0.85))
    # interior lattice points (visible upper half only): soft slate dots
    ix = np.array([dx + p[0] * UPX for p in inside])
    iy = np.array([BASE_Y + p[1] * UPX for p in inside])
    mm = iy <= BASE_Y  # upper half (y grows downward)
    if mm.any():
        splat_pts(ix[mm], iy[mm], np.full(mm.sum(), 0.09 * AMPF), 1.0 * SS * rs, (0.48, 0.55, 0.68))
    # rim beads: gold
    for p in on:
        by = BASE_Y + p[1] * UPX
        if by <= BASE_Y + 2:
            star(dx + p[0] * UPX, by, 1.15, 1.7 * SS * rs, (1.25, 1.0, 0.5))
    # thread from record star down to dome crest
    draw_line((X(n), Y(k) + 8 * SS * rs), (dx, BASE_Y - r * UPX - 6 * SS * rs),
              1.0 * SS * rs, (0.5, 0.45, 0.3), amp=0.22)
    dome_font_pts.append((dx, n, k))

# baseline
splat_pts(np.linspace(0.02 * S, 0.98 * S, 2000), np.full(2000, BASE_Y),
          np.full(2000, 0.010 * AMPF), 1.5 * SS * rs, (0.5, 0.52, 0.6))

# ---------------- tone map + bloom
hot = np.clip(img.sum(2) - 2.2, 0, None)
ds = 4
bloom = ndi.zoom(ndi.gaussian_filter(hot[::ds, ::ds], 9 * rs), ds, order=1)[:S, :S]
if bloom.shape != (S, S):
    bloom = np.pad(bloom, ((0, S - bloom.shape[0]), (0, S - bloom.shape[1])), mode="edge")
img += bloom[..., None] * np.array([0.9, 0.85, 0.6])[None, None, :] * 0.30
img = 1 - np.exp(-1.35 * np.clip(img, 0, None))
img = np.power(np.clip(img, 0, 1), 1 / 2.2)
img = (img + np.random.uniform(-1 / 255, 1 / 255, img.shape)).clip(0, 1)

im = Image.fromarray((img * 255).astype(np.uint8)).resize((SIZE, SIZE), Image.LANCZOS)

# ---------------- annotations
def loadfont(path, sz):
    try: return ImageFont.truetype(path, sz)
    except Exception: return ImageFont.load_default()
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
d = ImageDraw.Draw(im)
tx = int(0.050 * SIZE); ty = int(0.048 * SIZE)
d.text((tx, ty), "THE CEILING TOUCHED TWICE", font=loadfont(FB, int(31 * rs)),
       fill=(238, 216, 165)); ty += int(52 * rs)
for line in [
    "f(n) = the most lattice points on a circle's rim",
    "with exactly n lattice points inside  (MO 514772)",
    "exact census of every >= 3-point circle to n = 8192",
    "the ceiling f <= 2 + sqrt(8n+4) is met at n = 0 and 4,",
    "then never again: records ride the split-prime tower",
    "4r^2 = 2, 10, 50, 130, 650, 2210, 8450 — all centers",
    "half-integer; truth grows as n^(O(1)/loglog n)",
    "n = 6: the unique void (no 3-point circle holds it)",
    "f = 3 serves 14 stragglers; the last is n = 883",
    "past the shore: f(8660) >= 48, f(50304) >= 64 —",
    "known, not yet certain",
]:
    d.text((tx, ty), line, font=loadfont(FR, int(15 * rs)), fill=(168, 173, 185))
    ty += int(26 * rs)

fm = loadfont(FR, int(14.5 * rs))
fmL = loadfont(FR, int(13.0 * rs))
d.text((int(0.012 * SIZE), int(0.9865 * SIZE)),
       "n=0·4·32·96 -> f=4·8·12·16",
       font=fmL, fill=(130, 136, 150))
for i, (dx, n, k) in enumerate(dome_font_pts):
    if i < 4: continue
    lab = f"n={n}  f={k}"
    w = d.textlength(lab, font=fmL)
    d.text((dx / SS - w / 2, int(0.9865 * SIZE)), lab, font=fmL, fill=(130, 136, 150))
# axis hints
d.text((int(0.012 * SIZE), Y(KMAX) / SS / (S / SIZE)), "", font=fm)
for kk in (8, 16, 24, 32, 48):
    d.text((int(0.008 * SIZE), int(Y(kk) / SS) - int(8 * rs)), str(kk), font=fm, fill=(95, 100, 112))
for nn in (10, 100, 1000, 8192, 50000):
    xx = int(X(nn) / SS)
    d.text((xx - int(10 * rs), int(0.712 * SIZE)), f"{nn}", font=fm, fill=(95, 100, 112))
d.text((int(0.008 * SIZE), int(0.712 * SIZE)), "n (log) ->", font=fm, fill=(95, 100, 112))
d.text((int(X(8660) / SS) + int(14 * rs), int(Y(48) / SS) - int(8 * rs)),
       "f >= 48", font=fm, fill=(150, 185, 200))
d.text((int(X(0) / SS) + int(14 * rs), int(Y(4) / SS) - int(30 * rs)), "n=0", font=fm, fill=(190, 175, 130))
d.text((int(X(4) / SS) + int(14 * rs), int(Y(8) / SS) - int(30 * rs)), "n=4", font=fm, fill=(190, 175, 130))
d.text((int(X(6) / SS) - int(14 * rs), int(Y(15.5) / SS) - int(16 * rs)), "n=6: void", font=fm, fill=(120, 175, 205))
d.text((int(X(50304) / SS) - int(60 * rs), int(0.020 * S / SS) + int(16 * rs)),
       "f >= 64", font=fm, fill=(150, 185, 200))

OUT = "fhero_proto.png" if PROTO else "fhero_4096.png"
im.save(OUT)
print("wrote", OUT)
