"""render_eigen.py — THE PATTERN IS IN THE LAW.  The strange eigenmode of a periodic chaotic stirring.

A passive scalar on the torus is stirred by a fixed protocol of P sine-flow periods (phases chosen so the
leading Floquet eigenvalue is real and positive) with a little diffusion.  Two very different initial inks
(stripes; one blob) are run for NB blocks each; both converge to the SAME normalised pattern — the picture is
that pattern.  Warm pigment where the eigenmode is positive, cool where negative, density by |θ|; the two
small panels at the bottom show the two initial inks that both became it.

usage: python3 render_eigen.py FINAL n A P seed kappa nblocks out_prefix [phase_index]
"""
import sys, json, time
import numpy as np
from scipy.ndimage import gaussian_filter, zoom
import pastel as P
from eigenmode import SineFlow, initial

FINAL = int(sys.argv[1]); n = int(sys.argv[2]); A = float(sys.argv[3]); PP = int(sys.argv[4]); SEED = int(sys.argv[5])
KAP = float(sys.argv[6]); NB = int(sys.argv[7]); OUT = sys.argv[8]
PH_IDX = int(sys.argv[9]) if len(sys.argv) > 9 else 0
SS = 2; W = H = FINAL * SS; rs = FINAL / 1024.0 * SS
t0 = time.time()

rng = np.random.default_rng(SEED); ph = rng.uniform(0, 2 * np.pi, (PP, 2))
flows = [SineFlow(n, A=A, kappa=KAP, phases=tuple(p), tau=2.0) for p in ph]
def block(th, upto=None):
    for f in flows[:upto]:
        th = f.period(th)
    return th - th.mean()

fields = {}; hist = {}
for kind in ('sinx', 'blob'):
    th = initial(kind, n); th -= th.mean(); th /= np.sqrt((th ** 2).mean())
    cs, rs_ = [], []
    for b in range(NB):
        prev = th
        th = block(th); v = np.sqrt((th ** 2).mean()); rs_.append(float(v)); th = th / v
        cs.append(float((th * prev).mean()))
    # optional partial block: eigenmode at another phase of the protocol
    if PH_IDX > 0:
        th = block(th, upto=PH_IDX); th /= np.sqrt((th ** 2).mean())
    fields[kind] = th; hist[kind] = dict(consecutive_corr=cs[-6:], ratio_per_block=rs_[-6:])
    print(kind, 'done [%.0fs]' % (time.time() - t0), 'ratio', rs_[-1], 'consec', cs[-1], flush=True)
a, b = fields['sinx'], fields['blob']
cross = float((a * b).mean())
theta = a if cross > 0 else a       # the eigenmode (b = ±a)
print('cross-ink correlation', cross, flush=True)

# ---- sheet ----
sheet = P.Sheet(W, H, seed=SEED + 11)
# main panel: square, leaves room for caption + two small panels at the bottom
side = 0.78 * W; x0p = (W - side) / 2; y0p = 0.03 * H
def panel(th, x0, y0, s, strength, fade=True, sat=1.0):
    """upsample θ (n×n, mean 0, rms 1) into a s×s square at (x0,y0) — two pigments by sign"""
    S_ = int(round(s))
    f = zoom(th, S_ / n, order=3) if S_ != n else th
    f = f[:S_, :S_]
    if f.shape[0] < S_:
        f = np.pad(f, ((0, S_ - f.shape[0]), (0, S_ - f.shape[1])), mode='edge')
    mag = np.abs(f)
    d = mag / (mag + 0.55)                                  # soft knee on |θ| (rms 1)
    if fade:
        yy, xx = np.mgrid[:S_, :S_] / S_
        edge = np.minimum(np.minimum(xx, 1 - xx), np.minimum(yy, 1 - yy))
        e = np.clip(edge / 0.10, 0, 1); e = e * e * (3 - 2 * e)
        e = e * (1 + 0.35 * P.lowfreq(S_, S_, max(8, S_ // 10), SEED + 3))
        d = d * np.clip(e, 0, 1)
    warm = d * (f > 0); cool = d * (f < 0)
    X0, Y0 = int(round(x0)), int(round(y0))
    for dens, pig in ((warm, 'apricot'), (cool, 'cornflower')):
        full = np.zeros((H, W), np.float32); full[Y0:Y0 + S_, X0:X0 + S_] = dens
        sheet.wash(strength * sat * (1.25 if pig == 'apricot' else 1.0) * full, pig, granulate=0.12, seed=40 + (pig == 'apricot'))
    # second pigments in the strongest regions (bloom substitute): coral-free
    for dens, pig in ((warm * np.clip((mag - 1.2) / 1.5, 0, 1), 'blush'), (cool * np.clip((mag - 1.2) / 1.5, 0, 1), 'lavender')):
        full = np.zeros((H, W), np.float32); full[Y0:Y0 + S_, X0:X0 + S_] = dens
        sheet.wash(0.7 * strength * sat * full, pig)
    return S_

panel(theta, x0p, y0p, side, 2.0)
print('main panel [%.0fs]' % (time.time() - t0), flush=True)

# small panels: the two initial inks, and the same inks after one block (still different)
sm = 0.09 * W; ys = y0p + side + 0.02 * H
xs_ = [x0p, x0p + sm + 0.02 * W, W - x0p - 2 * sm - 0.02 * W, W - x0p - sm]
ins = {}
for kind in ('sinx', 'blob'):
    th = initial(kind, n); th -= th.mean(); th /= np.sqrt((th ** 2).mean()); ins[kind] = th
    th1 = block(th); th1 /= np.sqrt((th1 ** 2).mean()); ins[kind + '1'] = th1
for k, key in enumerate(['sinx', 'sinx1', 'blob1', 'blob']):
    panel(ins[key], xs_[k], ys, sm, 1.4, fade=False, sat=0.9)
# ink frames around the small panels
yy, xx = np.mgrid[:H, :W]
frame = np.zeros((H, W), np.float32)
for k in range(4):
    X0, Y0 = xs_[k], ys
    inside = (xx >= X0 - 1.5 * rs) & (xx <= X0 + sm + 1.5 * rs) & (yy >= Y0 - 1.5 * rs) & (yy <= Y0 + sm + 1.5 * rs)
    inner = (xx >= X0) & (xx <= X0 + sm) & (yy >= Y0) & (yy <= Y0 + sm)
    frame += inside & ~inner
sheet.wash(0.7 * frame, 'ink')
# coral arrows: from each initial ink toward the centre (the law pulls both into the same pattern)
ymid = ys + sm / 2
for (xa, xb) in ((xs_[1] + sm + 0.01 * W, W / 2 - 0.02 * W), (xs_[2] - 0.01 * W, W / 2 + 0.02 * W)):
    lo, hi = min(xa, xb), max(xa, xb)
    seg = np.exp(-((yy - ymid) / (1.2 * rs)) ** 2) * ((xx >= lo) & (xx <= hi))
    dash = 0.5 * (1 + np.cos(2 * np.pi * xx / (12 * rs))) ** 3
    sheet.wash(0.8 * seg * dash, 'coral')
del yy, xx
lab = [('ink A, t = 0', xs_[0] + sm / 2, ys + sm + 0.011 * H, int(0.0085 * H), 'italic', 'ms'),
       ('after one block', xs_[1] + sm / 2, ys + sm + 0.011 * H, int(0.0085 * H), 'italic', 'ms'),
       ('after one block', xs_[2] + sm / 2, ys + sm + 0.011 * H, int(0.0085 * H), 'italic', 'ms'),
       ('ink B, t = 0', xs_[3] + sm / 2, ys + sm + 0.011 * H, int(0.0085 * H), 'italic', 'ms'),
       (f'after {NB} blocks: the same pattern, correlation {abs(cross):.5f}', W / 2, ymid - 0.018 * H, int(0.0095 * H), 'italic', 'ms'),
       (f'decaying by ×{hist["sinx"]["ratio_per_block"][-1]:.3f} per block, shape unchanged', W / 2, ymid + 0.012 * H, int(0.0095 * H), 'italic', 'ms')]
sheet.wash(0.85 * P.text_density(W, H, lab), 'ink')

title = 'The Pattern Is in the Law'
sub = (f'A passive scalar stirred by a fixed protocol of {PP} sine-flow periods with weak diffusion: whatever ink you start with, '
       f'this is the shape it becomes — the strange eigenmode belongs to the stirring, not to the ink.')
fs_t = int(0.024 * H); fs_s = int(0.0105 * H)
items = [(title, 0.035 * W, 0.965 * H, fs_t, 'serif_bold', 'ls'), (sub, 0.035 * W, 0.982 * H, fs_s, 'italic', 'ls')]
print('caption width', P.text_width(sub, fs_s, 'italic') / W, flush=True)
sheet.wash(0.95 * P.text_density(W, H, items), 'ink')
img = sheet.develop()
P.finish(img, (FINAL, FINAL), OUT + f'_{FINAL}.png')
cert = dict(n=n, A=A, P=PP, seed=SEED, phases=ph.tolist(), kappa=KAP, nblocks=NB, phase_index=PH_IDX,
            cross_ink_correlation=cross, history=hist, seconds=time.time() - t0)
json.dump(cert, open(OUT + f'_{FINAL}_cert.json', 'w'), indent=1)
print(json.dumps({k: v for k, v in cert.items() if k != 'history'}, indent=1))
