"""THE KEYHOLE  (panel 3, 2560x2560)

Why door +3 is hard: mod p the frozen tower t = 2^^inf can only land
inside the tiny cyclic subgroup H = <2^(2^k)>, k = v2(p-1), of odd
order M = oddpart(ord_p(2)).  The door opens iff t lands EXACTLY on
-3 -- which first requires -3 to lie in H at all.  Among 92,937 primes
p < 1.2e6, only 23.4% are even eligible; the eligible fraction halves
with each step of k (the 2^-k law).  Each star: one eligible prime,
angle = how far around the subgroup the tower landed from -3 (the
keyhole ray points up, angle 0 -- forever empty), radius = ln ln p,
hue = k.  Ice-ringed stars: the five one-turn-off primes, where the
tower stopped a single generator step from the key.  Ledger: the
Sawin-Goucher expectation E = sum 1/M over eligible primes; by 6e15
E ~ 2.5 keys were 'due' -- none exist: P(such silence) ~ 8%.
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

d = np.load(SC + 'keyhole_data.npz')
p, k, M, elig, miss = d['p'], d['k'], d['M'], d['elig'], d['miss']
jt, j3 = d['jt'], d['j3']

CX, CY = S * 0.5, S * 0.445
LL = lambda x: np.log(np.log(np.asarray(x, dtype=np.float64)))
RMIN, RMAX = 0.055 * S, 0.385 * S
# rank-radius: uniform areal star density (chart declared in caption)
_psorted = np.sort(d['p'])
def rad_of(q):
    rk = np.searchsorted(_psorted, np.asarray(q, dtype=np.int64), side='right')
    return RMIN + np.sqrt(rk / len(_psorted)) * (RMAX - RMIN)

# strata hues by k = v2(p-1)
KHUE = {1: (1.00, 0.72, 0.28), 2: (1.00, 0.45, 0.22), 3: (0.95, 0.28, 0.33),
        4: (0.75, 0.22, 0.55), 5: (0.52, 0.25, 0.75), 6: (0.36, 0.32, 0.88)}
def khue(kk): return KHUE.get(int(min(kk, 6)))

buf = canvas(S, S)

# faint radius rings at p = 10^1..10^6
ringmask = np.zeros((S, S), np.float32)
yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
rr = np.sqrt((xx - CX) ** 2 + (yy - CY) ** 2)
for q in [100, 1000, 10 ** 4, 10 ** 5, 10 ** 6]:
    R = float(rad_of(q))
    ringmask += np.exp(-((rr - R) / (0.9 * rs)) ** 2) * 0.16
buf += ringmask[..., None] * np.array([0.28, 0.32, 0.45], np.float32) * 0.30
del rr

el = elig == 1
pe, ke, Me, me = p[el], k[el], M[el], miss[el]
jte, j3e = jt[el], j3[el]
ang = 2 * np.pi * me                      # 0 = keyhole ray (up)
theta = ang - np.pi / 2                   # screen angle; ray points up
xs = CX + rad_of(pe) * np.cos(theta)
ys = CY + rad_of(pe) * np.sin(theta)
# closeness accent: angular distance to the ray
adist = np.minimum(me, 1 - me)
boost = 1.0 + 5.0 * np.exp(-(adist / 0.006) ** 2) + 1.6 * np.exp(-(adist / 0.05) ** 2)

order = np.argsort(pe)                    # draw small p first
for i in order:
    c = khue(ke[i])
    a = 0.42 * boost[i]
    splat_points(buf, [xs[i]], [ys[i]], c, [a], (0.85 + 0.25 * (ke[i] == 1)) * rs)

# the keyhole ray: crimson, forever empty
n_ray = 900
tr = np.linspace(RMIN * 0.55, RMAX * 1.045, n_ray)
CRIM = (1.0, 0.16, 0.22)
splat_points(buf, CX + 0 * tr, CY - tr, CRIM, np.full(n_ray, 0.028), 1.6 * rs)
splat_points(buf, [CX], [CY - RMAX * 1.045], CRIM, [1.8], 3.0 * rs)
RAY_TIP = (CX, CY - RMAX * 1.045)

# one-turn-off primes: ice-ringed stars
one = el.copy()
one[el] = (Me > 2) & (((jte - j3e) % Me == 1) | ((jte - j3e) % Me == Me - 1))
po = p[one]
mo = miss[one]
th = 2 * np.pi * mo - np.pi / 2
xo = CX + rad_of(po) * np.cos(th)
yo = CY + rad_of(po) * np.sin(th)
ICE = (0.75, 0.93, 1.00)
for x_, y_, pp in zip(xo, yo, po):
    splat_points(buf, [x_], [y_], ICE, [2.2], 1.9 * rs)
    # ring
    tt = np.linspace(0, 2 * np.pi, 160)
    splat_points(buf, x_ + 5.5 * rs * np.cos(tt), y_ + 5.5 * rs * np.sin(tt), ICE,
                 np.full(160, 0.05), 1.0 * rs)

# smallest angular misses: gold champions
idx = np.argsort(adist)[:8]
GOLDC = (1.0, 0.82, 0.38)
for i in idx:
    splat_points(buf, [xs[i]], [ys[i]], GOLDC, [2.6], 2.1 * rs)

buf = bloom(buf, 7 * rs, 0.5, thresh=0.5)
buf = bloom(buf, 30 * rs, 0.28, thresh=0.6)
img = tonemap(buf, k=1.5, gamma=0.86)

im = Image.fromarray((img * 255).astype(np.uint8))
dr = ImageDraw.Draw(im)
f1 = font(int(0.019 * S), bold=True)
f2 = font(int(0.0110 * S))
f3 = font(int(0.0088 * S))

# ---- ledger strip ----
w = np.where(el, 1.0 / np.maximum(M, 1), 0.0)
cum = np.cumsum(w)
X0, X1 = LL(3), LL(6e15)
lx0, lx1 = int(0.075 * S), int(0.925 * S)
ly = int(0.900 * S)
lh = int(0.058 * S)
lxs = lx0 + (LL(p) - X0) / (X1 - X0) * (lx1 - lx0)
E_end = float(cum[-1])
C = float((cum[p > 1e5] - LL(p[p > 1e5])).mean())
E615 = float(LL(6e15) + C)
dr.line([(lx0, ly), (lx1, ly)], fill=(60, 62, 78), width=max(1, int(1.2 * rs)))
pts = [(float(lxs[i]), ly - cum[i] / E615 * lh) for i in range(0, len(p), 40)]
dr.line(pts, fill=(235, 185, 90), width=max(1, int(1.6 * rs)))
# dashed extrapolation
xe0, ye0 = pts[-1]
nseg = 26
for i in range(nseg):
    if i % 2: continue
    xa = xe0 + (lx1 - xe0) * i / nseg
    xb = xe0 + (lx1 - xe0) * (i + 1) / nseg
    ya = ly - (cum[-1] + (E615 - E_end) * (xa - xe0) / (lx1 - xe0)) / E615 * lh
    yb = ly - (cum[-1] + (E615 - E_end) * (xb - xe0) / (lx1 - xe0)) / E615 * lh
    dr.line([(xa, ya), (xb, yb)], fill=(200, 150, 70), width=max(1, int(1.4 * rs)))
for q, lab in [(1e2, "10²"), (1e6, "10⁶"), (1e10, "10¹⁰"), (6e15, "6·10¹⁵")]:
    xq = lx0 + (LL(q) - X0) / (X1 - X0) * (lx1 - lx0)
    dr.line([(xq, ly), (xq, ly + int(0.006 * S))], fill=(90, 92, 108), width=max(1, int(rs)))
    dr.text((xq - int(0.008 * S), ly + int(0.008 * S)), lab, font=f3, fill=(120, 122, 138))
dr.text((lx0, ly - lh - int(0.020 * S)),
        "the debt of keys E = Σ 1/M ≈ ln ln X + C · E(6×10¹⁵) ≈ %.2f keys due, 0 found · P(silence) ≈ %d%%"
        % (E615, round(100 * np.exp(-E615))), font=f3, fill=(150, 148, 158))

dr.text((int(CX + 0.012 * S), int(CY - RMAX * 1.06)), "−3", font=f3, fill=(235, 110, 118))
ty = int(0.938 * S)
dr.text((int(0.075 * S), ty), "THE KEYHOLE", font=f1, fill=(232, 224, 206))
dr.text((int(0.075 * S), ty + int(0.026 * S)),
        "door +3 · stars: the 21,731 eligible primes p < 1.2×10⁶ · angle = landing distance from −3 in H = ⟨2^(2^k)⟩",
        font=f2, fill=(150, 148, 158))
dr.text((int(0.075 * S), ty + int(0.0435 * S)),
        "crimson ray: the keyhole, empty below 6×10¹⁵ · blind primes (76.6%%, −3 ∉ H) not drawn · hue = v₂(p−1) · "
        "ice rings: one key-turn away (%s)" % ", ".join(str(int(q)) for q in po),
        font=f2, fill=(122, 120, 132))

if im.size != (FINAL, FINAL):
    im = im.resize((FINAL, FINAL), Image.LANCZOS)
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'keyhole_proto.png' if PROTO else 'keyhole.png')
im.save(out, optimize=True)
print("saved", out, im.size, "E615=%.3f" % E615)
