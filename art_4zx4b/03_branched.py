"""
03 — BRANCHES IN A DISORDERED SEA
================================================================
Send a wide, perfectly parallel sheet of particles (or a wavefront) into a weak,
smoothly random landscape -- a potential with gentle hills and hollows no deeper
than a ripple. You might expect them to spread evenly. They do the opposite:
tiny deflections accumulate and the flux collapses onto a few brilliant, forking
channels -- BRANCHED FLOW. The bright filaments are caustics again, the same fold
singularities as pieces 01 and 02, but now grown by DISORDER rather than by a
lens or a map. The pattern is universal: it steers electrons through
semiconductors, sound through the ocean, light through soap films, and (in the
tail of the distribution) rogue waves out of a calm sea.

Method: rays obey d^2r/dt^2 = -grad V through a Gaussian-correlated random field
V; their accumulated density is the image. The first branch points form at a
distance set only by the disorder's strength and correlation length -- not by
where any single hill happens to sit.
"""
import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image

SEED = 2
W = 2048
eps = 0.014; ell = 24
NR = W*10
steps = 2700
rng = np.random.default_rng(SEED)
V = gaussian_filter(rng.standard_normal((W, W)), ell); V /= V.std(); V *= eps
gyv, gxv = np.gradient(V)

x = np.linspace(2, W-2, NR).astype(np.float64); y = np.full(NR, 2.0)
vx = np.zeros(NR); vy = np.ones(NR)
H = np.zeros((W, W)); dt = 1.0
print("propagating rays...")
for s in range(steps):
    ix = np.clip(x.astype(int), 0, W-1); iy = np.clip(y.astype(int), 0, W-1)
    vx -= gxv[iy, ix]*dt; vy -= gyv[iy, ix]*dt
    x += vx*dt; y += vy*dt
    m = (x >= 0)&(x < W)&(y >= 0)&(y < W)
    np.add.at(H, (y[m].astype(int), x[m].astype(int)), 1.0)

# branches = excess density over the smooth flux
H = gaussian_filter(H, 0.7)
base = gaussian_filter(H, 34)
exc = np.clip(H-0.85*base, 0, None)
l = np.log1p(exc*1.5); l /= np.percentile(l, 99.6); l = np.clip(l, 0, 1)
# fade the uniform launch edge (y~0) BEFORE colour/bloom so no ring artifacts
yfade = np.clip((np.arange(W)/W - 0.015)/0.17, 0, 1)[:, None]
l *= (0.05+0.95*yfade)

# electric palette: deep blue -> cyan -> white
stops = [(0.00, (0.010, 0.020, 0.055)),
         (0.32, (0.03, 0.17, 0.50)),
         (0.60, (0.12, 0.58, 1.00)),
         (0.82, (0.55, 0.90, 1.00)),
         (1.00, (1.00, 1.00, 1.00))]
xs = np.array([s[0] for s in stops]); cols = np.array([s[1] for s in stops])
rgb = np.stack([np.interp(l, xs, cols[:, c]) for c in range(3)], -1)
rgb += np.array([0.012, 0.022, 0.05])[None, None, :]           # deep-sea base

# bloom the bright caustic cores
bright = np.clip(l-0.5, 0, None)
for sig, amp in ((W*0.0016, 0.6), (W*0.007, 0.35)):
    rgb += gaussian_filter(bright, sig)[..., None]*np.array([0.6, 0.85, 1.0])[None, None, :]*amp

rgb = 1-np.exp(-np.clip(rgb, 0, None)*1.8)
rgb = np.clip(rgb, 0, 1)**0.9
Image.fromarray((rgb*255).astype(np.uint8)[::-1]).save(          # flip: launch at bottom
    __file__.replace('03_branched.py', '03_branched.png'))
print("saved 03_branched.png", W)
