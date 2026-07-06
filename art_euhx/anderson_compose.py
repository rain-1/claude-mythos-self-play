"""Final composite: mobility-edge Anderson piece at L=1400, from per-shift files."""
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
import glob

L = 1400
X, Y = np.meshgrid(np.arange(L), np.arange(L))
V = np.load("anderson_V.npy")
wx = np.load("anderson_wx.npy")

modes_all, E_all = [], []
for f in sorted(glob.glob("ashift_modes_*.npy"), key=lambda s: int(s.split("_")[-1].split(".")[0])):
    idx = int(f.split("_")[-1].split(".")[0])
    m = np.load(f)
    e = np.load("ashift_E_%d.npy" % idx)
    modes_all.append(m); E_all.append(e)
modes = np.concatenate(modes_all, axis=0)
E = np.concatenate(E_all, axis=0)
print("total modes:", len(E))

# de-dup near-identical modes from overlapping shifts
keep = []
seen = []
for i in range(len(E)):
    m = modes[i]
    c = np.unravel_index(np.argmax(m), (L, L))
    dup = any(abs(c[0] - s[0]) < 3 and abs(c[1] - s[1]) < 3 and abs(E[i] - s[2]) < 1e-6 for s in seen)
    if not dup:
        keep.append(i); seen.append((c[0], c[1], E[i]))
print("kept after dedup:", len(keep))

xis = []
img = np.zeros((L, L, 3))
peak_global = max(modes[i].max() for i in keep)
DEC_LO, DEC_HI = -7.2, -2.0   # log10(m) window for the outer glow

for i in keep:
    m = modes[i].reshape(L, L)
    cy, cx = np.unravel_index(np.argmax(m), m.shape)
    r = np.hypot(X - cx, Y - cy).ravel()
    lg2 = 0.5 * np.log(m.ravel() + 1e-300)
    sel = (r > 2) & (r < 90) & (lg2 > -60)
    xi = -1 / np.polyfit(r[sel], lg2[sel], 1)[0] if sel.sum() > 50 else 40.0
    xis.append(xi)
    lg = np.clip((np.log10(m + 1e-15) - DEC_LO) / (DEC_HI - DEC_LO), 0, 1)
    core = (m / peak_global) ** 0.30
    t = np.clip(1 - (np.log(max(xi, 1e-3)) - np.log(2.5)) / (np.log(45) - np.log(2.5)), 0, 1)
    col = np.array([0.30 + 0.72 * t, 0.52 + 0.18 * np.sin(np.pi * t), 0.88 - 0.58 * t])
    img += (0.50 * lg ** 3.0 + 1.30 * core)[..., None] * col[None, None, :]

xis = np.array(xis)
print("xi: median %.1f range [%.1f,%.1f]" % (np.median(xis), np.min(xis), np.max(xis)))

# verify mobility-edge trend: xi should fall as local disorder rises
cxs = np.array([np.unravel_index(np.argmax(modes[i]), (L, L))[1] for i in keep])
Wloc = wx[np.clip(cxs, 0, L - 1)]
order = np.argsort(Wloc)
Wb, Xb = Wloc[order], xis[order]
print("xi vs local disorder W (6 bins):")
for k in range(6):
    seg = slice(k * len(Wb) // 6, (k + 1) * len(Wb) // 6)
    print("  W~%.1f -> xi median %.1f" % (np.median(Wb[seg]), np.median(Xb[seg])))

sub = gaussian_filter(np.abs(V), 1.0); sub /= sub.max()
img += (0.018 + 0.040 * sub)[..., None] * np.array([0.40, 0.50, 0.85])[None, None, :]

img = 1 - np.exp(-img)
img = np.clip(img, 0, 1) ** (1 / 1.8)
out = (img * 255).astype(np.uint8)
Image.fromarray(out).save("03_mobility_edge.png")
Image.fromarray(out).resize((768, 768), Image.LANCZOS).save("prev2.png")
print("saved 03_mobility_edge.png", out.shape)
