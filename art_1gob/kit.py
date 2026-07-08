"""Shared render kit — run 1gob."""
import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image

def filmic(x, k=1.0, gamma=0.88):
    y = 1.0 - np.exp(-k*np.maximum(x, 0))
    return np.power(y, gamma)

def bloom(rgb, mask_thresh=0.72, sigma=6.0, gain=0.55, tint=(1.0,0.9,0.75)):
    lum = 0.2126*rgb[...,0]+0.7152*rgb[...,1]+0.0722*rgb[...,2]
    t = np.clip((lum-mask_thresh)/(1-mask_thresh), 0, 1)
    m = t*t*(3-2*t)
    halo = np.stack([gaussian_filter(rgb[...,c]*m, sigma)*tint[c] for c in range(3)], -1)
    return rgb + gain*halo

def save(rgb, path, down=None):
    rgb = np.clip(rgb, 0, 1)
    img = Image.fromarray((rgb*255+0.5).astype(np.uint8))
    if down:
        img = img.resize((down, down), Image.LANCZOS)
    img.save(path, optimize=True)
    print("saved", path, img.size)

def lerp(a, b, t):
    t = np.asarray(t)[..., None] if np.ndim(t) and np.ndim(a)==1 else t
    return a + (b-a)*t

def smoothstep(e0, e1, x):
    t = np.clip((x-e0)/(e1-e0), 0, 1)
    return t*t*(3-2*t)
