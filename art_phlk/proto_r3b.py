"""Prototype R3 tone v2: diverging around the plateau; pearls blaze."""
import numpy as np
from scipy.ndimage import gaussian_filter, zoom
from PIL import Image

W = 840
H = np.load("r3_zeta2M.npy")
CROP = 30                       # trim to |u|,|v| < 3.6
H = H[CROP:-CROP, CROP:-CROP]
Hs = gaussian_filter(H, 1.3)
F = zoom(Hs, W / H.shape[0], order=3)

D = F - 1.0                     # deviation from the plateau

def tone(D, pos_gain=16.0, neg_soft=0.75):
    """negative -> cool depths, positive -> warm glow, both bounded."""
    neg = 1 - np.exp(D / neg_soft * 2.2)     # 0 at plateau -> -1 deep canyon
    neg = np.clip(-neg, 0, 1) if False else np.clip(np.where(D < 0, 1 - np.exp(D / neg_soft * 2.2), 0), 0, 1)
    pos = np.clip(np.where(D > 0, 1 - np.exp(-D * pos_gain), 0), 0, 1)
    return neg, pos

neg, pos = tone(D)
# base: plateau colour, dark dusky violet
img = np.zeros(F.shape + (3,))
PLATEAU = np.array([0.16, 0.11, 0.22])
CANYON1 = np.array([0.05, 0.09, 0.30])   # walls: deep blue
CANYON0 = np.array([0.005, 0.005, 0.03]) # floor: near-black
GOLD = np.array([1.00, 0.80, 0.38])
ROSE = np.array([0.85, 0.35, 0.45])

img += PLATEAU * (1 - neg[..., None])
# canyon: blend plateau->blue->black as neg goes 0->0.5->1
wall = np.clip(neg / 0.55, 0, 1); floor = np.clip((neg - 0.55) / 0.45, 0, 1)
img = img * (1 - wall[..., None]) + CANYON1 * wall[..., None]
img = img * (1 - floor[..., None]) + CANYON0 * floor[..., None]
# pearls: rose at low positive, gold at high
img += (ROSE * 0.6 + GOLD * 0.4) * (pos ** 1.6)[..., None] * 0.55
img += GOLD * (pos ** 3.2)[..., None] * 0.9
# bloom the pearls
lum = (img * [0.3, 0.5, 0.2]).sum(2)
mask = np.clip((lum - 0.30) / 0.5, 0, 1) ** 2
img += 0.5 * gaussian_filter(mask, 10)[..., None] * np.array([1.0, 0.75, 0.45])
img = 1 - np.exp(-2.1 * img)
Image.fromarray((np.clip(img, 0, 1) ** 0.95 * 255).astype(np.uint8)).save("proto_r3_C.png")
print("done", pos.max().round(3), neg.max().round(3))
