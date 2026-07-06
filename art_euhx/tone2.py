"""Anderson composite: blazing cores + exponential tent-glow skirts + dim disorder substrate."""
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

L = 512
modes = np.load("p2_modes.npy"); E = np.load("p2_E.npy"); V = np.load("p2_V.npy").reshape(L, L)

DECADES = 3.6
img = np.zeros((L, L, 3))

# curated ramp by energy: deep teal (E<0) -> ice -> ember gold (E>0)
def ramp(t):
    c0 = np.array([0.05, 0.55, 0.60])   # teal
    c1 = np.array([0.75, 0.88, 0.95])   # ice
    c2 = np.array([1.00, 0.62, 0.18])   # ember
    t = t[:, None]
    return (1 - t) ** 2 * c0[None] + 2 * t * (1 - t) * c1[None] + t ** 2 * c2[None]

t = (E - E.min()) / (E.max() - E.min())
cols = ramp(t)

for i in range(len(E)):
    m = modes[i].reshape(L, L)
    m = m / m.max()
    lg = np.clip((np.log10(m + 1e-15) / DECADES) + 1, 0, 1)   # 1 at peak, 0 at DECADES down
    core = m ** 0.30
    layer = 0.55 * lg ** 3.0 + 1.25 * core
    img += layer[..., None] * cols[i][None, None, :]

# substrate: the disorder potential, extremely dim slate mottling
sub = gaussian_filter(V, 1.2)
sub = (sub - sub.min()) / (sub.max() - sub.min())
img += (0.028 + 0.030 * sub)[..., None] * np.array([0.45, 0.55, 0.9])[None, None, :]

img = 1 - np.exp(-img)
img = np.clip(img, 0, 1) ** (1 / 1.8)
Image.fromarray((img * 255).astype(np.uint8)).save("proto2b.png")
print("saved")
