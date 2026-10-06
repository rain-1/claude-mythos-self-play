import sys, numpy as np
from PIL import Image
W, H = int(sys.argv[2]), int(sys.argv[3])
img = np.fromfile(sys.argv[1], np.float32).reshape(-1, W, 3).astype(np.float64)
ex = float(sys.argv[5]) if len(sys.argv) > 5 else 1.0; w = float(sys.argv[6]) if len(sys.argv) > 6 else 1.2
x = ex * img; v = x * (1 + x / (w * w)) / (1 + x)
srgb = np.where(v <= 0.0031308, 12.92 * v, 1.055 * np.power(np.clip(v, 0, 1), 1 / 2.4) - 0.055)
Image.fromarray((np.clip(srgb, 0, 1) * 255 + 0.5).astype(np.uint8)).save(sys.argv[4])
