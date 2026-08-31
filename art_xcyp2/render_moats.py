#!/usr/bin/env python3
"""THE WIDENING WATER — Gaussian prime moats (2560²).

The open Gaussian moat problem: can one walk to infinity on Gaussian primes
with bounded steps? Census (moats.c, verified against an independent
full-plane BFS at R=200): from 1+i, the step-sqrt2 walker is stranded on an
island of 27 quadrant primes (|z| <= 11.7); step 2 dies at 45.3; step 2*sqrt2
at 93.5; step 4 exhausts a COMPLETE continent of 695,275 quadrant primes
ending at |z| = 4312.6; the step-sqrt26 walker is still walking when it
crosses our horizon at |z| = 25,000 (32.4M primes, censored).

Chart: full disk, log-radius (the tiny first islands become inner rings);
hue = the smallest step class that reaches each prime; slate dust = primes
no ladder step reaches from home; beacons = the farthest stone of each
complete continent.
"""
import numpy as np, math, sys
import scipy.ndimage as ndi
from PIL import Image, ImageDraw, ImageFont

PROTO = len(sys.argv) > 1 and sys.argv[1] == "proto"
SIZE = 1024 if PROTO else 2560
SS = 2
S = SIZE * SS
rs = SIZE / 1024.0
R = 25000.0
B = 2048
NK = 6
bins = np.fromfile("moat_bins.bin", dtype=np.uint32).reshape(NK + 1, B, B)

# class colors: core white-gold -> gold -> amber -> ember -> teal -> ice; sea slate
CLASS_COL = np.array([
    [1.55, 1.35, 0.85],   # k=2
    [1.45, 1.05, 0.40],   # k=4
    [1.30, 0.80, 0.28],   # k=8
    [1.20, 0.44, 0.26],   # k=16  (the great continent)
    [0.20, 0.55, 0.55],   # k=26  (escapes; deep teal)
    [0.45, 0.62, 0.95],   # k=36
    [0.55, 0.60, 0.78],   # unreached orphan stones (bright slate sparkle)
], dtype=np.float32)
CLASS_AMP = [3.0, 2.4, 2.0, 0.95, 0.62, 0.7, 0.30]

# log-radius warp: rho = ln(r)/ln(R), clamped below at r0
r0 = 1.0
cx = 0.5 * S; cy = 0.60 * S
RAD = 0.368 * S

img = np.zeros((S, S, 3), np.float32)

cell = R / B                       # lattice units per bin cell
jj, ii = np.mgrid[0:B, 0:B]
a = (ii + 0.5) * cell              # x-coord of cell center (quadrant)
b = (jj + 0.5) * cell
r = np.hypot(a, b)
theta = np.arctan2(b, a)           # [0, pi/2]
rho = np.log(np.maximum(r, r0)) / math.log(R)
rho = np.clip(rho, 0, 1)

core = np.loadtxt("moat_core.txt", dtype=np.int64)
core_a, core_b, core_c = core[:, 0], core[:, 1], core[:, 2]
core_r = np.hypot(core_a, core_b)
RCUT = 560.0
Hs = []
for c in range(NK + 1):
    cnt = bins[c].astype(np.float32)
    cnt = np.where(r < RCUT, 0.0, cnt)
    nz = cnt > 0
    m = (core_c == c) & (core_r < RCUT) & (core_r > 0)
    w = np.concatenate([cnt[nz], np.ones(m.sum(), np.float32)])
    rh = np.concatenate([rho[nz], np.log(np.maximum(core_r[m], r0)) / math.log(R)])
    th = np.concatenate([theta[nz], np.arctan2(core_b[m], core_a[m])])
    H = np.zeros((S, S), np.float32)
    for sx, sy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
        px = cx + sx * rh * RAD * np.cos(th)
        py = cy + sy * rh * RAD * np.sin(th)
        x0 = np.clip(px.astype(int), 0, S - 1)
        y0 = np.clip(py.astype(int), 0, S - 1)
        np.add.at(H.ravel(), y0 * S + x0, w)
    Hs.append(ndi.gaussian_filter(H, 1.3 * SS * rs))
Hs = np.stack(Hs)                    # (NK+1, S, S)
Htot = Hs.sum(0)
share = Hs / np.maximum(Htot, 1e-12)[None]
# hue = share-weighted class colors; luminance = log-density (histeq-lite)
lum = np.log1p(Htot)
lum = lum / max(np.percentile(lum[lum > 0], 99.0), 1e-9)
lum = 1 - np.exp(-2.0 * np.power(np.clip(lum, 0, None), 1.6))
# grain: local detail ratio (unsharp) keeps the prime stipple alive
smooth = ndi.gaussian_filter(Htot, 7 * SS * rs) + 1e-6
detail = np.clip(Htot / smooth, 0, 2.5)
lum = lum * (0.38 + 0.62 * np.power(detail / 1.6, 1.3))
colmix = np.tensordot(share, CLASS_COL, axes=(0, 0))    # (S,S,3)
img += colmix * lum[..., None] * 1.25
# the inner islands get a gentle extra glow (they are the protagonists)
inner = Hs[0] + Hs[1] + Hs[2]
ig = ndi.gaussian_filter(inner, 4 * SS * rs)
img += (ig / max(ig.max(), 1e-9))[..., None] * np.array([0.5, 0.42, 0.2])[None, None, :] * 0.8

# the three first islands: every stone an individual star (the protagonists)
sig_by_class = {0: 2.4, 1: 2.0, 2: 1.55}
amp_by_class = {0: 1.0, 1: 0.8, 2: 0.65}
mcore = core_r <= 94.0
for aa, bb, cc in zip(core_a[mcore], core_b[mcore], core_c[mcore]):
    if cc > 2: continue
    rv = math.hypot(aa, bb)
    rh_ = math.log(max(rv, r0)) / math.log(R)
    th_ = math.atan2(bb, aa)
    for sx, sy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
        px = cx + sx * rh_ * RAD * math.cos(th_)
        py = cy + sy * rh_ * RAD * math.sin(th_)
        y0i, y1i = int(py - 10 * SS * rs), int(py + 10 * SS * rs)
        x0i, x1i = int(px - 10 * SS * rs), int(px + 10 * SS * rs)
        if y0i < 0 or x0i < 0 or y1i >= S or x1i >= S: continue
        gy, gx = np.ogrid[y0i:y1i, x0i:x1i]
        g = np.exp(-((gx - px) ** 2 + (gy - py) ** 2) /
                   (2 * (sig_by_class[cc] * SS * rs) ** 2)).astype(np.float32)
        for ch in range(3):
            img[y0i:y1i, x0i:x1i, ch] += g * CLASS_COL[cc, ch] * amp_by_class[cc]
# the home stone 1+i
rh_ = math.log(math.sqrt(2)) / math.log(R)
for sx, sy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
    px = cx + sx * rh_ * RAD * math.cos(math.pi / 4)
    py = cy + sy * rh_ * RAD * math.sin(math.pi / 4)
    gy, gx = np.ogrid[max(0,int(py-40*rs)):int(py+40*rs), max(0,int(px-40*rs)):int(px+40*rs)]
    g = np.exp(-((gx-px)**2+(gy-py)**2)/(2*(5.0*SS*rs)**2)).astype(np.float32)
    for ch, v in enumerate((1.6, 1.5, 1.3)):
        img[max(0,int(py-40*rs)):int(py+40*rs), max(0,int(px-40*rs)):int(px+40*rs), ch] += g * v

# the four moats: thin ice rings at the exact death radii
import math as _m
for rv in (11.7047, 45.31, 93.47, 4312.63):
    rr_m = (_m.log(rv) / _m.log(R)) * RAD
    yy0, xx0 = np.mgrid[0:S, 0:S].astype(np.float32)
    dd = np.hypot(xx0 - cx, yy0 - cy)
    ringm = np.exp(-((dd - rr_m) / (1.1 * SS * rs)) ** 2)
    for ch, v in enumerate((0.30, 0.52, 0.72)):
        img[..., ch] += ringm * v * 0.55
    del yy0, xx0, dd, ringm

# horizon ring (the census shore)
yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
rr = np.hypot(xx - cx, yy - cy)
ring = np.exp(-((rr - RAD) / (1.6 * SS * rs)) ** 2)
for ch, v in enumerate((0.5, 0.62, 0.75)):
    img[..., ch] += ring * v * 0.32

def rho_of(rv): return math.log(max(rv, r0)) / math.log(R)

# beacons: farthest stone of each COMPLETE continent + the escape point
BEACONS = [
    (4, 11, 0, "step sqrt2 ends: |z|=11.7"),
    (17, 42, 1, "step 2 ends: 45.3"),
    (41, 84, 2, "step 2sqrt2 ends: 93.5"),
    (2780, 3297, 3, "step 4 ends: 4312.6"),
    (5833, 24310, 4, "step sqrt26: still walking at the horizon"),
]
def star(px, py, amp, sig, col):
    y0, y1 = max(0, int(py - 6 * sig)), min(S, int(py + 6 * sig))
    x0, x1 = max(0, int(px - 6 * sig)), min(S, int(px + 6 * sig))
    if y0 >= y1 or x0 >= x1: return
    gy, gx = np.ogrid[y0:y1, x0:x1]
    g = np.exp(-((gx - px) ** 2 + (gy - py) ** 2) / (2 * sig * sig)).astype(np.float32) * amp
    for ch in range(3):
        img[y0:y1, x0:x1, ch] += g * col[ch]

bpos = []
for a_, b_, c, lab in BEACONS:
    rv = math.hypot(a_, b_); th = math.atan2(b_, a_)
    px = cx + rho_of(rv) * RAD * math.cos(th)
    py = cy + rho_of(rv) * RAD * math.sin(th) * (1 if c % 2 else -1)  # alternate halves
    star(px, py, 1.6, 3.4 * SS * rs, (1.1, 1.05, 0.95))
    star(px, py, 0.7, 1.4 * SS * rs, CLASS_COL[c] * 1.2)
    bpos.append((px, py, lab))

# bloom
hot = np.clip(img.sum(2) - 2.3, 0, None)
ds = 4
bloom = ndi.zoom(ndi.gaussian_filter(hot[::ds, ::ds], 9 * rs), ds, order=1)[:S, :S]
if bloom.shape != (S, S):
    bloom = np.pad(bloom, ((0, S - bloom.shape[0]), (0, S - bloom.shape[1])), mode="edge")
img += bloom[..., None] * np.array([0.9, 0.8, 0.6])[None, None, :] * 0.25

img = 1 - np.exp(-1.25 * np.clip(img, 0, None))
img = np.power(np.clip(img, 0, 1), 1 / 2.1)
img = (img + np.random.uniform(-1 / 255, 1 / 255, img.shape)).clip(0, 1)
im = Image.fromarray((img * 255).astype(np.uint8)).resize((SIZE, SIZE), Image.LANCZOS)

# annotations
def loadfont(p, sz):
    try: return ImageFont.truetype(p, sz)
    except Exception: return ImageFont.load_default()
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
d = ImageDraw.Draw(im)
d.text((int(0.035 * SIZE), int(0.030 * SIZE)), "THE WIDENING WATER",
       font=loadfont(FB, int(30 * rs)), fill=(238, 216, 165))
y = int(0.078 * SIZE)
for line in [
    "the Gaussian moat problem (open): can one walk to infinity on Gaussian primes in bounded steps?",
    "from 1+i: step sqrt2 strands on 27 stones · step 2 dies at |z|=45 · step 2sqrt2 at 93",
    "step 4 exhausts a complete continent of 695,275 stones, last at |z| = 4,312.6",
    "step sqrt26 is still walking at our horizon |z| = 25,000  (32.4M stones, fate unknown)",
    "chart: log radius; hue = smallest step that reaches a stone; ice rings = the four moats",
    "engine verified against an independent full-plane BFS (exact agreement, R=200)",
]:
    d.text((int(0.035 * SIZE), y), line, font=loadfont(FR, int(15 * rs)), fill=(168, 173, 185))
    y += int(25 * rs)
fm = loadfont(FR, int(13.5 * rs))
for px, py, lab in bpos:
    d.text((int(px / SS) + int(10 * rs), int(py / SS) - int(18 * rs)), lab,
           font=fm, fill=(190, 190, 200))

OUT = "moats_proto.png" if PROTO else "moats_2560.png"
im.save(OUT)
print("wrote", OUT)
