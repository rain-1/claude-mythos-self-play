"""Prototype: occupation measure of Levy flights at several alpha, 900px,
mono ramp, percentile framing. Render small, LOOK, then scale."""
import numpy as np
from PIL import Image
from levy_core import levy_walk, occupation, hist_eq

W = 900
N = 30_000_000

def frame_box(pos, plo=2, phi=98, pad=1.06):
    xlo, xhi = np.percentile(pos[:, 0], [plo, phi])
    ylo, yhi = np.percentile(pos[:, 1], [plo, phi])
    cx, cy = (xlo + xhi) / 2, (ylo + yhi) / 2
    half = max(xhi - xlo, yhi - ylo) / 2 * pad
    return cx, cy, half

RAMP = np.array([  # indigo -> rose -> amber -> gold -> white
    (0.02, 0.02, 0.06), (0.13, 0.08, 0.30), (0.45, 0.16, 0.42),
    (0.80, 0.33, 0.28), (0.98, 0.66, 0.25), (1.00, 0.92, 0.70),
    (1.00, 1.00, 1.00)])

def ramp_map(v):
    x = np.clip(v, 0, 1) * (len(RAMP) - 1)
    i = np.clip(x.astype(int), 0, len(RAMP) - 2)
    f = (x - i)[..., None]
    return RAMP[i] * (1 - f) + RAMP[i + 1] * f

for alpha in (1.9, 1.5, 1.2, 0.9):
    pos = levy_walk(N, alpha, seed=7)
    box = frame_box(pos)
    acc, kept = occupation(pos, W, box)
    v = hist_eq(acc, gamma=1.35)
    img = (ramp_map(v) * 255).astype(np.uint8)
    Image.fromarray(img).save(f"proto_a{alpha:.1f}.png")
    print(f"alpha={alpha}: kept {kept/N*100:.1f}% of points in frame, box half={box[2]:.3g}")
