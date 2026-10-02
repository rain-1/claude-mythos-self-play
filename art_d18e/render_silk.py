"""EVERY NUMBER WAITS ITS TURN — A124056 (each term counts the earlier terms dividing its predecessor),
2e8 terms on log–log axes, coloured by how many divisors the predecessor had."""
import numpy as np, sys, math
from scipy.ndimage import gaussian_filter
from PIL import Image
from sorbet import PIG, Sheet, lines, discs, text_mask
S = int(sys.argv[1]); OUT = sys.argv[2]
a = np.fromfile('a124056.bin', dtype=np.uint32); tau = np.load('tau.npy')
N = len(a)
W = H = S
x0, x1 = int(S * 0.07), int(S * 0.95); y0, y1 = int(S * 0.05), int(S * 0.84)
lnmin, lnmax = math.log(30), math.log(N)
lamin, lamax = math.log(3) - 0.02, math.log(float(a.max())) + 0.05
CL = [(2, 2), (3, 4), (5, 8), (9, 16), (17, 10**6)]
TINT = ['strawberry', 'butter', 'mint', 'sky', 'lilac']
TINT = ['coral', 'honey', 'mint', 'periwinkle', 'bubblegum']
hist = np.zeros((len(CL), H, W), np.float32)
ss = 2  # sub-pixel jitter count via fractional splat
for s in range(0, N - 1, 20_000_000):
    e = min(N - 1, s + 20_000_000)
    n = np.arange(s + 2, e + 2, dtype=np.float64)          # index of term a[s+1 .. e]
    v = a[s + 1:e + 1].astype(np.float64); tp = tau[a[s:e]]
    X = x0 + (np.log(n) - lnmin) / (lnmax - lnmin) * (x1 - x0)
    Y = y1 - (np.log(v) - lamin) / (lamax - lamin) * (y1 - y0)
    ok = (X >= x0) & (X < x1)
    for c, (lo, hi) in enumerate(CL):
        m = ok & (tp >= lo) & (tp <= hi)
        xi = X[m].astype(np.int64); yi = np.clip(Y[m], 0, H - 1).astype(np.int64)
        hist[c] += np.bincount(yi * W + xi, minlength=H * W).reshape(H, W).astype(np.float32)
    print(s, flush=True)
# column density normalisation: points per pixel column grow like n -> normalise by expected
colmass = hist.sum(0).sum(0) + 1
sheet = Sheet(W, H, seed=5, grain=0.004)
cm = gaussian_filter(hist.sum(0).sum(0), S / 200)[None, :] + 1e-9
P = hist / cm[None]                      # conditional distribution per column
tot = P.sum(0)
ref = np.percentile(tot[tot > 0], 99.0)
for c in range(len(CL)):
    h = gaussian_filter(P[c], 0.6)
    d = np.log1p(h / ref * 40) / np.log1p(40)
    sheet.wash(d, TINT[c], k=1.9)
# coral thread: value 3
y3 = y1 - (math.log(3) - lamin) / (lamax - lamin) * (y1 - y0)
sheet.wash(lines(W, H, [[(x0, y3), (x1, y3)]], max(2, S // 700), sigma=0.8), 'coral', k=1.4)
# axis ticks (decades) in thin ink
tk = []
items = []
for p in range(2, 9):
    xx = x0 + (p * math.log(10) - lnmin) / (lnmax - lnmin) * (x1 - x0)
    if x0 <= xx <= x1:
        tk.append([(xx, y1 + S * 0.006), (xx, y1 + S * 0.016)])
        items.append(('10' + '⁰¹²³⁴⁵⁶⁷⁸⁹'[p], xx, y1 + S * 0.021, S * 0.011, 'italic', 'mt'))
for p in range(1, 7):
    yy = y1 - (p * math.log(10) - lamin) / (lamax - lamin) * (y1 - y0)
    if y0 <= yy <= y1:
        tk.append([(x0 - S * 0.016, yy), (x0 - S * 0.006, yy)])
        items.append(('10' + '⁰¹²³⁴⁵⁶⁷⁸⁹'[p], x0 - S * 0.019, yy, S * 0.011, 'italic', 'rm'))
sheet.wash(lines(W, H, tk, max(1, S // 1400), sigma=0.6), 'ink', k=0.8)
img = sheet.develop(dmax=2.2)
srgb = np.asarray(img).astype(np.float32) / 255
cy0 = y1 + int(S * 0.05)
items += [('Every Number Waits Its Turn', S / 2, cy0, S * 0.03, 'serif_bold', 'mt'),
          ('A124056: each term counts how many earlier terms divide the one before it — two hundred million terms, position against value, both logarithmic', S / 2, cy0 + S * 0.043, S * 0.0148, 'italic', 'mt'),
          ('colour = divisors of the predecessor: coral a prime · honey 3–4 · mint 5–8 · periwinkle 9–16 · bubblegum 17+   ·   coral thread: the value 3, which came back 185 341 times', S / 2, cy0 + S * 0.068, S * 0.0118, 'italic', 'mt')]
tm = text_mask(W, H, items)
srgb = srgb * (1 - tm[..., None]) + tm[..., None] * np.array([0.40, 0.31, 0.44])
Image.fromarray((np.clip(srgb, 0, 1) * 255 + 0.5).astype(np.uint8)).save(OUT, optimize=True)
