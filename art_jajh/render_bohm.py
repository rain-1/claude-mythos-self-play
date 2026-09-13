"""render_bohm.py — THE PATTERN IS IN THE CROWD.  Bohmian two-slit trajectories on paper:
x across, time upward (square-root scale) from the wall at the bottom.

Materials (the 09-04 register): pigment cloud = equal-probability paths sampled at equal row spacing,
so the cloud IS |psi|² (equivariance); two families by slit of origin (cool from the left slit, warm
from the right) — the no-crossing theorem keeps them apart forever; within a family the second
pigment marks lateral SPEED.  Ink = a few actual paths (weight rises with speed: the kinks between
fringes darken).  Coral = the wall with its two slits, and the axis of symmetry that no path crosses.

Paths are EXACT: in one dimension no-crossing + equivariance make the path of probability-quantile u
the u-quantile of |psi(·,t)|² (bohm.quantile_paths; checked against RK4 to 2e-3).

usage: python3 render_bohm.py FINAL ncloud nink T out_prefix [seed] [lin|sqrt]
"""
import sys, json, time
import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image, ImageDraw
import pastel as P
from bohm import TwoSlit, quantile_paths

FINAL = int(sys.argv[1]); NC = int(sys.argv[2]); NI = int(sys.argv[3]); T = float(sys.argv[4]); OUT = sys.argv[5]
SEED = int(sys.argv[6]) if len(sys.argv) > 6 else 1
TAX = sys.argv[7] if len(sys.argv) > 7 else 'sqrt'
SS = 2
W = H = FINAL * SS
rs = FINAL / 1024.0 * SS
t0 = time.time()

A_HALF, SIG = 25.0, 1.0
S = TwoSlit(centers=(-A_HALF, A_HALF), sigma=SIG)
sT = SIG * np.sqrt(1 + (T / (2 * SIG ** 2)) ** 2)
XHALF = 2.35 * sT
y_bot, y_top = 0.935 * H, 0.035 * H
def X(x): return W / 2 + x / XHALF * (W / 2)
def Y(t):
    f = np.sqrt(np.asarray(t, float) / T) if TAX == 'sqrt' else np.asarray(t, float) / T
    return y_bot + f * (y_top - y_bot)
def T_of_row(y):
    f = (y - y_bot) / (y_top - y_bot)
    return T * (f * f if TAX == 'sqrt' else f)

sheet = P.Sheet(W, H, seed=SEED + 5)

# ---- cloud: exact quantile paths at ~1.25 samples per pixel row ----
SPR = 1.25
rows = y_bot - y_top
times = T_of_row(y_bot - np.arange(int(rows * SPR)) / SPR)
u = (np.arange(NC) + 0.5) / NC
Xc = quantile_paths(S, u, times).astype(np.float32)
slit = (u >= 0.5).astype(int)
print('cloud', Xc.shape, '[%.0fs]' % (time.time() - t0), flush=True)
order_ok = bool(np.all(np.diff(Xc, axis=0) > 0))
Vc = np.empty_like(Xc)
for j in range(len(times)):
    Vc[:, j] = S.velocity(Xc[:, j].astype(float), times[j])
print('speeds [%.0fs]' % (time.time() - t0), flush=True)
PX = X(Xc); PY = np.broadcast_to(Y(times)[None, :].astype(np.float32), Xc.shape)
inside = (PX >= 0) & (PX < W)
flat = (np.clip(PY.astype(np.int64), 0, H - 1) * W + np.clip(PX.astype(np.int64), 0, W - 1))[inside]
spd = np.abs(Vc)[inside]
fam = np.broadcast_to(slit[:, None], Xc.shape)[inside]
del PX, PY
total = np.bincount(flat, minlength=H * W).astype(np.float32).reshape(H, W)
total = gaussian_filter(total, 0.8 * rs)
d_ref = NC * SPR / W                      # mean count per pixel if the crowd were spread over the whole width
knee = lambda d: 2.0 * d / (d + 1.6 * d_ref)
v0 = 0.35
sr = (spd / (spd + v0)).astype(np.float32)
FAM = [('cornflower', 'mint'), ('apricot', 'orchid')]      # (slow, fast) per slit
K = knee(total)
# painter's fade at the top edge of the time window (last 5 % of rows)
yyf = np.arange(H, dtype=np.float32)
fade = np.clip((yyf - y_top) / (0.05 * (y_bot - y_top)), 0, 1); fade = fade * fade * (3 - 2 * fade)
K = K * fade[:, None]
for j, (slow, fast) in enumerate(FAM):
    m = fam == j
    for pig, wgt in ((slow, 1 - sr), (fast, sr)):
        d = np.bincount(flat[m], weights=wgt[m], minlength=H * W).astype(np.float32).reshape(H, W)
        d = gaussian_filter(d, 0.8 * rs)
        d = K * d / np.maximum(total, 1e-6)
        sheet.wash(1.0 * d, pig, granulate=0.15, seed=30 + 2 * j + (pig == fast))
        print('wash', pig, '[%.0fs]' % (time.time() - t0), flush=True)
del flat, spd, fam, sr, K, Vc, Xc
# certificate: RK4 cross-check of the exact quantile paths on 400 paths
uu = (np.arange(400) + 0.5) / 400
x0c, _ = S.sample_initial(400)
tt_c, Xr, _ = S.integrate(x0c, T, 8000, record_every=400)
rk_vs_q = float(np.abs(Xr - quantile_paths(S, uu, tt_c)).max())

# ---- ink paths ----
ui = (np.arange(NI) + 0.5) / NI
ti = T_of_row(y_bot - np.arange(int(rows * 2.0)) / 2.0)
Xi = quantile_paths(S, ui, ti)
Vi = np.empty_like(Xi)
for j in range(len(ti)):
    Vi[:, j] = S.velocity(Xi[:, j], ti[j])
imI = Image.new('F', (W, H), 0.0); drI = ImageDraw.Draw(imI)
wI = max(1, int(round(0.85 * rs)))
PXi = X(Xi); PYi = Y(ti)
m = Xi.shape[1]
for p in range(NI):
    sp = np.abs(Vi[p])
    for a in range(0, m - 1, 6):
        b = min(a + 7, m)
        wgt = 0.35 + 0.65 * float(np.mean(sp[a:b] / (sp[a:b] + v0)))
        drI.line(list(zip(PXi[p, a:b].astype(float), PYi[a:b].astype(float))), fill=wgt, width=wI, joint='curve')
ink = gaussian_filter(np.asarray(imI, np.float32), 0.4 * rs)
sheet.wash(0.85 * np.clip(ink, 0, 1), 'ink')
print('ink [%.0fs]' % (time.time() - t0), flush=True)

# ---- coral: the wall with two slits; the axis no path crosses ----
yy, xx = np.mgrid[:H, :W]
gap = 3.2 * SIG
wall = np.exp(-((yy - y_bot) / (2.0 * rs)) ** 2)
openings = np.ones(W, np.float32)
for xj in S.xj:
    openings *= 1 - np.exp(-(((np.arange(W) - X(xj)) / (X(gap) - X(0))) ** 6))
wall = wall * openings[None, :]
sheet.wash(1.6 * wall, 'coral')
t_ov = 2 * A_HALF * SIG
axis = np.exp(-((xx - W / 2) / (0.9 * rs)) ** 2) * (yy < Y(t_ov)) * (yy > y_top - 2 * rs)
dash = 0.5 * (1 + np.cos(2 * np.pi * yy / (14 * rs))) ** 3
sheet.wash(0.55 * axis * dash, 'coral')
for xj in S.xj:
    sheet.wash(1.0 * np.exp(-(((xx - X(xj)) ** 2 + (yy - y_bot) ** 2) / (2.6 * rs) ** 2)), 'ink')
del yy, xx

title = 'The Pattern Is in the Crowd'
sub = (f'Two slits, {NC:,} deterministic paths guided by the wave, time upward — blue from the left slit, '
       f'apricot from the right, {NI} of them in ink. No path ever crosses the middle; the fringes belong to the crowd.')
sheet.caption_strip(0.955, 0.995, 0.62)
fs_t = int(0.024 * H); fs_s = int(0.0105 * H)
items = [(title, 0.035 * W, 0.972 * H, fs_t, 'serif_bold', 'ls'), (sub, 0.035 * W, 0.988 * H, fs_s, 'italic', 'ls')]
print('caption width', P.text_width(sub, fs_s, 'italic') / W, flush=True)
sheet.wash(0.95 * P.text_density(W, H, items), 'ink')
img = sheet.develop()
P.finish(img, (FINAL, FINAL), OUT + f'_{FINAL}.png')

cert = dict(ncloud=NC, nink=NI, T=T, a=A_HALF, sigma=SIG, time_axis=TAX, frame_halfwidth=float(XHALF), s_T=float(sT),
            fringe_spacing_farfield=float(np.pi * T / A_HALF), no_crossing_order_preserved=order_ok,
            rk4_vs_quantile_max_diff_400_paths=rk_vs_q, samples_per_row=SPR, seconds=time.time() - t0)
json.dump(cert, open(OUT + f'_{FINAL}_cert.json', 'w'), indent=1)
print(json.dumps(cert, indent=1))
