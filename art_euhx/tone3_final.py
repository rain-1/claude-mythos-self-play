"""Final composite for 'Two Ways Home'."""
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

acc_t = np.load("d3_threads.npy").astype(np.float64)
acc_s = np.load("d3_mist.npy").astype(np.float64)
Hpx, Wpx = acc_t.shape

t = acc_t / np.percentile(acc_t[acc_t > 0], 99.3)
t = 1 - np.exp(-2.4 * np.clip(t, 0, 1.6))
t_glow = gaussian_filter(t, 2.2)

m = np.log1p(acc_s)
m = m / np.percentile(m[m > 0], 99.7)
m = 1 - np.exp(-2.0 * np.clip(m - 0.12, 0, None))

img = np.zeros((Hpx, Wpx, 3))
# mist: cool slate -> ice
img[..., 0] += 0.09 * m; img[..., 1] += 0.15 * m; img[..., 2] += 0.34 * m
# threads: warm rose-gold blaze with a soft halo
img[..., 0] += 1.25 * t + 0.35 * t_glow
img[..., 1] += 0.88 * t + 0.24 * t_glow
img[..., 2] += 0.40 * t + 0.10 * t_glow

img = 1 - np.exp(-img)
img = np.clip(img, 0, 1) ** (1 / 1.75)
out = (img * 255).astype(np.uint8)
Image.fromarray(out).save("02_two_ways_home.png")
Image.fromarray(out).resize((768, 1024), Image.LANCZOS).save("prev3.png")
print("saved 02_two_ways_home.png", out.shape)
