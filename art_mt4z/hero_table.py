"""HERO — 'The Republic of Rest' (working title), MO 513737.

One terrain, three grades of rest for a table with legs of side d:
 - violet atmosphere: best available TILT among balanced square placements
   (the wobbly-table theorem guarantees rest everywhere; almost never level)
 - teal rivers: level TRIPOD configurations (2 eqs in 3 unknowns -> curves);
   each traced config draws its triangle, the envelope braids the rivers
 - gold squares: fully level 4-leg placements (3 eqs in 3 unknowns ->
   isolated miracles)
Usage: python3 hero_table.py [proto|final]
"""
import sys, time
import numpy as np
from scipy.ndimage import gaussian_filter, grey_dilation, zoom
import table_lib as tl
import rkit

MODE = sys.argv[1] if len(sys.argv) > 1 else 'proto'
FINAL = 4096 if MODE == 'final' else 1024
SS = 2
S = FINAL * SS
rs = FINAL / 4096 * SS  # stroke scale vs final-4096 reference

SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 7
D = float(sys.argv[3]) if len(sys.argv) > 3 else 0.55

T = tl.make_terrain(seed=SEED)
Rc = D / np.sqrt(3)
Rs = D / np.sqrt(2)
cmax_t = 1.0 - Rc
cmax_s = 1.0 - Rs

# world window [-1.06, 1.06]
WLO, WHI = -1.06, 1.06
def px(x):
    return (np.asarray(x) - WLO) / (WHI - WLO) * (S - 1)

t0 = time.time()

# ---------------------------------------------------------------- layer 0: terrain
n = S // 2
xg = np.linspace(WLO, WHI, n)
X, Y = np.meshgrid(xg, xg)
H = tl.h_eval(T, X, Y)
R2 = X**2 + Y**2
inside = R2 <= 1.0
H = np.where(inside, H, 0.0)
hx, hy = tl.h_grad(T, X, Y)
hx = np.where(inside, hx, 0); hy = np.where(inside, hy, 0)
# lambertian, light from NW-up
lx, ly, lz = -0.5, -0.35, 0.8
nz = 1.0 / np.sqrt(1 + hx**2 + hy**2)
shade = np.clip((-hx * lx - hy * ly + lz) * nz, 0, None)
shade = shade / shade[inside].max()
hn = (H - H[inside].min()) / (H[inside].max() - H[inside].min())
# hypsometric: deep petrol lows -> slate mids -> dim umber highs
ground = rkit.ramp([(0.0, (0.010, 0.030, 0.055)),
                    (0.35, (0.028, 0.052, 0.080)),
                    (0.55, (0.052, 0.062, 0.075)),
                    (0.75, (0.085, 0.070, 0.058)),
                    (1.0, (0.13, 0.095, 0.065))], hn)
rgb = ground * 4.2 * (0.36 + 1.00 * shade[..., None]) ** 1.6
rgb[~inside] *= 0.0
# faint sea floor outside the disk + rim
rim = np.exp(-((np.sqrt(R2) - 1.0) * S / (14 * rs)) ** 2)
rgb += rim[..., None] * np.array([0.10, 0.13, 0.16]) * 0.5
# height contours, very faint
lev = hn * 14
gmag = np.hypot(*np.gradient(lev)) + 1e-9
cont = np.exp(-((lev - np.round(lev)) / (gmag * 1.4 * rs)) ** 2)
rgb += (cont * inside * 0.075)[..., None] * np.array([0.55, 0.75, 0.85]) * shade[..., None]
rgb = zoom(rgb.astype(np.float32), (2, 2, 1), order=1)[:S, :S]
del H, hx, hy, nz, shade, hn, ground, cont, lev, gmag, rim
X, Y = np.meshgrid(np.linspace(WLO, WHI, S, dtype=np.float32),
                   np.linspace(WLO, WHI, S, dtype=np.float32))
R2 = X**2 + Y**2
del X, Y
print(f'terrain {time.time()-t0:.0f}s')

# ------------------------------------------------- layer 1: balanced tilt fog
t0 = time.time()
ngf = 384 if MODE == 'proto' else 640
tilt, cnt, xs_f = tl.balanced_tilt_field(T, D, ngrid=ngf, ntheta=256 if MODE == 'proto' else 384)
# min tilt in radians; brightness = how level you can rest here
fog = np.exp(-(tilt / 0.055) ** 2)
fog = np.nan_to_num(fog, nan=0.0)
fog_s = gaussian_filter(fog, 1.2)
# map fog grid (over [-cmax_s, cmax_s]) into canvas
fz = zoom(fog_s, (S * (2 * cmax_s) / (WHI - WLO)) / fog_s.shape[0], order=1)
fbuf = np.zeros((S, S), np.float32)
o = int(round(px(-cmax_s)))
fbuf[o:o + fz.shape[0], o:o + fz.shape[1]] = fz[:min(fz.shape[0], S - o), :min(fz.shape[1], S - o)]
mask_c = (R2 <= cmax_s ** 2)
fbuf *= mask_c
rgb += (fbuf[..., None] * np.array([0.36, 0.19, 0.60]) * 3.4).astype(np.float32)
print(f'fog {time.time()-t0:.0f}s   fog max {fog.max():.2f}')

# ------------------------------------------------- layer 2: level-triangle rivers
t0 = time.time()
ngrid = 200 if MODE == 'proto' else 320
ntheta = 224 if MODE == 'proto' else 320
cx, cy, th, k = tl.tri_curve_points(T, D, ngrid=ngrid, ntheta=ntheta)
seeds = np.stack([cx, cy, th], axis=1)
step = 0.0035 if MODE == 'proto' else 0.0016
comps = tl.trace_tri_curves(T, D, seeds, cmax_t, step=step)
ncfg = sum(len(c['pts']) for c in comps)
print(f'tri: {len(seeds)} seeds -> {len(comps)} components, {ncfg} configs '
      f'({time.time()-t0:.0f}s)')

kmin, kmax = None, None
allk = []
for c in comps:
    p = c['pts']
    fx, fy = tl.feet(p[:, 0], p[:, 1], p[:, 2], Rc, 3)
    kk = tl.h_eval(T, fx[0], fy[0])
    c['k'] = kk
    allk.append(kk)
allk = np.concatenate(allk)
kmin, kmax = allk.min(), allk.max()

tri_buf = [np.zeros((S, S), np.float32) for _ in range(3)]  # rgb accumulation via 3 mono bufs
TRI_RAMP = [(0.0, (0.06, 0.42, 0.52)), (0.45, (0.22, 0.78, 0.76)),
            (0.8, (0.62, 0.95, 0.90)), (1.0, (0.85, 1.00, 0.96))]
mass = 7.0 * rs / max(ncfg / 24000, 1.0)
for c in comps:
    p = c['pts']
    fx, fy = tl.feet(p[:, 0], p[:, 1], p[:, 2], Rc, 3)
    tt = (c['k'] - kmin) / (kmax - kmin + 1e-12)
    col = rkit.ramp(TRI_RAMP, tt)
    for i in range(3):
        j = (i + 1) % 3
        for ch in range(3):
            rkit.line_splat(tri_buf[ch], px(fx[i]), px(fy[i]),
                            px(fx[j]), px(fy[j]), mass * col[:, ch],
                            npts=int(180 * rs))
tri_rgb = np.stack(tri_buf, axis=2)
# amplitude-restored thickening
tri_bl = np.stack([gaussian_filter(tri_rgb[..., ch], 1.1 * rs) for ch in range(3)], axis=2)
tri_rgb = tri_rgb * 0.5 + tri_bl * (0.35 + 0.65 * rs) * 1.15
rgb += (np.clip(tri_rgb, 0, 4.0) * 0.30).astype(np.float32)
del tri_rgb, tri_bl, tri_buf

# centroid rivers + feet threads (the linear structure)
riv = [np.zeros((S, S), np.float32) for _ in range(3)]
for c in comps:
    p = c['pts']
    tt = (c['k'] - kmin) / (kmax - kmin + 1e-12)
    col = rkit.ramp(TRI_RAMP, tt)
    # centroid thread
    for ch in range(3):
        rkit.line_splat(riv[ch], px(p[:-1, 0]), px(p[:-1, 1]),
                        px(p[1:, 0]), px(p[1:, 1]),
                        3.0 * rs * col[:-1, ch], npts=8)
    # feet threads (three footprints), fainter
    fx, fy = tl.feet(p[:, 0], p[:, 1], p[:, 2], Rc, 3)
    for i in range(3):
        for ch in range(3):
            rkit.line_splat(riv[ch], px(fx[i][:-1]), px(fy[i][:-1]),
                            px(fx[i][1:]), px(fy[i][1:]),
                            1.5 * rs * col[:-1, ch], npts=8)
riv = np.stack(riv, axis=2)
rivd = np.stack([grey_dilation(riv[..., ch], size=int(max(2, 1.1 * rs)))
                 for ch in range(3)], axis=2)
rgb += rivd * 0.55 + np.stack([gaussian_filter(rivd[..., ch], 3.0 * rs)
                               for ch in range(3)], axis=2) * 0.55
print(f'tri render {time.time()-t0:.0f}s')

# sparse legible hero triangles
t0 = time.time()
hero_every = max(ncfg // 26, 1)
hb = [np.zeros((S, S), np.float32) for _ in range(3)]
cnt_h = 0
for c in comps:
    p = c['pts'][::hero_every]
    kk = c['k'][::hero_every]
    fx, fy = tl.feet(p[:, 0], p[:, 1], p[:, 2], Rc, 3)
    tt = (kk - kmin) / (kmax - kmin + 1e-12)
    col = rkit.ramp(TRI_RAMP, tt) * 0.85 + 0.15
    cnt_h += len(p)
    for i in range(3):
        j = (i + 1) % 3
        for ch in range(3):
            rkit.line_splat(hb[ch], px(fx[i]), px(fy[i]), px(fx[j]), px(fy[j]),
                            2.2 * rs * col[:, ch], npts=int(240 * rs))
        # feet
        for ch in range(3):
            rkit.splat_points(hb[ch], px(fx[i]), px(fy[i]), 1.6 * rs * col[:, ch])
hb = np.stack(hb, axis=2)
hbd = np.stack([grey_dilation(hb[..., ch], size=int(max(2, 1.0 * rs)))
                for ch in range(3)], axis=2)
rgb += hbd * 0.16 + np.stack([gaussian_filter(hbd[..., ch], 2.5 * rs)
                              for ch in range(3)], axis=2) * 0.16
print(f'hero tris ({cnt_h}) {time.time()-t0:.0f}s')

# ------------------------------------------------- layer 3: level squares (gold)
t0 = time.time()
sg = 128 if MODE == 'proto' else 224
scx, scy, sth, sk = tl.sq_level_points(T, D, ngrid=sg, ntheta=192 if MODE == 'proto' else 288)
print(f'{len(scx)} level squares  ({time.time()-t0:.0f}s)')
gold = np.array([1.0, 0.78, 0.30])
gb = [np.zeros((S, S), np.float32) for _ in range(3)]
for i in range(len(scx)):
    fx, fy = tl.feet(scx[i], scy[i], sth[i], Rs, 4)
    fx = np.array(fx); fy = np.array(fy)
    for e in range(4):
        j = (e + 1) % 4
        for ch in range(3):
            rkit.line_splat(gb[ch], np.array([px(fx[e])]), np.array([px(fy[e])]),
                            np.array([px(fx[j])]), np.array([px(fy[j])]),
                            np.array([650.0 * rs * gold[ch]]), npts=int(500 * rs))
    # feet stars
    for ch in range(3):
        rkit.splat_points(gb[ch], px(fx), px(fy), 500.0 * rs * gold[ch])
gb = np.stack(gb, axis=2)
gbd = np.stack([grey_dilation(gb[..., ch], size=int(max(2, 1.6 * rs))) for ch in range(3)], axis=2)
star_halo = np.stack([gaussian_filter(gbd[..., ch], 7 * rs) for ch in range(3)], axis=2)
rgb += gbd * 0.30 + star_halo * 0.80

# ------------------------------------------------- finish
rgb = rkit.bloom(rgb, sigma=6 * rs, gain=0.55, mask_thresh=0.50)
rgb = rkit.filmic(rgb, k=1.35, gamma=0.86)
out = rkit.downscale(rgb, FINAL)
if MODE == 'final':
    out = rkit.caption(out, [
        'THE REPUBLIC OF REST',
        f'a smooth floor h on the unit disk, h = 0 at the shore. MO 513737 (jul 2026): must a table find a LEVEL rest?',
        f'violet air: the wobbly-table theorem rests a (tilted) 4-legged square everywhere; glow = how level it can get',
        f'teal rivers: ALL level 3-legged rests, side {D:.2f}: {len(comps)} closed curves in (position x angle)-space',
        f'gold: the only {len(scx)} placements where a 4-legged square stands LEVEL - 3 equations, 3 unknowns, isolated',
        f'{ncfg} traced placements, every foot-height equal to 1e-10; own Newton continuation on an analytic floor',
        'touching is a surface. resting level is a curve. standing true is a point. - claude fable 5, 2026-07-31'],
        size=12)
rkit.to_img(out, f'hero_{MODE}_s{SEED}_d{D:.2f}.png')
print(f'saved hero_{MODE}_s{SEED}_d{D:.2f}.png  total {time.time()-t0:.0f}s')
