"""
Weyl's Field -- Polynomial Equidistribution as Interfering Tides  (512x512)
===========================================================================
Inspired by the MathOverflow questions on irrational torus rotations and the
density of good approximations.

Weyl proved that not only {n*alpha} but the POLYNOMIAL orbit {n^2 * alpha}
equidistributes mod 1 for irrational alpha. Read radially, the sequence
{ r^2 * alpha mod 1 } paints concentric bands around a centre -- the bright
rings sitting where r^2*alpha is a near-integer, i.e. where r^2 well
approximates a multiple of 1/alpha. Two such centres, tuned to two different
irrationals, interfere into a MOIRE tide: the visual signature of how two
equidistributing sequences fall in and out of phase.
"""
import numpy as np
from PIL import Image

N = 512
phi = (np.sqrt(5) - 1) / 2          # golden
psi = np.sqrt(2) - 1               # silver-ish, second irrational

yy, xx = np.mgrid[0:N, 0:N].astype(np.float64)

# two centres, two ring systems
c1 = np.array([0.36 * N, 0.42 * N])
c2 = np.array([0.66 * N, 0.62 * N])
r1 = ((xx - c1[0]) ** 2 + (yy - c1[1]) ** 2)
r2 = ((xx - c2[0]) ** 2 + (yy - c2[1]) ** 2)


def near_int(t):
    f = t - np.floor(t)
    return np.minimum(f, 1.0 - f)


# scale r^2 so a comfortable number of rings fit the frame
s1 = near_int(r1 * phi * 6.0e-4)
s2 = near_int(r2 * psi * 6.0e-4)
ring1 = (1.0 - s1 / 0.5) ** 5.0
ring2 = (1.0 - s2 / 0.5) ** 5.0

# luminance: each ring system glows, and their PRODUCT lights the moire nodes
lum = 0.55 * ring1 + 0.55 * ring2 + 1.2 * ring1 * ring2
lum = np.clip(lum, 0, 1.6)

# colour: which tide dominates locally, plus a slow angular drift
dom = (ring1 - ring2)
ang = 2 * np.pi * (0.5 + 0.45 * dom + 0.10 * np.arctan2(yy - N / 2, xx - N / 2) / np.pi)

R = lum * (0.55 + 0.45 * np.cos(ang))
G = lum * (0.55 + 0.45 * np.cos(ang - 2.094))
B = lum * (0.55 + 0.45 * np.cos(ang + 2.094))

# deep-sea base so gaps glow faintly instead of dying to black
base = 0.04 + 0.05 * (0.5 + 0.5 * np.cos(2 * np.pi * (r1 + r2) * 3.0e-4))
img = np.stack([R, G, B], -1) + base[..., None] * np.array([0.10, 0.20, 0.55])

img = 1.0 - np.exp(-1.8 * img)
img = np.clip(img, 0, 1) ** (1 / 1.7)

out = (img * 255 + 0.5).astype(np.uint8)
Image.fromarray(out, "RGB").save("out/02_weyl_field.png")
print("wrote out/02_weyl_field.png")
