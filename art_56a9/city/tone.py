import numpy as np, sys
from PIL import Image
def tone(x, expo=1.0):
    x = np.clip(x * expo, 0, None)
    y = x / (1 + x / 4.0) * 1.25
    y = np.clip(y, 0, 1)
    return (np.where(y <= 0.0031308, 12.92 * y, 1.055 * y ** (1 / 2.4) - 0.055) * 255 + np.random.rand(*y.shape)).clip(0, 255).astype(np.uint8)
if __name__ == '__main__':
    parts = [np.load(p) for p in sys.argv[2:]]
    Image.fromarray(tone(np.concatenate(parts, 0))).save(sys.argv[1])
