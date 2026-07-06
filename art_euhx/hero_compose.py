"""HERO composite at 4096: two seas + island threads + golden pair. + barrier verify."""
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

S = 4096

def down2(a8):
    return a8.reshape(S, 2, S, 2).mean(axis=(1, 3))

ain = (np.load("hero_sea_inner_0.npy").astype(np.float64)
       + np.load("hero_sea_inner_1.npy").astype(np.float64))
aout = (np.load("hero_sea_outer_2.npy").astype(np.float64)
        + np.load("hero_sea_outer_3.npy").astype(np.float64))
gold = down2(np.load("hero_gold8.npy").astype(np.float64))
reg = down2(np.load("hero_reg8.npy").astype(np.float64))

# ---- barrier verification (fresh extremes) ----
gb = np.load("hero_gold_band.npy")   # gmin, gmax, mmin, mmax  (per 4096 x-bins)
gmin, gmax, mmin, mmax = gb
inner_lo = np.full(4096, 2.0); inner_hi = np.full(4096, -1.0)
for wid in (0, 1):
    ext = np.load("hero_ext_inner_%d.npy" % wid)
    inner_lo = np.minimum(inner_lo, ext[0]); inner_hi = np.maximum(inner_hi, ext[1])
print("BARRIER inner<golden everywhere:", bool(np.all(inner_hi < gmin)),
      "min margin %.3e" % np.min(gmin - inner_hi))
print("BARRIER inner>mirror everywhere:", bool(np.all(inner_lo > mmax)),
      "min margin %.3e" % np.min(inner_lo - mmax))
for wid in (2, 3):
    ext = np.load("hero_ext_outer_%d.npy" % wid)
    # outer sea must avoid the open strip strictly between mirror-top and golden-bottom
    bad = np.sum((ext[1] > mmax) & (ext[1] < gmin)) + np.sum((ext[0] > mmax) & (ext[0] < gmin))
    print("outer worker %d extreme-points inside forbidden strip: %d (expect 0)" % (wid, bad))

# ---- tone ----
def sea_tone(a, p_hi=99.7, base_gate=0.30, base_k=1.6, rim_gate=0.86, rim_w=0.30):
    c = np.log1p(a)
    c = c / np.percentile(c[c > 0], p_hi)
    base = 1 - np.exp(-base_k * np.clip(c - base_gate, 0, None) ** 1.4)
    rim = np.clip(c - rim_gate, 0, None) / rim_w
    rim = 1 - np.exp(-2.2 * rim)
    return base, rim

b_in, r_in = sea_tone(ain)
b_out, r_out = sea_tone(aout, base_gate=0.34, base_k=1.35)

def histeq_nonzero(a, floor=0.0):
    flat = a.ravel()
    nz = flat > 0
    out = np.zeros_like(flat)
    vals = np.log1p(flat[nz].astype(np.float64))
    order = np.argsort(vals)
    ranks = np.empty_like(order, dtype=np.float64)
    ranks[order] = np.arange(order.size)
    out[nz] = floor + (1 - floor) * ranks / max(order.size - 1, 1)
    return out.reshape(a.shape)

r = histeq_nonzero(reg, floor=0.0)
r = r ** 2.6
r = np.maximum(r, gaussian_filter(r, 1.0) * 0.75)

g = np.log1p(gold)
g = g / np.percentile(g[g > 0], 98.0)
g = 1 - np.exp(-3.2 * g)
g1 = gaussian_filter(g, 6.0); g1 /= max(g1.max(), 1e-9)
g2 = gaussian_filter(g, 28.0); g2 /= max(g2.max(), 1e-9)

img = np.zeros((S, S, 3), np.float64)
# outer sea: cold abyss indigo
img[..., 0] += 0.050 * b_out; img[..., 1] += 0.080 * b_out; img[..., 2] += 0.21 * b_out
img[..., 0] += 0.20 * r_out;  img[..., 1] += 0.33 * r_out;  img[..., 2] += 0.80 * r_out
# inner sea: warm imprisoned dusk (wine/rose)
img[..., 0] += 0.185 * b_in; img[..., 1] += 0.070 * b_in; img[..., 2] += 0.150 * b_in
img[..., 0] += 0.66 * r_in;  img[..., 1] += 0.26 * r_in;  img[..., 2] += 0.44 * r_in
# island threads: quiet amber
img[..., 0] += 0.46 * r; img[..., 1] += 0.335 * r; img[..., 2] += 0.15 * r
# golden pair: white-gold blaze + two-scale halo
img[..., 0] += 2.0 * g + 0.50 * g1 + 0.22 * g2
img[..., 1] += 1.62 * g + 0.375 * g1 + 0.16 * g2
img[..., 2] += 0.82 * g + 0.13 * g1 + 0.05 * g2

img = 1 - np.exp(-img)
img = np.clip(img, 0, 1) ** (1 / 1.75)
out = (img * 255).astype(np.uint8)[::-1]
Image.fromarray(out).save("01_the_last_circle.png")
Image.fromarray(out).resize((1024, 1024), Image.LANCZOS).save("prev1.png")
print("saved 01_the_last_circle.png")
