"""render_fan.py — Every Number Finds a Twin (MO 515573).

Every pair a < b with phi(a) = phi(b) and N = a + b <= 1e8, placed at height log N and at
horizontal position (b - a)/(a + b) (mirrored, so the picture is symmetric).  Each row is
normalised by its own total, so the tone is the SHAPE of the row's distribution: families
phi(ua) = phi(va) (a in a fixed residue class) fall as vertical threads at (v-u)/(v+u); the
sporadic pairs are rain.  Coral hairlines: the 435 sums N <= 1e8 that no pair reaches
(R(N) = 0); the last is 413 759.  Hue walks with |x| (mint at the middle -> strawberry at the rim).
usage: render_fan.py hist.bin GX GY M size out.png
"""
import sys, numpy as np
from scipy.ndimage import gaussian_filter, zoom, maximum_filter1d
from fractions import Fraction
import sorbet as sb

hb, GX, GY, M, S, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
Hh = np.fromfile(hb, np.float32).reshape(GY, GX)
XMAX = 0.74
gx = int(GX * XMAX)
Hh = Hh[:, :gx]
full = np.concatenate([Hh[:, ::-1], Hh], 1)          # x from -XMAX .. XMAX
rows = full.sum(1, keepdims=True)
P = full / (rows + 1e-9) * full.shape[1]              # 1 = uniform
SS = 2
W = H = S * SS
x0, x1 = 0.055 * W, 0.945 * W
y_top, y_bot = 0.050 * H, 0.845 * H
FW, FH = int(x1 - x0), int(y_bot - y_top)
# resample the field to the frame (area-average rows; field rows run bottom->top)
Pf = P[::-1]
Pr = zoom(Pf, (FH / Pf.shape[0], FW / Pf.shape[1]), order=1)
Cr = zoom(rows[::-1, 0], FH / rows.shape[0], order=1)
Pr = np.clip(Pr, 0, None)
tone = np.clip(np.log1p(Pr) / np.log1p(14.0), 0, 1) ** 0.85
# rain rows (few pairs): let single hits read as droplets, soften
tone = np.maximum(gaussian_filter(tone, (0.6 * SS, 0.6 * SS)), 0)
from scipy.ndimage import maximum_filter, gaussian_filter1d
# sparse rows (few pairs): let the droplets swell so the rain reads at full size
wl = np.clip(1 - np.log10(Cr + 1) / 3.2, 0, 1)[:, None]
drop = gaussian_filter(maximum_filter(tone, size=(3 * SS, 3 * SS)), 0.8 * SS)
tone = np.maximum(tone, wl * drop)
# threads: columns standing above their local horizontal baseline, in well-populated rows
base_ = gaussian_filter1d(gaussian_filter1d(Pr, 14 * SS, axis=1), 6 * SS, axis=0)
ratio = gaussian_filter1d(gaussian_filter1d(Pr, 0.7 * SS, axis=1), 10 * SS, axis=0) / (base_ + 1e-6)
thread = np.clip((ratio - 1.12) / 0.8, 0, 1) * np.clip((gaussian_filter(tone, 4 * SS) - 0.18) / 0.2, 0, 1) * np.clip(np.log10(Cr + 1) / 4 - 0.25, 0, 1)[:, None]
sh = sb.Sheet(W, H, seed=11)
xs = np.linspace(-XMAX, XMAX, FW)[None, :] * np.ones((FH, 1))
hue = 0.44 + 0.62 * np.abs(xs) / XMAX
nb = 28
dens = np.zeros((H, W), np.float32)
for b in range(nb):
    lo, hi = b / nb, (b + 1) / nb
    m = ((np.abs(xs) / XMAX >= lo) & (np.abs(xs) / XMAX < hi)).astype(np.float32)
    layer = np.zeros((H, W), np.float32)
    layer[int(y_top):int(y_top) + FH, int(x0):int(x0) + FW] = tone * m
    sh.wash(2.6 * layer, sb.wheel_tint(0.44 + 0.62 * (lo + hi) / 2))
th_ = np.zeros((H, W), np.float32)
th_[int(y_top):int(y_top) + FH, int(x0):int(x0) + FW] = thread
sh.wash(0.55 * th_, 'periwinkle')
sh.wash(0.25 * th_, 'plum')
# soft glow of the curtain's upper body
body = np.zeros((H, W), np.float32)
body[int(y_top):int(y_top) + FH, int(x0):int(x0) + FW] = tone
sh.wash(0.30 * gaussian_filter(body, 0.012 * W), 'lilac')

def yof(N):
    t = (np.log10(N) - 1) / (np.log10(M) - 1)
    return y_bot - t * FH

# coral: the unreachable sums
R = np.fromfile('data/R1e8.bin', np.uint32)
Z = np.nonzero(R[3:] == 0)[0] + 3
Z = Z[Z >= 10]
cx_ = (x0 + x1) / 2
rb = 2.6 * SS * S / 2560
B = sb.discs(W, H, [cx_] * (len(Z) - 1), [yof(N) for N in Z[:-1]], [rb] * (len(Z) - 1))
B = gaussian_filter(B, 0.5 * SS)
sh.lighten(np.clip(gaussian_filter(B, 2 * SS) * 3, 0, 1), 0.7)
sh.wash(1.3 * B, 'coral')
last = Z[-1]
Ll = sb.lines(W, H, [[(x0 - 0.01 * FW, yof(last)), (x1 + 0.01 * FW, yof(last))]], 2.4 * SS * S / 2560, [1.0], sigma=0.6 * SS)
sh.lighten(np.clip(gaussian_filter(Ll, 3 * SS) * 3, 0, 1), 0.6)
sh.wash(1.25 * Ll, 'coral')

# label the strongest family threads at the top: match peaks to (v-u)/(v+u)
top = P[int(0.93 * GY):].mean(0)[gx:]                 # right half, x >= 0
pk = [i for i in range(3, gx - 3) if top[i] == top[i - 3:i + 4].max() and top[i] > 3.0]
pk = sorted(pk, key=lambda i: -top[i])[:7]
fams = []
for i in pk:
    xv = (i + 0.5) / GX
    best = min(((abs(Fraction(v - u, v + u) - Fraction(xv).limit_denominator(10 ** 6)), u, v)
                for u in range(1, 40) for v in range(u + 1, 60)), key=lambda t: t[0])
    fams.append((xv, best[1], best[2]))
fs = S / 2560 * SS
items = []
ticks = []
fams = [f for f in fams if f[0] > 0.1]
keep = []
for f in fams:
    if all(abs(f[0] - g[0]) > 0.035 for g in keep): keep.append(f)
fams = keep
for xv, u, v in fams:
    X = x0 + (xv + XMAX) / (2 * XMAX) * FW
    items.append((f'{u}:{v}', X, y_top - 10 * fs, 19 * fs, 'mono', 'mb'))
# log-N ticks on the left
for e in range(1, 9):
    y = yof(10 ** e)
    items.append((f'10{str(e).translate(str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹"))}', x0 - 16 * fs, y, 20 * fs, 'serif', 'rm'))
    ticks.append([(x0 - 10 * fs, y), (x0 - 2 * fs, y)])
items.append((f'{last:,}'.replace(',', ' ') + ' — the last sum no twin pair can reach', x1 + 0.0 * FW, yof(last) - 14 * fs, 23 * fs, 'italic', 'rb'))
sh.wash(0.6 * sb.lines(W, H, ticks, 1.5 * fs, sigma=0.5 * SS), 'ink')
sh.wash(3.0 * sb.text_mask(W, H, items), 'ink')
yy = np.linspace(0, 1, H)[:, None] * np.ones((1, W))
band = np.clip((yy - 0.875) / 0.01, 0, 1)
sh.A *= (1 - 0.6 * band)[..., None]
cap = [('Every Number Finds a Twin', 0.07 * W, 0.915 * H, 58 * fs, 'serif_bold', 'ls'),
       ('Every pair a < b with φ(a) = φ(b): height log(a + b), across (b − a)/(a + b). Families such as φ(a) = φ(2a), φ(3a) = φ(4a) fall as threads (labelled a:b ratios).',
        0.07 * W, 0.945 * H, 23 * fs, 'italic', 'ls'),
       (f'MO 515573 · every pair with a + b ≤ {M:.0e} · coral beads: the {int((R[3:] == 0).sum())} sums N ≤ 10⁸ with no representation (R(N) = 0); each row normalised to its own total'.replace('1e+08', '10⁸'),
        0.07 * W, 0.970 * H, 20 * fs, 'mono', 'ls')]
sh.wash(3.0 * sb.text_mask(W, H, cap), 'ink')
img = sh.develop(dmax=2.4, glow=0.12)
sb.finish(img, S, out)
print('families', fams, 'zeros', len(Z), 'last', last)
