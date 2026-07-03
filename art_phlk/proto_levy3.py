"""Prototype 3: time-hue channels + leap chords + aura + gentler tone."""
import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image
from levy_core import levy_walk, occupation, hist_eq, splat_bilinear

W = 1024
N = 60_000_000
ALPHA = 1.5
SEED = 7
NCH = 6

# epoch palette: deep indigo -> teal -> rose -> amber -> gold -> pale gold
EPOCH = np.array([
    (0.22, 0.30, 0.95), (0.10, 0.75, 0.85), (0.95, 0.35, 0.55),
    (1.00, 0.55, 0.25), (1.00, 0.80, 0.30), (0.95, 0.92, 0.70)])

def dense_center(pos, G=512):
    xlo, xhi = np.percentile(pos[:, 0], [1, 99])
    ylo, yhi = np.percentile(pos[:, 1], [1, 99])
    H, xe, ye = np.histogram2d(pos[:, 0], pos[:, 1], bins=G,
                               range=[[xlo, xhi], [ylo, yhi]])
    i, j = np.unravel_index(np.argmax(H), H.shape)
    return (xe[i] + xe[i + 1]) / 2, (ye[j] + ye[j + 1]) / 2

pos = levy_walk(N, ALPHA, seed=SEED)
cx, cy = dense_center(pos)
r = np.maximum(np.abs(pos[:, 0] - cx), np.abs(pos[:, 1] - cy))
half = np.quantile(r, 0.40) * 1.02
del r
print("half", half)

t = np.linspace(0, NCH - 1e-9, len(pos))
acc, kept = occupation(pos, W, (cx, cy, half), channels=NCH, tchan=t)
print("kept", kept / N)

# ---- leap chords: jumps longer than 3 px, constant-px-spacing samples ----
scale = (W - 1) / (2 * half)
P = (pos - np.array([cx - half, cy - half])) * scale   # pixel coords
seg = np.diff(P, axis=0)
L = np.hypot(seg[:, 0], seg[:, 1])
idx = np.where(L > 3.0)[0]
# only chords with at least one endpoint near frame
inb = ((P[idx] > -W * 0.2) & (P[idx] < W * 1.2)).all(1) | \
      ((P[idx + 1] > -W * 0.2) & (P[idx + 1] < W * 1.2)).all(1)
idx = idx[inb]
print("chords:", len(idx))
chord = np.zeros((W, W), np.float32)
CAP = 4000  # max samples per chord
for i in idx:
    a, b = P[i], P[i + 1]
    n = int(min(np.hypot(*(b - a)) / 1.2, CAP)) + 2
    s = np.linspace(0, 1, n)
    X = a[0] + (b[0] - a[0]) * s
    Y = a[1] + (b[1] - a[1]) * s
    splat_bilinear(chord, X, Y, W, w=np.full(n, 1.0 / n, np.float32))

np.save("proto3_acc.npy", acc)
np.save("proto3_chord.npy", chord)

# ---------------- tone / colour ----------------
def compose(acc, chord, gamma=3.0, blur=0.7, aura=0.5, chord_amp=0.35):
    dens = acc.sum(0)
    dens_b = gaussian_filter(dens, blur)
    v = hist_eq(dens_b, gamma=gamma)              # luminance in [0,1]
    # epoch hue = weighted mean channel
    wsum = gaussian_filter(acc.sum(0), 1.2) + 1e-12
    mean_c = sum(gaussian_filter(acc[c], 1.2) * c for c in range(NCH)) / wsum
    x = np.clip(mean_c, 0, NCH - 1)
    i = np.clip(x.astype(int), 0, NCH - 2)
    f = (x - i)[..., None]
    hue = EPOCH[i] * (1 - f) + EPOCH[i + 1] * f
    img = hue * v[..., None]
    # aura: blurred luminance added back, tinted cool
    au = gaussian_filter(v, 14)
    img += aura * au[..., None] * np.array([0.25, 0.32, 0.55]) * 0.5
    # chords: cool pale threads
    cb = gaussian_filter(chord, 0.8)
    cv = 1 - np.exp(-cb / np.percentile(cb[cb > 0], 99) * 3) if (cb > 0).any() else cb
    img += chord_amp * cv[..., None] * np.array([0.55, 0.75, 1.0])
    # filmic bound
    img = 1 - np.exp(-1.6 * img)
    img = np.clip(img, 0, 1) ** 0.92
    return (img * 255).astype(np.uint8)

Image.fromarray(compose(acc, chord)).save("proto3.png")
Image.fromarray(compose(acc, chord, gamma=4.5, aura=0.8)).save("proto3_soft.png")
print("done")
