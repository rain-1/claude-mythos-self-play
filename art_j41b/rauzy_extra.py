"""rauzy_extra.py — boundary box-counting dimension of the Rauzy fractal and its lattice neighbours
(points streamed in chunks through render_rauzy.gen_points so the memory stays small)."""
import numpy as np, json
from scipy.ndimage import binary_dilation
import rauzy as rz
from render_rauzy import gen_points

beta, alpha, v = rz.eig()
K, N = 27, 2048
coarse = rz.admissible_strings(20).astype(float) @ alpha ** np.arange(20)
x0, y0 = coarse.real.min() - 0.05, coarse.imag.min() - 0.05
ext = max(np.ptp(coarse.real), np.ptp(coarse.imag)) + 0.1
S = 0.62 * N / ext
off = 0.19 * N
sup = np.zeros(N * N, np.int32)


def fn(z, ad):
    ix = np.clip(np.floor(off + S * (z.real - x0)).astype(int), 0, N - 1)
    iy = np.clip(np.floor(off + S * (z.imag - y0)).astype(int), 0, N - 1)
    sup[:] += np.bincount(iy * N + ix, minlength=N * N).astype(np.int32)


npts = gen_points(K, 14, alpha, fn)
sup = sup.reshape(N, N) > 0
print('points', npts, 'per px', npts / sup.sum())
b = sup & ~(np.roll(sup, 1, 0) & np.roll(sup, -1, 0) & np.roll(sup, 1, 1) & np.roll(sup, -1, 1))
res = []
for bs in [1, 2, 4, 8, 16, 32, 64, 128]:
    r = N // bs * bs
    w = b[:r, :r].reshape(r // bs, bs, r // bs, bs).any(axis=(1, 3))
    res.append((bs, int(w.sum())))
lb = np.log([r[0] for r in res]); lc = np.log([r[1] for r in res])
slope = -np.polyfit(lb[1:6], lc[1:6], 1)[0]
print('boundary box counts', res, 'dimension (scales 2..32 px)', slope)
lam_a, lam_b = (1 - v[2]), (v[1] - v[2])
dil = binary_dilation(sup, iterations=2)
touch = []
for a in range(-3, 4):
    for bb in range(-3, 4):
        if a == 0 and bb == 0: continue
        lam = a * lam_a + bb * lam_b
        dx, dy = int(round(S * lam.real)), int(round(S * lam.imag))
        sh = np.roll(np.roll(sup, dy, 0), dx, 1)
        if dy > 0: sh[:dy] = False
        elif dy < 0: sh[dy:] = False
        if dx > 0: sh[:, :dx] = False
        elif dx < 0: sh[:, dx:] = False
        ov = (sh & dil).sum()
        if ov > 0:
            touch.append(((a, bb), int(ov), float((sh & sup).sum() / sup.sum())))
print('touching translates:', len(touch))
for t in touch: print('  ', t)
json.dump(dict(points=int(npts), boundary_box_counts=res, boundary_dim_est=float(slope),
               neighbours=[dict(ab=list(t[0]), touch_px=t[1], overlap_frac=t[2]) for t in touch]),
          open('rauzy_extra.json', 'w'), indent=1)
