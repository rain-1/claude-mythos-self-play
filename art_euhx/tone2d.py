"""Gradient-Anderson, honest luminance: every mode carries total light 1 (its L2 norm).
Free modes spread thin and pale; caught modes burn bright."""
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

L = 640
modes = np.load("p2c_modes.npy").astype(np.float64)   # each row: |psi|^2, sums to 1
E = np.load("p2c_E.npy")
V = np.load("p2c_V.npy"); wx = np.load("p2c_wx.npy")
X, Y = np.meshgrid(np.arange(L), np.arange(L))

# de-duplicate nearly-identical modes from adjacent sigma batches
keep = []
seen = []
for i in range(len(E)):
    m = modes[i]
    c = np.unravel_index(np.argmax(m), (L, L))
    dup = any(abs(c[0] - s[0]) < 3 and abs(c[1] - s[1]) < 3 and abs(E[i] - s[2]) < 1e-6 for s in seen)
    if not dup:
        keep.append(i); seen.append((c[0], c[1], E[i]))
print("modes kept:", len(keep), "of", len(E))

xis, cols_list, layers = [], [], []
img = np.zeros((L, L, 3))
peak_global = max(modes[i].max() for i in keep)

for i in keep:
    m = modes[i].reshape(L, L)
    cy, cx = np.unravel_index(np.argmax(m), m.shape)
    r = np.hypot(X - cx, Y - cy).ravel()
    lg2 = 0.5 * np.log(m.ravel() + 1e-300)
    sel = (r > 2) & (r < 90) & (lg2 > -60)
    xi = -1 / np.polyfit(r[sel], lg2[sel], 1)[0] if sel.sum() > 50 else 40.0
    xis.append(xi)
    # global log window: absolute brightness (NOT per-mode normalized)
    lg = np.clip((np.log10(m + 1e-15) + 7.2) / 5.2, 0, 1)   # 1 at m=1e-2, 0 at m=1e-7.2
    core = (m / peak_global) ** 0.30
    t = np.clip(1 - (np.log(max(xi, 1e-3)) - np.log(2.5)) / (np.log(45) - np.log(2.5)), 0, 1)
    col = np.array([0.30 + 0.72 * t, 0.52 + 0.18 * np.sin(np.pi * t), 0.88 - 0.58 * t])
    img += (0.50 * lg ** 3.0 + 1.30 * core)[..., None] * col[None, None, :]

xis = np.array(xis)
print("xi: median %.1f range [%.1f,%.1f]" % (np.median(xis), np.min(xis), np.max(xis)))

sub = gaussian_filter(np.abs(V), 1.0); sub /= sub.max()
img += (0.018 + 0.040 * sub)[..., None] * np.array([0.40, 0.50, 0.85])[None, None, :]

img = 1 - np.exp(-img)
img = np.clip(img, 0, 1) ** (1 / 1.8)
Image.fromarray((img * 255).astype(np.uint8)).save("proto2d.png")
print("saved")
