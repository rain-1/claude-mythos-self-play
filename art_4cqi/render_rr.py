"""render_rr.py — A FRACTION OF A FRACTION: the Rogers–Ramanujan continued fraction on its disc.
Reads cache/rr_polar.npz (one tenth of the disc), unfolds by the five-fold symmetry and conjugation.
Pigment: the argument of R through a nine-pigment cycle; density: a bell in log|R| (zeros and poles are
paper).  Ink: the level curves |R| = phi^(k/2).  Coral: the five points tau = i where R is Ramanujan's
closed form sqrt((5+sqrt5)/2) - phi.
    python3 render_rr.py FINAL
"""
import sys, json, numpy as np
from scipy.ndimage import map_coordinates, gaussian_filter
from PIL import Image, ImageDraw
from pastel import *
FINAL = int(sys.argv[1]); SS = 2; W = H = FINAL * SS; rs = FINAL / 1024 * SS
d = np.load('cache/rr_polar.npz'); Rp, r, th = d['R'], d['r'], d['th']
NR, NTH = Rp.shape
# resolved mask on the polar grid: where the argument turns more than 0.8 rad between neighbouring samples the
# product is under-sampled and its interpolation is noise -> paper, not mud
argp = np.angle(Rp)
def wd(a, axis):
    d = np.diff(a, axis=axis); d = np.abs((d + np.pi) % (2 * np.pi) - np.pi)
    pad = [(0, 0), (0, 0)]; pad[axis] = (0, 1)
    return np.pad(d, pad, mode='edge')
resolved = ((wd(argp, 0) < 0.8) & (wd(argp, 1) < 0.8)).astype(np.float32)
from scipy.ndimage import minimum_filter
resolved = minimum_filter(resolved, size=(3, 5))
del argp
smax = -np.log(1 - r[-1]); RMAX = r[-1]
cx = cy = W / 2; RAD = 0.43 * W
# fields in row chunks, float32 only (an 8192² render with whole-canvas float64 temporaries was OOM-killed)
logR = np.zeros((H, W), np.float32); argR = np.zeros((H, W), np.float32); inside = np.zeros((H, W), bool)
rho_full = np.zeros((H, W), np.float32); res_full = np.zeros((H, W), np.float32)
CH = 256
xx = (np.arange(W, dtype=np.float32) - cx) / RAD
for y0 in range(0, H, CH):
    y1 = min(H, y0 + CH)
    Y = -(np.arange(y0, y1, dtype=np.float32) - cy) / RAD
    X = np.broadcast_to(xx[None, :], (y1 - y0, W)); Yb = np.broadcast_to(Y[:, None], (y1 - y0, W))
    rho = np.hypot(X, Yb); ang = np.arctan2(Yb, X)
    ins = rho < 1.0
    k = np.round(ang / (2 * np.pi / 5))
    a = ang - k * 2 * np.pi / 5
    conj = a < 0
    a = np.abs(a)
    si = np.clip(rho, 0, 1) * (NR - 1)
    ti = a / (np.pi / 5) * (NTH - 1)
    Rre = map_coordinates(Rp.real, [si, ti], order=1, mode='nearest')
    Rim = map_coordinates(Rp.imag, [si, ti], order=1, mode='nearest')
    res_full[y0:y1] = map_coordinates(resolved, [si, ti], order=1, mode='nearest')
    R = (Rre + 1j * Rim).astype(np.complex64)
    R = np.where(conj, np.conj(R), R) * np.exp(1j * 2 * np.pi * k / 5).astype(np.complex64)
    absR = np.abs(R)
    logR[y0:y1] = np.log(np.clip(absR, 1e-8, 1e8)); argR[y0:y1] = np.angle(R); inside[y0:y1] = ins; rho_full[y0:y1] = rho
    del X, Yb, rho, ang, k, a, conj, si, ti, Rre, Rim, R, absR
rho = rho_full; del rho_full
absR = np.exp(logR)
print('fields done', flush=True)
sheet = Sheet(W, H, seed=23)
FAM = ['apricot', 'lemon', 'pistachio', 'mint', 'aqua', 'cornflower', 'lavender', 'orchid', 'blush']
h = (argR / (2 * np.pi)) % 1.0 * len(FAM)
i0 = np.floor(h).astype(int) % len(FAM); i1 = (i0 + 1) % len(FAM); fr = (h - np.floor(h)).astype(np.float32)
bell = np.exp(-(logR / 1.6) ** 2 / 2).astype(np.float32) * inside * res_full
del res_full
def wdiff(a, axis):
    d = np.diff(a, axis=axis)
    d = np.abs((d + np.pi) % (2 * np.pi) - np.pi)
    pad = [(0, 0), (0, 0)]; pad[axis] = (0, 1)
    return np.pad(d, pad, mode='edge')
dph = wdiff(argR, 0) + wdiff(argR, 1)
bell *= np.clip(1.5 - dph / 0.32, 0, 1).astype(np.float32)
del dph
dens = 0.95 * bell
for j, name in enumerate(FAM):
    m = dens * (np.where(i0 == j, 1 - fr, 0) + np.where(i1 == j, fr, 0))
    sheet.wash(m, name, granulate=0.10, seed=j + 11)
# ink: level curves of log|R| at multiples of log(phi)/2
phi = (1 + np.sqrt(5)) / 2
step = np.log(phi) / 2
gy, gx = np.gradient(logR)
grad = (np.hypot(gx, gy) + 1e-9).astype(np.float32)
del gx, gy
frac = (logR / step + 0.5) % 1.0      # levels at phi^((k+1/2)/2): R -> phi^-1 on the real ray and phi on the pi/5 ray are PLATEAUS, not lines
dist = np.minimum(frac, 1 - frac) * step / grad
del frac
ink = ink_from_distance(dist, 0.7 * rs) * inside * np.clip(1.4 - np.abs(logR) / 3.0, 0.15, 1)
ink = np.where(grad * step > 0.5, 0, ink)         # drop the aliased hairlines where the field varies faster than a pixel
del grad, dist
sheet.wash(ink * 0.55, 'ink')
del ink, logR, absR, argR, bell, dens, h, i0, i1, fr
# rim of the disc (ink hairline)
rim_d = np.abs(rho - 1.0) * RAD
sheet.wash(ink_from_distance(rim_d, 0.9 * rs) * 0.7, 'ink')
# coral: five points tau = i  -> w = e^{-2pi/5} zeta^k
w0 = np.exp(-2 * np.pi / 5)
rho0 = -np.log(1 - w0) / smax
px = [cx + RAD * rho0 * np.cos(2 * np.pi * j / 5) for j in range(5)]
py = [cy - RAD * rho0 * np.sin(2 * np.pi * j / 5) for j in range(5)]
sheet.wash(discs_density(W, H, px, py, [4 * rs] * 5, [1.0] * 5, sigma=0.8 * rs), 'coral')
ring = np.zeros((H, W), np.float32)
for x_, y_ in zip(px, py):
    im = Image.new('F', (W, H), 0.0); ImageDraw.Draw(im).ellipse([x_ - 13 * rs, y_ - 13 * rs, x_ + 13 * rs, y_ + 13 * rs], outline=1.0, width=int(round(1.4 * rs)))
    ring += np.asarray(im, np.float32)
sheet.wash(gaussian_filter(ring, 0.5 * rs) * 0.9, 'coral')
sheet.caption_strip(0.915, 0.985, 0.5)
title = 'A Fraction of a Fraction'
sub = ('Ramanujan\'s continued fraction 1/(1+q/(1+q²/(1+q³/…))) drawn on the disc of q^(1/5), rings of the disc spaced by decades of 1−|q|: pigment by its argument, tone by its size, '
       'hairlines at |R| = φ^(k/2+1/4). The five coral points are where it equals √((5+√5)/2) − φ, the value Hardy could not believe.')
lines = wrap(sub, 19 * rs, 'italic', 0.86 * W)
items = [(title, W / 2, 0.935 * H, 40 * rs, 'serif_bold', 'mm')] + [(ln, W / 2, (0.960 + 0.017 * i) * H, 19 * rs, 'italic', 'mm') for i, ln in enumerate(lines)]
sheet.wash(text_density(W, H, items), 'ink')
img = sheet.develop()
out = f'cache/rr_{FINAL}.png' if FINAL < 2048 else f'fraction_{FINAL}.png'
finish(img, (FINAL, FINAL), out)
