# render_kraw.py — the orthonormal Krawtchouk matrix of order N as a sorbet mandala, one coefficient per pixel.
# usage: python3 render_kraw.py N W out.png [zeros-file]
import sys, numpy as np
from scipy.ndimage import gaussian_filter, distance_transform_edt
from sorbet import Sheet, PIG, absorb, wheel_tint, text_mask, text_w, discs
N = int(sys.argv[1]); W = int(sys.argv[2]); out = sys.argv[3]
H = W
d = np.load(f'kf{N}.npz'); S = d['S'].astype(np.float32); LP = d['LP'].astype(np.float64)
n = N + 1
k = np.arange(n)[:, None]; x = np.arange(n)[None, :]
# fold the parity signs so the four quadrants mirror each other (|Q| = |phi| exactly)
fold = np.where(x > N // 2, (-1.0) ** np.minimum(k, N - k), 1) * np.where(k > N // 2, (-1.0) ** np.minimum(x, N - x), 1)
Q = (S * np.exp2(LP) * fold).astype(np.float32)
zero = (S == 0)
rms = np.sqrt(gaussian_filter(Q * Q, 2.5)) + 1e-30
g = np.clip(Q / rms / 1.25, -1, 1)
amp = rms * np.sqrt(N)                     # ~0.6-1 inside the disc, exponentially small outside
w = np.clip((np.log10(amp + 1e-30) + 3.2) / 2.6, 0, 1) ** 1.6
# geometry on the sheet
ox = (W - n) // 2; oy = int(0.06 * H) if W > n + 0.1 * W else (W - n) // 2
sh = Sheet(W, H, seed=7)
c = N / 2
ang = (np.arctan2(k - c, x - c) / (2 * np.pi) + 0.5 + 0.06) % 1
rad = np.hypot(k - c, x - c) / c
# hue by angle (four-fold kaleidoscope repeats it twice for a rose), light lobes pale, deep lobes full
hue = (ang * 2) % 1
T = np.zeros((n, n, 3), np.float32)
for i in range(64):
    m = (np.floor(hue * 64) == i)
    T[m] = absorb(wheel_tint((i + 0.5) / 64))
lobe = 0.5 + 0.5 * g
dens = w * (0.10 + 0.95 * lobe ** 1.4) * (1.0 - 0.25 * np.clip(rad - 0.92, 0, 1) / 0.08)
A = (dens[..., None] * T) * 1.05
# a whisper of plum ink on the nodal seams where |g| small inside the disc
seam = w * np.exp(-(g / 0.12) ** 2) * 0.10
A += seam[..., None] * absorb('plum')
sh.A[oy:oy + n, ox:ox + n] += A
# zeros: coral pearls with a paper halo (non-trivial integer zeros only)
zk, zx = np.nonzero(zero)
print('zeros', len(zk))
if len(zk):
    pr = max(5, W / 420)
    halo = discs(W, H, zx + ox, zk + oy, np.full(len(zk), pr * 2.4), sigma=pr * 0.5)
    sh.lighten(np.clip(halo, 0, 1), 0.85)
    shadow = discs(W, H, zx + ox + pr * 0.25, zk + oy + pr * 0.35, np.full(len(zk), pr), sigma=pr * 0.35)
    sh.wash(shadow, 'periwinkle', 0.35)
    body = discs(W, H, zx + ox, zk + oy, np.full(len(zk), pr), sigma=0.6)
    sh.lighten(np.clip(body, 0, 1), 1.0)
    sh.wash(body, 'coral', 1.5)
    gl = discs(W, H, zx + ox - pr * 0.35, zk + oy - pr * 0.35, np.full(len(zk), pr * 0.32), sigma=pr * 0.15)
    sh.lighten(np.clip(gl, 0, 1), 0.85)
img = sh.develop(dmax=1.7)
img.save(out)
