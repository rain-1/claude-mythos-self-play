import sys, numpy as np
from PIL import Image
def tone(img, exp=1.0, sat=1.0):
    x = np.maximum(img * exp, 0)
    # soft shoulder: identity below 0.8, compress above
    k = 0.8
    y = np.where(x < k, x, k + (1 - k) * (1 - np.exp(-(x - k) / (1 - k))))
    if sat != 1.0:
        l = y.mean(-1, keepdims=True); y = l + (y - l) * sat
    y = np.clip(y, 0, 1)
    s = np.where(y <= 0.0031308, 12.92 * y, 1.055 * y ** (1 / 2.4) - 0.055)
    return s
if __name__ == '__main__':
    img = np.load(sys.argv[1]); exp = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
    s = tone(img, exp)
    Image.fromarray((np.clip(s, 0, 1) * 255 + 0.5).astype(np.uint8)).save(sys.argv[2])
