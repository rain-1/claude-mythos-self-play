"""Neither Side Is a Prison — a pivot-sampled honeycomb SAW (one enormous bee number) extended to the
frame; it splits the page into two sides; tide lines of distance on each side."""
import numpy as np, sys
from scipy.ndimage import distance_transform_edt, label, binary_dilation
from sorbet import *
S = int(sys.argv[1]); src = sys.argv[2]; out = sys.argv[3]
FILL = float(sys.argv[4]) if len(sys.argv) > 4 else 0.62
DK = float(sys.argv[5]) if len(sys.argv) > 5 else 0.9
G = float(sys.argv[6]) if len(sys.argv) > 6 else 1.23
SS = 2; N = S * SS
w = np.loadtxt(src)
x = w[:, 0] - w[:, 1] / 2; y = w[:, 1] * np.sqrt(3) / 2
# rotate so the end-to-end vector is horizontal
e = np.array([x[-1] - x[0], y[-1] - y[0]]); th = -np.arctan2(e[1], e[0])
x, y = x * np.cos(th) - y * np.sin(th), x * np.sin(th) + y * np.cos(th)
x -= (x.max() + x.min()) / 2; y -= (y.max() + y.min()) / 2
sc = FILL * N / max(np.ptp(x), np.ptp(y) * 1.0)
X = N / 2 + sc * x; Y = 0.45 * N - sc * y
# extend: from each end straight out to the frame (left end -> left edge, right end -> right edge)
path = np.concatenate([[[-10, Y[0]]], np.stack([X, Y], 1), [[N + 10, Y[-1]]]])
lw = max(2, round(N / 1400))
im = Image.new('L', (N, N), 0); ImageDraw.Draw(im).line([tuple(p) for p in path], fill=255, width=lw)
curve = np.asarray(im) > 0
lab, nl = label(~curve)
sizes = np.bincount(lab.ravel()); order = np.argsort(sizes[1:])[::-1] + 1
print('components', nl, 'largest', sizes[order[:4]])
top = lab == order[0]; bot = lab == order[1]
if np.mean(np.nonzero(top)[0]) > np.mean(np.nonzero(bot)[0]): top, bot = bot, top
# tiny enclosed pockets (raster artefacts) join the side they touch most — assign by nearest
side = np.zeros((N, N), np.int8); side[top] = 1; side[bot] = -1
d = distance_transform_edt(~curve).astype(np.float32) / N        # distance in canvas units
idx = distance_transform_edt(side == 0, return_distances=False, return_indices=True)
side = side[idx[0], idx[1]]
sh = Sheet(N, N, seed=21)
# tide bands: geometric spacing, each band a soft glaze; hue walks with depth
nb = int(sys.argv[7]) if len(sys.argv) > 7 else 30
edges = 0.002 * (G ** np.arange(nb + 1)) - 0.002
LAND = ['strawberry', 'peach', 'honey', 'butter', 'lime']
SEA = ['lilac', 'periwinkle', 'sky', 'mint', 'mint']
for sgn, pal in ((1, LAND), (-1, SEA)):
    for k in range(nb):
        m = (side == sgn) & (d >= edges[k]) & (d < edges[k + 1])
        if not m.any(): continue
        f = k / nb * (len(pal) - 1); i = int(f); t = f - i
        tint = tuple(np.array(PIG[pal[i]]) ** (1 - t) * np.array(PIG[pal[min(i + 1, len(pal) - 1)]]) ** t)
        dens = DK * (1.0 - 0.6 * k / nb) * (1 - 0.28 * (k % 2)) * min(1.0, (nb - k) / 8.0) ** 1.5
        sh.wash(gaussian_filter(m.astype(np.float32), 0.8 * SS) * dens, tint)
# tide lines: thin paper-ward glaze lines at band edges
tl = np.zeros((N, N), np.float32)
for k in range(1, nb):
    tl += np.exp(-((d - edges[k]) * N / (0.7 * SS)) ** 2)
sh.lighten(np.clip(tl, 0, 1) * 0.35, 1.0)
# the bee: plum ink thread on the walk, lighter on the extensions
ink = lines(N, N, [np.stack([X, Y], 1)], max(1, round(N / 1800)), sigma=0.45 * SS)
ext = lines(N, N, [path[:2], path[-2:]], max(1, round(N / 1800)), sigma=0.45 * SS)
sh.wash(1.25 * ink, 'plum'); sh.wash(0.35 * ext, 'plum')
sh.wash(1.3 * discs(N, N, [X[0], X[-1]], [Y[0], Y[-1]], [N / 260] * 2, sigma=0.8 * SS), 'coral')
nsteps = len(w) - 1
txt = [("Neither Side Is a Prison", N / 2, 0.915 * N, 0.028 * N, 'serif_bold', 'mm'),
       (f"one bee number {nsteps:,} binary digits long: a {nsteps:,}-step self-avoiding flight on the honeycomb, pivot-sampled", N / 2, 0.948 * N, 0.0150 * N, 'italic', 'mm'),
       ("it never closes a loop, so the page it cuts in two stays two open countries; bands = distance to the coast", N / 2, 0.970 * N, 0.0122 * N, 'italic', 'mm')]
sh.lighten(np.clip((np.arange(N)[:, None] / N - 0.89) / 0.01, 0, 1) * np.ones((1, N)), 0.7)
sh.wash(1.25 * text_mask(N, N, txt), 'ink')
finish(sh.develop(dmax=1.7), S, out)
