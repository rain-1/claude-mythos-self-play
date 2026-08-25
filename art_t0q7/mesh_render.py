#!/usr/bin/env python3
"""Piece 3 (2560^2): THE LATTICE OF SETTLED DEBTS -- mesh game closed form.

Level sets of t = min(x+y, y+z, z+x, floor(s/2)) in the cube [0,N]^3:
each value v = hexagonal diagonal plate + three 45-degree walls, glued on
gold seams. Nested shells colored by v. Inset: exact t(x,y,9) table (the
poster's own picture, from our verified DP).
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont

SS = 2
W = H = 2560 * SS
rng = np.random.default_rng(42)

N = 44.0            # cube extent
VLIST = list(range(3, 40, 4))   # shell values
CAM = np.array([3.1*N, 2.05*N, 1.5*N])   # asymmetric view, pulled back
CTR = np.array([N*0.42, N*0.42, N*0.40])

def orthonormal_cam():
    f = CTR - CAM; f = f/np.linalg.norm(f)
    up = np.array([0.0, 0.0, 1.0])
    r = np.cross(f, up); r /= np.linalg.norm(r)
    u = np.cross(r, f)
    return f, r, u

F, R, U = orthonormal_cam()
FOV = 0.38

def project(P):
    """P: (m,3) -> screen xy in [0,1], depth"""
    Q = P - CAM
    z = Q @ F
    x = (Q @ R) / (z * FOV)
    y = (Q @ U) / (z * FOV)
    return x, y, z

buf = np.zeros((H, W, 3), np.float32)

def splat(P, color, amp, jitter=0.0):
    x, y, z = project(P)
    if jitter > 0:
        x = x + rng.normal(0, jitter, x.shape); y = y + rng.normal(0, jitter, y.shape)
    px = (0.5 + x * 0.98) * W
    py = (0.52 - y * 0.98) * H
    ok = (px >= 1) & (px < W-1) & (py >= 1) & (py < H-1) & (z > 1)
    px, py, z = px[ok], py[ok], z[ok]
    w = amp / (z / np.median(z) + 0.2)**2
    ix = np.floor(px).astype(np.int64); iy = np.floor(py).astype(np.int64)
    fx = px - ix; fy = py - iy
    for dy in (0, 1):
        for dx in (0, 1):
            wt = w * (fx if dx else 1-fx) * (fy if dy else 1-fy)
            idx = (iy+dy) * W + (ix+dx)
            for c in range(3):
                np.add.at(buf[..., c].reshape(-1), idx, wt * color[c])

def ramp(t):
    """0..1 -> deep teal -> cyan -> amber -> pale gold"""
    t = np.clip(t, 0, 1)
    stops = np.array([[0.06,0.16,0.30],[0.10,0.45,0.55],[0.85,0.60,0.20],[1.0,0.88,0.55]])
    pos = np.array([0.0, 0.38, 0.75, 1.0])
    c = np.empty(3)
    for k in range(3):
        c[k] = np.interp(t, pos, stops[:, k])
    return c

# ---------------- shells ----------------
DENS = 5200   # points per unit area (scaled)
for vi, v in enumerate(VLIST):
    tv = vi / (len(VLIST)-1)
    col = ramp(tv)
    depthfade = 0.35 + 0.65*tv
    # plate: s in [2v, 2v+1], all coords <= v; sample s-slab
    m = int(DENS * (v*v) / 18)
    if m > 100:
        # sample barycentric on triangle x+y+z=s, then reject max> v
        s = 2*v + rng.random(m)
        a = rng.random(m); b = rng.random(m)
        flip = a + b > 1; a[flip] = 1 - a[flip]; b[flip] = 1 - b[flip]
        x = s * a; y = s * b; z = s - x - y
        keep = (x <= v) & (y <= v) & (z <= v) & (z >= 0)
        P = np.stack([x[keep], y[keep], z[keep]], 1)
        splat(P, col*np.array([0.9, 0.95, 1.0]), 1.5*depthfade, jitter=0.0006)
    # walls: {x+y=v, z in [v, N]} and cyclic
    marea = int(DENS * v * (N - v) / 26)
    for axis in range(3):
        if marea < 60: continue
        aa = rng.random(marea) * v
        zz = v + rng.exponential(7.0, marea)
        zz = np.where(zz > N, v + rng.random(marea) * (N - v) * 0.15, zz)
        u1 = rng.random(marea)
        if axis == 0:  P = np.stack([aa, v-aa, zz], 1)
        elif axis == 1: P = np.stack([zz, aa, v-aa], 1)
        else:           P = np.stack([v-aa, zz, aa], 1)
        splat(P, col, 0.30*depthfade, jitter=0.0006)
    # gold seams: plate-wall glue edges {x+y=v, z=v} cyclic  + plate rim
    ms = 2600
    aa = np.linspace(0, v, ms)
    for axis in range(3):
        if axis == 0:  P = np.stack([aa, v-aa, np.full(ms, float(v))], 1)
        elif axis == 1: P = np.stack([np.full(ms, float(v)), aa, v-aa], 1)
        else:           P = np.stack([v-aa, np.full(ms, float(v)), aa], 1)
        splat(P, np.array([1.0, 0.83, 0.35]), 3.4*depthfade**1.5, jitter=0.0004)

# faint cube edges for grounding
for e in range(12):
    t = np.linspace(0, 1, 1200)
    corners = [(x, y, z) for x in (0, N) for y in (0, N) for z in (0, N)]
    edges = [(0,1),(0,2),(0,4),(1,3),(1,5),(2,3),(2,6),(3,7),(4,5),(4,6),(5,7),(6,7)]
    a, b = edges[e]
    A = np.array(corners[a], float); B = np.array(corners[b], float)
    P = A[None, :] + t[:, None] * (B - A)[None, :]
    splat(P, np.array([0.35, 0.45, 0.6]), 0.22)


print("splat done", buf.max(), flush=True)

# ---------------- post: bloom + tonemap ----------------
from scipy.ndimage import gaussian_filter, zoom as ndzoom

def wide_bloom(img, sigma, ds=6):
    small = img[::ds, ::ds]
    bl = gaussian_filter(small, (sigma/ds, sigma/ds, 0))
    return np.clip(ndzoom(bl, (ds, ds, 1), order=1)[:img.shape[0], :img.shape[1]], 0, None)

base = gaussian_filter(buf, (1.1*SS, 1.1*SS, 0))
lum = base.sum(2)
hi = np.clip(base - np.percentile(lum, 99.2)/3, 0, None)
glow = wide_bloom(hi, 26*SS)
img = base + 0.55*glow

k = 2.1 / max(np.percentile(img.sum(2), 99.5)/3, 1e-9)
img = 1 - np.exp(-k * img)
img = np.power(np.clip(img, 0, 1), 1/1.9)
img8 = np.clip(img*255 + rng.uniform(-1, 1, img.shape), 0, 255).astype(np.uint8)
out = Image.fromarray(img8).resize((2560, 2560), Image.LANCZOS)
out.save("mesh_main_nolabel.png")
print("main saved", flush=True)
