"""Gradient-Anderson composite + xi(W) verification."""
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

L = 640
modes = np.load("p2c_modes.npy"); E = np.load("p2c_E.npy")
V = np.load("p2c_V.npy"); wx = np.load("p2c_wx.npy")
X, Y = np.meshgrid(np.arange(L), np.arange(L))

# measure per-mode: centroid x, localization length xi (radial log-slope fit)
cxs, xis, peaks = [], [], []
for i in range(len(E)):
    m = modes[i].reshape(L, L).astype(np.float64)
    cy, cx = np.unravel_index(np.argmax(m), m.shape)
    r = np.hypot(X - cx, Y - cy).ravel()
    lg = 0.5 * np.log(m.ravel() + 1e-300)
    sel = (r > 2) & (r < 90) & (lg > -60)
    xi = -1 / np.polyfit(r[sel], lg[sel], 1)[0] if sel.sum() > 50 else np.nan
    cxs.append(cx); xis.append(xi); peaks.append(m.max())
cxs = np.array(cxs); xis = np.array(xis)
# verification: xi should DECREASE with local disorder W(cx)
Wloc = wx[np.clip(cxs, 0, L - 1)]
sel = np.isfinite(xis) & (xis > 0)
order = np.argsort(Wloc[sel])
print("xi vs local W (binned):")
Wb = Wloc[sel][order]; Xb = xis[sel][order]
for k in range(6):
    seg = slice(k * len(Wb) // 6, (k + 1) * len(Wb) // 6)
    print("  W~%.1f -> xi median %.1f" % (np.median(Wb[seg]), np.median(Xb[seg])))

img = np.zeros((L, L, 3))
DEC = 4.2
rng = np.random.default_rng(2)
for i in range(len(E)):
    m = modes[i].reshape(L, L).astype(np.float64)
    m = m / m.max()
    lg = np.clip((np.log10(m + 1e-15) / DEC) + 1, 0, 1)
    core = m ** 0.32
    # hue: how caught the mode is (xi): free = pale cyan-white, caught = ember
    x = xis[i] if np.isfinite(xis[i]) else 40.0
    t = np.clip(1 - (np.log(x) - np.log(2.5)) / (np.log(45) - np.log(2.5)), 0, 1)
    col = np.array([0.30 + 0.75 * t, 0.55 + 0.15 * np.sin(np.pi * t), 0.85 - 0.55 * t])
    img += (0.42 * lg ** 3.2 + 1.15 * core)[..., None] * col[None, None, :]

sub = gaussian_filter(np.abs(V), 1.0)
sub = sub / sub.max()
img += (0.020 + 0.045 * sub)[..., None] * np.array([0.40, 0.50, 0.85])[None, None, :]

img = 1 - np.exp(-img)
img = np.clip(img, 0, 1) ** (1 / 1.8)
Image.fromarray((img * 255).astype(np.uint8)).save("proto2c.png")
print("saved")
