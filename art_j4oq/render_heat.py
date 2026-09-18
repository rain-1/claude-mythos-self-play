"""render_heat.py — BARELY TRUE. The de Bruijn–Newman heat flow of the Riemann zeros.
x: the flow time lambda (backward heat on the left, the present Riemann line at lambda = 0, forward heat right);
y: the height t on the critical line. Every real zero is a thread; where two threads meet (lambda < 0) the pair
leaves the real line: coral bud, ghost thread beyond (real part, faded by the imaginary part).
Pigment by crowding: nearest-neighbour spacing over the local mean spacing (warm = crowded, cool = lonely)."""
import numpy as np, sys, os, json, time
from scipy.ndimage import gaussian_filter
from PIL import Image, ImageDraw
from pastel import *

FINAL_W = int(sys.argv[1]) if len(sys.argv) > 1 else 640
FINAL_H = int(FINAL_W * 1.6)
SS = 2
W, H = FINAL_W * SS, FINAL_H * SS
rs = FINAL_W / 1024 * SS
out = sys.argv[2] if len(sys.argv) > 2 else f'cache/heat_{FINAL_W}.png'
T = int(os.environ.get('T', '260'))
dat = np.load(f'cache/heat_T{T}.npz', allow_pickle=True)
lams = dat['lams']; rows = dat['rows']
ctr = json.load(open(f'cache/heat_T{T}_complex.json'))
LMIN, LMAX = lams.min(), lams.max()
TMAX = float(os.environ.get('TMAX', str(T)))
# frame
mx, my0, my1 = 0.09 * W, 0.06 * H, 0.885 * H
def X(l): return mx + (l - LMIN) / (LMAX - LMIN) * (W - 2 * mx)
def Y(t): return my1 - t / TMAX * (my1 - my0)

# --- build real-zero tracks by nearest matching between consecutive lambda rows
tracks = []          # list of lists of (lam, t)
open_tr = {}         # index in current row -> track
prev = None
for li, lam in enumerate(lams):
    r = np.asarray(rows[li], float)
    new_open = {}
    if prev is None:
        for j, t in enumerate(r):
            tr = [(lam, t)]; tracks.append(tr); new_open[j] = tr
    else:
        used = set()
        for j, t in enumerate(r):
            k = int(np.argmin(np.abs(prev - t))) if len(prev) else -1
            if k >= 0 and abs(prev[k] - t) < 0.35 and k in open_tr and k not in used:
                tr = open_tr[k]; tr.append((lam, t)); new_open[j] = tr; used.add(k)
            else:
                tr = [(lam, t)]; tracks.append(tr); new_open[j] = tr
    open_tr = new_open; prev = r
print('real tracks', len(tracks), 'complex', len(ctr))

sh = Sheet(W, H, seed=5)
# local mean spacing at height t (Riemann–von Mangoldt): 2 pi / log(t / 2 pi)
def mean_sp(t): return 2 * np.pi / np.log(np.maximum(t, 8.0) / (2 * np.pi))

# pigment field per track point: crowding = nn spacing / mean spacing
# draw threads as short segments with pigment mix; accumulate into a few pigment channels
chan = {k: np.zeros((H, W), np.float32) for k in ['warm0', 'warm1', 'cool0', 'cool1']}
def add_seg(ch, x0, y0, x1, y1, w, wd):
    pass
segs = {k: [] for k in chan}
for li, lam in enumerate(lams):
    r = np.asarray(rows[li], float)
    if len(r) < 2: continue
    nn = np.minimum(np.abs(np.diff(r, prepend=r[0] - 99)), np.abs(np.diff(r, append=r[-1] + 99)))
    q = nn / mean_sp(r)                      # ~1 typical, <0.5 crowded, >1.5 lonely
    if li + 1 >= len(lams): break
    r2 = np.asarray(rows[li + 1], float)
    for j, t in enumerate(r):
        if t > TMAX: continue
        k = int(np.argmin(np.abs(r2 - t))) if len(r2) else -1
        if k < 0 or abs(r2[k] - t) > 0.35: continue
        qq = q[j]
        # warm family for crowded (q<1): apricot -> coral-ish blush; cool for lonely: aqua -> cornflower
        if qq < 1.0:
            a = np.clip((1.0 - qq) / 0.6, 0, 1)
            segs['warm0'].append((X(lam), Y(t), X(lams[li + 1]), Y(r2[k]), 1 - a)); segs['warm1'].append((X(lam), Y(t), X(lams[li + 1]), Y(r2[k]), a))
        else:
            a = np.clip((qq - 1.0) / 0.8, 0, 1)
            segs['cool0'].append((X(lam), Y(t), X(lams[li + 1]), Y(r2[k]), 1 - a)); segs['cool1'].append((X(lam), Y(t), X(lams[li + 1]), Y(r2[k]), a))
LW = float(os.environ.get('LW', '2.2')) * rs
for k in chan:
    if not segs[k]: continue
    arr = np.array(segs[k]); m = arr[:, 4] > 0.01
    chan[k] = draw_lines_density(W, H, arr[m, :4], LW, weights=arr[m, 4], sigma=0.6 * rs)
tint = dict(warm0='lemon', warm1='apricot', cool0='mint', cool1='cornflower')
tint = dict(warm0=mix_tint('apricot', 'blush', 0.3), warm1='coral', cool0=mix_tint('aqua', 'mint', 0.3), cool1='cornflower')
# never coral for a family: warm1 = orchid-blush
tint['warm1'] = mix_tint('blush', 'orchid', 0.5)
STR = float(os.environ.get('STR', '0.9'))
for k in chan:
    sh.wash(STR * np.clip(chan[k], 0, 1.4), tint[k], granulate=0.1, seed=hash(k) % 100)

# complex ghosts: real part as a thread fading with imaginary part; coral bud at the collision
buds = []
gs = []
for tr in ctr:
    lam = np.array(tr['lam']); re = np.array(tr['re']); im = np.array(tr['im'])
    if re[0] > TMAX: continue
    buds.append((X(lam[0]), Y(re[0]), im[0]))
    for i in range(len(lam) - 1):
        f = np.exp(-abs(im[i]) / 1.2)
        gs.append((X(lam[i]), Y(re[i]), X(lam[i + 1]), Y(re[i + 1]), f))
if gs:
    arr = np.array(gs)
    g = draw_lines_density(W, H, arr[:, :4], 1.4 * rs, weights=arr[:, 4], sigma=0.6 * rs)
    sh.wash(0.55 * np.clip(g, 0, 1), 'ink')
    # the imaginary part as a lavender halo widening with |im|
    hs = [(X(l), Y(r_), 0.8 * rs + 6.0 * rs * min(abs(i_), 3.0), 0.25) for tr in ctr for l, r_, i_ in zip(tr['lam'][::3], tr['re'][::3], tr['im'][::3]) if r_ <= TMAX]
    if hs:
        hx, hy, hr, hw = zip(*hs)
        sh.wash(np.clip(discs_density(W, H, hx, hy, hr, hw, sigma=1.0 * rs), 0, 1) * 0.5, 'lavender')
if buds:
    bx, by, _ = zip(*buds)
    sh.wash(discs_density(W, H, bx, by, [4.5 * rs] * len(bx), [1.0] * len(bx), sigma=1.0 * rs) * 1.1, 'coral')

# the present: lambda = 0, an ink hairline; the Polymath band [0, 0.2] a lemon wash
yy, xx = np.mgrid[0:H, 0:W]
band = ((xx >= X(0)) & (xx <= X(0.2)) & (yy >= my0) & (yy <= my1)).astype(np.float32)
sh.wash(0.16 * gaussian_filter(band, 2 * rs), 'lemon')
line = np.exp(-((xx - X(0)) / (0.9 * rs)) ** 2) * ((yy >= my0 - 6 * rs) & (yy <= my1 + 6 * rs))
sh.wash(0.75 * line, 'ink')
# axes ticks
items = []
for l in [-1, -0.5, 0, 0.5, 1, 2, 3]:
    if LMIN <= l <= LMAX:
        items.append((f'{l:g}', X(l), my1 + 14 * rs, 10 * rs, 'serif', 'mt'))
for t in range(0, int(TMAX) + 1, 50):
    items.append((f'{t}', mx - 8 * rs, Y(t), 10 * rs, 'serif', 'rm'))
items.append(('λ', X(LMAX) + 10 * rs, my1 + 14 * rs, 11 * rs, 'italic', 'lt'))
items.append(('t', mx - 8 * rs, my0 - 12 * rs, 11 * rs, 'italic', 'rm'))
sh.wash(text_density(W, H, items) * 0.8, 'ink')
sh.caption_strip(0.905, 0.985, 0.62)
items = [('Barely True', W / 2, 0.925 * H, 30 * rs, 'serif_bold', 'mm')]
sub = 'the zeros of the Riemann Ξ under the heat flow of de Bruijn and Newman: forward (right) they stay real and space out; run backward (left) they meet in pairs and leave the line. Newman: if the zeros are all real today, it is only barely so — Λ ≥ 0 (Rodgers–Tao 2018), Λ ≤ 0.2 (Polymath, the lemon band).'
lines = wrap(sub, 12.5 * rs, 'italic', 0.86 * W)
for i, ln in enumerate(lines):
    items.append((ln, W / 2, 0.95 * H + i * 15 * rs, 12.5 * rs, 'italic', 'mm'))
sh.wash(text_density(W, H, items) * 0.95, 'ink')
finish(sh.develop(), (FINAL_W, FINAL_H), out)
