"""01 hero compose: tone + epoch hue + chords + aura. Preview or final.
Usage: python3 hero_compose.py preview|final [tag]"""
import sys
import numpy as np
from scipy.ndimage import gaussian_filter, zoom
from PIL import Image
from levy_core import hist_eq

MODE = sys.argv[1] if len(sys.argv) > 1 else "preview"
TAG = sys.argv[2] if len(sys.argv) > 2 else ""

acc = np.load("hero_acc.npy")            # 6144^2 float32
chord = np.load("hero_chord.npy")
M = np.load("hero_moments.npz")
mw, mt, mt2, T = M["mw"].astype(np.float64), M["mt"].astype(np.float64), \
                 M["mt2"].astype(np.float64), float(M["T"])
Tn = T / float(np.load("hero_moments.npz")["T"])  # 1; ranks were already /T_est

if MODE == "preview":
    S = 2048
    def pool(a, k):
        return a.reshape(a.shape[0]//k, k, a.shape[1]//k, k).sum((1, 3))
    acc = pool(acc, 3); chord = pool(chord, 3)
else:
    S = acc.shape[0]

# epoch stats at moment-buffer res -> upscale to S
tau = mt / np.maximum(mw, 1e-9)
var = np.maximum(mt2 / np.maximum(mw, 1e-9) - tau ** 2, 0.0)
# normalise tau to [0,1] using its occupied range
occ = mw > 0
lo, hi = np.percentile(tau[occ], [1, 99])
tau = np.clip((tau - lo) / (hi - lo), 0, 1)
sig = np.sqrt(var) / max(hi - lo, 1e-9)          # epoch spread, 0..~0.5
tau_s = gaussian_filter(tau * mw, 2.0) / np.maximum(gaussian_filter(mw, 2.0), 1e-9)
sig_s = gaussian_filter(sig * mw, 2.0) / np.maximum(gaussian_filter(mw, 2.0), 1e-9)
ztau = zoom(np.clip(tau_s, 0, 1), S / tau.shape[0], order=1)
zsig = zoom(np.clip(sig_s, 0, 1), S / tau.shape[0], order=1)

# ---- epoch palette: indigo dawn -> teal -> jade -> rose -> ember -> amber -> gold
EPOCH = np.array([
    (0.15, 0.18, 0.70), (0.10, 0.45, 0.90), (0.10, 0.70, 0.65),
    (0.55, 0.35, 0.75), (0.90, 0.32, 0.45), (1.00, 0.55, 0.22),
    (1.00, 0.80, 0.32), (1.00, 0.93, 0.68)])

def epoch_rgb(t):
    x = np.clip(t, 0, 1) * (len(EPOCH) - 1)
    i = np.clip(x.astype(int), 0, len(EPOCH) - 2)
    f = (x - i)[..., None]
    return EPOCH[i] * (1 - f) + EPOCH[i + 1] * f

def compose(gamma=3.4, blur=1.0, aura=0.75, chord_amp=0.42, desat=1.2,
            expo=2.0, mixlin=0.45, name="hero_preview.png"):
    ab = gaussian_filter(acc, blur)
    ve = hist_eq(ab, gamma=gamma)
    vl = np.clip(ab / np.percentile(ab[ab > 0], 99.0), 0, 1.6) ** 0.6
    v = (1 - mixlin) * ve + mixlin * vl        # rank detail + true hierarchy
    hue = epoch_rgb(ztau)
    pale = np.clip(zsig * desat, 0, 1)[..., None]
    hue = hue * (1 - pale) + pale * np.array([1.0, 0.97, 0.90])
    # saturated body, only true cores whiten
    img = hue * (np.clip(v, 0, 1) ** 1.25)[..., None]
    img += np.array([1.0, 0.95, 0.85]) * (np.clip(v - 0.82, 0, 1) ** 1.8)[..., None] * 0.95
    au = gaussian_filter(v, S * 0.009)
    img += aura * au[..., None] * np.array([0.13, 0.17, 0.44])
    au2 = gaussian_filter(v, S * 0.035)
    img += 0.55 * au2[..., None] * np.array([0.10, 0.11, 0.30])
    cb = gaussian_filter(chord, blur)
    if (cb > 0).any():
        cv = 1 - np.exp(-cb / np.percentile(cb[cb > 0], 99.2) * 3)
        img += chord_amp * cv[..., None] * np.array([0.60, 0.78, 1.0])
    lum = img.mean(2)
    mask = np.clip((lum - 0.60) / 0.40, 0, 1) ** 2
    img += 0.45 * gaussian_filter(mask, S * 0.004)[..., None] * np.array([1.0, 0.88, 0.65])
    img = 1 - np.exp(-expo * img)
    img = np.clip(img, 0, 1) ** 0.94
    out = (img * 255).astype(np.uint8)
    im = Image.fromarray(out)
    if MODE == "final":
        im = im.resize((4096, 4096), Image.LANCZOS)
    im.save(name)
    print("saved", name)

if MODE == "preview":
    compose(name=f"hero_preview{TAG}.png")
else:
    compose(name="01_the_moment_that_escaped.png")
