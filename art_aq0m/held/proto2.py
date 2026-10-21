import numpy as np, sys
from PIL import Image
import depth, paper
n = int(sys.argv[1]); seed = int(sys.argv[2]); jit = float(sys.argv[3]); W = int(sys.argv[4])
rng = np.random.default_rng(seed)
th = np.sort((np.arange(n) + 0.5 + jit * rng.uniform(-0.5, 0.5, n)) * 2 * np.pi / n + rng.uniform(0, 6.3))
D = depth.depth(W, -1.06, 1.06, np.cos(th), np.sin(th))
print('max', D.max(), 'centre', D[W // 2, W // 2])
img = paper.render(D, thick=2.6 * W / 1000, ss_px=W / 1000)
Image.fromarray((paper.srgb(img) * 255).astype(np.uint8)).save(sys.argv[5])
