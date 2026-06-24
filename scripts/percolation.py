#!/usr/bin/env python3
"""03 — Emergence.
Critical site percolation. Every cell is occupied independently with
probability p; nothing in the rule says 'connect'. Yet at p_c = 0.5927 a single
cluster suddenly spans the whole lattice -- a global, fractal whole with no
global cause. Clusters are found by connected-component labelling and coloured
by size; the spanning cluster blazes.

mode 'crit'  : uniform p = p_c.
mode 'grad'  : p ramps top->bottom across p_c, so the transition is spatial.
"""
import numpy as np
from scipy import ndimage
from PIL import Image
import sys

L    = int(sys.argv[1]) if len(sys.argv) > 1 else 768
MODE = sys.argv[2] if len(sys.argv) > 2 else "crit"
OUT  = sys.argv[3] if len(sys.argv) > 3 else "out/percolation_proto.png"
SEED = int(sys.argv[4]) if len(sys.argv) > 4 else 7
PC   = 0.592746

rng = np.random.default_rng(SEED)
u = rng.random((L, L))
if MODE == "crit":
    occ = u < PC
else:
    pcol = np.linspace(0.45, 0.74, L)[:, None]   # p increases down the rows
    occ = u < pcol

lbl, n = ndimage.label(occ, structure=np.array([[0,1,0],[1,1,1],[0,1,0]]))
sizes = np.bincount(lbl.ravel())
sizes[0] = 0
print(f"{n} clusters, biggest {sizes.max()} cells", flush=True)

# does the biggest cluster span (touch both top & bottom or both sides)?
giant = int(sizes.argmax())

# colour table per label
logmax = np.log10(max(sizes.max(), 2))
col = np.zeros((n + 1, 3), np.float64)
# cool palette by log-size for finite clusters
COOL = np.array([(20,40,90),(40,110,170),(70,180,200),(150,225,205)], float)
def cool(t):
    t = np.clip(t, 0, 1) * (len(COOL) - 1)
    i = int(t); f = t - i
    j = min(i + 1, len(COOL) - 1)
    return COOL[i] * (1 - f) + COOL[j] * f
for lab in range(1, n + 1):
    s = sizes[lab]
    if s == 0:
        continue
    t = np.log10(s) / logmax
    col[lab] = cool(t)
# spanning / giant cluster blazes warm
col[giant] = np.array([255, 196, 96], float)

rgb = col[lbl]                       # (L,L,3)
rgb[~occ] = np.array([6, 7, 11])     # empty = near-black

# bloom: the spanning cluster blazes with a soft halo (emergence made luminous)
giant_mask = (lbl == giant).astype(np.float32)
halo = ndimage.gaussian_filter(giant_mask, sigma=max(1.0, L/700.0))
halo = (halo / halo.max()) ** 1.3
rgb += halo[..., None] * np.array([120, 70, 18], np.float32)   # warm glow added
# filmic-ish bounded lift so nothing clips harshly
rgb = 255.0 * (1.0 - np.exp(-rgb / 200.0))

img = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8))
img.save(OUT)
print("saved", OUT, flush=True)
