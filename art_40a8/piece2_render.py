"""THE GATE OF TWENTY-FIVE — 2560^2, atlas piece 42.
Lower register: the Wall of 144 residues; arches = admissible run-starts
(l=3: 12 steel arches, l=4: 4 amber, l=5: the single gold arch at 94 mod 144).
Upper register: the depth country; the 14 open channels as lanes with their
first fences as beacons (574 up to 1.59e11), the ten closed channels as ice
stubs (certified: every 2-adic class dies), channel 25's lane with tonight's
hunt coverage and the drift-model's predicted fence band.
Run: python3 piece2_render.py proto|final
"""
import json, sys, math, re, os
import numpy as np
from artlib import canvas, polyline, star, bloom, tonemap, save, bake_text
from artlib import _splat_points
from scipy.ndimage import gaussian_filter

MODE = sys.argv[1] if len(sys.argv) > 1 else 'proto'
FINAL = 2560 if MODE == 'final' else 1024
SS = 2 if MODE == 'final' else 1
S = FINAL * SS
rs = S / 2048.0

gate = json.load(open('gate25_sets.json'))
FENCES = [(1, 574), (2, 4892), (8, 195617), (7, 1338754), (4, 1824184),
          (9, 5004814), (16, 101829775), (15, 119340578), (18, 2142811228),
          (14, 22690103300), (17, 33099743774), (24, 52909727729),
          (23, 158783559650)]
CLOSED = [3, 5, 6, 10, 11, 12, 13, 19, 20, 21, 22]

# hunt verdict
HUNT_X1 = 4.0e11
found25 = None
try:
    for ln in open('hunt_alarms_160000000000_400000000000.txt'):
        m = re.match(r'FIRST l=5 g=25 start=(\d+)', ln)
        if m: found25 = int(m.group(1))
except FileNotFoundError:
    pass
hunt_done = os.path.exists('hunt_rungap_160000000000_400000000000.txt')
# coverage now (density checkpoints)
cov = HUNT_X1 if hunt_done else 1.6e11
try:
    for ln in open('hunt_density_160000000000_400000000000.txt'):
        cov = max(cov, float(ln.split()[0]))
except Exception:
    pass

buf = canvas(S)
STEEL  = np.array([0.42, 0.58, 0.80])
AMBER  = np.array([1.00, 0.66, 0.25])
GOLD   = np.array([1.00, 0.80, 0.32])
WHGOLD = np.array([1.00, 0.93, 0.65])
ICE    = np.array([0.55, 0.75, 1.00])
LANE   = np.array([0.30, 0.36, 0.58])
PRED   = np.array([0.55, 0.85, 0.75])

# ---------------- the wall ----------------
WX0, WX1 = 0.055 * S, 0.945 * S
WY0, WY1 = 0.640 * S, 0.905 * S       # top, bottom of wall band
ncol = 144
colw = (WX1 - WX0) / ncol
def colx(r): return WX0 + (r + 0.5) * colw

# masonry: a real slab with glowing arch openings (distance-field capsules)
y0i, y1i = int(WY0), int(WY1)
Hs, Ws = y1i - y0i, S
yy, xx = np.mgrid[0:Hs, 0:Ws].astype(np.float32)
rng = np.random.default_rng(144)
slab = 0.055 + 0.016 * rng.standard_normal((Hs, Ws)).astype(np.float32)
slab = gaussian_filter(slab, 1.6 * rs)
# column mortar lines
mort = 0.5 + 0.5 * np.cos((xx - WX0) / colw * 2 * np.pi)
slab *= (0.86 + 0.14 * mort ** 8)
inwall = ((xx >= WX0) & (xx <= WX1)).astype(np.float32)
slabrgb = slab[..., None] * np.array([0.30, 0.36, 0.60], np.float32)[None, None, :]
glow = np.zeros((Hs, Ws, 3), np.float32)

def arch_df(r, col, amp, height, halfw):
    x = colx(r)
    ytop_rel = Hs - (WY1 - WY0) * height   # in slab coords (y grows down)
    d_seg = np.abs(xx - x)
    below = yy >= ytop_rel + halfw
    dx = xx - x
    dyc = yy - (ytop_rel + halfw)
    d_cap = np.sqrt(dx * dx + dyc * dyc)
    d = np.where(below, d_seg, d_cap)
    body = np.exp(-(d / halfw) ** 4)          # flat core, soft edge
    rim  = np.exp(-((d - halfw) / (0.9 * rs)) ** 2) * 0.8
    m = (yy >= ytop_rel - halfw)
    field = (body + rim) * m * amp
    for c in range(3):
        glow[..., c] += field * col[c]

for r in gate['3']['mod144']:
    arch_df(r, STEEL, 0.85, 0.50, 2.4 * rs)
for r in gate['4']['mod144']:
    arch_df(r, AMBER, 1.0, 0.70, 3.2 * rs)
for r in gate['5']['mod144']:
    arch_df(r, WHGOLD, 1.9, 0.93, 4.4 * rs)

buf[y0i:y1i] += (slabrgb * inwall[..., None] + glow * inwall[..., None])
del yy, xx, slab, mort, slabrgb, glow, inwall

# ---------------- the depth country ----------------
DY0, DY1 = 0.575 * S, 0.075 * S      # bottom (low n) -> top (high n)
NLO, NHI = 1e2, 1e13
def fy(n): return DY0 + (DY1 - DY0) * (math.log10(n) - 2) / (13 - 2)
GX0, GX1 = 0.075 * S, 0.925 * S
def gx(g): return GX0 + (GX1 - GX0) * (g - 1) / 25.0

# lanes
for g, first in FENCES:
    x = gx(g)
    n = 90
    ys = np.linspace(DY0, fy(first), n)
    amps = np.linspace(1.0, 0.35, n - 1)
    polyline(buf, np.stack([np.full(n, x), ys], 1), LANE * 1.6, amp=0.85 * rs, amps=list(amps))
    star(buf, x, fy(first), GOLD, amp=3.6, rad=3.8 * rs)
    star(buf, x, fy(first), GOLD*0.7, amp=1.0, rad=9.0 * rs)
    star(buf, x, fy(first), WHGOLD, amp=1.2, rad=1.7 * rs)
for g in CLOSED:
    x = gx(g)
    n = 24
    ys = np.linspace(DY0, DY0 - 0.028 * S, n)
    polyline(buf, np.stack([np.full(n, x), ys], 1), ICE, amp=0.5 * rs)
    star(buf, x, DY0 - 0.030 * S, ICE, amp=1.2, rad=1.9 * rs)

# channel 25
x25 = gx(25)
n = 120
ys = np.linspace(DY0, fy(cov), n)
amps = np.linspace(1.5, 0.9, n - 1)
polyline(buf, np.stack([np.full(n, x25), ys], 1), GOLD * 0.55 + STEEL * 0.45,
         amp=1.1 * rs, amps=list(amps))
# shoreline tick at coverage
polyline(buf, np.array([[x25 - 0.012 * S, fy(cov)], [x25 + 0.012 * S, fy(cov)]]),
         WHGOLD, amp=0.8 * rs)
if found25:
    star(buf, x25, fy(found25), WHGOLD, amp=5.0, rad=5.2 * rs)
    star(buf, x25, fy(found25), GOLD, amp=1.8, rad=12.0 * rs)
# prediction band (kappa in [0.28, 0.55]): glow between quantiles ~[3e11, 3e12]
pb = np.zeros((S, S, 3), np.float32)
nsamp = np.geomspace(2.2e11, 4.5e12, 320)
dens = np.exp(-0.5 * ((np.log10(nsamp) - math.log10(8.5e11)) / 0.33) ** 2)
for nn, dd in zip(nsamp, dens):
    star(pb, x25, fy(nn), PRED, amp=0.10 * dd, rad=7.5 * rs)
buf += pb
# ghost fence at the median prediction
polyline(buf, np.array([[x25 - 0.016 * S, fy(8.5e11)], [x25 + 0.016 * S, fy(8.5e11)]]),
         PRED, amp=0.7 * rs)

# beam from the gold arch to the base of lane 25
from artlib import catmull as _cat
bp = _cat([(colx(94), WY0 + 0.01 * S), ((colx(94) + gx(25)) / 2, (WY0 + DY0) / 2 - 0.02 * S),
           (gx(25), DY0)], closed=False, subdiv=80)
polyline(buf, bp, GOLD * 0.5 + STEEL * 0.5, amp=0.30 * rs)

# depth ticks
for e in (3, 6, 9, 12):
    yt = fy(10 ** e)
    polyline(buf, np.array([[0.052 * S, yt], [0.066 * S, yt]]), LANE * 2.2, amp=0.7 * rs)

img = bloom(buf, sigmas=(2 * rs, 9 * rs, 30 * rs), weights=(1.0, 0.38, 0.20), thresh=0.85)
img = tonemap(img, k=1.6, gamma=0.90, base=(0.010, 0.013, 0.024))

W = FINAL
from PIL import Image
arr = np.clip(img, 0, 1)
if SS != 1:
    im = Image.fromarray((arr * 255).astype(np.uint8)).resize((FINAL, FINAL), Image.LANCZOS)
    arr = np.asarray(im).astype(np.float32) / 255.0

def T(x, y, s, size, col, bold=False, anchor='la'):
    return (x * W, y * W, s, max(9, int(size * W / 2048)), col, bold, anchor)

GA = (1.0, 0.85, 0.55); GD = (0.62, 0.66, 0.82); CY2 = (0.62, 0.82, 0.78); IC = (0.62, 0.78, 0.95)
verdict = (f'HEARD at n = {found25:,}' if found25 else
           (f'still silent through {cov:.2e}' if hunt_done else f'hunt live, coverage {cov:.2e}'))
texts = [
    T(0.033, 0.014, 'THE GATE OF TWENTY-FIVE', 42, GA, True),
    T(0.033, 0.043, 'atlas piece 42 — ℤ[√2] members (primes ≡ ±3 mod 8 to even order): equal-gap runs of five, and the one channel that has never spoken', 18, GD),
    T(0.967, 0.014, 'channels g ≤ 25 · first fences 574 → 1.6·10¹¹', 17, GD, False, 'ra'),
    T(x25 / S, fy(8.5e11) / S - 0.025, 'predicted fence · drift-aware model', 15, CY2, False, 'ma'),
    T(x25 / S, fy(cov) / S + 0.013, f'g = 25: {verdict}', 16, GA, False, 'ma'),
    T(0.033, 0.918, 'the Wall: run-starts mod 144. steel arches: l=3 admissible (12) · amber: l=4 (4) · gold: the single l=5 arch at 94 (mod 144) — n ≡ 14 (mod 16), 4 (mod 9), proved & verified on 137 runs', 15, GD),
    T(0.033, 0.936, 'above: each open channel’s lane rises to its first fence (gold beacons, log-depth) · ice stubs: channels 3,5,6,10–13,19–22 CLOSED by finite 2-adic certificate (this run)', 15, GD),
    T(0.033, 0.954, 'surprise kept honest: gate 25 is ~4× WIDER than gate 17 (density 3.4e-3 vs 8.1e-4) — the silence is the width-tail of the gap law, not the door', 15, GD),
    T(0.033, 0.972, f'prediction committed before the verdict: E[fence in tonight’s window] ≈ 0.22–0.43, P(silent through 4·10¹¹) ≈ 65–80%, median fence ≈ 6·10¹¹–1.2·10¹²  ·  2026-08-22', 15, GD),
]
for g, first in FENCES:
    texts.append(T(gx(g) / S, fy(first) / S - 0.020, f'{g}', 14, GA, False, 'ma'))
texts.append(T(gx(25) / S, DY0 / S + 0.012, '25', 17, GA, False, 'ma'))
for e in (3, 6, 9, 12):
    texts.append(T(0.048, fy(10 ** e) / S - 0.007, f'10{chr(0x2070+e) if e<10 else "¹²"}', 14, GD, False, 'ra'))
texts.append(T(gx(11) / S, DY0 / S + 0.012, 'closed', 14, IC, False, 'ma'))
arr = bake_text(arr, texts, W)
save(arr, f'gate_{MODE}.png', dither=True)
print('saved', f'gate_{MODE}.png', 'verdict:', verdict)
