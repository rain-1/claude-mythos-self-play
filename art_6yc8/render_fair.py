"""render_fair.py — Every Wheel Leans a Little (Ferris wheel numbers, MO 515611).

Three wheels at a pastel fair.  Each carries every divisor of its n as a gondola of AREA
proportional to the divisor, hung at equally spaced points in the best order our annealer
found (heaviest car at the top); the centre of mass misses the hub by ~0.002, which is as
close as we could get and — by the exact solver — as close as anyone can get without
reaching zero.  Hue of a gondola = log d / log n (light cars cool, heavy cars warm).
usage: render_fair.py size out.png
"""
import sys, numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter
import sorbet as sb

S = int(sys.argv[1]); out = sys.argv[2]
SS = 2
W = H = S * SS
sh = sb.Sheet(W, H, seed=5)
yy = np.linspace(0, 1, H, dtype=np.float32)[:, None] * np.ones((1, W), np.float32)
# sky: faint periwinkle high up, peach glow toward the horizon
HOR = 0.815
sh.wash(0.20 * np.clip(1 - yy / HOR, 0, 1) ** 1.4, 'sky')
sh.wash(0.26 * np.exp(-((yy - HOR) / 0.16) ** 2) * (yy < HOR), 'peach')
sh.wash(0.07 * np.exp(-((yy - HOR) / 0.06) ** 2) * (yy < HOR), 'butter')
sun = sb.discs(W, H, [0.16 * W], [0.17 * H], [0.055 * W])
sh.wash(0.20 * gaussian_filter(sun, 0.02 * W) + 0.22 * gaussian_filter(sun, SS * 2), 'honey')
sh.wash(0.10 * gaussian_filter(sun, 0.06 * W), 'peach')
# meadow
g = (yy > HOR).astype(np.float32)
meadow = g * (0.45 + 0.12 * sb.lowfreq(H, W, W // 12, 3))
sh.wash(gaussian_filter(meadow, SS * 1.5), 'mint')
sh.wash(gaussian_filter(g * np.clip((yy - HOR) / 0.08, 0, 1) * 0.10, SS * 2), 'lime')

WHEELS = [  # n, hub x, hub y, radius (fractions of S)
    (720, 0.175, 0.560, 0.135),
    (55440, 0.505, 0.395, 0.300),
    (5040, 0.825, 0.520, 0.165),
]

def load_best(n):
    l = open(f'data/best{n}.txt').readline().split()
    return float(l[0]), [int(v) for v in l[1:]]

ink_lines = []; ink_w = []
fine_lines = []
labels = []
coral_pts = []
rims = {}
LOUPE = None
for (n, hx, hy, R) in WHEELS:
    gap, perm = load_best(n)
    k = len(perm)
    cx, cy, R = hx * W, hy * H, R * W
    ground = HOR * H + 0.012 * H
    # A-frame legs
    for sgn in (-1, 1):
        ink_lines.append(([(cx, cy), (cx + sgn * 0.62 * R, ground)], 1.0))
        ink_lines.append(([(cx, cy), (cx + sgn * 0.40 * R, ground)], 0.55))
    # cross braces
    for t in (0.45, 0.75):
        y = cy + t * (ground - cy)
        ink_lines.append(([(cx - 0.62 * R * t, y), (cx - 0.40 * R * t, y)], 0.5))
        ink_lines.append(([(cx + 0.40 * R * t, y), (cx + 0.62 * R * t, y)], 0.5))
    # rim: two circles + zigzag truss
    th = np.linspace(0, 2 * np.pi, 721)
    for rr in (1.0, 0.94):
        ink_lines.append(([(cx + rr * R * np.cos(a), cy + rr * R * np.sin(a)) for a in th], 0.8))
    rb = np.zeros((H, W), np.float32)
    im_ = Image.new('F', (W, H), 0.0); dr_ = ImageDraw.Draw(im_)
    dr_.ellipse([cx - R, cy - R, cx + R, cy + R], fill=1.0); dr_.ellipse([cx - 0.94 * R, cy - 0.94 * R, cx + 0.94 * R, cy + 0.94 * R], fill=0.0)
    sh.wash(0.30 * gaussian_filter(np.asarray(im_, np.float32), SS), 'lilac')
    disc_ = sb.discs(W, H, [cx], [cy], [0.94 * R])
    sh.wash(0.035 * gaussian_filter(disc_, SS * 3), 'sky')
    zz = []
    for i in range(4 * k + 1):
        a = 2 * np.pi * i / (4 * k); rr = 1.0 if i % 2 == 0 else 0.94
        zz.append((cx + rr * R * np.cos(a), cy + rr * R * np.sin(a)))
    fine_lines.append((zz, 0.5))
    # gondolas
    rho_max = 0.17 * R if k <= 60 else 0.15 * R
    hues = []
    for j, d in enumerate(perm):
        a = -np.pi / 2 + 2 * np.pi * j / k                 # position 0 (n) at the top
        px, py = cx + R * np.cos(a), cy + R * np.sin(a)
        fine_lines.append(([(cx, cy), (px, py)], 0.45))    # spoke
        rho = max(rho_max * np.sqrt(d / n), 0.009 * R + 1.5 * SS)
        hang = 0.018 * R + 0.35 * rho
        gx, gy = px, py + hang + rho
        fine_lines.append(([(px, py), (gx, gy - rho)], 0.7))
        h = sorted(perm).index(d) / k
        hues.append((gx, gy, rho, h))
    # paint gondolas binned by hue (one wash per bin)
    nb = 24
    for b in range(nb):
        sel = [q for q in hues if min(int(q[3] * nb), nb - 1) == b]
        if not sel: continue
        m = sb.discs(W, H, [q[0] for q in sel], [q[1] for q in sel], [q[2] for q in sel])
        m = gaussian_filter(m, SS * 0.7)
        tint = sb.wheel_tint(0.58 * (1 - (b + 0.5) / nb))   # rank walks the whole wheel: light cars sky ... heavy cars strawberry
        sh.wash(1.05 * m, tint)
        hl = sb.discs(W, H, [q[0] - 0.35 * q[2] for q in sel], [q[1] - 0.38 * q[2] for q in sel], [0.28 * q[2] for q in sel])
        sh.lighten(gaussian_filter(hl, SS * 1.5 + 0.0), 0.55)
        # rim of each car: slightly deeper edge
        from scipy.ndimage import binary_erosion
        edge = m - gaussian_filter(m, SS * 2.2)
        sh.wash(0.8 * np.clip(edge, 0, None), tint)
    angs = -np.pi / 2 + 2 * np.pi * np.arange(k) / k
    v = np.sum(np.array(perm) * np.exp(1j * angs)) / np.sum(perm)
    coral_pts.append((cx, cy, R, gap, n, k))
    if n == 55440: LOUPE = (cx, cy, R, v)
    rims[n] = (cx, cy, R)
    labels.append((n, k, gap, cx, ground, R))

# bunting: catenaries between the rims, triangular flags in rank order of the wheel
def catenary(p, q, sag, m=200):
    t = np.linspace(0, 1, m)
    x = p[0] + (q[0] - p[0]) * t; y = p[1] + (q[1] - p[1]) * t + sag * 4 * t * (1 - t)
    return x, y
flags = []
# loupe on the big hub: the centre of mass, magnified
cxl, cyl, Rl, v = LOUPE
lx, ly, lr = cxl + 0.36 * Rl, cyl - 0.40 * Rl, 0.16 * Rl
mag = 0.62 * lr / (abs(v) * Rl)
exp10 = int(np.floor(np.log10(mag)))
mag = 10 ** exp10 * np.floor(mag / 10 ** exp10)
lens = sb.discs(W, H, [lx], [ly], [lr])
sh.lighten(gaussian_filter(lens, SS), 0.92)
sh.wash(0.06 * gaussian_filter(lens, SS), 'sky')
th = np.linspace(0, 2 * np.pi, 400)
ink_lines.append(([(lx + lr * np.cos(a), ly + lr * np.sin(a)) for a in th], 1.0))
ink_lines.append(([(lx + 1.02 * lr * np.cos(a), ly + 1.02 * lr * np.sin(a)) for a in th], 0.5))
dx, dy = lx - cxl, ly - cyl; dd = np.hypot(dx, dy)
ink_lines.append(([(cxl + dx / dd * 0.05 * Rl, cyl + dy / dd * 0.05 * Rl), (lx - dx / dd * lr, ly - dy / dd * lr)], 0.5))
fine_lines.append(([(lx - 0.8 * lr, ly), (lx + 0.8 * lr, ly)], 1.0))
fine_lines.append(([(lx, ly - 0.8 * lr), (lx, ly + 0.8 * lr)], 1.0))
fine_lines.append(([(lx + 0.18 * lr * np.cos(a), ly + 0.18 * lr * np.sin(a)) for a in th], 1.0))
comx, comy = lx + mag * Rl * v.real, ly + mag * Rl * v.imag
cm = sb.discs(W, H, [comx], [comy], [0.07 * lr])
sh.wash(1.4 * gaussian_filter(cm, SS * 0.8), 'coral')
LOUPE_TXT = (f'centre of mass, x10^{exp10}' if False else f'the centre of mass, magnified {mag:.0e}'.replace('e+0', ' × 10^').replace('e+', ' × 10^'), lx, ly + lr + 30 * S / 2560 * SS)

# ink
A = sb.lines(W, H, [p for p, _ in ink_lines], 2.2 * SS * S / 2560, [w for _, w in ink_lines], sigma=0.6 * SS)
sh.wash(1.1 * A, 'ink')
F = sb.lines(W, H, [p for p, _ in fine_lines], 1.2 * SS * S / 2560, [w for _, w in fine_lines], sigma=0.5 * SS)
sh.wash(0.65 * F, 'plum')
# hubs: plum boss + coral heart
for (cx, cy, R, gap, n, k) in coral_pts:
    boss = sb.discs(W, H, [cx], [cy], [0.035 * R])
    sh.lighten(gaussian_filter(boss, SS), 0.9)
    sh.wash(0.35 * gaussian_filter(boss, SS) - 0.30 * gaussian_filter(sb.discs(W, H, [cx], [cy], [0.025 * R]), SS), 'plum')
    c = sb.discs(W, H, [cx], [cy], [0.016 * R])
    sh.wash(1.3 * gaussian_filter(c, SS * 0.8), 'coral')

# text
items = []
fs = S / 2560 * SS
for (n, k, gap, cx, ground, R) in labels:
    items.append((f'n = {n:,}'.replace(',', ' '), cx, ground + 34 * fs, 30 * fs, 'serif_bold', 'mt'))
    items.append((f'{k} divisors · misses the hub by {gap:.4f}', cx, ground + 74 * fs, 22 * fs, 'italic', 'mt'))
SUP = str.maketrans('0123456789', '⁰¹²³⁴⁵⁶⁷⁸⁹')
items.append(((f'centre of mass, magnified 10{str(exp10).translate(SUP)}' if mag == 10 ** exp10 else f'centre of mass, magnified {int(mag / 10 ** exp10)}·10{str(exp10).translate(SUP)}'), lx, ly + lr + 16 * fs, 21 * fs, 'italic', 'mt'))
tm = sb.text_mask(W, H, items)
sh.wash(3.2 * tm, 'ink')
cap = [('Every Wheel Leans a Little', 0.07 * W, 0.915 * H, 58 * fs, 'serif_bold', 'ls'),
       ('Hang every divisor of n as a car on an evenly spaced wheel (car area proportional to the divisor, heaviest at the top). Can the centre of mass sit on the hub?',
        0.07 * W, 0.945 * H, 25 * fs, 'italic', 'ls'),
       ('MO 515611 · best hangings found by annealing · exact balance impossible when τ(n) has ≤ 2 prime factors (proved), and for all n ≤ 1.94·10⁶ but five undecided (CP-SAT)',
        0.07 * W, 0.970 * H, 20 * fs, 'mono', 'ls')]
band = np.clip((yy - 0.885) / 0.01, 0, 1)
sh.A *= (1 - 0.55 * band)[..., None]
sh.wash(3.2 * sb.text_mask(W, H, cap), 'ink')
img = sh.develop(dmax=2.4, glow=0.10)
sb.finish(img, S, out)
print('done')
