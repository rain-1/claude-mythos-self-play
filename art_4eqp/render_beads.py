# render_beads.py — orthonormal Krawtchouk matrix of order N as a bead mandala: one glossy bead per coefficient.
# bead area ~ |phi|^p, warm beads positive / cool negative (parity signs folded so quadrants mirror),
# exact zeros = empty coral sockets.   usage: python3 render_beads.py N W out.png
import sys, numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image, ImageDraw
from sorbet import Sheet, PIG, absorb, wheel_tint, text_mask, text_w
N = int(sys.argv[1]); W = int(sys.argv[2]); out = sys.argv[3]
H = int(W * float(sys.argv[4])) if len(sys.argv) > 4 else W
SS = 2                                           # supersample for bead edges
d = np.load(f'kf{N}.npz'); S = d['S'].astype(np.float64); LP = d['LP'].astype(np.float64)
n = N + 1
k = np.arange(n)[:, None]; x = np.arange(n)[None, :]
fold = np.where(x > N // 2, (-1.0) ** np.minimum(k, N - k), 1) * np.where(k > N // 2, (-1.0) ** np.minimum(x, N - x), 1)
Q = S * np.exp2(LP) * fold
env = np.sqrt(2 * gaussian_filter(Q * Q, 1.6)) + 1e-300
glob = np.abs(Q) / np.abs(Q).max()
mag = np.clip(np.abs(Q) / env, 0, 1) * np.clip(glob / 0.08, 0, 1) ** 0.5   # local, faded where the field dies
field = 0.78 * W
pitch = field / n
ox = (W - field) / 2 + pitch / 2; oy = 0.045 * W + pitch / 2
c = N / 2
rad = np.hypot(k - c, x - c) / c
qa = np.arctan2(np.abs(k - c), np.abs(x - c)) / (np.pi / 2)      # 0 on the horizontal axis, 1 on the vertical
r = pitch * 0.47 * np.clip(mag, 0, 1) ** 0.5
Ws, Hs = W * SS, H * SS
def layer(sel, rr, dx=0, dy=0, val=None):
    im = Image.new('F', (Ws, Hs), 0.0); dr = ImageDraw.Draw(im)
    for (i, j) in zip(*np.nonzero(sel)):
        R = rr[i, j] * SS
        if R < 0.4: continue
        cx = (ox + j * pitch + dx) * SS; cy = (oy + i * pitch + dy) * SS
        dr.ellipse([cx - R, cy - R, cx + R, cy + R], fill=float(1.0 if val is None else val[i, j]))
    a = np.asarray(im, np.float32)
    return a.reshape(H, SS, W, SS).mean(axis=(1, 3))
sh = Sheet(W, H, seed=11)
pos = Q > 0; neg = Q < 0; zero = S == 0
# soft shadow under every bead
shd = gaussian_filter(layer(pos | neg, r * 1.0, pitch * 0.10, pitch * 0.14), pitch * 0.12)
sh.wash(shd, 'periwinkle', 0.30)
sh.lighten(np.clip(layer(pos | neg, r * 1.0), 0, 1), 0.9)
# warm family for +, cool family for -, walking along the quadrant angle
warm = ['strawberry', 'coral', 'peach', 'honey', 'butter']
cool = ['mint', 'sky', 'periwinkle', 'lilac', 'bubblegum']
def tint_of(fam, t):
    t = np.clip(t, 0, 0.999) * (len(fam) - 1); i = int(t); f = t - i
    a, b = np.array(PIG[fam[i]]), np.array(PIG[fam[min(i + 1, len(fam) - 1)]])
    return a ** (1 - f) * b ** f
NB = 12
for fam, sel in ((warm, pos), (cool, neg)):
    tb = np.minimum((qa * NB).astype(int), NB - 1)
    for b in range(NB):
        m = sel & (tb == b)
        if not m.any(): continue
        body = layer(m, r)
        sh.wash(body, tuple(tint_of(fam, (b + 0.5) / NB)), 2.6)
# gloss: small lighten offset up-left, plus a darker rim at the lower right
gl = gaussian_filter(layer(pos | neg, r * 0.36, -pitch * 0.13 * 1, -pitch * 0.13), pitch * 0.05)
sh.lighten(np.clip(gl, 0, 1), 0.75)
# zeros: empty coral sockets
zk, zx = np.nonzero(zero)
print('zeros', len(zk), list(zip(zk[:16], zx[:16])))
c0 = N // 2
triv = zero & ((k == c0) | (x == c0)) if N % 2 == 0 else zero & False
deep = zero & ~triv
rz = np.full((n, n), pitch * 0.40)
sh.wash(layer(triv, rz * 0.22), 'plum', 0.9)
halo = gaussian_filter(layer(deep, rz * 5.0), pitch * 0.9)
sh.lighten(np.clip(halo * 1.3, 0, 1), 0.92)
ring = layer(deep, rz * 3.6) - layer(deep, rz * 2.9)
sh.wash(gaussian_filter(ring, 0.5 * W / 1200), 'coral', 3.2)
ring2 = layer(deep, rz * 1.75) - layer(deep, rz * 1.35)
sh.wash(gaussian_filter(ring2, 0.5 * W / 1200), 'strawberry', 2.2)
sh.wash(layer(deep, rz * 0.45), 'coral', 3.2)
# caption
CAP = {214: ('Eight Empty Sockets',
             'the orthonormal Krawtchouk matrix of order 214 — bead (k, A) is the coefficient of zᵏ in (1−z)ᴬ(1+z)ᴮ with A + B = 214, scaled so every row has unit length',
             'warm beads positive, cool negative (parity signs folded so the quadrants mirror) · bead area ~ |value| / local envelope · coral: the only exact zeros off the trivial axes,',
             '(A, B, k) = (31, 183, 103) and its seven mirror images — MathOverflow 515696 asks whether any zero hides deeper than eight from every edge'),
       132: ('Eight Empty Sockets', 'order 132', '', '')}
t1, t2, t3, t4 = CAP.get(N, ('', '', '', ''))
y0 = oy + field + 0.035 * W
items = [(t1, W / 2, y0, 0.026 * W, 'serif_bold', 'mm'),
         (t2, W / 2, y0 + 0.032 * W, 0.0125 * W, 'italic', 'mm'),
         (t3, W / 2, y0 + 0.054 * W, 0.0098 * W, 'italic', 'mm'),
         (t4, W / 2, y0 + 0.071 * W, 0.0098 * W, 'italic', 'mm')]
tm = text_mask(W, H, items)
sh.wash(tm, 'ink', 2.6)
img = sh.develop(dmax=2.4)
img.save(out)
