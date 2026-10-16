import numpy as np, sys
from PIL import Image
from scipy.ndimage import gaussian_filter
def load(fn, W, H): return np.fromfile(fn, dtype=np.float32).reshape(H, W, 3)
def tone(a, expo=1.0, white=1.3, bloom=0.0, bsig=0.01, gamma=2.2):
    a = a * expo
    if bloom > 0:
        hi = np.maximum(a - 1.0, 0); s = bsig * a.shape[1]
        b = sum(gaussian_filter(hi, (s * k, s * k, 0)) for k in (0.5, 1.5, 4.0)) / 3
        a = a + bloom * b
    L = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
    Lt = L * (1 + L / white ** 2) / (1 + L); a = a * (Lt / np.maximum(L, 1e-6))[..., None]
    return np.clip(a, 0, 1) ** (1 / gamma)
def save(a, fn): Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8)).save(fn)
if __name__ == '__main__':
    fn, W, H = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]); e = float(sys.argv[4]) if len(sys.argv) > 4 else 1
    save(tone(load(fn, W, H), e, bloom=float(sys.argv[5]) if len(sys.argv) > 5 else 0), fn.replace('.f32', '.png'))
def local(a, sig=0.06, k=0.8, target=0.55):
    """dodge & burn: divide by a heavily blurred luminance^k (keeps shadows and caustics, flattens 1/r^2)"""
    L = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
    s = sig * a.shape[1]; Lb = gaussian_filter(np.log(np.maximum(L, 1e-4)), s)
    Lb = np.exp(Lb); g = (target / Lb) ** k
    return a * g[..., None]
