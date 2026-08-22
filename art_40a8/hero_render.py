"""THE SKY OF OPEN DOORS — 4096^2 hero.
MO 514531: is 51 the sum of three rational fourth powers?
Chart: every fiber z/t = p/q (q <= 96) of the K3 surface x^4+y^4+z^4 = 51 t^4
at position (p/q, q). Verdicts from this run's computation:
  conic-dead fog (hue = witness prime), local-dead cyan micro-stars,
  survivors as golden doors (brightness by Jacobian rank; parity-forced),
  sealed / undecided fibers in ice / violet,
  near-miss ladders rising from fibers that own visible D_M-points,
  and the empty shore of squares that nothing reaches.
Run: python3 hero_render.py proto|final
"""
import json, sys, math
import numpy as np
from artlib import canvas, polyline, star, bloom, tonemap, save, bake_text, get_font
from scipy.ndimage import gaussian_filter

MODE = sys.argv[1] if len(sys.argv) > 1 else 'proto'
FINAL = 4096 if MODE == 'final' else 1024
SS = 2 if MODE == 'final' else 1
S = FINAL * SS
rs = S / 2048.0

D = json.load(open('hero_data.json'))
fib = D['fibers']
lad = {(l['p'], l['q']): l['pts'] for l in D['ladders']}

RHO_MAX = 51 ** 0.25          # 2.6724
QMAX = 96

# layout: sky occupies x in [0.055, 0.945]*S ; q rows from bottom (q=1) up.
XL, XR = 0.055 * S, 0.965 * S
Y0, Y1 = 0.905 * S, 0.115 * S           # q=1 baseline -> q=96 top row
SHORE_Y = 0.076 * S                     # the shore of squares
def fx(rho): return XL + (XR - XL) * rho / RHO_MAX
def fy(q):   return Y0 + (Y1 - Y0) * (q - 1) / (QMAX - 1)

buf = canvas(S)

# ---- palettes -------------------------------------------------------------
IND    = np.array([0.22, 0.26, 0.58])   # witness 3 fog: indigo
DBLUE  = np.array([0.17, 0.36, 0.60])   # witness 7 fog: dusty blue
TAIL   = np.array([0.36, 0.28, 0.55])   # big-prime tail: violet-grey
CYAN   = np.array([0.45, 0.95, 1.00])   # local-dead (deep wall) cyan
GOLD   = np.array([1.00, 0.78, 0.30])
EMBER  = np.array([1.00, 0.58, 0.22])
WHGOLD = np.array([1.00, 0.92, 0.62])
ICE    = np.array([0.62, 0.82, 1.00])   # sealed rank-0
VIOL   = np.array([0.75, 0.62, 0.95])   # undecided [0,2]
SHOREC = np.array([0.70, 0.98, 0.92])

# ---- dead fog -------------------------------------------------------------
xs3, ys3, xs7, ys7, xst, yst, ampt = [], [], [], [], [], [], []
amp3, amp7 = [], []
for f in fib:
    if f['verdict'] != 'conic_dead':
        continue
    x, y = fx(f['p'] / f['q']), fy(f['q'])
    w = int(f['wit'])
    qa = (1.0 / f['q']) ** 0.22
    if w == 3:   xs3.append(x); ys3.append(y); amp3.append(qa)
    elif w == 7: xs7.append(x); ys7.append(y); amp7.append(qa)
    else:
        xst.append(x); yst.append(y)
        ampt.append((1.0 + 0.35 * math.log(w / 11.0)) * qa)
fog = np.zeros((S, S, 3), np.float32)
def fogsplat(xs, ys, col, amp):
    if not xs: return
    a = np.full(len(xs), amp) if np.isscalar(amp) else np.asarray(amp) * 0.30
    from artlib import _splat_points
    _splat_points(fog, xs, ys, a, col, 1.0)
fogsplat(xs3, ys3, IND, np.asarray(amp3)*3.4)
fogsplat(xs7, ys7, DBLUE, np.asarray(amp7)*3.1)
fogsplat(xst, yst, TAIL, np.asarray(ampt)*3.2)
fogboost = (rs / 0.5) ** 1.85     # peak-preserving under the rs-scaled blur
fog = np.stack([gaussian_filter(fog[..., c], 1.1 * rs) for c in range(3)], -1)
buf += fog * 1.75 * fogboost / 1.0 if False else fog * (1.75 * fogboost)

# ---- local-dead: the 25 deep-wall fibers ----------------------------------
for f in fib:
    if f['verdict'] == 'local_dead':
        x, y = fx(f['p'] / f['q']), fy(f['q'])
        star(buf, x, y, CYAN, amp=1.9, rad=2.1 * rs)

# ---- survivors ------------------------------------------------------------
for f in fib:
    if f['verdict'] != 'survivor':
        continue
    x, y = fx(f['p'] / f['q']), fy(f['q'])
    rl, rh = f.get('rlow', -1), f.get('rhigh', -1)
    qsc = (1.0 / f['q']) ** 0.28
    if (rl, rh) == (0, 0):
        star(buf, x, y, ICE, amp=3.0, rad=2.9 * rs * qsc)
    elif rl == 0:
        star(buf, x, y, VIOL, amp=2.4, rad=2.5 * rs * qsc)
    elif rl >= 3:
        star(buf, x, y, WHGOLD, amp=5.0, rad=5.2 * rs * qsc)
        star(buf, x, y, GOLD, amp=1.8, rad=11.0 * rs * qsc)
    elif rl == 2:
        star(buf, x, y, EMBER, amp=3.8, rad=3.9 * rs * qsc)
    elif rh > rl:  # [1,3]
        star(buf, x, y, GOLD, amp=4.2, rad=3.6 * rs * qsc)
    else:          # (1,1) the parity-forced doors
        star(buf, x, y, GOLD, amp=3.4, rad=2.9 * rs * qsc)

# ---- near-miss ladders ----------------------------------------------------
# thread rises from the fiber; rung k at height ~ log(point height); thread
# fades upward (it is infinite); no thread reaches the shore.
LADTOP = 0.104 * S
rng = np.random.default_rng(51)
for (p, q), pts in lad.items():
    if not pts: continue
    x0, y0 = fx(p / q), fy(q)
    hmaxlog = math.log(3e7)
    ytop = y0 - (y0 - LADTOP) * 0.32          # visible thread length
    n = 60
    ts = np.linspace(0, 1, n)
    wob = 0.006 * S * np.sin(ts * 6.28 * (1.5 + rng.random()) + rng.random() * 6)
    xs = x0 + wob * ts
    ys = y0 - (y0 - ytop) * ts
    amps = (1 - ts) ** 1.6
    pl = np.stack([xs, ys], 1)
    polyline(buf, pl, GOLD * 0.85 + 0.15, amp=0.34 * rs, amps=list(amps[:-1]))
    for pt in pts:
        h = max(2.0, math.log(max(pt['hv'], 2)))
        t = min(0.92, h / hmaxlog)
        yr = y0 - (y0 - ytop) * t
        xr = x0 + 0.006 * S * math.sin(t * 6.28 * 1.8)
        star(buf, xr, yr, WHGOLD, amp=3.0, rad=2.2 * rs)

# ---- the primal fiber (1,1): architectural specimen -----------------------
xp, yp = fx(1.0), fy(1)
star(buf, xp, yp, WHGOLD, amp=3.2, rad=5.2 * rs)
star(buf, xp, yp, GOLD, amp=1.1, rad=13 * rs)
# its two real rungs drawn as beads on a brighter thread
for hv, t in ((1, 0.14), (7199, 0.52)):
    yr = yp - (yp - LADTOP) * 0.35 * t
    star(buf, xp + 0.004 * S * t, yr, WHGOLD, amp=1.6, rad=2.0 * rs)

# ---- the shore of squares -------------------------------------------------
xs = np.linspace(XL - 0.02 * S, XR + 0.02 * S, 900)
ys = SHORE_Y + 0.0035 * S * np.sin(xs / S * 19.0)
polyline(buf, np.stack([xs, ys], 1), SHOREC, amp=0.55 * rs)
gl = np.zeros((S, S, 3), np.float32)
polyline(gl, np.stack([xs, ys], 1), SHOREC, amp=0.9 * rs)
gl = np.stack([gaussian_filter(gl[..., c], 5 * rs) for c in range(3)], -1)
buf += gl * 0.45

img = bloom(buf, sigmas=(2 * rs, 9 * rs, 30 * rs), weights=(1.0, 0.38, 0.20),
            thresh=0.85)
img = tonemap(img, k=1.6, gamma=0.90, base=(0.010, 0.013, 0.024))

# ---- annotations ----------------------------------------------------------
W = FINAL
img_small = img if SS == 1 else None
from PIL import Image
arr = np.clip(img, 0, 1)
if SS != 1:
    im = Image.fromarray((arr * 255).astype(np.uint8)).resize((FINAL, FINAL), Image.LANCZOS)
    arr = np.asarray(im).astype(np.float32) / 255.0

def T(x, y, s, size, col, bold=False, anchor='la'):
    return (x * W, y * W, s, max(10, int(size * W / 2048)), col, bold, anchor)

GA = (1.0, 0.85, 0.55); GD = (0.62, 0.66, 0.82); CY = (0.55, 0.9, 0.95)
texts = [
    T(0.033, 0.012, 'THE SKY OF OPEN DOORS', 44, GA, True),
    T(0.033, 0.038, 'is 51 a sum of three rational fourth powers?  (MathOverflow 514531 — open; the shortest open diagonal equation, ℓ = 16+log₂51 ≈ 21.67)', 19, GD),
    T(0.968, 0.086, 'a ∈ ℚ² — the shore of squares: nothing has ever landed here', 18, CY, False, 'ra'),
    T(0.033, 0.930, 'every fiber z/t = p/q of  x⁴+y⁴+z⁴ = 51·t⁴  (7,495 fibers, q ≤ 96)   ·   fog: killed by the two-squares wall at a prime ≡ 3 (mod 4) — indigo 3, blue 7, violet tail', 17, GD),
    T(0.033, 0.948, 'cyan: killed by the deeper 2-adic / quartic-residue wall (25 fibers)   ·   gold: locally alive, Jacobian y² = x³+4Mx of rank ≥ 1 — 806 doors parity-forced open, ember rank 2, white rank 3', 17, GD),
    T(0.033, 0.966, 'ice: rank 0, sealed (9)   ·   violet: undecided [0,2] (10)   ·   root number w = −1 on 841 of 863 alive fibers: the walls that let a fiber live force its parity odd', 17, GD),
    T(0.033, 0.984, 'threads: real points of a² = M − v⁴ climbing each open door — every rung asks whether a is a square; every rung found (2·10⁵ all doors, 5·10⁶ on the brightest and the primal) answers no  ·  2026-08-22', 17, GD),
    T(fx(1.0)/S*1.0 + 0.012, 0.9195, 'the primal door  z = t :  50 = 1⁴ + 7² — but 7 is not a square', 15, GA, False, 'ma'),
]
arr = bake_text(arr, texts, W)
save(arr, f'sky_{MODE}.png', dither=True)
print('saved', f'sky_{MODE}.png')
