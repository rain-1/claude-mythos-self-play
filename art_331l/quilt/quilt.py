# A weighing matrix as a patchwork quilt. Goethals–Seidel array from four ternary circulants A,B,C,D;
# each circulant has its own hue (so the 4×4 block layout is a Latin square of colours), +1 = pale print,
# −1 = deeper print of the same hue, 0 = white patch with a coral French knot. Puffy height-field patches,
# sunken seams with running stitches, a binding, soft light from the top-left.
import numpy as np, sys, argparse
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter, shift as ndshift
sys.path.insert(0, '..'); sys.path.insert(0, '.')
import silk

ap = argparse.ArgumentParser()
ap.add_argument('seqfile'); ap.add_argument('--W', type=int, default=1024)
ap.add_argument('--out', default='quilt.png'); ap.add_argument('--title', default='')
ap.add_argument('--sub', default=''); ap.add_argument('--leg', default='')
a = ap.parse_args()
lines = [l.strip() for l in open(a.seqfile) if l.strip() and l.strip()[0] in '+-0']
X = [np.array([{'+': 1, '-': -1, '0': 0}[c] for c in l]) for l in lines[:4]]
v = len(X[0])
def circ(x): return np.array([[x[(j - i) % v] for j in range(v)] for i in range(v)])
R = np.fliplr(np.eye(v, dtype=int))
A, B, C, D = [circ(x) for x in X]
G = np.block([[A, B @ R, C @ R, D @ R],
              [-B @ R, A, D.T @ R, -C.T @ R],
              [-C @ R, -D.T @ R, A, B.T @ R],
              [-D @ R, C.T @ R, -B.T @ R, A]])
n = 4 * v; k = int((G[0] != 0).sum())
assert (G @ G.T == k * np.eye(n, dtype=int)).all(), 'not a weighing matrix'
print('W(%d,%d) verified' % (n, k))
np.savetxt(a.seqfile + '.matrix.txt', G, fmt='%2d')
src = np.block([[np.full((v, v), q) for q in row] for row in [[0, 1, 2, 3], [1, 0, 3, 2], [2, 3, 0, 1], [3, 2, 1, 0]]])

W = a.W; S = W / 4096.0; Hh = int(W * 1.12)
qs = int(3560 * S); x0 = (W - qs) // 2; y0 = int(470 * S)
cell = qs / n
yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)
u = (xx - x0) / cell; w = (yy - y0) / cell
inq = (u >= 0) & (u < n) & (w >= 0) & (w < n)
iu = np.clip(u.astype(int), 0, n - 1); iw = np.clip(w.astype(int), 0, n - 1)
fu = u - np.floor(u); fw = w - np.floor(w)
val = G[iw, iu]; sq = src[iw, iu]
hues = [silk.WHEEL[0], silk.WHEEL[2], silk.WHEEL[4], silk.WHEEL[6]]  # strawberry, butter, mint, periwinkle
hues = np.array(hues)
pale = 1 - 0.36 * (1 - hues); deep = 1 - 0.88 * (1 - hues)
deep = np.clip(deep, 0, 1)
col = np.where((val > 0)[..., None], pale[sq], deep[sq])
col = np.where((val == 0)[..., None], np.array([0.995, 0.99, 0.985]), col)
# prints: + small dots, − fine diagonal stripes, in a lighter/darker version of the patch colour
pd = ((fu * 3 % 1 - 0.5) ** 2 + (fw * 3 % 1 - 0.5) ** 2) < 0.06
stripe = (np.sin((fu + fw) * np.pi * 8) > 0.55)
col = np.where(((val > 0) & pd)[..., None], col * 0.93 + 0.07, col)
col = np.where(((val < 0) & stripe)[..., None], np.minimum(col * 1.10 + 0.04, 1), col)
# puffy patch height: pillow, seams sink
pil = (np.sin(np.pi * fu) * np.sin(np.pi * fw)) ** 0.32
h = np.where(inq, 0.6 + 0.4 * pil, 0.0) * cell * 0.22
# binding strip around the quilt
bw = cell * 1.3
du = np.minimum(np.minimum(xx - (x0 - bw), (x0 + qs + bw) - xx), np.minimum(yy - (y0 - bw), (y0 + qs + bw) - yy))
inb = (du > 0) & ~inq
h = np.where(inb, cell * 0.24 * np.sin(np.clip(du / bw, 0, 1) * np.pi / 2) ** 0.5, h)
col = np.where(inb[..., None], np.array([0.80, 0.70, 0.95]), col)  # lilac binding
rng = np.random.default_rng(5)
wav = gaussian_filter(rng.normal(0, 1, (Hh // 16 + 1, W // 16 + 1)), 14)
wav = np.kron(wav, np.ones((16, 16)))[:Hh, :W]; wav = gaussian_filter(wav / wav.std(), 8 * S + 1)
msk_ = gaussian_filter((inq | inb).astype(np.float32), cell * 2.0) * (inq | inb)
h = h + msk_ * (wav + 2.0) * cell * 1.0
hs = gaussian_filter(h, 0.8 * S + 0.6)
gy, gx = np.gradient(hs)
nrm = np.stack([-gx, -gy, np.ones_like(gx)], -1); nrm /= np.linalg.norm(nrm, axis=-1, keepdims=True)
L = np.array([-0.5, -0.6, 0.62]); L /= np.linalg.norm(L)
diff = np.clip((nrm * L).sum(-1), 0, 1)
ao = np.clip(1 - 1.2 * (gaussian_filter(hs, cell * 0.4) - hs) / (cell * 0.22), 0.6, 1.1)
shade = (0.55 + 0.52 * diff) * ao
img = col * shade[..., None]
# running stitches along the seams (quilting): short dashes slightly inside each seam
sx = (np.abs(fu - 0.5) > 0.40) & (np.abs(fu - 0.5) < 0.45) & ((fw * 4 % 1) < 0.55)
sy = (np.abs(fw - 0.5) > 0.40) & (np.abs(fw - 0.5) < 0.45) & ((fu * 4 % 1) < 0.55)
st = (sx | sy) & inq & (cell > 14)
img = np.where(st[..., None], img * 0.85 + 0.15 * 0.98, img)
# coral French knots on the zeros
zr = 0.17
dz = np.sqrt((fu - 0.5) ** 2 + (fw - 0.5) ** 2)
zm = inq & (val == 0)
kn = np.clip((zr - dz) * cell + 0.5, 0, 1) * zm
nz = np.sqrt(np.clip(1 - (dz / zr) ** 2, 0, 1))
knc = silk.CORAL[None, None, :] * (0.65 + 0.35 * nz)[..., None] + 0.3 * np.exp(-(((fu - 0.44) ** 2 + (fw - 0.43) ** 2) / 0.003))[..., None]
img = img * (1 - kn[..., None]) + knc * kn[..., None]
# floor + shadow
floor = silk.linen(Hh, W, period=max(2.0, 7 * S), base=(0.985, 0.982, 0.990))
m = (inq | inb).astype(np.float32)
sh = ndshift(gaussian_filter(m, 30 * S + 1), (24 * S, 16 * S), order=1)
floor = floor * (1 - sh[..., None] * np.array([0.20, 0.21, 0.10]))
ma = gaussian_filter(m, 0.6)[..., None]
img = img * ma + floor * (1 - ma)
im = Image.fromarray(silk.to_u8(img)); dr = ImageDraw.Draw(im)
ink = tuple(int(c * 255) for c in silk.INK); soft = tuple(int(0.30 * 255 + 0.70 * c * 255) for c in silk.INK)
X0 = x0 - int(bw); Y0 = int(110 * S)
dr.text((X0, Y0), a.title or f'W({n},{k})', font=silk.font('title', int(120 * S)), fill=ink)
dr.text((X0, Y0 + int(150 * S)), a.sub, font=silk.font('ital', int(56 * S)), fill=ink)
dr.text((X0, Y0 + int(225 * S)), a.leg, font=silk.font('reg', int(44 * S)), fill=soft)
im.save(a.out)
print('saved', a.out)
