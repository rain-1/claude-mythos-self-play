"""
01 — THE FOLDING OF LIGHT     (hero, 4096^2)
================================================================
Parallel light falls through a gently wavy water surface and lands on the floor.
Where the surface is convex it focuses the rays; where the ray-map folds back on
itself the light piles up without bound along bright curves and pinches to
brilliant points. Those curves and points are not painted in — they are the
FOLD and CUSP catastrophes of Rene Thom's theory: the only two singularities a
smooth map of the plane can have that survive a small perturbation. Every dancing
net of light on the bottom of a swimming pool is a live catalogue of them.

Method: a smooth height field h(x,y) is built from a handful of wave octaves; a
vertical ray striking the surface is deflected by the slope (grad h) and travels
to the floor, landing at (x,y) + s*grad h. Millions of rays are gathered with
bilinear weights, so brightness IS the caustic density (unbounded at the folds).
Red, green and blue are refracted by slightly different amounts -- real
dispersion -- so the fold edges break into rainbow, exactly as they do in water.
"""
import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image

SEED = 3
rng = np.random.default_rng(SEED)
NW = 11
ks = rng.normal(0, 1, (NW, 2))
ks = ks/np.linalg.norm(ks, axis=1, keepdims=True)
freqs = rng.uniform(1.2, 3.0, (NW, 1)); freqs[-4:] = rng.uniform(3.5, 7.5, (4, 1))
ks = ks*freqs
amp = (1.0/np.linalg.norm(ks, axis=1))**1.25 * rng.uniform(0.6, 1.0, NW)
ph = rng.uniform(0, 2*np.pi, NW)

FLOOR = 4096
FS = 7000                    # surface samples per axis (gathered rays)
extent = 6.0
acc = np.zeros((FLOOR, FLOOR, 3), np.float32)
disp = (0.60*1.030, 0.60*1.0, 0.60*0.970)   # per-channel refraction (subtle dispersion)

def add_rays(Xc, Yc):
    # slope of h at these points
    gx = np.zeros_like(Xc); gy = np.zeros_like(Yc)
    for i in range(NW):
        a = amp[i]*np.cos(ks[i, 0]*Xc + ks[i, 1]*Yc + ph[i])
        gx += a*ks[i, 0]; gy += a*ks[i, 1]
    for chan, s in enumerate(disp):
        lx = Xc + s*gx; ly = Yc + s*gy
        px = (lx+extent)/(2*extent)*(FLOOR-1)
        py = (ly+extent)/(2*extent)*(FLOOR-1)
        ix = np.floor(px).astype(np.int32); iy = np.floor(py).astype(np.int32)
        fx = px-ix; fy = py-iy
        m = (ix >= 0)&(ix < FLOOR-1)&(iy >= 0)&(iy < FLOOR-1)
        ixm = ix[m]; iym = iy[m]; fxm = fx[m]; fym = fy[m]
        A = acc[..., chan]
        for ox in (0, 1):
            for oy in (0, 1):
                w = ((1-fxm) if ox == 0 else fxm)*((1-fym) if oy == 0 else fym)
                np.add.at(A, (iym+oy, ixm+ox), w.astype(np.float32))

import os
_cache = __file__.replace('01_caustics.py', '_acc.npy')
if os.path.exists(_cache):
    print("loading cached field...")
    acc = np.load(_cache)
else:
    u = np.linspace(-extent, extent, FS)
    print("casting rays...")
    CH = 500
    for r0 in range(0, FS, CH):
        ys = u[r0:r0+CH]
        Xc, Yc = np.meshgrid(u, ys)
        add_rays(Xc, Yc)
        if r0 % 2000 == 0:
            print(f"  {r0}/{FS}")
    np.save(_cache, acc)

# ---- tone + colour ----
print("tone-mapping...")
acc = gaussian_filter(acc, (0.6, 0.6, 0))
mean = acc.mean() + 1e-9
d = acc/mean                                 # 1 = average lighting; caustics >> 1
# per-channel log so a hint of dispersion survives; keep dark pools dark
lum = np.log1p(np.clip(d-0.32, 0, None)*2.1)
lum /= np.percentile(lum, 99.6)
lum = np.clip(lum, 0, 1)
g = lum.mean(-1)                              # achromatic caustic strength 0..1
fringe = (lum - g[..., None])                 # tiny chromatic residual (rainbow edges)

# caustic colour ramp: dim webs teal -> mid gold -> hot folds white
def ramp(t):
    teal = np.array([0.20, 0.62, 0.95]); gold = np.array([1.0, 0.82, 0.42]); white = np.array([1.0, 0.99, 0.92])
    t = t[..., None]
    lowc = teal*(1-np.clip(t/0.45, 0, 1)) + gold*np.clip(t/0.45, 0, 1)
    hi = np.clip((t-0.55)/0.45, 0, 1)
    return lowc*(1-hi) + white*hi
caus = ramp(g)*g[..., None]

gy2, gx2 = np.mgrid[0:FLOOR, 0:FLOOR]
depth = gy2/FLOOR
water = (np.array([0.010, 0.045, 0.075])[None, None, :]*(1-0.5*depth[..., None])
         + np.array([0.0, 0.018, 0.045])[None, None, :]*depth[..., None])
out = water*(0.5+0.5*(1-g[..., None])) + caus + fringe*0.45
light = 0.80+0.42*np.exp(-(((gx2-FLOOR*0.30)**2+(gy2-FLOOR*0.28)**2)/(FLOOR*0.72)**2))
out *= light[..., None]
# a soft bloom of the very brightest folds
bright = np.clip(g-0.62, 0, None)
bl = gaussian_filter(bright, FLOOR*0.004)
out += bl[..., None]*np.array([1.0, 0.9, 0.7])[None, None, :]*0.9
out = 1-np.exp(-np.clip(out, 0, None)*1.75)
out = np.clip(out, 0, 1)**0.92
Image.fromarray((out*255).astype(np.uint8)).save(
    __file__.replace('01_caustics.py', '01_caustics.png'))
print("saved 01_caustics.png", FLOOR)
