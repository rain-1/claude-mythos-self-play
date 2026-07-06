"""Composite the standard-map layers -> dark painterly phase portrait."""
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
import sys

S = 900
reg = np.load("p1_reg.npy"); regW = np.load("p1_regW.npy")
cha = np.load("p1_cha.npy"); gold = np.load("p1_gold.npy")

# mean rotation number per pixel (hue driver for threads)
Wmean = np.where(reg > 1e-9, regW / np.maximum(reg, 1e-9), 0.0)

# --- tone the regular threads ---
r = reg / np.percentile(reg[reg > 0], 99.0)
r = 1 - np.exp(-2.2 * r)

# --- chaotic mist: log density, keep dark pools ---
c = np.log1p(cha.astype(np.float64))
c = c / np.percentile(c[c > 0], 99.5)
c = np.clip(c, 0, 1.15)
mist = 1 - np.exp(-2.0 * np.clip(c - 0.18, 0, None))   # subtract baseline -> pools stay dark

# sticky rims: the brightest chaotic occupation (stickiness near islands)
rim = np.clip(c - 0.80, 0, None) / 0.35
rim = 1 - np.exp(-2.5 * rim)

# --- golden circle layer ---
g = np.log1p(gold.astype(np.float64))
g = g / max(np.percentile(g[g > 0], 98.0), 1e-9)
g = 1 - np.exp(-3.0 * g)
g_glow = gaussian_filter(g, 3.0); g_glow /= max(g_glow.max(), 1e-9)

# --- palettes ---
img = np.zeros((S, S, 3), np.float64)

# chaotic sea: deep indigo -> slate blue
img[..., 0] += 0.10 * mist
img[..., 1] += 0.14 * mist
img[..., 2] += 0.30 * mist
# sticky rims: electric periwinkle
img[..., 0] += 0.30 * rim
img[..., 1] += 0.42 * rim
img[..., 2] += 0.85 * rim

# regular threads: hue by rotation number W (rose W~0/1 -> amber W~1/2)
t = np.clip(Wmean, 0, 1)
hue_r = 0.95 - 0.15 * np.sin(np.pi * t)
hue_g = 0.35 + 0.45 * np.sin(np.pi * t)
hue_b = 0.28 + 0.10 * np.sin(np.pi * t) ** 2
lum = 0.85
img[..., 0] += lum * r * hue_r
img[..., 1] += lum * r * hue_g
img[..., 2] += lum * r * hue_b

# golden thread: white-gold blaze + halo
img[..., 0] += 1.6 * g + 0.55 * g_glow
img[..., 1] += 1.35 * g + 0.42 * g_glow
img[..., 2] += 0.75 * g + 0.18 * g_glow

img = 1 - np.exp(-img)               # filmic bound
img = np.clip(img, 0, 1) ** (1 / 1.65)
Image.fromarray((img * 255).astype(np.uint8)[::-1]).save("proto1b.png")
print("saved")
