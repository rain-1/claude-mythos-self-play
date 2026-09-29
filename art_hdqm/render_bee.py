"""The Longest Bee — one pivot-sampled self-avoiding walk on the honeycomb (an N-bit bee number)."""
import numpy as np, sys
from sorbet import *
S = int(sys.argv[1]); src = sys.argv[2]; out = sys.argv[3]; mode = sys.argv[4]
SS = 2; N = S * SS
w = np.loadtxt(src)
x = w[:, 0] - w[:, 1] / 2; y = w[:, 1] * np.sqrt(3) / 2
# centre + fit
x -= (x.max() + x.min()) / 2; y -= (y.max() + y.min()) / 2
ext = max(np.ptp(x), np.ptp(y)); sc = 0.80 * N / ext
X = N / 2 + sc * x; Y = N / 2 - sc * y
n = len(X); tt = np.arange(n) / (n - 1)
sh = Sheet(N, N, seed=5)
NB = 48
if mode == 'cells':
    # hexagon centres adjacent to each vertex: the honeycomb's faces = class-0 Eisenstein points
    a, b = w[:, 0].astype(int), w[:, 1].astype(int)
    first = {}
    U = [(1, 0), (0, 1), (-1, -1), (-1, 0), (0, -1), (1, 1)]
    for i in range(n):
        for du, dv in U:
            c = (a[i] + du, b[i] + dv)
            if (c[0] + c[1]) % 3 == 0 and c not in first: first[c] = i
    cells = np.array(list(first.keys())); ti = np.array(list(first.values())) / (n - 1)
    cxs = N / 2 + sc * (cells[:, 0] - cells[:, 1] / 2 - (w[:, 0] - w[:, 1] / 2).max() / 2 - (w[:, 0] - w[:, 1] / 2).min() / 2)
    cys = N / 2 - sc * (cells[:, 1] * np.sqrt(3) / 2 - (w[:, 1].max() + w[:, 1].min()) * np.sqrt(3) / 4)
    r = sc * 1.0 * 0.86
    ang = np.pi / 6 + np.arange(6) * np.pi / 3
    for k in range(NB):
        m = (np.minimum((ti * NB).astype(int), NB - 1) == k)
        im = Image.new('F', (N, N), 0.0); dr = ImageDraw.Draw(im)
        for px, py in zip(cxs[m], cys[m]):
            dr.polygon([(px + r * np.cos(q), py + r * np.sin(q)) for q in ang], fill=1.0)
        sh.wash(0.55 * gaussian_filter(np.asarray(im, np.float32), 0.8 * SS), wheel_tint(k / NB * 0.92))
    sh.wash(0.9 * lines(N, N, [np.stack([X, Y], 1)], max(1, round(sc * 0.16)), sigma=0.5 * SS), 'plum')
else:
    polys, ws = [], []
    for k in range(NB):
        i0, i1 = k * n // NB, min(n, (k + 1) * n // NB + 1)
        d = lines(N, N, [np.stack([X[i0:i1], Y[i0:i1]], 1)], max(1, round(N / 1100)), sigma=0.6 * SS)
        sh.wash(1.1 * d, wheel_tint(k / NB * 0.92))
        sh.wash(0.22 * gaussian_filter(d, 10 * SS), wheel_tint(k / NB * 0.92))
# coral: start bee
sh.wash(1.2 * discs(N, N, [X[0]], [Y[0]], [N / 180], sigma=SS), 'coral')
finish(sh.develop(dmax=1.7), S, out)
