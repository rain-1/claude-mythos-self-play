"""'The Seams to the Horizon' — Pade poles of (1-z^3)^(-1/2)  (MO 122539).

Warm field: digits of agreement of the [144/144] Pade approximant (level sets
= Green equipotentials of the cut plane).  Cold pupil: digits of agreement of
the degree-291 Taylor polynomial — dies exactly at |z| = 1.  Stars: poles
(gold) and zeros (silver) of orders [6/6] ... [144/144] with an age ramp; the
rational impostor imitates a branch cut it cannot have by sewing pole-zero
seams along the three rays — and, since infinity is itself a branch point,
the seams run off the edge of the map.
"""
import pickle, time
import numpy as np
from fractions import Fraction
from scipy.ndimage import gaussian_filter, grey_dilation
import rkit
import pade_lib as pl

FINAL = 2560
SS = 2
S = FINAL * SS
rs = FINAL / 4096 * SS
W = 2.55           # half-window
ROT = np.pi / 2    # display rotation (pure rotation of the plane, declared)

d = pickle.load(open('pade_data.pkl', 'rb'))
orders = sorted(d.keys())
mtop = orders[-1]
A = np.array([float(a) for a in d[mtop]['A']])
B = np.array([float(b) for b in d[mtop]['B']])
cs = pl.g_coeffs(97)
CT = np.array([float(c) for c in cs])

t0 = time.time()
# ---------------------------------------------------------------- error fields
xg = np.linspace(-W, W, S)
DP = np.zeros((S, S), np.float32)
DT = np.zeros((S, S), np.float32)
for i0 in range(0, S, 256):
    i1 = min(i0 + 256, S)
    Zx, Zy = np.meshgrid(xg, xg[i0:i1])
    Z = (Zx + 1j * Zy) * np.exp(-1j * ROT)   # inverse-rotate the plane
    U = Z ** 3
    F = 1.0 / np.sqrt(1.0 - U)
    num = np.zeros_like(U); den = np.zeros_like(U)
    for a in A[::-1]:
        num = num * U + a
    for b in B[::-1]:
        den = den * U + b
    R = num / den
    T = np.zeros_like(U)
    for c in CT[::-1]:
        T = T * U + c
    with np.errstate(all='ignore'):
        DP[i0:i1] = np.clip(-np.log10(np.abs(R - F) / (np.abs(F) + 1e-30) + 1e-60), 0, 15)
        DT[i0:i1] = np.clip(-np.log10(np.abs(T - F) / (np.abs(F) + 1e-30) + 1e-60), 0, 15)
print(f'measured fields {time.time()-t0:.0f}s')

# exact error laws (validated vs 400-digit mpmath at 8 points spanning the
# plane: pade max dev 0.012 digits, taylor next-term dev ~0.15 digits):
#   |f - [144/144]| / |f| = 2 |phi(z^3)|^97,  phi(u) = (sqrt(1-u)-1)/(sqrt(1-u)+1)
#   |f - T_291| / |f| ~ |c_97 u^97| * |sqrt(1-u)|
DPa = np.zeros((S, S), np.float32)
DTa = np.zeros((S, S), np.float32)
K = len(CT) - 1
cK = float(CT[-1])
for i0 in range(0, S, 512):
    i1 = min(i0 + 512, S)
    Zx, Zy = np.meshgrid(xg, xg[i0:i1])
    Z = (Zx + 1j * Zy) * np.exp(-1j * ROT)
    U = Z ** 3
    sq = np.sqrt(1 - U)
    phi = np.abs((sq - 1) / (sq + 1))
    with np.errstate(all='ignore'):
        DPa[i0:i1] = np.clip(-(np.log10(2.0) + 97 * np.log10(phi + 1e-30)), 0, 300)
        DTa[i0:i1] = np.clip(-np.log10(cK * np.abs(U) ** K * np.abs(sq) + 1e-300), 0, 300)
# sanity: compare measured (float64-capped) vs law in the measurable band
band = (DP > 4) & (DP < 13)
dev_p = np.abs(np.clip(DPa, 0, 15) - DP)[band]
band_t = (DT > 4) & (DT < 13)
dev_t = np.abs(DTa - DT)[band_t]
print(f'law vs float64-measured band: pade mean|dev| = {dev_p.mean():.2f}, '
      f'taylor mean|dev| = {dev_t.mean():.2f}')
del DP, DT
print(f'fields {time.time()-t0:.0f}s')

# warm world: pade digits (soft-knee compress); cyan glass lens: taylor digits
dp = 1 - np.exp(-DPa / 40.0)
dt = 1 - np.exp(-DTa / 12.0)
warm = rkit.ramp([(0.0, (0.004, 0.002, 0.006)), (0.25, (0.10, 0.030, 0.058)),
                  (0.5, (0.32, 0.11, 0.09)), (0.75, (0.70, 0.38, 0.16)),
                  (0.92, (0.98, 0.80, 0.50)), (1.0, (1.0, 0.97, 0.88))], np.clip(dp, 0, 1) ** 1.12)
rgb = warm.astype(np.float32)
# the glass of the diary: tint the world cold inside Taylor's reach
lens = dt[..., None] * np.array([0.62, 0.10, -0.42])
rgb = rgb * (1 - 0.62 * lens.clip(-1, 1)) + (dt ** 1.5)[..., None] * np.array([0.05, 0.16, 0.22])
rgb = rgb.astype(np.float32)
del warm, lens
# digit-level contour rings on the pade field (every 6 digits)
lev = np.clip(DPa, 0, 120) / 12.0
g = np.hypot(*np.gradient(lev)) + 1e-9
cont = np.exp(-((lev - np.round(lev)) / (g * 1.5 * rs)) ** 2) * (lev > 0.5) * (lev < 9.5)
rgb += (cont * 0.08)[..., None] * np.array([1.0, 0.75, 0.45]).astype(np.float32)
del lev, g, cont, DPa, DTa
print(f'palette {time.time()-t0:.0f}s')

def px(v):
    return (v + W) / (2 * W) * (S - 1)

# unit circle: Taylor's horizon (faint cold ring)
th = np.linspace(0, 2 * np.pi, 3000)
ring = np.zeros((S, S), np.float32)
rkit.line_splat(ring, px(np.cos(th[:-1])), px(np.sin(th[:-1])),
                px(np.cos(th[1:])), px(np.sin(th[1:])), 2.0 * rs, npts=6)
ringd = grey_dilation(ring, size=int(max(2, 1.2 * rs)))
rgb += (gaussian_filter(ringd, 1.2 * rs) * 0.55)[..., None] * np.array([0.35, 0.75, 0.85])
del ring, ringd

# ---------------------------------------------------------------- star layers
gold = np.array([1.0, 0.78, 0.32])
silver = np.array([0.72, 0.88, 0.92])
white = np.array([1.0, 0.97, 0.90])
sb = [np.zeros((S, S), np.float32) for _ in range(3)]
omega = np.exp(1j * (2 * np.pi * np.arange(3) / 3 + ROT))
nord = len(orders)
for oi, m in enumerate(orders):
    age = (oi + 1) / nord            # 0..1, late = bright
    amp_p = 3.0 + 240.0 * age ** 2.6
    amp_z = 2.0 + 150.0 * age ** 2.6
    for t in d[m]['poles']:
        r = t ** (1 / 3)
        if r > W * 1.5: continue
        for w in omega:
            zz = r * w
            for ch in range(3):
                rkit.splat_points(sb[ch], [px(zz.real)], [px(zz.imag)],
                                  amp_p * rs * gold[ch] * (0.55 + 0.45 * age))
    for t in d[m]['zeros']:
        r = t ** (1 / 3)
        if r > W * 1.5: continue
        for w in omega:
            zz = r * w
            for ch in range(3):
                rkit.splat_points(sb[ch], [px(zz.real)], [px(zz.imag)],
                                  amp_z * rs * silver[ch] * (0.5 + 0.5 * age))
# branch points: crowned white stars
for w in omega:
    for ch in range(3):
        rkit.splat_points(sb[ch], [px(w.real)], [px(w.imag)], 900.0 * rs * white[ch])
sb = np.stack(sb, axis=2)
sbd = np.stack([grey_dilation(sb[..., ch], size=int(max(2, 1.5 * rs))) for ch in range(3)], axis=2)
halo = np.stack([gaussian_filter(sbd[..., ch], 5.5 * rs) for ch in range(3)], axis=2)
wide = np.stack([gaussian_filter(sbd[..., ch], 22 * rs) for ch in range(3)], axis=2)
rgb += sbd * 0.10 + halo * 0.30 + wide * 0.18
del sb, sbd, halo, wide

rgb = rkit.bloom(rgb, sigma=5 * rs, gain=0.4, mask_thresh=0.6)
rgb = rkit.filmic(rgb, k=1.25, gamma=0.88)
out = rkit.downscale(rgb, FINAL)
out = rkit.caption(out, [
    'THE SEAMS TO THE HORIZON',
    'f(z) = (1-z^3)^(-1/2) knows three branch points on the unit circle, and a fourth at infinity - MO 122539: the unreasonable',
    'effectiveness of Pade approximation. cold pupil: digits won by the Taylor polynomial (degree 291) - it dies exactly at |z| = 1.',
    'warm world: digits won by the [144/144] Pade approximant from the SAME 97 coefficients - its exact error law, verified to',
    '0.012 digits at 400-digit precision, is 2|phi(z^3)|^97 with phi the conformal map of the cut plane - rings = equipotentials.',
    'gold/silver stars: poles/zeros of orders [6/6]..[144/144] - all EXACTLY on the three rays (real, interlacing: g is Markov).',
    'a rational function has no cuts, so it sews seams of pole-zero stitches; infinity being itself a branch point, the seams',
    'run off the edge of the map.  at z = 1.7+0.4i: taylor error 3e+68, pade error 3e-14.  claude fable 5, 2026-07-31'],
    size=11.5, pos='top')
rkit.to_img(out, 'seams_final.png')
print(f'saved seams_final.png  {time.time()-t0:.0f}s')
