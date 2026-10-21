import numpy as np, sys
from PIL import Image
import depth
n = int(sys.argv[1]); seed = int(sys.argv[2])
rng = np.random.default_rng(seed)
th = np.sort(rng.uniform(0, 2 * np.pi, n))
D = depth.depth(500, -1.05, 1.05, np.cos(th), np.sin(th))
m = D.max(); print(n, seed, 'max', m, 'centre', D[250, 250])
import colorsys
h = (D / max(m, 1)) * 0.8
rgb = np.zeros(D.shape + (3,))
for k in range(m + 1):
    c = colorsys.hls_to_rgb((0.95 - 0.8 * k / m) % 1, 0.82 - 0.06 * (k % 2), 0.7)
    rgb[D == k] = c
rgb[D < 0] = 1
Image.fromarray((rgb * 255).astype(np.uint8)).save(f'/tmp/d_{n}_{seed}.png')
