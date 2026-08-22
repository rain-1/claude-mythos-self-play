"""THE FIFTH GUEST — 2560^2. The other country: x^4+y^4+z^4 = 17 t^4.
Same chart grammar as the hero (fiber sky, verdict palette) but log-q axis
climbing to the four landed constellations (Tomita's solutions, re-verified
and re-found by this run's independent engine), plus the trivial guest
0,1,2;1 on the ground row, plus the certified silence band above.
Run: python3 piece3_render.py proto|final
"""
import json, sys, math
import numpy as np
from artlib import canvas, polyline, star, bloom, tonemap, save, bake_text, catmull
from artlib import _splat_points
from scipy.ndimage import gaussian_filter
from math import gcd

MODE = sys.argv[1] if len(sys.argv) > 1 else 'proto'
FINAL = 2560 if MODE == 'final' else 1024
SS = 2 if MODE == 'final' else 1
S = FINAL * SS
rs = S / 2048.0

D = json.load(open('piece3_data.json'))
fib = D['fibers']
sols = D['sols']          # [[758,765,1066,583], ...]
TBOUND = 60000            # this run's certified search depth (updated at final)

RHO_MAX = 17 ** 0.25      # 2.0305
QTOP = 90000.0
XL, XR = 0.06 * S, 0.955 * S
Y0, Y1 = 0.895 * S, 0.070 * S
def fx(rho): return XL + (XR - XL) * rho / RHO_MAX
def fy(q):   return Y0 + (Y1 - Y0) * math.log(max(q, 1)) / math.log(QTOP)

buf = canvas(S)

IND    = np.array([0.22, 0.26, 0.58])
DBLUE  = np.array([0.17, 0.36, 0.60])
TAIL   = np.array([0.36, 0.28, 0.55])
CYAN   = np.array([0.45, 0.95, 1.00])
GOLD   = np.array([1.00, 0.78, 0.30])
EMBER  = np.array([1.00, 0.58, 0.22])
WHGOLD = np.array([1.00, 0.92, 0.62])
ICE    = np.array([0.62, 0.82, 1.00])
VIOL   = np.array([0.75, 0.62, 0.95])

# ---- ground sky (q <= 96), same grammar as hero ---------------------------
xs3, ys3, a3, xs7, ys7, a7, xst, yst, at_ = [], [], [], [], [], [], [], [], []
for f in fib:
    x, y = fx(f['p'] / f['q']), fy(f['q'])
    qa = (1.0 / f['q']) ** 0.22
    if f['verdict'] == 'conic_dead':
        w = int(f['wit'])
        if w == 3:   xs3.append(x); ys3.append(y); a3.append(qa)
        elif w == 7: xs7.append(x); ys7.append(y); a7.append(qa)
        else:
            xst.append(x); yst.append(y)
            at_.append((1.0 + 0.35 * math.log(w / 11.0)) * qa)
fog = np.zeros((S, S, 3), np.float32)
_splat_points(fog, xs3, ys3, np.asarray(a3) * 1.0, IND, 1.0)
_splat_points(fog, xs7, ys7, np.asarray(a7) * 0.92, DBLUE, 1.0)
if xst: _splat_points(fog, xst, yst, np.asarray(at_) * 0.95, TAIL, 1.0)
fogboost = (rs / 0.5) ** 1.85
fog = np.stack([gaussian_filter(fog[..., c], 1.1 * rs) for c in range(3)], -1)
buf += fog * (1.75 * fogboost)

for f in fib:
    x, y = fx(f['p'] / f['q']), fy(f['q'])
    v = f['verdict']
    if v == 'local_dead':
        star(buf, x, y, CYAN, amp=1.6, rad=1.9 * rs)
    elif v == 'survivor':
        rl, rh = f.get('rlow', -1), f.get('rhigh', -1)
        qsc = (1.0 / f['q']) ** 0.28
        if (rl, rh) == (0, 0):
            star(buf, x, y, ICE, amp=1.9, rad=2.3 * rs * qsc)      # many: dimmer than hero
        elif rl == 0:
            star(buf, x, y, VIOL, amp=1.5, rad=2.0 * rs * qsc)
        elif rl >= 3:
            star(buf, x, y, WHGOLD, amp=4.6, rad=4.6 * rs * qsc)
        elif rl == 2:
            star(buf, x, y, EMBER, amp=2.6, rad=3.0 * rs * qsc)
        else:
            star(buf, x, y, GOLD, amp=2.6, rad=2.6 * rs * qsc)

# ---- the guests -----------------------------------------------------------
def constellation(xyzt, label_y_off=0.0, trivial=False):
    x_, y_, z_, t = xyzt
    pts = []
    for v in (x_, y_, z_):
        g = gcd(v, t) if v else t
        p, q = (v // g, t // g) if v else (0, 1)
        pts.append((fx(p / q), fy(q)))
    pts.sort()
    P = np.asarray(pts, float)
    # gentle arc through the three stars
    mid = P[1] + np.array([0, -0.012 * S])
    arc = catmull([P[0], mid, P[2]], closed=False, subdiv=60)
    polyline(buf, arc, WHGOLD, amp=0.75 * rs)
    for (px, py) in pts:
        star(buf, px, py, WHGOLD, amp=5.0, rad=4.2 * rs)
        star(buf, px, py, GOLD, amp=1.6, rad=10.0 * rs)
    return pts

cpts = [constellation(s) for s in sols]
tpts = constellation([0, 1, 2, 1], trivial=True)
# the newcomer blazes
for (px, py) in cpts[-1]:
    star(buf, px, py, WHGOLD, amp=3.0, rad=6.5 * rs)
    star(buf, px, py, GOLD, amp=1.2, rad=16.0 * rs)

# ---- silence band above the guests ---------------------------------------
yb = fy(TBOUND)
xs = np.linspace(XL - 0.01 * S, XR + 0.01 * S, 700)
ys = yb + 0.003 * S * np.sin(xs / S * 23.0)
polyline(buf, np.stack([xs, ys], 1), np.array([0.55, 0.75, 0.85]), amp=0.4 * rs)

img = bloom(buf, sigmas=(2 * rs, 9 * rs, 30 * rs), weights=(1.0, 0.38, 0.20),
            thresh=0.85)
img = tonemap(img, k=1.6, gamma=0.90, base=(0.010, 0.013, 0.024))

W = FINAL
from PIL import Image
arr = np.clip(img, 0, 1)
if SS != 1:
    im = Image.fromarray((arr * 255).astype(np.uint8)).resize((FINAL, FINAL), Image.LANCZOS)
    arr = np.asarray(im).astype(np.float32) / 255.0

def T(x, y, s, size, col, bold=False, anchor='la'):
    return (x * W, y * W, s, max(9, int(size * W / 2048)), col, bold, anchor)

GA = (1.0, 0.85, 0.55); GD = (0.62, 0.66, 0.82); CY2 = (0.62, 0.80, 0.88)
sol_strs = ['1066⁴·… t=583', 't=1011', 't=1259', 't=2353']
texts = [
    T(0.033, 0.014, 'THE FIFTH GUEST', 44, GA, True),
    T(0.033, 0.044, 'the other country:  x⁴+y⁴+z⁴ = 17·t⁴ — same walls, same parity law; here the witnesses exist, and tonight a NEW one arrived', 20, GD),
    T(0.037, fy(TBOUND)/S + 0.010, f'certified: exactly five guests with t ≤ {TBOUND:,}  (this run’s meet-in-the-middle sweep)', 16, CY2, False, 'la'),
    T(0.033, 0.918, 'ground sky: 5,692 fibers q ≤ 96 (log-q axis) — 4,119 conic-dead, 124 deep-wall dead, 1,449 alive; only 348 parity-open (24%, against 97% for 51)', 16, GD),
    T(0.033, 0.936, 'constellations: each solution is three ratio-stars x/t, y/t, z/t joined by an arc — the four known re-found by this run’s engine, and a FIFTH discovered: t = 49,187 = 101·487', 16, GD),
    T(0.033, 0.954, '583 · 1011 · 1259 · 2353 (Tomita) — then a 21× gap to the newcomer:  52637⁴ + 78482⁴ + 85680⁴ = 17 · 49187⁴   (verified exactly; primitive)', 16, GD),
    T(0.033, 0.972, 'the country of mostly-shut doors has received five guests; the country of open doors (51) still none. MathOverflow 514531 · computed 2026-08-22', 16, GD),
]
# label each constellation near its top star (right-aligned if near edge)
for i, (sl, pts) in enumerate(zip(sols, cpts)):
    px, py = pts[-1]
    if i == len(sols) - 1:
        mx, my = pts[1]
        texts.append(T(mx / S, my / S + 0.024, f'the newcomer   t = {sl[3]}', 18, GA, False, 'ma'))
    elif px / S > 0.86:
        texts.append(T(px / S - 0.012, py / S - 0.017, f't = {sl[3]}', 17, GA, False, 'ra'))
    else:
        texts.append(T(px / S + 0.010, py / S - 0.017, f't = {sl[3]}', 17, GA))
texts.append(T(tpts[-1][0] / S - 0.012, tpts[-1][1] / S - 0.022, 'the trivial guest  0, 1, 2', 15, GA, False, 'ra'))
arr = bake_text(arr, texts, W)
save(arr, f'guests_{MODE}.png', dither=True)
print('saved', f'guests_{MODE}.png')
