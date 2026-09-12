"""render_keep.py — THE CHEAPEST WAY TO STAY (MO 511767): Brownian motion kept in [−1, 1] by the
L²-cheapest force u = ∂x log φ(T−t, x), φ = probability of staying, as a space–time river.

Tall sheet: x across, time UP from the bottom.  Three materials (the 09-04 register):
  pigment cloud = the law: thousands of kept paths sampled at equal time steps (dwell density),
                  tinted by the FORCE acting at that point (cornflower = free … apricot = pushed hard);
  ink threads   = a handful of actual paths, their ink weight following the force they feel;
  coral         = the walls, which the kept process never touches.
Certificate: mean cost of the sampled paths vs −log φ(T, 0); occupation vs cos²(πx/2) mid-horizon.

usage: python3 render_keep.py WIDTH HEIGHT ncloud nink T out_prefix [seed]
"""
import sys, json, time
import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image, ImageDraw
import pastel as P
from keep import Keeper1D

FW = int(sys.argv[1]); FH = int(sys.argv[2]); NC = int(sys.argv[3]); NI = int(sys.argv[4]); T = float(sys.argv[5]); OUT = sys.argv[6]
SEED = int(sys.argv[7]) if len(sys.argv) > 7 else 1
SS = 2
W, H = FW * SS, FH * SS
rs = FW / 1024.0 * SS
t0 = time.time()

D = Keeper1D(T)
theory = -np.log(D.survival(T))
print('table [%.0fs]' % (time.time() - t0), flush=True)

x_left, x_right = 0.14 * W, 0.86 * W
y_bot, y_top = 0.90 * H, 0.05 * H
def X(x): return x_left + (x + 1) / 2 * (x_right - x_left)
def Y(t): return y_bot + t / T * (y_top - y_bot)

sheet = P.Sheet(W, H, seed=SEED + 5)

# ---- cloud: many paths, equal-time samples, binned by the force they feel ----
dt = 5e-5
xs, tim, fs, cost, maxf = D.run(NC, dt, seed=SEED, record_every=10)
print('cloud paths', xs.shape, 'mean cost %.3f (theory %.3f)' % (cost.mean(), theory), '[%.0fs]' % (time.time() - t0), flush=True)
RAMP = ['cornflower', 'aqua', 'mint', 'pistachio', 'lemon', 'apricot']
PX = X(xs).astype(np.float32); PY = np.broadcast_to(Y(tim)[None, :], xs.shape).astype(np.float32)
ix = np.clip(PX.astype(np.int64), 0, W - 1); iy = np.clip(PY.astype(np.int64), 0, H - 1)
flat = (iy * W + ix).ravel()
del ix, iy, PX, PY
# continuous ramp position by force: f = log(1 + |u|/0.5) / log(1 + 30/0.5) in [0, 1]
fr = np.clip(np.log1p(np.abs(fs).ravel() / 0.5) / np.log1p(30 / 0.5), 0, 0.999) * (len(RAMP) - 1)
i0 = np.floor(fr).astype(int); tt = (fr - i0).astype(np.float32)
total = np.bincount(flat, minlength=H * W).astype(np.float32).reshape(H, W)
total = gaussian_filter(total, 0.9 * rs)
d0 = np.percentile(total[total > 0], 85)
knee = lambda d: (d / (d + 0.5 * d0)) * (1 + 0.5)     # soft knee, keeps the centre-to-edge gradient
for k, pig in enumerate(RAMP):
    w = np.where(i0 == k, 1 - tt, 0.0) + np.where(i0 == k - 1, tt, 0.0)
    if not (w > 0).any():
        continue
    d = np.bincount(flat, weights=w, minlength=H * W).astype(np.float32).reshape(H, W)
    d = gaussian_filter(d, 0.9 * rs)
    d = knee(total) * (d / np.maximum(total, 1e-6))       # share of this pigment × global knee
    sheet.wash(1.25 * d, pig, granulate=0.18, seed=30 + k)
    print('ramp', pig, '[%.0fs]' % (time.time() - t0), flush=True)
del flat, fr, i0, tt, total
# the force field itself, faint, where the cloud is too thin to carry it (beside the walls)
yy, xx = np.mgrid[:H, :W]
xn = (xx - x_left) / (x_right - x_left) * 2 - 1; tn = (yy - y_bot) / (y_top - y_bot) * T
inside = (np.abs(xn) < 1) & (tn >= 0) & (tn <= T)
gf = np.abs(D.force(np.clip(T - tn, 1e-4, T), np.clip(xn, -1, 1)))
glow = np.where(inside, 1 - np.exp(-gf / 40.0), 0)
sheet.wash(0.60 * glow, 'apricot', granulate=0.3, seed=9)
sheet.wash(0.30 * glow ** 2, 'blush')
del yy, xx, xn, tn, inside, gf, glow
# occupation certificate from the cloud
mid = (tim > 0.25 * T) & (tim < 0.75 * T)
h, e = np.histogram(xs[:, mid].ravel(), bins=16, range=(-1, 1)); xc = 0.5 * (e[1:] + e[:-1])
occ = (h / h.sum() * 8).tolist(); gs = np.cos(np.pi * xc / 2) ** 2; gs = (gs / gs.sum() * 8).tolist()
cloud_cost = dict(mean=float(cost.mean()), sem=float(cost.std() / np.sqrt(NC)), median=float(np.median(cost)),
                  trimmed_mean_99=float(np.mean(np.sort(cost)[:int(0.99 * NC)])), max=float(cost.max()))
del xs, fs

# ---- ink threads: a few actual paths ----
xs, tim, fs, cost_i, maxf_i = D.run(NI, dt, seed=SEED + 100, record_every=20)
PX = X(xs); PY = Y(tim)
f0 = 4.0
imI = Image.new('F', (W, H), 0.0); drI = ImageDraw.Draw(imI)
wI = max(1, int(round(1.15 * rs)))
m = xs.shape[1]
for p in range(NI):
    f = np.abs(fs[p])
    for a in range(0, m - 1, 5):
        b = min(a + 6, m)
        wgt = 0.30 + 0.70 * float(np.mean(f[a:b] / (f[a:b] + f0)))
        drI.line(list(zip(PX[p, a:b].astype(float), PY[a:b].astype(float))), fill=wgt, width=wI, joint='curve')
ink = gaussian_filter(np.asarray(imI, np.float32), 0.45 * rs)
sheet.wash(0.9 * np.clip(ink, 0, 1), 'ink')
kmax = np.argmax(np.abs(fs), axis=1)
bead = P.discs_density(W, H, PX[np.arange(NI), kmax], PY[kmax], np.full(NI, 2.4 * rs), np.full(NI, 1.0), sigma=0.5 * rs)
sheet.wash(0.9 * bead, 'ink')
print('threads [%.0fs]' % (time.time() - t0), flush=True)

# ---- walls, origin, ticks ----
yy, xx = np.mgrid[:H, :W]
wall = np.zeros((H, W), np.float32)
for xw in (x_left, x_right):
    wall += np.exp(-((xx - xw) / (1.8 * rs)) ** 2) * ((yy >= y_top - 2 * rs) & (yy <= y_bot + 2 * rs))
sheet.wash(1.5 * wall, 'coral')
sheet.wash(1.2 * np.exp(-(((xx - X(0.0)) ** 2 + (yy - y_bot) ** 2) / (3.5 * rs) ** 2)), 'ink')
tick = np.zeros((H, W), np.float32)
for k in range(int(T) + 1):
    tick += np.exp(-((yy - Y(k)) / (0.8 * rs)) ** 2) * ((xx > x_left - 0.035 * W) & (xx < x_left - 0.012 * W))
sheet.wash(0.5 * tick, 'ink')
del yy, xx

title = 'The Cheapest Way to Stay'
sub = (f'Brownian motion kept between two walls until T = {T:g} by the cheapest force, time upward: '
       f'{NC} paths tinted by the push they feel (blue free, apricot hard), {NI} of them in ink')
sheet.caption_strip(0.925, 0.985, 0.62)
fs_t = int(0.030 * H * FW / FH); fs_s = int(0.0135 * H * FW / FH)
items = [(title, 0.04 * W, 0.955 * H, fs_t, 'serif_bold', 'ls'), (sub, 0.04 * W, 0.978 * H, fs_s, 'italic', 'ls')]
print('caption width', P.text_width(sub, fs_s, 'italic') / W, flush=True)
sheet.wash(0.95 * P.text_density(W, H, items), 'ink')
img = sheet.develop()
P.finish(img, (FW, FH), OUT + f'_{FW}x{FH}.png')

cert = dict(ncloud=NC, nink=NI, T=T, dt=dt, seed=SEED, theory_cost=float(theory), cloud_cost=cloud_cost,
            ink_costs=cost_i.tolist(), max_force_median_cloud=float(np.median(maxf)),
            occupation_mid=dict(x=xc.tolist(), measured=occ, cos2_law=gs), seconds=time.time() - t0)
json.dump(cert, open(OUT + f'_{FW}x{FH}_cert.json', 'w'), indent=1)
print(json.dumps({k: v for k, v in cert.items() if k not in ('occupation_mid', 'ink_costs')}, indent=1))
