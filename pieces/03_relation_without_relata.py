"""
Relation Without Relata  (512x512)
==================================
Inspired by the Philosophy SE question "Can 'relation without relata' be
understood...".

A Voronoi tessellation is built from scattered seeds -- but then the SEEDS ARE
ERASED. We keep only the boundaries: the loci equidistant from the two nearest
generators (where the gap d2 - d1 collapses to zero). What remains is a glowing
web of pure BETWEEN. Every filament is a relation; nothing in the picture is a
relatum. Colour is the identity of the relating pair (a hash of the two nearest
seed indices), so the web sorts itself into communities of relation.
"""
import numpy as np
from PIL import Image

W = H = 512
rng = np.random.default_rng(11)

# --- scatter the (soon to be erased) generators -----------------------------
M = 130
seeds = rng.random((M, 2)) * [W, H]
# a gentle bias toward a spiral so the web has large-scale flow
theta = np.linspace(0, 6 * np.pi, M)
seeds[:, 0] = 0.6 * seeds[:, 0] + 0.4 * (W / 2 + theta * 11 * np.cos(theta))
seeds[:, 1] = 0.6 * seeds[:, 1] + 0.4 * (H / 2 + theta * 11 * np.sin(theta))
seeds = np.clip(seeds, 0, [W - 1, H - 1])

yy, xx = np.mgrid[0:H, 0:W].astype(np.float64)
P = np.stack([xx.ravel(), yy.ravel()], -1)          # (W*H, 2)

# distance to every seed, in tiles to keep memory modest
d1 = np.full(P.shape[0], 1e9)       # nearest distance
d2 = np.full(P.shape[0], 1e9)       # second-nearest distance
i1 = np.zeros(P.shape[0], np.int32)  # nearest index
i2 = np.zeros(P.shape[0], np.int32)  # second-nearest index

TILE = 65536
for s in range(0, P.shape[0], TILE):
    chunk = P[s:s + TILE]                            # (t,2)
    dd = np.sqrt(((chunk[:, None, :] - seeds[None, :, :]) ** 2).sum(-1))  # (t,M)
    order = np.argpartition(dd, 1, axis=1)[:, :2]
    near = np.take_along_axis(dd, order, axis=1)
    # ensure column 0 is the true nearest
    swap = near[:, 0] > near[:, 1]
    order[swap] = order[swap][:, ::-1]
    near[swap] = near[swap][:, ::-1]
    d1[s:s + TILE] = near[:, 0]
    d2[s:s + TILE] = near[:, 1]
    i1[s:s + TILE] = order[:, 0]
    i2[s:s + TILE] = order[:, 1]

gap = (d2 - d1).reshape(H, W)                        # 0 exactly on boundaries
# boundary intensity: bright where gap is small (the relation), dark in cells
edge = np.exp(-(gap / 2.6) ** 2)                     # crisp luminous filaments

# colour = identity of the relating PAIR (unordered), hashed to a hue
a = np.minimum(i1, i2).reshape(H, W)
b = np.maximum(i1, i2).reshape(H, W)
pair_hash = ((a * 73856093) ^ (b * 19349663)) % 9973
ang = 2 * np.pi * (pair_hash / 9973.0)

R = edge * (0.55 + 0.45 * np.cos(ang))
G = edge * (0.55 + 0.45 * np.cos(ang - 2.094))
B = edge * (0.55 + 0.45 * np.cos(ang + 2.094))

# faint ghost of the field so the void is not dead-black: distance shading
ghost = 0.05 * np.exp(-(d1.reshape(H, W) / 90.0))
img = np.stack([R + ghost * 0.3, G + ghost * 0.4, B + ghost * 0.9], -1)

img = 1.0 - np.exp(-1.9 * img)
img = np.clip(img, 0, 1) ** (1 / 1.6)

out = (img * 255 + 0.5).astype(np.uint8)
Image.fromarray(out, "RGB").save("out/03_relation_without_relata.png")
print("wrote out/03_relation_without_relata.png")
