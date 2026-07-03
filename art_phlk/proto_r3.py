"""Prototype tone/palette for the R3 'flower of repulsion'."""
import numpy as np
from scipy.ndimage import gaussian_filter, zoom
from PIL import Image

W = 840
H = np.load("r3_zeta2M.npy")          # 420x420, [-4.2, 4.2]^2

Hs = gaussian_filter(H, 1.3)
F = zoom(Hs, W / H.shape[0], order=3)  # value field ~[0, 1.15]
print("field range:", F.min().round(3), F.max().round(3))

def palette_map(V, mode):
    """V in [0, ~1.15] -> rgb"""
    if mode == "A":   # linear ramp, canyon-focused
        t = np.clip(V / 1.12, 0, 1)
    elif mode == "B": # blend hist-eq (plaid pops) with linear (canyons stay)
        flat = V.ravel()
        order = np.argsort(flat, kind='stable')
        ranks = np.empty_like(order, np.float64)
        ranks[order] = np.arange(order.size) / order.size
        t = 0.55 * ranks.reshape(V.shape) + 0.45 * np.clip(V / 1.12, 0, 1)
    # curated ramp: void navy -> electric blue -> dusky violet -> rose ->
    # amber -> pale gold
    STOPS = np.array([
        (0.02, 0.03, 0.10), (0.10, 0.14, 0.42), (0.24, 0.28, 0.66),
        (0.45, 0.34, 0.62), (0.72, 0.42, 0.50), (0.95, 0.62, 0.38),
        (1.00, 0.86, 0.58)])
    x = np.clip(t, 0, 1) * (len(STOPS) - 1)
    i = np.clip(x.astype(int), 0, len(STOPS) - 2)
    f = (x - i)[..., None]
    return STOPS[i] * (1 - f) + STOPS[i + 1] * f

for mode in ("A", "B"):
    img = palette_map(F, mode)
    # gentle bloom on the brightest ridges
    lum = img.mean(2)
    mask = np.clip((lum - 0.62) / 0.38, 0, 1) ** 2
    blm = gaussian_filter(mask, 9)
    img += 0.35 * blm[..., None] * np.array([1.0, 0.85, 0.55])
    img = 1 - np.exp(-1.9 * img)
    Image.fromarray((np.clip(img, 0, 1) ** 0.95 * 255).astype(np.uint8)
                    ).save(f"proto_r3_{mode}.png")
print("done")
