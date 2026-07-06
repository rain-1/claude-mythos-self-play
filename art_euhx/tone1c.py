"""Two-seas composite."""
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

S = 900
ain = np.load("p1c_in.npy").astype(np.float64)
aout = np.load("p1c_out.npy").astype(np.float64)
reg = np.load("p1c_reg.npy").astype(np.float64)
gold = np.load("p1c_gold.npy").astype(np.float64)

def sea_tone(a):
    c = np.log1p(a)
    if (c > 0).any():
        c = c / np.percentile(c[c > 0], 99.7)
    base = 1 - np.exp(-1.6 * np.clip(c - 0.30, 0, None) ** 1.4)   # dim mist, pools dark
    rim = np.clip(c - 0.86, 0, None) / 0.30
    rim = 1 - np.exp(-2.2 * rim)                                   # sticky rims
    return base, rim

b_in, r_in = sea_tone(ain)
b_out, r_out = sea_tone(aout)

r = reg / np.percentile(reg[reg > 0], 99.0)
r = 1 - np.exp(-1.8 * r)

g = np.log1p(gold)
g = g / max(np.percentile(g[g > 0], 98.0), 1e-9)
g = 1 - np.exp(-3.0 * g)
g_glow = gaussian_filter(g, 4.0); g_glow /= max(g_glow.max(), 1e-9)

img = np.zeros((S, S, 3), np.float64)
# outer sea: cold deep indigo
img[..., 0] += 0.055 * b_out; img[..., 1] += 0.085 * b_out; img[..., 2] += 0.22 * b_out
img[..., 0] += 0.22 * r_out;  img[..., 1] += 0.34 * r_out;  img[..., 2] += 0.80 * r_out
# inner sea: warm dusk violet-rose
img[..., 0] += 0.20 * b_in;  img[..., 1] += 0.075 * b_in;  img[..., 2] += 0.16 * b_in
img[..., 0] += 0.68 * r_in;  img[..., 1] += 0.28 * r_in;   img[..., 2] += 0.46 * r_in
# regular threads: quiet amber
img[..., 0] += 0.50 * r; img[..., 1] += 0.36 * r; img[..., 2] += 0.16 * r
# golden pair: blaze
img[..., 0] += 1.9 * g + 0.60 * g_glow
img[..., 1] += 1.55 * g + 0.45 * g_glow
img[..., 2] += 0.80 * g + 0.16 * g_glow

img = 1 - np.exp(-img)
img = np.clip(img, 0, 1) ** (1 / 1.75)
Image.fromarray((img * 255).astype(np.uint8)[::-1]).save("proto1c.png")
print("saved")
