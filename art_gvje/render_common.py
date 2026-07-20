import numpy as np
from scipy.ndimage import gaussian_filter, zoom as ndzoom

def filmic(x, k=1.0, gamma=0.9):
    y = 1.0 - np.exp(-k * np.clip(x, 0, None))
    return np.clip(y, 0, 1) ** gamma

def ramp(stops, t):
    """stops: list of (pos, (r,g,b)); t array in [0,1] -> (...,3) colors"""
    t = np.clip(t, 0, 1)
    pos = np.array([s[0] for s in stops])
    cols = np.array([s[1] for s in stops], dtype=np.float64)
    out = np.empty(t.shape + (3,))
    for c in range(3):
        out[..., c] = np.interp(t, pos, cols[:, c])
    return out

def fast_bloom(img, sigma):
    """downsample -> blur -> upsample wide bloom (craft note)"""
    if sigma <= 8:
        return gaussian_filter(img, sigma if img.ndim == 2 else (sigma, sigma, 0))
    ds = max(1, int(sigma / 6))
    if img.ndim == 3:
        small = img[::ds, ::ds]
        b = gaussian_filter(small, (sigma/ds, sigma/ds, 0))
        big = ndzoom(b, (img.shape[0]/b.shape[0], img.shape[1]/b.shape[1], 1), order=1)
    else:
        small = img[::ds, ::ds]
        b = gaussian_filter(small, sigma/ds)
        big = ndzoom(b, (img.shape[0]/b.shape[0], img.shape[1]/b.shape[1]), order=1)
    return big[:img.shape[0], :img.shape[1]]

def save(rgb, path):
    from PIL import Image
    arr = (np.clip(rgb, 0, 1) * 255).astype(np.uint8)
    Image.fromarray(arr).save(path)
    print('saved', path, arr.shape)
