"""render_heat2.py — BARELY TRUE (field version).
The de Bruijn–Newman heat flow H_lam(t) drawn as a FIELD over the (lambda, t) plane:
tone = |H| over its local envelope (paper at the zeros), warm where H > 0, cool where H < 0 (families drifting
with height), ink hairlines on the real zeros, coral buds where a pair leaves the line (lambda < 0), and beyond
each bud the field keeps a pale dimple: the zero that is no longer there. Lemon band: 0 <= Lambda <= 0.2."""
import numpy as np, sys, os, json, time
from scipy.ndimage import gaussian_filter, maximum_filter1d, uniform_filter1d
from PIL import Image
from pastel import *
from heat import H

FINAL_W = int(sys.argv[1]) if len(sys.argv) > 1 else 640
FINAL_H = int(FINAL_W * 1.6)
SS = 2
W, Hh = FINAL_W * SS, FINAL_H * SS
rs = FINAL_W / 1024 * SS
out = sys.argv[2] if len(sys.argv) > 2 else f'cache/heat2_{FINAL_W}.png'
T = int(os.environ.get('T', '260'))
LMIN = float(os.environ.get('LMIN', '-1.3')); LMAX = float(os.environ.get('LMAX', '3.0'))
TMAX = float(os.environ.get('TMAX', str(T)))
ctr = json.load(open(f'cache/heat_T{T}_complex.json'))
dat = np.load(f'cache/heat_T{T}.npz', allow_pickle=True)
lams_all = dat['lams']; rows = dat['rows']
mx, my0, my1 = 0.085 * W, 0.055 * Hh, 0.885 * Hh
def X(l): return mx + (l - LMIN) / (LMAX - LMIN) * (W - 2 * mx)
def Y(t): return my1 - t / TMAX * (my1 - my0)
def Linv(x): return LMIN + (x - mx) / (W - 2 * mx) * (LMAX - LMIN)
def Tinv(y): return (my1 - y) / (my1 - my0) * TMAX

t0 = time.time()
# --- the field: one column per pixel column inside the frame; rows = t per pixel row
cols = np.arange(int(mx), int(W - mx) + 1)
rws = np.arange(int(my0), int(my1) + 1)
tt = Tinv(rws + 0.5)
F = np.zeros((len(rws), len(cols)), np.float64)
scale = np.exp(np.pi * tt / 4)          # undo the e^{-pi t/4} decay so float storage never underflows
cache_fn = f'cache/heatfield_{W}x{Hh}_{T}_{LMIN}_{LMAX}.npy'
if os.path.exists(cache_fn):
    F = np.load(cache_fn)
else:
    for ci, c in enumerate(cols):
        lam = Linv(c + 0.5)
        F[:, ci] = np.real(H(lam, tt)) * scale
        if ci % 200 == 0: print('col', ci, len(cols), time.time() - t0, flush=True)
    np.save(cache_fn, F)
print('field', F.shape, time.time() - t0)
# local envelope along t: running max of |F| over a window of ~1.5 mean spacings (in pixels)
win = int(np.ceil(1.5 * 4.0 / (TMAX / len(rws))))
env = maximum_filter1d(np.abs(F), size=win, axis=0)
env = uniform_filter1d(env, size=win, axis=0) + 1e-300
R = np.abs(F) / np.maximum(env, 1e-300)
R = np.clip(R, 0, 1)
GAM = float(os.environ.get('GAM', '0.8'))
tone = R ** GAM
sgn = np.sign(F)
# families drift with height t: warm lemon->apricot->blush->orchid, cool mint->aqua->cornflower->lavender
tfrac = (tt / TMAX)[:, None] * np.ones_like(F)
def drift(names, f):
    n = len(names) - 1
    i0 = np.clip(np.floor(f * n).astype(int), 0, n - 1); a = f * n - i0
    A = np.zeros(F.shape + (3,), np.float32)
    for k in range(n):
        m = (i0 == k)
        if not m.any(): continue
        mixA = absorb(PIG[names[k]]); mixB = absorb(PIG[names[k + 1]])
        A[m] = (1 - a[m])[:, None] * mixA + a[m][:, None] * mixB
    return A
WARM = ['lemon', 'apricot', 'blush', 'orchid']
COOL = ['mint', 'aqua', 'cornflower', 'lavender']
STR = float(os.environ.get('STR', '0.95'))
sh = Sheet(W, Hh, seed=5)
Aw = drift(WARM, tfrac); Ac = drift(COOL, tfrac)
dens = (STR * tone).astype(np.float32)
g = noise(len(rws), len(cols), 1.6, 9) * 0.10
dens = dens * (1 + g)
block = np.where((sgn > 0)[..., None], Aw, Ac) * dens[..., None]
sh.A[rws[0]:rws[-1] + 1, cols[0]:cols[-1] + 1, :] += block
del block, Aw, Ac
print('washed', time.time() - t0)

# ink hairlines on the real zeros (tracks from the rows)
segs = []
for li in range(len(lams_all) - 1):
    lam, lam2 = lams_all[li], lams_all[li + 1]
    if lam < LMIN or lam2 > LMAX: continue
    r = np.asarray(rows[li], float); r2 = np.asarray(rows[li + 1], float)
    if len(r2) == 0: continue
    for t in r:
        if t > TMAX: continue
        k = int(np.argmin(np.abs(r2 - t)))
        if abs(r2[k] - t) < 0.35:
            segs.append((X(lam), Y(t), X(lam2), Y(r2[k])))
INK = float(os.environ.get('INK', '0.5'))
if segs:
    ink = draw_lines_density(W, Hh, np.array(segs), 1.1 * rs, sigma=0.5 * rs)
    sh.wash(INK * np.clip(ink, 0, 1), 'ink')
# coral buds at the collisions + a faint ink ghost of the real part
buds, gs = [], []
for tr in ctr:
    lam = np.array(tr['lam']); re = np.array(tr['re']); im = np.array(tr['im'])
    if re[0] > TMAX or lam[0] < LMIN: continue
    buds.append((X(lam[0]), Y(re[0])))
    for i in range(len(lam) - 1):
        if lam[i + 1] < LMIN: break
        gs.append((X(lam[i]), Y(re[i]), X(lam[i + 1]), Y(re[i + 1]), float(np.exp(-abs(im[i]) / 2.0))))
if gs:
    arr = np.array(gs)
    sh.wash(0.28 * np.clip(draw_lines_density(W, Hh, arr[:, :4], 1.0 * rs, weights=arr[:, 4], sigma=0.5 * rs), 0, 1), 'ink')
if buds:
    bx, by = zip(*buds)
    sh.wash(discs_density(W, Hh, bx, by, [4.2 * rs] * len(bx), [1.0] * len(bx), sigma=1.0 * rs) * 1.1, 'coral')
    sh.wash(discs_density(W, Hh, bx, by, [9.0 * rs] * len(bx), [1.0] * len(bx), sigma=3.0 * rs) * 0.10, 'coral')
print('buds', len(buds))
# the present (lambda = 0) and the Polymath band
yy, xx = np.mgrid[0:Hh, 0:W]
band = ((xx >= X(0)) & (xx <= X(0.2)) & (yy >= my0) & (yy <= my1)).astype(np.float32)
sh.lighten(gaussian_filter(band, 1.5 * rs), 0.35)
sh.wash(0.22 * gaussian_filter(band, 1.5 * rs), 'lemon')
line = np.exp(-((xx - X(0)) / (1.0 * rs)) ** 2) * ((yy >= my0 - 6 * rs) & (yy <= my1 + 6 * rs))
sh.wash(0.8 * line, 'ink')
frame = ((np.abs(xx - mx) < 0.7 * rs) | (np.abs(xx - (W - mx)) < 0.7 * rs)) & (yy >= my0) & (yy <= my1)
frame |= ((np.abs(yy - my0) < 0.7 * rs) | (np.abs(yy - my1) < 0.7 * rs)) & (xx >= mx) & (xx <= W - mx)
sh.wash(0.25 * frame, 'ink')
items = []
for l in [-1, -0.5, 0, 0.5, 1, 1.5, 2, 2.5, 3]:
    if LMIN <= l <= LMAX:
        items.append((f'{l:g}', X(l), my1 + 8 * rs, 10 * rs, 'serif', 'mt'))
for t in range(0, int(TMAX) + 1, 50):
    items.append((f'{t}', mx - 8 * rs, Y(t), 10 * rs, 'serif', 'rm'))
items.append(('λ', X(LMAX) + 8 * rs, my1 + 8 * rs, 12 * rs, 'italic', 'lt'))
items.append(('t', mx - 8 * rs, my0 - 14 * rs, 12 * rs, 'italic', 'rm'))
items.append(('the past that never was', X(LMIN) + 10 * rs, my0 + 10 * rs, 11 * rs, 'italic', 'lt'))
items.append(('the present: every zero on the line', X(0) + 6 * rs, my0 + 10 * rs, 11 * rs, 'italic', 'lt'))
sh.wash(text_density(W, Hh, items) * 0.8, 'ink')
sh.caption_strip(0.905, 0.985, 0.62)
items = [('Barely True', W / 2, 0.925 * Hh, 30 * rs, 'serif_bold', 'mm')]
sub = 'the Riemann Ξ under the heat flow of de Bruijn and Newman, its zeros as paper threads between warm (Ξ > 0) and cool (Ξ < 0). Forward (right) the zeros stay real and even out; backward (left) they meet in pairs, leave the line (coral) and haunt the field as dimples. Newman: if they are all real today it is only barely so — Λ ≥ 0 (Rodgers–Tao 2018), Λ ≤ 0.2 (Polymath 15, the lemon band).'
lines = wrap(sub, 12.5 * rs, 'italic', 0.86 * W)
for i, ln in enumerate(lines):
    items.append((ln, W / 2, 0.949 * Hh + i * 15 * rs, 12.5 * rs, 'italic', 'mm'))
sh.wash(text_density(W, Hh, items) * 0.95, 'ink')
finish(sh.develop(), (FINAL_W, FINAL_H), out)
print('done', time.time() - t0)
