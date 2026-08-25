#!/usr/bin/env python3
"""Piece 3 v2: nested Grundy shells as glass panes converging to the golden origin."""
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, zoom as ndzoom

SS = 2
W = H = 2560 * SS
rng = np.random.default_rng(42)

N = 46.0
VLIST = list(range(3, 45, 5))       # 3,8,...,43
CAM = np.array([3.25*N, 1.5*N, 1.15*N])
CTR = np.array([N*0.40, N*0.40, N*0.36])

f = CTR - CAM; f /= np.linalg.norm(f)
up = np.array([0.0, 0.0, 1.0])
r = np.cross(f, up); r /= np.linalg.norm(r)
u = np.cross(r, f)
FOV = 0.40

buf = np.zeros((H, W, 3), np.float32)

def splat(P, color, amp, jitter=0.0):
    Q = P - CAM
    z = Q @ f
    x = (Q @ r) / (z * FOV); y = (Q @ u) / (z * FOV)
    if jitter > 0:
        x = x + rng.normal(0, jitter, x.shape); y = y + rng.normal(0, jitter, y.shape)
    px = (0.5 + x * 0.98) * W; py = (0.54 - y * 0.98) * H
    ok = (px >= 1) & (px < W-1) & (py >= 1) & (py < H-1) & (z > 1)
    px, py, z = px[ok], py[ok], z[ok]
    w = amp * (2.6*N / z)**2
    ix = np.floor(px).astype(np.int64); iy = np.floor(py).astype(np.int64)
    fx = px - ix; fy = py - iy
    for dy in (0, 1):
        for dx in (0, 1):
            wt = w * (fx if dx else 1-fx) * (fy if dy else 1-fy)
            idx = (iy+dy) * W + (ix+dx)
            for c in range(3):
                np.add.at(buf[..., c].reshape(-1), idx, wt * color[c])

def ramp(t):
    """t=0 (innermost, near nothing) -> white-gold ... t=1 (outer) -> deep indigo"""
    stops = np.array([[1.00,0.93,0.62],[1.00,0.72,0.28],[0.35,0.55,0.60],
                      [0.12,0.28,0.52],[0.05,0.10,0.28]])
    pos = np.array([0.0, 0.22, 0.55, 0.8, 1.0])
    return np.array([np.interp(t, pos, stops[:, k]) for k in range(3)])

nv = len(VLIST)
for vi, v in enumerate(VLIST):
    tv = vi / (nv - 1)
    col = ramp(tv)
    hot = (1 - tv)**1.6            # inner shells brighter
    # plate: medial triangle {x+y+z in [2v,2v+1], max<=v} -- dense, smooth
    m = int(60000 * max(v, 4)**2 / 100)
    s = 2*v + rng.random(m)
    a = rng.random(m); b = rng.random(m)
    flip = a + b > 1; a[flip] = 1-a[flip]; b[flip] = 1-b[flip]
    x = s*a; y = s*b; z = s - x - y
    keep = (x <= v) & (y <= v) & (z <= v) & (z >= 0)
    P = np.stack([x[keep], y[keep], z[keep]], 1)
    dens = m / max(v, 4)**2
    splat(P, col, (0.42 + 1.6*hot) / dens * 900, jitter=0.0004)
    # curtains: short fading walls below the three glue edges
    mc = 22000
    aa = rng.random(mc) * v
    drop = rng.exponential(2.6, mc)
    wgt = np.exp(-drop / 2.6)
    for axis in range(3):
        zz = v + drop
        if axis == 0:  P = np.stack([aa, v-aa, zz], 1)
        elif axis == 1: P = np.stack([zz, aa, v-aa], 1)
        else:           P = np.stack([v-aa, zz, aa], 1)
        keep = zz <= N
        splat(P[keep], col*0.8 + 0.2, 0.020*(0.4+hot), jitter=0.0005)
    # gold seam ring: the medial triangle's three edges (max = v)
    ms = 4200
    tt = np.linspace(0, 1, ms)
    for (Ap, Bp) in (((v,v,0),(v,0,v)), ((v,0,v),(0,v,v)), ((0,v,v),(v,v,0))):
        A = np.array(Ap, float); B = np.array(Bp, float)
        P = A[None] + tt[:, None]*(B-A)[None]
        seamcol = np.array([1.0, 0.85, 0.42])*(0.55+0.45*hot) + col*0.25
        splat(P, seamcol, 1.9*(0.35 + 0.85*hot), jitter=0.00035)

# origin star: the point of nothing
P = np.zeros((2400, 3)) + rng.normal(0, 0.26, (2400, 3))**2
splat(P, np.array([1.0, 0.95, 0.75]), 2.2, jitter=0.0012)

# faint axes rays from origin (the three trivial P-position lines t=0)
tt = np.linspace(0, N*1.02, 3000)
for axis in range(3):
    P = np.zeros((3000, 3)); P[:, axis] = tt
    for chunk in range(3):
        sl = slice(chunk*1000, (chunk+1)*1000)
        fade = 0.62*np.exp(-tt[sl].mean()/(0.55*N))
        splat(P[sl], np.array([0.55, 0.75, 0.85]), fade, jitter=0.0004)

print("splat done", buf.max(), flush=True)

def wide_bloom(img, sigma, ds=6):
    small = img[::ds, ::ds]
    bl = gaussian_filter(small, (sigma/ds, sigma/ds, 0))
    return np.clip(ndzoom(bl, (ds, ds, 1), order=1)[:img.shape[0], :img.shape[1]], 0, None)

base = gaussian_filter(buf, (1.35*SS, 1.35*SS, 0))
lum = base.sum(2)
thr = np.percentile(lum, 99.55) / 3
hi = np.clip(base - thr, 0, None)
glow = wide_bloom(hi, 30*SS)
img = base + 0.7*glow
k = 1.35 / max(np.percentile(img.sum(2), 99.8)/3, 1e-9)
img = 1 - np.exp(-k * img)
img = np.power(np.clip(img, 0, 1), 1/2.0)
img8 = np.clip(img*255 + rng.uniform(-1, 1, img.shape), 0, 255).astype(np.uint8)
Image.fromarray(img8).resize((2560, 2560), Image.LANCZOS).save("mesh_main_nolabel.png")
print("main saved", flush=True)
