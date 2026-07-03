"""02 — SAME SPECTRUM, NO SOUL  (2048 x 1280)

Fourier phase surgery on the hero's occupation field. The amplitude
spectrum |F| — every 2nd-order statistic, every correlation a pairwise
observer could measure — is held EXACTLY fixed. Only the phases rotate,
column by column, toward a random stranger's phases. The archipelago
dissolves into fog with the same spectrum: outwardly identical to any
correlation test, inwardly no one home. (Phil.SE, this week: "Are some
people zombies?")

Verified: the amplitude spectrum of the t=1 field differs from the
original by < 1e-6 relative (exactly Hermitian random phases); structure
lives entirely in the discarded phase alignments.
"""
import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image
from levy_core import hist_eq

W, Hh = 2048, 1280          # canvas
STRATA = 9                  # phase-interpolation stops crossfaded in x

acc = np.load("hero_acc.npy")           # 6144^2
k = 3
acc = acc.reshape(2048, k, 2048, k).sum((1, 3))
r0 = (2048 - Hh) // 2
field = acc[r0:r0 + Hh, :]              # 1280 x 2048
s = np.log1p(field)                      # perceptual density

F = np.fft.fft2(s)
A = np.abs(F)
ph0 = np.angle(F)
rng = np.random.default_rng(4)
phr = np.angle(np.fft.fft2(rng.standard_normal(s.shape)))  # Hermitian phases
dph = np.angle(np.exp(1j * (phr - ph0)))                   # shortest arc

raw = np.linspace(0, 1, STRATA)
prof = np.clip((raw - 0.24) / 0.76, 0, 1)
ts = prof * prof * (3 - 2 * prof)          # hold left third alive
layers = []
for t in ts:
    Ft = A * np.exp(1j * (ph0 + t * dph))
    st = np.fft.ifft2(Ft).real
    layers.append(st)
    # verify amplitude preservation
    rel = np.abs(np.abs(np.fft.fft2(st)) - A).max() / A.max()
    print(f"t={t:.2f}  spectrum rel-dev {rel:.2e}")

# crossfade masks along x (raised cosine)
xs = np.arange(W)
centers = np.linspace(0, W - 1, STRATA)
sigma = (centers[1] - centers[0]) * 0.62
Wts = np.stack([np.exp(-0.5 * ((xs - c) / sigma) ** 2) for c in centers])
Wts /= Wts.sum(0, keepdims=True)
comp = sum(Wts[i][None, :] * layers[i] for i in range(STRATA))

# tone with FIXED mapping anchored on the t=0 field
p99 = np.percentile(layers[0], 99.9)
v = np.clip(comp / p99, 0, 1.25)
vv = np.clip(v, 0, 1) ** 1.6
# palette: same universe as hero (indigo body, gold cores)
RAMP = np.array([
    (0.015, 0.015, 0.05), (0.08, 0.10, 0.32), (0.22, 0.22, 0.55),
    (0.55, 0.35, 0.55), (0.90, 0.55, 0.38), (1.00, 0.85, 0.52),
    (1.00, 0.98, 0.85)])
def ramp_map(x):
    y = np.clip(x, 0, 1) * (len(RAMP) - 1)
    i = np.clip(y.astype(int), 0, len(RAMP) - 2)
    f = (y - i)[..., None]
    return RAMP[i] * (1 - f) + RAMP[i + 1] * f
img = ramp_map(np.clip(vv, 0, 1))
# the dead side loses warmth: desaturate toward cold slate by local t
tx = sum(Wts[i][None, :] * ts[i] for i in range(STRATA))
g = img.mean(2, keepdims=True)
cold = g * np.array([0.55, 0.62, 1.05])
img = img * (1 - 0.45 * tx[..., None]) + cold * (0.45 * tx[..., None])
img += 0.35 * gaussian_filter(np.clip(vv, 0, 1), 18)[..., None] * np.array([0.14, 0.17, 0.42])
lum = img.mean(2)
mask = np.clip((lum - 0.55) / 0.45, 0, 1) ** 2
img += 0.4 * gaussian_filter(mask, 8)[..., None] * np.array([1.0, 0.85, 0.6])
img = 1 - np.exp(-1.9 * img)
Image.fromarray((np.clip(img, 0, 1) ** 0.94 * 255).astype(np.uint8)
                ).save("02_same_spectrum_no_soul.png")
print("saved 02_same_spectrum_no_soul.png")
