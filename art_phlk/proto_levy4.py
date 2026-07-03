"""Prototype 4: K independent flights from one origin, per-flight hue.
The shared home blazes; island-chain arms radiate at every scale."""
import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image
from levy_core import levy_walk, occupation, hist_eq, splat_bilinear

W = 1024
K = 24
NPER = 3_000_000
ALPHA = 1.4
NCH = 8

# hue wheel for flights (curated, no raw HSV): jewel tones
WHEEL = np.array([
    (0.95, 0.30, 0.40), (1.00, 0.55, 0.20), (1.00, 0.85, 0.30),
    (0.55, 0.95, 0.45), (0.20, 0.85, 0.75), (0.25, 0.55, 1.00),
    (0.55, 0.35, 1.00), (0.90, 0.35, 0.85)])

accs = np.zeros((NCH, W, W), np.float32)
chord = np.zeros((W, W), np.float32)

# first pass: collect all positions to choose the frame
allpos = []
for k in range(K):
    p = levy_walk(NPER, ALPHA, seed=100 + k)
    allpos.append(p.astype(np.float32))
P = np.concatenate(allpos)
r = np.maximum(np.abs(P[:, 0]), np.abs(P[:, 1]))
half = np.quantile(r, 0.55) * 1.05
print("half:", half)
del P, r

scale = (W - 1) / (2 * half)
for k, p in enumerate(allpos):
    ch = k % NCH
    X = (p[:, 0] + half) * scale
    Y = (p[:, 1] + half) * scale
    splat_bilinear(accs[ch], X, Y, W)
    # chords
    seg = np.diff(p, axis=0) * scale
    L = np.hypot(seg[:, 0], seg[:, 1])
    idx = np.where(L > 3.0)[0]
    inb = ((X[idx] > -W*0.2) & (X[idx] < W*1.2) & (Y[idx] > -W*0.2) & (Y[idx] < W*1.2)) | \
          ((X[idx+1] > -W*0.2) & (X[idx+1] < W*1.2) & (Y[idx+1] > -W*0.2) & (Y[idx+1] < W*1.2))
    idx = idx[inb]
    for i in idx:
        n = int(min(L[i] / 1.2, 4000)) + 2
        s = np.linspace(0, 1, n)
        splat_bilinear(chord, X[i] + seg[i, 0] * s, Y[i] + seg[i, 1] * s, W,
                       w=np.full(n, 1.0 / n, np.float32))
print("splatted")
np.save("proto4_accs.npy", accs); np.save("proto4_chord.npy", chord)

def compose(gamma=3.2, chord_amp=0.30, aura=0.55):
    dens = accs.sum(0)
    v = hist_eq(gaussian_filter(dens, 0.7), gamma=gamma)
    wsum = gaussian_filter(dens, 1.0) + 1e-12
    hue = np.zeros((W, W, 3))
    for c in range(NCH):
        hue += gaussian_filter(accs[c], 1.0)[..., None] * WHEEL[c]
    hue /= wsum[..., None]
    img = hue * v[..., None]
    au = gaussian_filter(v, 16)
    img += aura * au[..., None] * np.array([0.28, 0.34, 0.55]) * 0.5
    cb = gaussian_filter(chord, 0.8)
    if (cb > 0).any():
        cv = 1 - np.exp(-cb / np.percentile(cb[cb > 0], 99) * 3)
        img += chord_amp * cv[..., None] * np.array([0.55, 0.75, 1.0])
    img = 1 - np.exp(-1.7 * img)
    return (np.clip(img, 0, 1) ** 0.92 * 255).astype(np.uint8)

Image.fromarray(compose()).save("proto4.png")
print("done")
