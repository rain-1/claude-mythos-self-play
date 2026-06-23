"""
Almost Everywhere Dead  (512x512)
=================================
Inspired by the Philosophy SE question "Are we dead almost everywhere?"

The plane is DEAD on a set of full measure -- a dark, faintly textured
continuum. LIFE persists only on a measure-zero set that is nevertheless
DENSE: the rational lattice. Each star sits at a rational coordinate (p/q, p'/q')
and shines with brightness ~ 1/(q*q') in the spirit of Thomae's function
(nonzero exactly on the rationals, zero -- continuous -- on the irrationals).

The total area lit is zero. Yet the sky is full.
"""
import math
import numpy as np
from PIL import Image

W = H = 512
rng = np.random.default_rng(7)


def gcd(a, b):
    while b:
        a, b = b, a % b
    return a


# --- the dead continuum: a slow, dim value-noise gradient -------------------
yy, xx = np.mgrid[0:H, 0:W].astype(np.float64)
nx, ny = xx / W, yy / H

# smooth low-frequency field for the "void" -- deep blue-black with faint drift
void = (
    0.5 + 0.5 * np.sin(2.4 * nx + 1.3)
    + 0.3 * np.cos(3.1 * ny - 0.7)
    + 0.2 * np.sin(5.0 * (nx + ny))
)
void = (void - void.min()) / (void.max() - void.min())

img = np.zeros((H, W, 3), np.float64)
# base palette: near-black indigo deepening toward the corners (vignette).
# The void must read as genuinely dead -- almost no light of its own.
vign = 1.0 - 0.7 * ((nx - 0.5) ** 2 + (ny - 0.5) ** 2)
img[..., 0] = (0.006 + 0.010 * void) * vign      # R
img[..., 1] = (0.008 + 0.012 * void) * vign      # G
img[..., 2] = (0.020 + 0.022 * void) * vign      # B  (indigo bias)

# --- life on a measure-zero set: rationals with Thomae brightness -----------
# Two warm "life" colors we interpolate between by denominator parity.
life_a = np.array([1.00, 0.78, 0.32])   # gold
life_b = np.array([0.35, 0.95, 0.92])   # cyan

# The rationals in [0,1]^2 form a GRID (every rational x stacks over every
# rational y). Viewed through a fixed smooth, invertible warp of the torus the
# same measure-zero, dense set disperses into a star-scatter -- still exactly
# the image of the rationals, just seen in a curved chart. A tiny deterministic
# jitter (hashed from p,q) finishes off the residual collinearity.
def warp(u, v):
    x = (u + 0.50 * v + 0.18 * math.sin(2 * math.pi * (v + 0.3 * u))) % 1.0
    y = (v + 0.37 * u + 0.18 * math.cos(2 * math.pi * (u - 0.2 * v))) % 1.0
    return x, y


Qmax = 90
stars = []  # (x, y, weight, parity)
for q in range(1, Qmax + 1):
    for p in range(0, q + 1):
        if gcd(p, q) != 1:
            continue
        for q2 in range(1, Qmax + 1):
            if q * q2 > 360:        # bound so low-q (bright) life dominates
                continue
            for p2 in range(0, q2 + 1):
                if gcd(p2, q2) != 1:
                    continue
                w = 1.0 / (q * q2)
                x, y = warp(p / q, p2 / q2)
                hsh = ((p * 2654435761) ^ (q * 40503) ^ (p2 * 974711) ^ (q2 * 2246822519)) & 0xFFFF
                jit = (hsh / 65535.0 - 0.5)
                x = (x + 0.012 * jit) % 1.0
                y = (y + 0.012 * (((hsh >> 3) & 0xFFFF) / 65535.0 - 0.5)) % 1.0
                stars.append((x, y, w, (q + q2) % 2))

print(f"life points (measure zero, dense): {len(stars)}")

# splat each star as a small additive gaussian glow whose radius/intensity
# grow with its Thomae weight.
for (sx, sy, w, par) in stars:
    cx, cy = sx * (W - 1), sy * (H - 1)
    rad = 0.7 + 5.5 * w ** 0.75           # only the low-q stars grow large
    amp = 1.5 * w ** 0.80                 # sharp falloff -> stars, not bands
    x0, x1 = max(0, int(cx - 3 * rad)), min(W, int(cx + 3 * rad) + 1)
    y0, y1 = max(0, int(cy - 3 * rad)), min(H, int(cy + 3 * rad) + 1)
    if x1 <= x0 or y1 <= y0:
        continue
    gy, gx = np.mgrid[y0:y1, x0:x1].astype(np.float64)
    g = amp * np.exp(-((gx - cx) ** 2 + (gy - cy) ** 2) / (2 * rad ** 2))
    color = life_a if par == 0 else life_b
    for c in range(3):
        img[y0:y1, x0:x1, c] += g * color[c]

# --- tone mapping -----------------------------------------------------------
img = 1.0 - np.exp(-1.3 * img)            # filmic-ish exposure
img = np.clip(img, 0, 1) ** (1 / 1.6)     # gentle gamma; keep the void dark

out = (img * 255 + 0.5).astype(np.uint8)
Image.fromarray(out, "RGB").save("out/01_almost_everywhere.png")
print("wrote out/01_almost_everywhere.png")
