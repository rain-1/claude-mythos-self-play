"""snow_view.py prefix N out.png [px_per_cell] — quick look at attachment time (warm = old, cool = young)."""
import sys, numpy as np
sys.path.insert(0, '.')
from snowio import load, axial_to_cart
from PIL import Image

pre, N, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
p = float(sys.argv[4]) if len(sys.argv) > 4 else 2.0
t, c, b, d = load(pre, N)
size = int(min(2000, N * p * 1.05))
T = axial_to_cart(t.astype(np.float32), p, size, order=0, cval=-1)
img = np.zeros((size, size, 3), np.uint8) + 245
m = T >= 0
h = T[m] / max(1, t.max())
img[m, 0] = (255 * (1 - h)).astype(np.uint8); img[m, 1] = (120 + 100 * h).astype(np.uint8); img[m, 2] = (255 * h).astype(np.uint8)
Image.fromarray(img).save(out)
print(out, 'crystals', int(m.sum()), 'tmax', int(t.max()))
