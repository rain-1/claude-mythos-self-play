"""HERO: The nim-multiplication carpet.  1 cell = 1 px, v = i (x) j.
Brightness = simplicity of the product (small nim-products glow).
"""
import numpy as np, sys
from nim import nmul
from render_common import filmic, ramp, fast_bloom, save
from scipy.ndimage import gaussian_filter

S = int(sys.argv[1]) if len(sys.argv) > 1 else 1024
rs = S / 4096.0

i = np.arange(S, dtype=np.int32)
V = nmul(i[:, None], i[None, :])          # S x S nim products, < 65536
u = np.log2(1.0 + V) / 16.0               # 0..1 "depth" (0 = simplest)

# luminance: simple products glow; deep products form the dark plaid
L = (1.0 - u) ** 5.0
Ldark = 0.030 * (1.0 - u) ** 1.2           # faint body so the dark plaid reads

# dusk ramp by depth u: ivory/gold (simple) -> ember -> indigo (deep)
stops = [
    (0.00, (1.00, 0.97, 0.88)),
    (0.20, (1.00, 0.82, 0.45)),
    (0.42, (0.87, 0.45, 0.22)),
    (0.62, (0.45, 0.20, 0.30)),
    (0.80, (0.16, 0.12, 0.34)),
    (1.00, (0.07, 0.08, 0.20)),
]
col = ramp(stops, u)
img = col * (L + Ldark)[..., None] * 3.2

# white-hot: product exactly 1 (nim-inverse pairs)
inv_mask = (V == 1)
print('inverse pairs in frame:', int(inv_mask.sum()))
star = inv_mask.astype(np.float64)
star_b = gaussian_filter(star, 2.0) * 30 + star * 8
img += star_b[..., None] * np.array([0.9, 0.95, 1.0])

# bloom on the bright filigree
lum = img.mean(axis=2)
hi = np.clip(lum - np.percentile(lum, 99.0), 0, None)
img += fast_bloom(hi, 6 * max(rs,0.25))[..., None] * np.array([1.0, 0.85, 0.55]) * 0.6

out = filmic(img, k=1.0, gamma=0.85)
save(out, f'proto_hero_{S}.png')
