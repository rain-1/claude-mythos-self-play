#!/usr/bin/env python3
"""Piece 2 (2560^2): THE UNBREAKABLE FLOOR -- MO 514626.

Field: 4M generalized eigenvalues of pencils (A, PAP^T), n=10, in the chart
(log10|mu|, arg mu). Gold fences at +-60 deg (sharp cone conjecture),
half-reversal comets riding to the fence, the floor star at the origin.
Inset: n=10 exhaustive det/floor spectrum skyline.
"""
import numpy as np, json
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter
from scipy.linalg import eig
from annot import annotate, fonts

SS = 2
W = H = 2560 * SS
rng = np.random.default_rng(1)

XR = (-2.35, 2.35)     # log10 |mu|
THMAX = 67.0           # degrees; power-warped axis
PW = 0.40

def warp(th):
    return np.sign(th) * (np.abs(th)/THMAX)**PW

def to_px(lx, th):
    px = (lx - XR[0]) / (XR[1]-XR[0]) * W
    py = (1 - warp(th)) * 0.5 * H
    return px, py

z = np.load("manh_rain.npz")
mus = z["mus"].ravel()
isC = np.abs(mus.imag) > 1e-9
lx = np.log10(np.abs(mus))
th = np.degrees(np.angle(mus))
ok = (lx > XR[0]) & (lx < XR[1]) & (np.abs(th) < THMAX) & isC
lxc, thc = lx[ok], th[ok]
px, py = to_px(lxc, thc)
Hst, _, _ = np.histogram2d(py, px, bins=(H, W), range=((0, H), (0, W)))
# real-eigenvalue river: 1-D density -> symmetric thickness around theta=0
okr = (~isC) & (lx > XR[0]) & (lx < XR[1]) & (mus.real > 0)
hr, edges = np.histogram(lx[okr], bins=W, range=XR)
dens = gaussian_filter(hr.astype(np.float32), 3.0*SS)
dens /= dens.max()
thick = (dens ** 0.55) * 0.055 * H          # max half-width ~5.5% of H
ygrid2 = np.abs(np.arange(H)[:, None] - H/2)
river = np.clip(1 - ygrid2 / np.maximum(thick[None, :], 1e-6), 0, 1) ** 1.6
river *= dens[None, :] ** 0.25
print("hist done", Hst.max(), Hst.sum())

# base density colorize: log-equalized cyan-ice
h = gaussian_filter(Hst.astype(np.float32), 1.2*SS)
t = np.log1p(h) / np.log1p(np.percentile(h[h > 0], 99.92))
t = np.clip(t, 0, 1) ** 0.85
# wing region: |warped y - center| > band -> own normalization
ygrid = np.abs(np.arange(H) - H/2) / (H/2)
wingmask = np.clip((ygrid - 0.16) / 0.1, 0, 1)[:, None].astype(np.float32)
hw = h * (wingmask > 0)
if hw.max() > 0:
    tw = np.log1p(h) / np.log1p(max(np.percentile(hw[hw > 0], 99.5), 4))
    t = np.maximum(t, np.clip(tw, 0, 1)**0.85 * wingmask * 0.9)
stops = np.array([[0.015,0.025,0.06],[0.05,0.16,0.30],[0.15,0.45,0.62],
                  [0.65,0.90,0.97],[1.0,1.0,1.0]])
pos = np.array([0.0, 0.3, 0.6, 0.87, 1.0])
img = np.zeros((H, W, 3), np.float32)
for c in range(3):
    img[..., c] = np.interp(t, pos, stops[:, c])
img *= (0.15 + 0.85 * t[..., None])
rivercol = np.array([0.55, 0.85, 0.95], np.float32)
img += river[..., None] * rivercol[None, None, :] * 1.15

# ---- overlays buffer (additive) ----
ov = np.zeros((H, W, 3), np.float32)
def splat_pts(pxs, pys, color, amp, rad):
    okm = (pxs >= rad+1) & (pxs < W-rad-1) & (pys >= rad+1) & (pys < H-rad-1)
    pxs, pys = pxs[okm], pys[okm]
    for x0, y0 in zip(pxs, pys):
        x0i, y0i = int(x0), int(y0)
        s = int(3*rad)
        yy, xx = np.mgrid[y0i-s:y0i+s+1, x0i-s:x0i+s+1]
        g = np.exp(-((xx-x0)**2 + (yy-y0)**2) / rad**2)
        for c in range(3):
            ov[yy, xx, c] += amp * g * color[c]

# half-reversal comets, n = 10..256
def halfrev(n):
    h = n // 2
    return np.concatenate([np.arange(h)[::-1], np.arange(h, n)[::-1]])
gold = np.array([1.0, 0.80, 0.30])
for n in (10, 12, 16, 24, 32, 48, 64, 96, 128, 192, 256):
    A = np.abs(np.subtract.outer(np.arange(n), np.arange(n))).astype(float)
    p = halfrev(n)
    B = np.abs(np.subtract.outer(p, p)).astype(float)
    mu = eig(A, B, right=False)
    lxx = np.log10(np.abs(mu)); thh = np.degrees(np.angle(mu))
    pxs, pys = to_px(lxx, thh)
    splat_pts(pxs, pys, gold, 1.15, 2.6*SS)

# the floor star: identity, all mu = 1 -> origin of chart
fx, fy = to_px(np.array([0.0]), np.array([0.0]))
yy, xx = np.mgrid[0:H, 0:W]
r2 = (xx - fx[0])**2 + (yy - fy[0])**2
star = np.exp(-r2 / (26*SS)**2) * 2.6 + np.exp(-r2 / (7*SS)**2) * 8.0
for c, g in enumerate([1.0, 0.88, 0.55]):
    ov[..., c] += star * g
del r2, xx, yy

# gold fences at +-60 degrees
for fence in (60.0, -60.0):
    _, fyv = to_px(np.array([0.0]), np.array([fence]))
    yline = int(fyv[0])
    band = np.zeros((H, 1), np.float32)
    ygrid = np.arange(H)[:, None].astype(np.float32)
    band = np.exp(-((ygrid - yline)**2) / (1.6*SS)**2) * 1.9
    for c, g in enumerate([1.0, 0.78, 0.28]):
        ov[..., c] += band * g

img = img + gaussian_filter(ov, (1.0*SS, 1.0*SS, 0))
# bloom on hot spots
lum = img.sum(2)
hi = np.clip(img - np.percentile(lum, 99.7)/3, 0, None)
small = hi[::6, ::6]
bl = gaussian_filter(small, (24/6, 24/6, 0))
from scipy.ndimage import zoom as ndzoom
glow = np.clip(ndzoom(bl, (6, 6, 1), order=1)[:H, :W], 0, None)
img = img + 0.6 * glow
img = 1 - np.exp(-1.25 * img)
img = np.power(np.clip(img, 0, 1), 1/1.9)
img8 = np.clip(img*255 + rng.uniform(-1, 1, img.shape), 0, 255).astype(np.uint8)
out = Image.fromarray(img8).resize((2560, 2560), Image.LANCZOS)
out.save("manh_main_nolabel.png")
print("main saved")
