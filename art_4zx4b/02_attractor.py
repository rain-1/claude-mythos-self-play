"""
02 — THE VEIL A SINGLE ORBIT WEAVES
================================================================
A de Jong map,
        x' = sin(a y) - cos(b x),     y' = sin(c x) - cos(d y),
with (a,b,c,d) = (1.4, -2.3, 2.4, -2.1). It is fully deterministic and has no
attracting fixed point; a single starting dot, iterated forever, never repeats
and never escapes -- it wanders a strange attractor, and the fraction of its
life it spends near each spot is that point's INVARIANT MEASURE. We run a third
of a billion iterations (many orbits in lockstep) and let brightness BE that
measure: the veil is not drawn, it is where the orbit chooses to live. The
sharp bright seams are caustics of the dynamics -- folds where the map creases
phase space onto itself -- the same fold catastrophe that lights a pool floor,
here made by a rule instead of by water.
"""
import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image

a, b, c, d = 1.4, -2.3, 2.4, -2.1
W = 2048
K = 260000; T = 1500; BURN = 200
rng = np.random.default_rng(7)
x = rng.uniform(-2, 2, K); y = rng.uniform(-2, 2, K)
H = np.zeros((W, W), np.float64)
lo, hi = -2.15, 2.15
print("iterating...")
for t in range(T):
    xn = np.sin(a*y)-np.cos(b*x)
    yn = np.sin(c*x)-np.cos(d*y)
    x, y = xn, yn
    if t < BURN:
        continue
    px = ((x-lo)/(hi-lo)*(W-1)).astype(np.int32)
    py = ((y-lo)/(hi-lo)*(W-1)).astype(np.int32)
    m = (px >= 0)&(px < W)&(py >= 0)&(py < W)
    np.add.at(H, (py[m], px[m]), 1.0)
print(f"  {int(H.sum()):,} points landed")

H = gaussian_filter(H, 0.6)
l = np.log1p(H*0.7)
l /= np.percentile(l, 99.9)
l = np.clip(l, 0, 1)

# warm silk ramp: indigo -> rose -> amber -> gold -> white
stops = [(0.00, (0.05, 0.05, 0.13)),
         (0.22, (0.42, 0.13, 0.40)),
         (0.45, (0.85, 0.30, 0.34)),
         (0.66, (1.00, 0.62, 0.26)),
         (0.85, (1.00, 0.86, 0.52)),
         (1.00, (1.00, 0.98, 0.93))]
xs = np.array([s[0] for s in stops])
cols = np.array([s[1] for s in stops])
rgb = np.empty((W, W, 3))
for ch in range(3):
    rgb[..., ch] = np.interp(l, xs, cols[:, ch])
rgb *= l[..., None]**0.62                     # luminance falloff -> dark where sparse

# background: near-black with a faint warm central nebula
gy, gx = np.mgrid[0:W, 0:W]
neb = np.exp(-(((gx-W*0.5)**2+(gy-W*0.52)**2)/(W*0.55)**2))
bg = np.array([0.015, 0.012, 0.030])[None, None, :] + neb[..., None]*np.array([0.03, 0.015, 0.02])[None, None, :]
img = bg + rgb

# bloom the brightest strands
bright = np.clip(l-0.5, 0, None)
for sig, amp in ((W*0.0016, 0.6), (W*0.006, 0.4)):
    img += gaussian_filter(bright, sig)[..., None]*np.array([1.0, 0.82, 0.55])[None, None, :]*amp

img = 1-np.exp(-np.clip(img, 0, None)*1.6)
img = np.clip(img, 0, 1)**0.90
Image.fromarray((img*255).astype(np.uint8)).save(
    __file__.replace('02_attractor.py', '02_attractor.png'))
print("saved 02_attractor.png", W)
