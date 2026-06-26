#!/usr/bin/env python3
"""
02 — The Presence of Absence
The Eisenstein integers a + b*omega (omega = e^{2*pi*i/3}) form a triangular
lattice in C with 6-fold symmetry. We plot the PRIMES among them. An Eisenstein
integer is prime iff its norm N = a^2 - a*b + b^2 is a rational prime (the split
primes p = 1 mod 3 and the ramified 3), or N = p^2 with p = 2 mod 3 (inert).

Rendered so the eye reads the piece through its VOIDS: crisp prime glints on
near-black, the dark 6-fold corridors between them framed by a faint density
bloom. Presence arranged so that absence is the figure. (philosophy.SE:
"the difference between the absence of presence and the presence of absence".)
"""
import sys, numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

S   = int(sys.argv[1]) if len(sys.argv) > 1 else 512
OUT = sys.argv[2] if len(sys.argv) > 2 else "02_presence_of_absence.png"
SS  = 2
R   = int(sys.argv[3]) if len(sys.argv) > 3 else 88    # lattice radius (zoomed)
N   = S * SS

# --- lattice & norms ------------------------------------------------------
a = np.arange(-R, R + 1)
A, B = np.meshgrid(a, a)
norm = (A*A - A*B + B*B).astype(np.int64)        # Eisenstein norm form

# --- primality of norms via a sieve --------------------------------------
maxn = int(norm.max())
sieve = np.ones(maxn + 1, bool); sieve[:2] = False
for i in range(2, int(maxn**0.5) + 1):
    if sieve[i]:
        sieve[i*i::i] = False
is_p = sieve                                      # is_p[n] : n is a rational prime

isprime_norm = np.zeros_like(norm, bool)
flat = norm.ravel()
valid = flat > 1
isprime_norm.ravel()[valid] = is_p[flat[valid]]

# inert case: norm == p^2 with p = 2 mod 3
root = np.round(np.sqrt(norm.astype(np.float64))).astype(np.int64)
is_sq = (root*root == norm) & (root > 1)
root_c = np.clip(root, 0, maxn)
inert = is_sq & is_p[root_c] & (root_c % 3 == 2)

eis_prime = isprime_norm | inert
eis_prime &= (norm > 1)

# --- map every lattice point to the plane (omega embedding) ---------------
extent = R * 0.90
scale  = (N*0.5) / extent
allx = (A - 0.5*B).astype(np.float64)
ally = (np.sqrt(3.0)/2.0) * B.astype(np.float64)
inframe = (allx*allx + ally*ally) < extent*extent

def to_px(mx, my):
    ii = np.clip(np.round(mx*scale + N*0.5).astype(int), 0, N-1)
    jj = np.clip(np.round(my*scale + N*0.5).astype(int), 0, N-1)
    return ii, jj

# (1) the dim GROUND: every Eisenstein integer is a faint node. Where a prime
#     is absent, this faint node is all that remains -> the visible absence.
gi, gj = to_px(allx[inframe], ally[inframe])
ground = np.zeros((N, N), np.float32)
np.add.at(ground, (gj, gi), 1.0)

# (2) the PRIMES, bright, coloured by norm (small=warm near origin, large=cool)
pm = eis_prime & inframe
px, py, nn = allx[pm], ally[pm], norm[pm].astype(np.float64)
print(f"R={R}  primes {int(pm.sum())} of {int(inframe.sum())} sites  max norm {maxn}")
pi, pj = to_px(px, py)
t = np.clip(np.log(nn) / np.log(3.0*extent*extent), 0, 1)
cstops = np.array([
    [255, 240, 200], [255, 196, 104], [242, 132, 74],
    [150, 150, 230], [150, 205, 255], [205, 232, 255],
], np.float32)
def ramp(u):
    u = np.clip(u, 0, 1)*(len(cstops)-1)
    i0 = np.clip(np.floor(u).astype(int), 0, len(cstops)-2); f = (u-i0)[:, None]
    return cstops[i0]*(1-f)+cstops[i0+1]*f
pcol = ramp(t)
prime_acc = np.zeros((N, N, 3), np.float32)
np.add.at(prime_acc, (pj, pi), pcol)

# splat both fields into round dots; dot radius tracks lattice spacing.
# restore peak amplitude after the blur (gaussian_filter conserves total mass)
spacing = scale
sig_g = max(0.9, spacing*0.16)
sig_p = max(0.9, spacing*0.22)
ground_dot = gaussian_filter(ground, sigma=sig_g) * (2*np.pi*sig_g**2)
prime_dot  = gaussian_filter(prime_acc, sigma=sig_p) * (2*np.pi*sig_p**2)

img = np.zeros((N, N, 3), np.float32)
img += ground_dot[..., None] * np.array([22, 26, 40], np.float32)/255.0  # ash nodes
img += prime_dot * 1.7                                                  # bright primes

# faint density nebula so prime-rich zones glow, voids stay black
bloom = gaussian_filter(prime_acc.sum(axis=2), sigma=spacing*1.4)
bloom /= (bloom.max() + 1e-9)
img += (bloom[..., None]**1.5) * np.array([20, 26, 56], np.float32) * 1.1

# warm halo around the origin: 0 is not prime, ringed by the six units -- the
# most pointed absence in the field gets the warmest glow (presence of absence)
yy0, xx0 = np.mgrid[0:N, 0:N]
rr0 = np.hypot(xx0 - N/2, yy0 - N/2)
core_halo = np.exp(-(rr0/(spacing*2.6))**2) - np.exp(-(rr0/(spacing*0.9))**2)
core_halo = np.clip(core_halo, 0, 1)
img += core_halo[..., None] * np.array([90, 60, 26], np.float32)

# --- tone -----------------------------------------------------------------
k = 165.0
img = 255.0*(1.0 - np.exp(-img/k))
yy, xx = np.mgrid[0:N, 0:N]
rr = np.hypot(xx - N/2, yy - N/2) / (N/2)
img *= (1.0 - 0.45*np.clip(rr-0.5, 0, 1)**2)[..., None]
img = np.clip(img, 0, 255).astype(np.uint8)

im = Image.fromarray(img, "RGB")
if SS > 1:
    im = im.resize((S, S), Image.LANCZOS)
im.save(OUT)
print("saved", OUT, im.size)
