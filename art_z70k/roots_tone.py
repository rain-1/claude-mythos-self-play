"""Tone-map a Littlewood-roots field. Histogram-equalize the (log) density so
structure reads at ALL density levels (the dragon filigree, the unit-circle
ridge, the holes at roots of unity). Teal->gold palette, restrained bloom.
"""
import numpy as np, sys
from PIL import Image
from scipy.ndimage import gaussian_filter

inp = sys.argv[1]
outp = sys.argv[2] if len(sys.argv) > 2 else inp.replace(".npy", "_tone.png")
gamma = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
fix_seam = (len(sys.argv) > 4 and sys.argv[4] == "seam")

acc = np.load(inp).astype(np.float64)
S = acc.shape[0]

if fix_seam:
    mid = S // 2
    for r in (mid-1, mid):
        acc[r] = 0.5 * (acc[r-2] + acc[r+2])

a = np.log1p(acc)

# histogram-equalize the nonzero log-density into [0,1]
nz = a > 0
vals = a[nz]
order = np.argsort(vals)
ranks = np.empty_like(vals)
ranks[order] = np.arange(vals.size)
eq = np.zeros_like(a)
eq[nz] = (ranks + 1) / vals.size
eq = eq ** gamma

# palette control points (deep void -> indigo -> teal -> green-gold -> gold -> white)
pal = [
    (0.00, (2,   4,   10)),
    (0.18, (12,  22,  58)),
    (0.36, (16,  74,  104)),
    (0.55, (28, 146, 150)),
    (0.72, (96, 178, 128)),
    (0.85, (220,176,  92)),
    (0.94, (252,214, 130)),
    (1.00, (255,250, 240)),
]
xs = np.array([p[0] for p in pal])
cs = np.array([p[1] for p in pal], float)
rgb = np.empty(eq.shape + (3,))
for c in range(3):
    rgb[..., c] = np.interp(eq, xs, cs[:, c])
# darken pure-zero background to true void
rgb[~nz] = np.array([2, 4, 10])

# restrained bloom from the high-equalized regions
bri = np.clip((eq - 0.55) / 0.45, 0, 1)
bl = gaussian_filter(bri, sigma=S/900.0)
bl /= (bl.max() + 1e-9)
rgb[..., 0] += bl * 55
rgb[..., 1] += bl * 46
rgb[..., 2] += bl * 22

rgb = np.clip(rgb, 0, 255).astype(np.uint8)
Image.fromarray(rgb).save(outp)
print("saved", outp, "S=", S)
