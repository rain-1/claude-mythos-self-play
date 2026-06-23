"""
Diffractive Geodesic  (4096 x 4096)  --  the FANCY showcase
===========================================================
Inspired by the MathOverflow question:
  "Expression for the half-wave propagator e^{it sqrt(-Delta)} microlocalized
   along a geometrically diffractive geodesic."

We launch a coherent bundle of wavelets along a curved geodesic gamma(t) -- a
clothoid-like spiral whose curvature varies smoothly. Each wavelet carries the
tangent wavevector of the geodesic (an obliquity factor microlocalizes the
energy in the forward direction) and a Gaussian arc-length envelope. The total
field is the diffraction integral

        U(x,y) = SUM_t  w(t) * obliquity * exp(i k r) / sqrt(r)

Where the rays' normals envelope, the stationary phase piles up and a CAUSTIC
ignites -- the bright cusped curve that is the evolute of the geodesic. The
chromatic fringes are the phase arg(U) made visible. |U|^2 is the intensity.

Computed in row-tiles, float32, accumulating over sources to stay in memory.
"""
import numpy as np
from PIL import Image
import time

S = 4096                      # image size
NSRC = 720                    # wavelets along the geodesic
K = 0.92                      # wavenumber (fringe density)
t0 = time.time()

# --- the geodesic: a clothoid-like spiral in [0,1]^2 ------------------------
t = np.linspace(0.0, 1.0, NSRC)
# arc parameter with smoothly increasing curvature -> Euler-spiral character
theta = 2.0 * np.pi * (0.15 + 1.65 * t * t)          # turning angle
rad = 0.10 + 0.34 * t                                 # growing radius
gx = (0.46 + rad * np.cos(theta)) * S                 # source x (pixels)
gy = (0.52 + rad * np.sin(theta)) * S                 # source y
# tangent direction (for the obliquity / microlocalization)
tx = np.gradient(gx); ty = np.gradient(gy)
tn = np.hypot(tx, ty) + 1e-9
tx, ty = tx / tn, ty / tn
# normal direction
nx, ny = -ty, tx
# Gaussian arc-length envelope (energy concentrated mid-geodesic) + a phase
# ramp so the packet actually propagates along gamma
env = np.exp(-((t - 0.5) ** 2) / (2 * 0.34 ** 2)).astype(np.float32)
src_phase = (K * np.cumsum(tn)).astype(np.float32)    # accumulated optical path

gx = gx.astype(np.float32); gy = gy.astype(np.float32)
nx = nx.astype(np.float32); ny = ny.astype(np.float32)
env = env.astype(np.float32); src_phase = src_phase.astype(np.float32)

# --- accumulate the field in row tiles --------------------------------------
re = np.zeros((S, S), np.float32)
im = np.zeros((S, S), np.float32)
xs = np.arange(S, dtype=np.float32)
TILE = 128
for y0 in range(0, S, TILE):
    y1 = min(S, y0 + TILE)
    Y, X = np.mgrid[y0:y1, 0:S].astype(np.float32)
    accr = np.zeros_like(X)
    acci = np.zeros_like(X)
    for s in range(NSRC):
        dx = X - gx[s]
        dy = Y - gy[s]
        r = np.sqrt(dx * dx + dy * dy) + 8.0
        # obliquity: forward emission along +normal of the geodesic
        ob = (dx * nx[s] + dy * ny[s]) / r
        ob = np.clip(ob, 0.0, None) ** 1.5
        amp = (env[s] * ob) / np.sqrt(r)
        ph = K * r + src_phase[s]
        accr += amp * np.cos(ph)
        acci += amp * np.sin(ph)
    re[y0:y1] = accr
    im[y0:y1] = acci
    if (y0 // TILE) % 8 == 0:
        print(f"  rows {y0:4d}/{S}   t={time.time()-t0:5.1f}s")

inten = re * re + im * im                  # |U|^2
phase = np.arctan2(im, re)                 # arg(U), for chromatic fringes

# cache the raw field so the colour map can be tuned without re-solving
np.save("out/_geo_inten.npy", inten.astype(np.float32))
np.save("out/_geo_phase.npy", phase.astype(np.float32))
print(f"  field solved & cached  t={time.time()-t0:.1f}s")

# --- tone & colour ----------------------------------------------------------
I = inten / np.percentile(inten, 99.85)
I = np.clip(I, 0, 1)
I = I ** 0.42                              # lift the faint diffraction fringes

# iridescent caustic palette: hue from phase, value from intensity, with a
# deep indigo floor and gold/white at the caustic crest.
hue = (phase + np.pi) / (2 * np.pi)        # 0..1
a = 2 * np.pi * (hue + 0.08 * I)
warm = np.stack([                          # phase-tinted iridescence
    0.5 + 0.5 * np.cos(a),
    0.5 + 0.5 * np.cos(a - 2.094),
    0.5 + 0.5 * np.cos(a + 2.094),
], -1)

floor = np.array([0.02, 0.03, 0.07], np.float32)         # indigo void
crest = np.array([1.00, 0.86, 0.55], np.float32)         # gold caustic crest
Ie = I[..., None]
# blend: void -> iridescent body -> gold crest as intensity rises
body = floor[None, None, :] * (1 - Ie) + warm * (0.35 + 0.65 * Ie) * Ie
img = body + crest[None, None, :] * (np.clip(I - 0.72, 0, 1)[..., None] ** 1.6) * 1.4

img = 1.0 - np.exp(-1.5 * img)
img = np.clip(img, 0, 1) ** (1 / 1.8)

out = (img * 255 + 0.5).astype(np.uint8)
Image.fromarray(out, "RGB").save("out/05_diffractive_geodesic_4096.png", optimize=True)
print(f"wrote out/05_diffractive_geodesic_4096.png  in {time.time()-t0:.1f}s")

# also a 768px preview for quick viewing
Image.fromarray(out, "RGB").resize((768, 768), Image.LANCZOS).save(
    "out/05_diffractive_geodesic_preview.png")
print("wrote out/05_diffractive_geodesic_preview.png")
