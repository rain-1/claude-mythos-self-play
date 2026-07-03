"""Prototype 5: ONE walker, alpha decaying over time (the second moment
dying mid-journey). Brownian wool core -> archipelagos -> gold departures.
Hue = epoch, luminance = occupation density."""
import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image
from levy_core import splat_bilinear, hist_eq

W = 1024
N = 80_000_000
A_HI, A_LO = 2.6, 1.02
SEED = 11
NCH = 8

# epoch palette: deep blue wool -> teal -> jade -> rose -> ember -> amber -> gold -> pale gold
EPOCH = np.array([
    (0.16, 0.26, 0.85), (0.10, 0.55, 0.90), (0.15, 0.80, 0.65),
    (0.75, 0.30, 0.60), (0.95, 0.35, 0.35), (1.00, 0.60, 0.22),
    (1.00, 0.82, 0.30), (1.00, 0.95, 0.75)])

def walk_annealed(n, seed, chunk=10_000_000):
    rng = np.random.default_rng(seed)
    pos = np.zeros(2)
    out = np.empty((n, 2), np.float32)
    done = 0
    while done < n:
        m = min(chunk, n - done)
        t = (done + np.arange(m)) / n
        alpha = A_HI + (A_LO - A_HI) * t          # linear anneal
        u = rng.random(m)
        L = u ** (-1.0 / alpha)
        th = rng.random(m) * (2 * np.pi)
        xs = np.cumsum(L * np.cos(th)) + pos[0]
        ys = np.cumsum(L * np.sin(th)) + pos[1]
        out[done:done+m, 0] = xs; out[done:done+m, 1] = ys
        pos = np.array([xs[-1], ys[-1]]); done += m
    return out

pos = walk_annealed(N, SEED)
core = pos[: N // 5]
cx, cy = core[:, 0].mean(), core[:, 1].mean()
r = np.maximum(np.abs(pos[:, 0] - cx), np.abs(pos[:, 1] - cy))
for q, tag in ((0.55, "a"), (0.75, "b")):
    half = np.quantile(r, q) * 1.05
    scale = (W - 1) / (2 * half)
    accs = np.zeros((NCH, W, W), np.float32)
    chord = np.zeros((W, W), np.float32)
    t = np.linspace(0, NCH - 1e-9, N)
    c0 = t.astype(np.int64)
    X = (pos[:, 0] - (cx - half)) * scale
    Y = (pos[:, 1] - (cy - half)) * scale
    f32 = np.float32
    for c in range(NCH):
        m = c0 == c
        fr = (t[m] - c)
        splat_bilinear(accs[c], X[m], Y[m], W)  # nearest-channel (cheap)
    seg = np.stack([np.diff(X), np.diff(Y)], 1)
    L = np.hypot(seg[:, 0], seg[:, 1])
    idx = np.where(L > 3.0)[0]
    inb = ((X[idx] > -W*0.2) & (X[idx] < W*1.2) & (Y[idx] > -W*0.2) & (Y[idx] < W*1.2)) | \
          ((X[idx+1] > -W*0.2) & (X[idx+1] < W*1.2) & (Y[idx+1] > -W*0.2) & (Y[idx+1] < W*1.2))
    idx = idx[inb]
    print(tag, "chords:", len(idx), "half", half)
    for i in idx:
        n = int(min(L[i] / 1.2, 4000)) + 2
        s = np.linspace(0, 1, n)
        splat_bilinear(chord, X[i] + seg[i, 0]*s, Y[i] + seg[i, 1]*s, W,
                       w=np.full(n, 1.0/n, f32))
    dens = accs.sum(0)
    v = hist_eq(gaussian_filter(dens, 0.7), gamma=3.2)
    wsum = gaussian_filter(dens, 1.0) + 1e-12
    hue = np.zeros((W, W, 3))
    for c in range(NCH):
        hue += gaussian_filter(accs[c], 1.0)[..., None] * EPOCH[c]
    hue /= wsum[..., None]
    img = hue * v[..., None]
    au = gaussian_filter(v, 16)
    img += 0.5 * au[..., None] * np.array([0.28, 0.34, 0.55]) * 0.5
    cb = gaussian_filter(chord, 0.8)
    if (cb > 0).any():
        cv = 1 - np.exp(-cb / np.percentile(cb[cb > 0], 99) * 3)
        img += 0.3 * cv[..., None] * np.array([0.75, 0.82, 1.0])
    img = 1 - np.exp(-1.7 * img)
    Image.fromarray((np.clip(img, 0, 1) ** 0.92 * 255).astype(np.uint8)).save(f"proto5_{tag}.png")
print("done")
