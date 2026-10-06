"""render_silk.py — tied silk: the two sides of MO 330620 as bundles of random lattice paths.

LHS of the q-inequality counts up/right lattice paths from 0 to jk(c,d) that pass through the
j−1 knots m·k(c,d); RHS counts those through the k−1 knots m·j(c,d); the q-weight is the area.
Each bundle is a uniform sample of its own path set (each segment between knots an independent
uniform shuffle), drawn along the diagonal (x = steps taken, y = ups − rights, exaggerated).
Warm silk = fewer knots (LHS), cool silk = more knots (RHS); hue within each family walks with the
path's signed area, the very statistic the inequality compares.  Coral beads are the knots.

usage: render_silk.py W H out.png [rows=2:3,3:4,...] [key=val]
"""
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter

ARG = dict(a.split('=', 1) for a in sys.argv[4:] if '=' in a)
def P(k, d): return type(d)(ARG.get(k, d))
W, H, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
rng = np.random.default_rng(P('seed', 5))

WARM = [(1.00, 0.48, 0.58), (1.00, 0.62, 0.56), (1.00, 0.76, 0.52)]
COOL = [(0.48, 0.80, 1.00), (0.58, 0.68, 1.00), (0.70, 0.58, 1.00)]
def ramp(pal, t):
    t = np.clip(t, 0, 1) * (len(pal) - 1); i = np.minimum(t.astype(int), len(pal) - 2); f = (t - i)[:, None]
    a, b = np.array(pal)[i], np.array(pal)[i + 1]
    return a ** (1 - f) * b ** f

def sample(nseg, ups, rights, N):
    """N paths made of nseg independent segments, each a uniform shuffle of ups U and rights R. -> y (N, T+1)"""
    seglen = ups + rights
    steps = np.concatenate([np.ones(ups, np.int8), -np.ones(rights, np.int8)])
    Y = np.zeros((N, nseg * seglen + 1), np.int32)
    for s in range(nseg):
        st = np.tile(steps, (N, 1))
        idx = np.argsort(rng.random((N, seglen)), axis=1)
        st = np.take_along_axis(st, idx, 1)
        Y[:, 1 + s * seglen:1 + (s + 1) * seglen] = np.cumsum(st, 1) + Y[:, s * seglen][:, None]
    return Y

SS = 2
WW, HH = W * SS, H * SS
rows = [tuple(map(int, r.split(':'))) for r in P('rows', '2:3,3:4,3:5,4:5').split(',')]
c, dd = P('c', 6), P('d', 6)
N = P('N', 1600)
canvas = Image.new('RGBA', (WW, HH), (253, 251, 248, 255))
paper = np.asarray(canvas).astype(np.float32)
x0, x1 = 0.07 * WW, 0.93 * WW
band_top, band_bot = P('top', 0.08) * HH, P('bot', 0.80) * HH
rh = (band_bot - band_top) / len(rows)
knots_all = []
layers = []
for ri, (j, k) in enumerate(rows):
    T = j * k * (c + dd)
    yc = band_top + rh * (ri + 0.5)
    amp = P("amp", 0.16) * rh / (np.sqrt(k * (c + dd) / 4))   # 1 sd of the widest (LHS) segment = amp
    # LHS: j segments with k*c ups, k*d rights ; RHS: k segments with j*c ups, j*d rights
    YL = sample(j, k * c, k * dd, N)
    YR = sample(k, j * c, j * dd, N)
    for Y, pal, kn, fam in ((YL, WARM, [m * k * (c + dd) for m in range(j + 1)], 'L'), (YR, COOL, [m * j * (c + dd) for m in range(k + 1)], 'R')):
        S = Y.sum(1).astype(float)
        sd = S.std() + 1e-9
        tcol = 0.5 + 0.5 * np.tanh(S / (1.6 * sd))
        cols = ramp(pal, tcol)
        xs = x0 + (x1 - x0) * np.arange(T + 1) / T
        ys = yc - amp * Y
        for i in range(N):
            layers.append((rng.random(), xs, ys[i], cols[i], fam))
        knots_all.append((xs[kn], np.full(len(kn), yc), fam))

# draw: interleave the two families at random so neither sits on top
layers.sort(key=lambda t: t[0])
dr = ImageDraw.Draw(canvas, 'RGBA')
lw = max(1, int(round(P('lw', 0.0011) * WW)))
alpha = P('alpha', 26)
for _, xs, ys, col, fam in layers:
    rgb = tuple(int(255 * v) for v in col ** (1 / 2.2))
    pts = list(zip(xs.tolist(), ys.tolist()))
    dr.line(pts, fill=rgb + (alpha,), width=lw, joint='curve')
# knots: coral beads, warm knots slightly larger
img = np.asarray(canvas.convert('RGB')).astype(np.float32) / 255
yy, xx = np.mgrid[0:HH, 0:WW].astype(np.float32)
R = P('kr', 0.0062) * WW
for kx, ky, fam in knots_all:
    for px, py in zip(kx, ky):
        r = R * (1.0 if fam == 'L' else 0.78)
        x0b, x1b, y0b, y1b = int(px - 2 * r), int(px + 2 * r), int(py - 2 * r), int(py + 2 * r)
        X_, Y_ = xx[y0b:y1b, x0b:x1b] - px, yy[y0b:y1b, x0b:x1b] - py
        rr = np.sqrt(X_ ** 2 + Y_ ** 2) / r
        a = np.clip((1 - rr) * r * 0.7, 0, 1)[..., None]
        sh = np.exp(-((X_ - 0.25 * r) ** 2 + (Y_ - 0.35 * r) ** 2) / (r * r * 0.9))[..., None] * 0.25
        z = np.sqrt(np.clip(1 - rr ** 2, 0, 1))
        base = np.array([0.98, 0.52, 0.46]) if fam == 'L' else np.array([0.99, 0.62, 0.55])
        shade = base * (0.72 + 0.28 * np.clip(-0.4 * X_ / r - 0.5 * Y_ / r + 0.75 * z, 0, 1))[..., None]
        spec = np.exp(-((X_ / r + 0.35) ** 2 + (Y_ / r + 0.4) ** 2) / 0.03)[..., None]
        shade = shade + 0.6 * spec
        img[y0b:y1b, x0b:x1b] = img[y0b:y1b, x0b:x1b] * (1 - sh * (1 - a)) * (1 - a) + a * np.clip(shade, 0, 1)
pim = Image.fromarray((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)).resize((W, H), Image.LANCZOS)
pim.save(out)
print('saved', out)
