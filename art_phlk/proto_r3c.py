"""Prototype R3 tone v3: crisp emblem — grain kept, narrow glowing-edged
canyons, sharp gold pearls, vignette."""
import numpy as np
from scipy.ndimage import gaussian_filter, zoom
from PIL import Image

W = 840
H = np.load("r3_zeta2M.npy")
CROP = 30
H = H[CROP:-CROP, CROP:-CROP]

Hs = gaussian_filter(H, 0.8)           # keep grain
F = zoom(Hs, W / H.shape[0], order=3)
D = F - 1.0

neg = np.clip(np.where(D < 0, -D, 0), 0, 1)          # 0..1 into canyon
pos = np.clip(np.where(D > 0, D, 0), 0, None)

img = np.zeros(F.shape + (3,))
PLATEAU = np.array([0.13, 0.095, 0.19])
WALLGLOW = np.array([0.10, 0.35, 0.95])   # electric blue rim
FLOOR = np.array([0.004, 0.004, 0.025])
GOLD = np.array([1.00, 0.78, 0.30])
ROSE = np.array([0.95, 0.42, 0.40])

# plateau with grain shimmer (grain = deviation, both signs, tiny)
img += PLATEAU * (1 + 2.2 * np.clip(D, -0.04, 0.04) / 0.04 * 0.35)[..., None]
# canyon: rim glow peaks at neg~0.45, floor beyond 0.75
rim = np.exp(-((neg - 0.45) / 0.16) ** 2) * (neg > 0.08)
floor = np.clip((neg - 0.55) / 0.4, 0, 1) ** 1.3
img += WALLGLOW * (rim * 0.55)[..., None]
img *= (1 - floor[..., None] * 0.985)
img += FLOOR * floor[..., None]
# pearls
p1 = 1 - np.exp(-pos * 22)
img += ROSE * (p1 ** 1.5)[..., None] * 0.5
img += GOLD * (p1 ** 3.0)[..., None] * 1.1
# bloom pearls + rims
lum = (img * [0.35, 0.5, 0.15]).sum(2)
mask = np.clip((lum - 0.35) / 0.45, 0, 1) ** 2
img += 0.45 * gaussian_filter(mask, 8)[..., None] * np.array([0.9, 0.7, 0.5])
# vignette
yy, xx = np.mgrid[0:W, 0:W] / (W - 1) * 2 - 1
r2 = xx ** 2 + yy ** 2
img *= (1 - 0.32 * np.clip(r2 - 0.35, 0, 1.2) / 1.2)[..., None]
img = 1 - np.exp(-2.2 * img)
Image.fromarray((np.clip(img, 0, 1) ** 0.95 * 255).astype(np.uint8)).save("proto_r3_D.png")
print("done")
