"""Tissue-paper discs on a lightbox: MO 458793 (random discs of area pi/n on the unit disc).

Disc n has radius n^-1/2 and a uniform random centre in the unit disc.  Each disc is a sheet of
translucent tissue; the light table shines through the window (the unit disc), so brightness is
exp(-coverage) and the points not yet covered glow white.

usage: python3 lightbox.py SIZE N SEED OUT.png [--hue angle|index|size] [--dens 0.16]
"""
import sys, json, argparse
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

ap = argparse.ArgumentParser()
ap.add_argument('size', type=int)
ap.add_argument('N', type=int)
ap.add_argument('seed', type=int)
ap.add_argument('out')
ap.add_argument('--hue', default='angle')
ap.add_argument('--dens', type=float, default=0.16)
ap.add_argument('--scale', type=float, default=0.40, help='window radius / image size')
ap.add_argument('--holes', default='', help='json of hole info to write')
ap.add_argument('--ss', type=int, default=1)
ap.add_argument('--last', default='')
ap.add_argument('--cy', type=float, default=0.5)
args = ap.parse_args()

S = args.size * args.ss
R = args.scale * S          # unit radius in pixels
cx = S / 2; cy = args.cy * S
rng = np.random.default_rng(args.seed)
# centres uniform in disc
POOL = 10 ** 6   # fixed pool: disc k is the same whatever N is
u = rng.random(POOL)[:args.N]; th = rng.random(POOL)[:args.N] * 2 * np.pi
rad = np.sqrt(u)
X = rad * np.cos(th); Y = rad * np.sin(th)
r = 1.0 / np.sqrt(np.arange(1, args.N + 1))

def lin(h):
    h = h.lstrip('#'); c = np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)]) / 255.0
    return c ** 2.2
WHEEL = [lin(h) for h in ['ff8fa6', 'ffa98a', 'ffc98a', 'ffe58a', 'cdee90', '9fe8c4', '9adcf3',
                          'a9bcf7', 'c3aef5', 'eda9ea']]
def wheel(t):
    t = (t % 1.0) * len(WHEEL)
    i = int(t) % len(WHEEL); f = t - int(t)
    a, b = WHEEL[i], WHEEL[(i + 1) % len(WHEEL)]
    return a ** (1 - f) * b ** f

yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
# absorbance per channel
A = np.zeros((S, S, 3), np.float32)
cover = np.zeros((S, S), np.int32)
# fibre texture: anisotropic noise, fixed per image (tissue is all the same paper)
fr = np.random.default_rng(7)
fib = gaussian_filter(fr.standard_normal((S, S)).astype(np.float32), (0.7 * args.ss, 3.0 * args.ss)) + gaussian_filter(fr.standard_normal((S, S)).astype(np.float32), (3.0 * args.ss, 0.7 * args.ss)) + 0.7 * gaussian_filter(fr.standard_normal((S, S)).astype(np.float32), 1.4 * args.ss)
fib = fib / fib.std()
fib2 = gaussian_filter(fr.standard_normal((S, S)).astype(np.float32), 8 * args.ss); fib2 /= fib2.std()

for n in range(args.N):
    rp = r[n] * R
    px = cx + X[n] * R; py = cy + Y[n] * R
    x0 = max(int(px - rp - 2), 0); x1 = min(int(px + rp + 3), S)
    y0 = max(int(py - rp - 2), 0); y1 = min(int(py + rp + 3), S)
    if x1 <= x0 or y1 <= y0:
        continue
    d = np.hypot(xx[y0:y1, x0:x1] - px, yy[y0:y1, x0:x1] - py)
    inside = np.clip(rp - d + 0.5, 0, 1)            # antialiased coverage
    edge = np.exp(-((d - rp) / (0.9 * args.ss + 0.004 * rp)) ** 2)   # cut edge reads a little denser
    if args.hue == 'angle':
        t = np.arctan2(Y[n], X[n]) / (2 * np.pi)
    elif args.hue == 'index':
        t = (n * 0.6180339887) % 1
    else:
        t = 0.5 * np.log(n + 1) / np.log(args.N + 1)
    c = wheel(t)
    sig = -np.log(c)
    sig = sig / sig.max()
    dens = args.dens * (1 + 0.18 * fib[y0:y1, x0:x1] + 0.12 * fib2[y0:y1, x0:x1]) * inside + 0.28 * edge * inside
    A[y0:y1, x0:x1] += dens[..., None] * sig[None, None, :]
    cover[y0:y1, x0:x1] += (d < rp)

# ---- light table seen through a round window in a cream mat ----
dw = np.hypot(xx - cx, yy - cy) / R
win = np.clip((1 - dw) * R + 0.5, 0, 1)
back = 1.06 - 0.12 * dw ** 2
img = back[..., None] * np.exp(-A)
# mat bevel shadow: the mat sits above the tissue, light from the top-left of the room
ang = np.arctan2(yy - cy, xx - cx)
sh = np.clip(1 - (1 - dw) * R / (0.022 * R), 0, 1) ** 2 * (0.45 + 0.35 * np.cos(ang + 2.36))
img *= (1 - 0.35 * sh)[..., None]
# holes glow
hole = ((cover == 0) & (dw < 1)).astype(np.float32)
print('uncovered px', int(hole.sum()))
glow = gaussian_filter(hole, 2.5 * args.ss) * 1.0 + gaussian_filter(hole, 12 * args.ss) * 2.2 + gaussian_filter(hole, 40 * args.ss) * 2.6
img += glow[..., None] * np.array([1.0, 0.96, 0.86])[None, None, :]
# mat card: cream white, grain, bevel ring lit on lower-right, shadowed upper-left
grain = gaussian_filter(np.random.default_rng(3).standard_normal((S, S)).astype(np.float32), 1.2 * args.ss)
grain /= grain.std()
mat = np.array([0.945, 0.93, 0.91])[None, None, :] * (1 + 0.012 * grain[..., None])
bev = np.clip(((dw - 1) * R) / (0.028 * R), 0, 1)
bevring = (bev > 0) & (bev < 1)
lit = 0.5 + 0.5 * np.cos(ang - 0.785)       # bevel facing lower-right catches light
bevcol = np.array([0.97, 0.955, 0.94])[None, None, :] * (0.86 + 0.16 * lit)[..., None]
outside = np.where(bevring[..., None], bevcol, mat)
img = img * win[..., None] + outside * (1 - win[..., None])
# coral pencil rings round the holes that are left (one per component)
from scipy.ndimage import label, center_of_mass
lab, k = label(hole > 0)
info = []
if k:
    for c in center_of_mass(hole, lab, range(1, k + 1)):
        info.append([float(c[1]), float(c[0])])
    # merge pixel-split fragments of one hole: cluster centroids closer than 0.07 R
    merged = []
    for p in info:
        for q in merged:
            if np.hypot(p[0] - q[0] / q[2], p[1] - q[1] / q[2]) < 0.10 * R:
                q[0] += p[0]; q[1] += p[1]; q[2] += 1; break
        else:
            merged.append([p[0], p[1], 1])
    info = [[q[0] / q[2], q[1] / q[2]] for q in merged]
coral = np.array([0.98, 0.42, 0.36]) ** 2.2
LAST = [float(v) for v in args.last.split(',')] if args.last else None
for (hx, hy) in info:
    if LAST and np.hypot(hx - (cx + LAST[0] * R), hy - (cy + LAST[1] * R)) < 0.1 * R:
        continue
    rr = 0.06 * R
    d = np.hypot(xx - hx, yy - hy)
    m = np.exp(-((d - rr) / (2.4 * args.ss)) ** 2) * 0.85
    img = img * (1 - m[..., None]) + coral[None, None, :] * m[..., None]
if args.last:
    lx, ly = [float(v) for v in args.last.split(',')]
    hx, hy = cx + lx * R, cy + ly * R
    d = np.hypot(xx - hx, yy - hy)
    for rr in (0.075 * R, 0.088 * R):
        m = np.exp(-((d - rr) / (2.4 * args.ss)) ** 2) * 0.85
        img = img * (1 - m[..., None]) + coral[None, None, :] * m[..., None]
if args.holes:
    json.dump({'N': args.N, 'holes': [[(x - cx) / R, (y - cy) / R] for x, y in info]}, open(args.holes, 'w'))
img = img / (1 + img / 6.0) * 1.12
srgb = np.clip(img, 0, 1) ** (1 / 2.2)
out = Image.fromarray((srgb * 255 + 0.5).astype(np.uint8))
if args.ss > 1:
    out = out.resize((args.size, args.size), Image.LANCZOS)
out.save(args.out)
