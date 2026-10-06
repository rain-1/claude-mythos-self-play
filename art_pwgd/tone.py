"""tone.py lin.npy out.png [expo] [white] — extended-Reinhard tone map, no overlay."""
import sys, numpy as np
from PIL import Image
img = np.load(sys.argv[1]).astype(np.float64)
ex = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0; w = float(sys.argv[4]) if len(sys.argv) > 4 else 1.2
x = ex * img; v = x * (1 + x / (w * w)) / (1 + x)
srgb = np.where(v <= 0.0031308, 12.92 * v, 1.055 * np.power(np.clip(v, 0, 1), 1 / 2.4) - 0.055)
Image.fromarray((np.clip(srgb, 0, 1) * 255 + 0.5).astype(np.uint8)).save(sys.argv[2])
