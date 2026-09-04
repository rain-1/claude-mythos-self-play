"""render_cloud.py — hero: the value cloud of Z(sigma+it) with the ladder of rims (possible worlds)
and the origin: where the actual line meets zero.

usage: python3 render_cloud.py SIZE SIGMA NSAMP OUT [rims.json]
"""
import sys, json, time, os
import numpy as np
from math import log, pi
from scipy.ndimage import gaussian_filter, zoom
from pastel import *
from cloud import sample_cloud
from zeta_g import gseq

S = int(sys.argv[1]); SIG = float(sys.argv[2]); NS = int(float(sys.argv[3])); OUT = sys.argv[4]
RIMS = sys.argv[5] if len(sys.argv) > 5 else 'rims_v2.json'
SSTAR = 1.0086
if os.path.exists('frontier2_N200.json'):
    SSTAR = round(json.load(open('frontier2_N200.json'))['res']['sigma_star'], 4)
SS = 2
W = H = S * SS
rs = S / 1024.0

# value-plane window (square), origin left of centre, room for caption below
X0, X1 = -0.72, 2.58
Y0, Y1 = -1.82, 1.48
def to_px(z):
    return ((np.real(z) - X0) / (X1 - X0) * W, (Y1 - np.imag(z)) / (Y1 - Y0) * H)

t0 = time.time()
HRES = W // 2                        # histogram at half res, bilinear zoom (grain control)
counts, C = sample_cloud(SIG, NS, 2.0e6, HRES, X0, X1, Y0, Y1, nterms=110, seed=1)
print('sampled', NS, 'in', round(time.time() - t0), 's; max count', counts.max())
# histogram rows are y-index from Y0 upward; image rows go downward -> flip
counts = counts[::-1]; C = C[::-1]

# density: soft log of counts, normalised by a reference count (the median of the occupied cells)
occ = counts[counts > 0]
ref = np.percentile(occ, 50)
dlog = np.log1p(counts / ref) / np.log1p(occ.max() / ref)
dpow = np.clip(counts / np.percentile(occ, 99.5), 0, 1) ** 0.55
d = 0.55 * dlog + 0.45 * dpow
coh = np.abs(C) / np.maximum(counts, 1)
hue = np.angle(C) / (2 * pi)             # in (-0.5, 0.5]
d = zoom(d.astype(np.float32), 2, order=1)[:H, :W]
coh = zoom(coh.astype(np.float32), 2, order=1)[:H, :W]
# hue must be zoomed as a vector
hx = zoom(np.cos(2 * pi * hue).astype(np.float32), 2, order=1)[:H, :W]
hy = zoom(np.sin(2 * pi * hue).astype(np.float32), 2, order=1)[:H, :W]
hue = np.arctan2(hy, hx) / (2 * pi)
d = gaussian_filter(d, 0.7 * rs)
del counts, C

sheet = Sheet(W, H, seed=11)

# --- pigment washes: 10-pigment cycle by the phase of 2^{-it}; incoherent cells go pale/neutral
AMP = 1.85
i0, i1, tt = hue_to_pigments(hue + 0.05)
sat = 0.30 + 0.70 * np.clip((coh - 0.15) / 0.6, 0, 1)
for k, name in enumerate(CYCLE):
    wk = np.where(i0 == k, 1 - tt, 0) + np.where(i1 == k, tt, 0)
    dens = AMP * d * sat * wk
    if dens.max() > 1e-4:
        sheet.wash(dens, name, granulate=0.25, seed=20 + k)
# the incoherent core: a pale paper-blue/sepia veil
sheet.wash(AMP * 0.55 * d * (1 - sat), 'paperblue', granulate=0.2, seed=31)
sheet.wash(AMP * 0.10 * d, 'ink', seed=32)          # a whisper of ink gives the cloud a body
print('washes done', round(time.time() - t0), 's')

# --- rims: outer boundaries of the value sets for a ladder of sigma (possible worlds)
if os.path.exists(RIMS):
    R = json.load(open(RIMS))
    sigs = sorted(float(k) for k in R)
    sigs = [sg for sg in sigs if sg >= SIG - 1e-6 and sg <= 1.5 + 1e-9]
    nl = len(sigs)
    for li, sg in enumerate(sigs):
        key = [k for k in R if abs(float(k) - sg) < 1e-9][0]
        pts = np.array(R[key]); z = pts[:, 0] + 1j * pts[:, 1]
        # circular smoothing (3-tap, several passes) then close
        for _ in range(6):
            z = (np.roll(z, 1) + 2 * z + np.roll(z, -1)) / 4
        z = np.concatenate([z, z[:1]])
        px, py = to_px(z)
        frontier = abs(sg - SSTAR) < 1e-6
        own = abs(sg - SIG) < 1e-6
        wdt = (2.8 if frontier else 1.2) * rs * SS / 2
        dens = polyline_density(W, H, list(zip(px, py)), wdt, weight=1.0, sigma=0.5 * rs)
        if frontier:
            sheet.wash(dens * 1.7, 'coral')
            sheet.wash(dens * 0.45, 'ink')
        else:
            sheet.wash(dens * (0.7 if own else 0.5), 'ink')
        # label: fan the labels along the right side by direction
        phi = np.deg2rad(-34 + 68 * li / max(nl - 1, 1))
        j = int(np.argmin(np.abs(np.angle(z[:-1] - 1) - phi)))
        lx, ly = to_px(z[j])
        lab = f'σ = {sg:.4g}' if not frontier else f'σ* = {sg:.4f}'
        txt = text_density(W, H, [(lab, lx + 9 * rs, ly, int(14 * rs), 'italic', 'lm')])
        sheet.wash(txt * (1.0 if frontier else 0.7), 'coral' if frontier else 'ink')

# --- the actual path: t -> Z(SIG + it) from t = 0 (real, rightmost) to just past the first zero on this line
ZEROS = [l.split() for l in open('zeros_A.txt')] if os.path.exists('zeros_A.txt') else []
ZEROS = [(float(a), float(b)) for a, b in ZEROS]
online = [z for z in ZEROS if abs(z[0] - SIG) < 2e-4]
tz = min((z[1] for z in online), default=None)
if SIG == 0.9054 or abs(SIG - 0.9054210547737378) < 1e-3:
    SIGX = 0.9054210547737378; tz = 13.648710968998584
else:
    SIGX = SIG
T_END = (tz + 1.2) if tz is not None else 30.0
g110 = gseq(110); lg110 = np.array([log(x) for x in g110])
tt_ = np.linspace(0, T_END, int(T_END * 2500))
Zt = np.exp(-np.multiply.outer(SIGX + 1j * tt_, lg110)).sum(axis=1)
px, py = to_px(Zt)
# ink weight grows toward the arrival (the thread is the story: from 2.4 at t=0 to 0 at the zero)
from PIL import Image, ImageDraw
_im = Image.new('F', (W, H), 0.0); _dr = ImageDraw.Draw(_im)
nseg = 60
for i in range(nseg):
    a, b = int(i * len(tt_) / nseg), int((i + 1) * len(tt_) / nseg) + 1
    wgt = 0.35 + 0.65 * (i / (nseg - 1)) ** 1.5
    _dr.line([(float(x), float(y)) for x, y in zip(px[a:b], py[a:b])], fill=float(wgt), width=int(max(1, round(2.0 * rs * SS / 2))), joint='curve')
thread = gaussian_filter(np.asarray(_im, np.float32), 0.5 * rs)
del _im, _dr
sheet.wash(thread * 1.05, 'ink')
sheet.wash(thread * 0.6, 'coral')
if tz is not None:
    # a small coral star where the sum came home
    zx, zy = to_px(0j)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    star = np.exp(-(np.hypot(xx - zx, yy - zy) / (5.5 * rs)) ** 2)
    sheet.wash(star * 1.8, 'coral')
    lab = text_density(W, H, [(f'Z({SIGX:.4f} + {tz:.3f}i) = 0', zx + 30 * rs, zy + 34 * rs, int(15 * rs), 'italic', 'lm')])
    sheet.wash(lab * 0.9, 'ink')
    sheet.wash(lab * 0.5, 'coral')
    del xx, yy
# t = 0 mark
lab = text_density(W, H, [('t = 0', px[0] + 12 * rs, py[0], int(15 * rs), 'italic', 'lm')])
sheet.wash(lab * 0.8, 'ink')

# --- the origin and the point 1
ox, oy = to_px(0j); ux, uy = to_px(1 + 0j)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
rr = np.hypot(xx - ox, yy - oy)
ring = ink_from_distance(np.abs(rr - 9 * rs), 1.1 * rs)
cross = np.maximum(ink_from_distance(np.abs(xx - ox), 0.9 * rs) * (np.abs(yy - oy) < 22 * rs),
                   ink_from_distance(np.abs(yy - oy), 0.9 * rs) * (np.abs(xx - ox) < 22 * rs)) * (rr > 11 * rs)
sheet.lighten(np.clip(1 - rr / (7 * rs), 0, 1), 0.9)           # paper-white star at 0
sheet.wash(np.maximum(ring, cross) * 0.9, 'ink')
dot = ink_from_distance(np.hypot(xx - ux, yy - uy), 3.0 * rs)
sheet.wash(dot * 0.9, 'ink')
lab = text_density(W, H, [('0', ox - 26 * rs, oy - 26 * rs, int(20 * rs), 'italic', 'mm'),
                          ('1', ux + 4 * rs, uy + 22 * rs, int(20 * rs), 'italic', 'mm')])
sheet.wash(lab * 0.85, 'ink')
del xx, yy, rr

# --- caption
sheet.caption_strip(0.905, 0.985, f=0.62)
title = 'The Sum That Came Home'
sub = (f'values of Z(σ+it) = Σ g(n)^(−σ−it) on the line σ = {SIG:.4g}, g = binary partitions: the cloud is where the '
       f'actual line goes; the rims are how far any possible world reaches; the coral rim touches zero at σ* ≈ {SSTAR}')
items = [(title, W * 0.5, H * 0.928, int(40 * rs), 'serif_bold', 'mm')]
# wrap the subtitle
words = sub.split(); lines = []; cur = ''
for w_ in words:
    trial = (cur + ' ' + w_).strip()
    if text_width(trial, int(16 * rs), 'italic') > W * 0.86:
        lines.append(cur); cur = w_
    else:
        cur = trial
lines.append(cur)
for i, ln in enumerate(lines):
    items.append((ln, W * 0.5, H * (0.955 + 0.019 * i), int(16 * rs), 'italic', 'mm'))
sheet.wash(text_density(W, H, items) * 0.95, 'ink')

img = sheet.develop(dmax=2.4)
finish(img, (S, S), OUT)
print('total', round(time.time() - t0), 's')
