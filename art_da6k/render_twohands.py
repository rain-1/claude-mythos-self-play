"""render_twohands.py — the circle covered by two hands: 2^k arcs per shell k, hierarchy as palette.

usage: python3 render_twohands.py SIZE L K OUT
shell k (k = 1..K) holds the images of all 2^k words, one hairline arc each, sorted by word
(first letter = most significant).  f-words warm, g-words cool; second letter picks the pigment
within the family; depth lightens.  The word g^k (its arc never shrinks: g maps [1/2, 1/2+1/L]
onto itself) is drawn in coral — the accent is the theorem's failure.
"""
import sys, json, time
import numpy as np
from math import pi
from scipy.ndimage import gaussian_filter
from pastel import *
from twohands import all_words, fold, stats

S = int(sys.argv[1]); L = int(sys.argv[2]); K = int(sys.argv[3]); OUT = sys.argv[4]
SS = 2; W = H = S * SS; rs = S / 1024.0
t0 = time.time()
levels = all_words(L, K, exact=False)
st = stats({k: v for k, v in levels.items()})
print('max diam by depth', [round(st[k][0], 4) for k in range(1, K + 1)])

cx, cy = W * 0.5, H * 0.47
# shells: inner radius R1, each shell k thickness = 2^k * s_k, gap between shells
s_k = [0] + [max(0.9 * SS * rs, 4.2 * SS * rs * 0.74 ** (k - 1)) for k in range(1, K + 1)]
gap = 9 * SS * rs
R = [0.0, 0.15 * W]
for k in range(1, K + 1):
    R.append(R[-1] + (2 ** (k - 1)) * s_k[k] + gap)
Rmax = R[-1]
print('outer radius', Rmax / W, 'of W')
scale = min(1.0, 0.455 * W / Rmax)      # fit in the canvas
R = [r * scale for r in R]; s_k = [s * scale for s in s_k]

yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
rr = np.hypot(xx - cx, yy - cy)
ang = (np.arctan2(-(yy - cy), xx - cx) / (2 * pi)) % 1.0      # counter-clockwise, 0 at east
sheet = Sheet(W, H, seed=5)

fam = {0: ['apricot', 'lemon', 'blush', 'pistachio'], 1: ['cornflower', 'aqua', 'lavender', 'mint']}
layers = {name: np.zeros((H, W), np.float32) for name in PIG}
ink = np.zeros((H, W), np.float32)
for k in range(1, K + 1):
    arcs = np.array(levels[k], dtype=np.float64)          # (2^k, 2) lifts, word index = row
    lo = arcs[:, 0] % 1.0; ln = arcs[:, 1] - arcs[:, 0]
    r0, r1 = R[k], R[k] + (2 ** (k - 1)) * s_k[k]
    band = (rr >= r0 - s_k[k]) & (rr < r1 + s_k[k])
    ys, xs = np.nonzero(band)
    rb = rr[ys, xs]; ab = ang[ys, xs]
    # sub-band = the suffix (word without its first letter); the two hands f·w and g·w share a sub-band
    # (their arcs lie in opposite halves), so every ring is complete: warm on one side, cool on the other
    nsub = 2 ** (k - 1)
    jj = np.clip(np.floor((rb - r0) / s_k[k]).astype(np.int64), 0, nsub - 1)
    frac = (rb - r0) / s_k[k] - jj                         # position inside the sub-band
    j_f = jj; j_g = jj + nsub                              # word indices of f·suffix and g·suffix
    in_f = ((ab - lo[j_f]) % 1.0) <= ln[j_f]
    in_g = ((ab - lo[j_g]) % 1.0) <= ln[j_g]
    j = np.where(in_g & ~in_f, j_g, j_f)                   # (overlap of the two: f wins, only at the seams)
    inside = in_f | in_g
    # soft line profile centred in the sub-band, width ~0.62 of the spacing (min 0.9 px)
    wpx = max(0.78 * s_k[k], 1.0 * SS * rs / 2)
    prof = np.exp(-(((frac - 0.5) * s_k[k]) / wpx) ** 2)
    # soft angular ends
    dlo = ((ab - lo[j]) % 1.0) * 2 * pi * rb; dhi = (ln[j] - ((ab - lo[j]) % 1.0)) * 2 * pi * rb
    endsoft = np.clip(dlo / (0.8 * SS * rs), 0, 1) * np.clip(dhi / (0.8 * SS * rs), 0, 1)
    val = prof * inside * endsoft
    first = j >> (k - 1); second = (j >> max(k - 2, 0)) & 1 if k >= 2 else np.zeros_like(j)
    third = (j >> max(k - 3, 0)) & 1 if k >= 3 else np.zeros_like(j)
    depth_amp = 1.0 if k <= 3 else 0.9 * 0.96 ** (k - 3)
    stuck = (j == 2 ** k - 1) | (j == 2 ** (k - 1) - 1)
    for f_ in (0, 1):
        for s_ in (0, 1):
            for t_ in (0, 1):
                sel = (first == f_) & (second == s_) & (third == t_) & ~stuck
                if not sel.any():
                    continue
                name = fam[f_][2 * s_ + t_]
                np.add.at(layers[name], (ys[sel], xs[sel]), (val[sel] * depth_amp).astype(np.float32))
    # the arcs that never shrink (g^k and f g^(k-1)): drawn separately, wide, coral + ink, on the outer sub-band
    r_s = r0 + (nsub - 0.5) * s_k[k]
    wS = 1.5 * SS * rs
    sel_r = np.abs(rr - r_s) < 3.5 * wS
    yr, xr = np.nonzero(sel_r)
    prof2 = np.exp(-((rr[yr, xr] - r_s) / wS) ** 2)
    for widx in (2 ** k - 1, 2 ** (k - 1) - 1):
        a_ = ang[yr, xr]
        d0 = (a_ - lo[widx]) % 1.0
        ins = d0 <= ln[widx]
        soft = np.clip(d0 * 2 * pi * r_s / (1.5 * SS * rs), 0, 1) * np.clip((ln[widx] - d0) * 2 * pi * r_s / (1.5 * SS * rs), 0, 1)
        v2 = (prof2 * ins * soft).astype(np.float32)
        np.add.at(layers['coral'], (yr, xr), v2 * 1.5)
        np.add.at(ink, (yr, xr), v2 * 0.3)
    if k <= 4:
        np.add.at(ink, (ys, xs), (val * 0.22).astype(np.float32))
    print(f'shell {k}: {2**k} arcs in {nsub} sub-bands, spacing {s_k[k]:.2f}px, radius {r0/W:.3f}-{r1/W:.3f}  ({time.time()-t0:.0f}s)')

AMP = 2.6
for name, lay in layers.items():
    if lay.max() > 0:
        sheet.wash(np.clip(lay, 0, 2.2) * AMP, name, granulate=0.18, seed=hash(name) % 1000)
sheet.wash(ink, 'ink')

# --- centre: the graph of the fold f (the hand) in a small square of paper
xs_, ys_ = fold(L, exact=False)
side = R[1] * 1.15
gx0, gy0 = cx - side / 2, cy + side / 2
segs = []
ptsx = np.linspace(0, 1, 400)
ptsy = np.interp(ptsx, xs_, ys_)
poly = [(gx0 + px * side, gy0 - py * side) for px, py in zip(ptsx, ptsy)]
dens = polyline_density(W, H, poly, 2.2 * rs * SS / 2, sigma=0.5 * rs)
frame = np.zeros((H, W), np.float32)
fb = polyline_density(W, H, [(gx0, gy0), (gx0 + side, gy0), (gx0 + side, gy0 - side), (gx0, gy0 - side)], 1.0 * rs * SS / 2, closed=True, sigma=0.4 * rs)
sheet.wash(fb * 0.45, 'ink')
sheet.wash(dens * 1.0, 'ink')
# the diagonal y=x (fixed points) and g = f + 1/2 as a pale cool copy
diag = polyline_density(W, H, [(gx0, gy0), (gx0 + side, gy0 - side)], 0.8 * rs * SS / 2, sigma=0.4 * rs)
sheet.wash(diag * 0.35, 'ink')
polyg = [(gx0 + px * side, gy0 - ((py + 0.5) % 1.0) * side) for px, py in zip(ptsx, ptsy)]
# draw g in two pieces (it wraps)
brk = np.where(np.abs(np.diff([(py + 0.5) % 1.0 for py in ptsy])) > 0.5)[0]
pieces = np.split(np.arange(len(ptsx)), brk + 1)
for pc in pieces:
    if len(pc) > 1:
        sheet.wash(polyline_density(W, H, [polyg[i] for i in pc], 2.2 * rs * SS / 2, sigma=0.5 * rs) * 0.9, 'cornflower')
lab = text_density(W, H, [('f', gx0 + side * 0.30, gy0 - side * 0.93, int(15 * rs * 2), 'italic', 'mm'),
                          ('g', gx0 + side * 0.78, gy0 - side * 0.93, int(15 * rs * 2), 'italic', 'mm')])
sheet.wash(lab, 'ink')

# --- caption
sheet.caption_strip(0.90, 0.985, f=0.62)
first_q = next((k for k in range(1, K + 1) if st[k][0] < 0.25), None)
title = 'Two Hands Cover the Clock'
sub = (f'f folds the whole circle onto one half, g = f + ½ onto the other; every point lies in one hand or the other. '
       f'Ring k holds the images of all 2^k compositions (L = {L}): by ring {first_q} every arc is shorter than a quarter turn — '
       f'but the coral arc, g(g(…g(T))), is mapped onto itself and stays exactly 1/{L} forever — so the fixed-pair question stays open.')
items = [(title, W * 0.5, H * 0.924, int(38 * rs * 2), 'serif_bold', 'mm')]
words = sub.split(); lines = []; cur = ''
for w_ in words:
    trial = (cur + ' ' + w_).strip()
    if text_width(trial, int(15 * rs * 2), 'italic') > W * 0.84:
        lines.append(cur); cur = w_
    else:
        cur = trial
lines.append(cur)
for i, ln in enumerate(lines):
    items.append((ln, W * 0.5, H * (0.952 + 0.017 * i), int(15 * rs * 2), 'italic', 'mm'))
sheet.wash(text_density(W, H, items) * 0.95, 'ink')
img = sheet.develop(dmax=2.4)
finish(img, (S, S), OUT)
json.dump(dict(L=L, K=K, max_diam=[st[k][0] for k in range(1, K + 1)], first_depth_below_quarter=first_q),
          open(OUT.replace('.png', '_cert.json'), 'w'), indent=1)
print('total', round(time.time() - t0), 's')
