"""Prototype 2: frame = densest cluster, half sized so a target fraction of
the walk's TIME is inside. Try alphas x fractions."""
import numpy as np
from PIL import Image
from levy_core import levy_walk, occupation, hist_eq
from proto_levy import ramp_map

W = 900
N = 30_000_000

def dense_center(pos, G=512):
    """centroid of the peak cell of a coarse histogram over the 1-99% box"""
    xlo, xhi = np.percentile(pos[:, 0], [1, 99])
    ylo, yhi = np.percentile(pos[:, 1], [1, 99])
    H, xe, ye = np.histogram2d(pos[:, 0], pos[:, 1], bins=G,
                               range=[[xlo, xhi], [ylo, yhi]])
    i, j = np.unravel_index(np.argmax(H), H.shape)
    return (xe[i] + xe[i + 1]) / 2, (ye[j] + ye[j + 1]) / 2

def frame_at(pos, cx, cy, frac):
    r = np.maximum(np.abs(pos[:, 0] - cx), np.abs(pos[:, 1] - cy))
    return np.quantile(r, frac)

for alpha in (1.5, 1.2):
    pos = levy_walk(N, alpha, seed=7)
    cx, cy = dense_center(pos)
    for frac in (0.15, 0.4, 0.7):
        half = frame_at(pos, cx, cy, frac) * 1.02
        acc, kept = occupation(pos, W, (cx, cy, half))
        v = hist_eq(acc, gamma=1.35)
        img = (ramp_map(v) * 255).astype(np.uint8)
        Image.fromarray(img).save(f"proto2_a{alpha:.1f}_f{frac:.2f}.png")
        print(f"a={alpha} frac={frac}: kept {kept/N*100:.0f}%  half={half:.3g}")
