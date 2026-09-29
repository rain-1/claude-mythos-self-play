"""Every Loop of One Length — ellipses of perimeter 1 (MO 515557)."""
import numpy as np, sys, time
from sorbet import *
from ellipses import family, envelope, Pa, Pb
S = int(sys.argv[1]); NF = int(sys.argv[2]); NE = int(sys.argv[3]); out = sys.argv[4]
SS = 2; N = S * SS
sc = 0.37 * N / 0.25           # 1/4 (the segment half-length) -> 0.40 N
cx, cy = N / 2, 0.45 * N
F = family(NE // 2 + 1)                     # a >= b half; mirror for the other half
half = [(a, b) for a, b in F]
fam = half[::-1] + [(b, a) for a, b in half[1:]]   # segment-y ... circle ... segment-x
sh = Sheet(N, N, seed=11)
tt = np.linspace(0, 2 * np.pi, 720)
NB = 36
bins = [[] for _ in range(NB)]
for f in range(NF):
    rot = np.pi * f / NF / (1 if NF > 1 else 1)
    rot = f * np.pi / (2 * NF) * (2 if NF == 3 else 1) if NF != 3 else f * np.pi / 3
    for i, (a, b) in enumerate(fam):
        s = i / (len(fam) - 1)                       # 0..1 across the family
        hue = (0.5 * abs(2 * s - 1) + f / NF * 0.35 + 0.02) % 1
        x, y = a * np.cos(tt), b * np.sin(tt)
        X = cx + sc * (x * np.cos(rot) - y * np.sin(rot)); Y = cy + sc * (x * np.sin(rot) + y * np.cos(rot))
        bins[int(hue * NB) % NB].append(np.stack([X, Y], 1))
lw = max(1, round(N / 900))
LK = float(sys.argv[5]); FK = float(sys.argv[6])
COV = np.zeros((N, N), np.float32)
for k, pl in enumerate(bins):
    if not pl: continue
    d = lines(N, N, pl, lw, sigma=0.6 * SS)
    sh.wash(LK * d, wheel_tint(k / NB))
    im = Image.new('F', (N, N), 0.0); dr = ImageDraw.Draw(im)
    for p in pl:
        im2 = Image.new('F', (N, N), 0.0); ImageDraw.Draw(im2).polygon([tuple(q) for q in p], fill=1.0)
        COV[:] += np.asarray(im2, np.float32)
q = gaussian_filter(COV / COV.max(), 1.0 * SS)
H0, H1 = float(sys.argv[7]), float(sys.argv[8])
nlev = 64; qi = np.minimum((q * nlev).astype(int), nlev - 1)
Acov = np.zeros((N, N, 3), np.float32)
for l in range(nlev):
    m = qi == l
    if l == 0 or not m.any(): continue
    Acov[m] = (FK * (0.35 + 0.65 * l / nlev)) * absorb(wheel_tint(H0 + (H1 - H0) * l / nlev))
sh.wash_rgb(gaussian_filter(Acov, (0.7 * SS, 0.7 * SS, 0)))
# envelope in coral, for each family rotation, 4 quadrants
F2, E = envelope(161)
env = []
for f in range(NF):
    rot = f * np.pi / 3 if NF == 3 else f * np.pi / (2 * NF)
    for sx, sy in [(1, 1), (-1, 1), (-1, -1), (1, -1)]:
        for swap in (0, 1):
            ex, ey = (E[:, 0], E[:, 1]) if not swap else (E[:, 1], E[:, 0])
            ex, ey = sx * ex, sy * ey
            env.append(np.stack([cx + sc * (ex * np.cos(rot) - ey * np.sin(rot)), cy + sc * (ex * np.sin(rot) + ey * np.cos(rot))], 1))
sh.wash(1.3 * lines(N, N, env, max(2, round(N / 500)), sigma=0.5 * SS), 'coral')
# the straight lines hiding in the family: b -> 0 gives a doubled segment of length 1/2
segs = []
for f in range(NF):
    rot = f * np.pi / 3 if NF == 3 else f * np.pi / (2 * NF)
    for phi in (rot, rot + np.pi / 2):
        segs.append([(cx - sc * 0.25 * np.cos(phi), cy - sc * 0.25 * np.sin(phi)), (cx + sc * 0.25 * np.cos(phi), cy + sc * 0.25 * np.sin(phi))])
sh.wash(0.75 * lines(N, N, segs, max(1, round(N / 1300)), sigma=0.5 * SS), 'plum')
# the one circle every family shares, r = 1/(2 pi)
tc = np.linspace(0, 2 * np.pi, 1440)
r0 = sc / (2 * np.pi)
sh.wash(1.7 * lines(N, N, [np.stack([cx + r0 * np.cos(tc), cy + r0 * np.sin(tc)], 1)], max(2, round(N / 700)), sigma=0.5 * SS), 'honey')
txt = [("Every Loop of One Length", N / 2, 0.905 * N, 0.029 * N, 'serif_bold', 'mm'),
       ("ellipses of perimeter 1, in three turns; coral = their envelope  (x/a)² = a∂P/∂a,  (y/b)² = b∂P/∂b", N / 2, 0.940 * N, 0.0150 * N, 'italic', 'mm'),
       ("flattened all the way, a loop of length 1 becomes a straight line of length ½, walked twice", N / 2, 0.963 * N, 0.0150 * N, 'italic', 'mm')]
sh.wash(1.25 * text_mask(N, N, txt), 'ink')
img = sh.develop(dmax=1.7)
finish(img, S, out)
