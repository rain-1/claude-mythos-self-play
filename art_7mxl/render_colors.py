"""'The Last Colour' — 2560^2. MO 41939 balls-and-colours.

512 colours, each a horizontal thread; y = extinction rank (first death at
top, winner at bottom); x = event-time (axis warped by the empirical
paint-event CDF: equal activity per column). Thread luminance = log2 of the
colour's population. Death = cold spark. The wedge silhouette is the
block-counting curve of the dual Kingman-style coalescent; the exact
theory curve k(t) = 1/(1-(1-1/n)e^{-t/(n(n-1))}) is overlaid in cyan.
E[T] = n(n-1) * sum_{k=2..n} 1/(k(k-1)) = (n-1)^2 — verified exactly for
n <= 8 by linear solve, by ensemble for n = 32,128.
"""
import numpy as np
import pickle
import sys
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter, zoom

S = int(sys.argv[1]) if len(sys.argv) > 1 else 2560
rs = S / 2560.0

h = pickle.load(open("colors_history.pkl", "rb"))
n = h["n"]
events = h["events"]          # (t, painter, painted, old_colour, new_colour)
E = len(events)
COLS = 2048
ROWS = n

# ---- reconstruct population per colour at column snapshots
counts = np.ones(n, dtype=np.int64)
pop = np.zeros((n, COLS), dtype=np.float32)      # population per colour
death_col = np.full(n, -1)
snap_idx = np.unique(np.round(np.geomspace(1, E, COLS)).astype(np.int64)) - 1
# pad to COLS by re-sampling
snap_idx = np.round(np.geomspace(1, E, COLS)).astype(np.int64) - 1
snap_t = np.zeros(COLS)


def col_of_event(idx):
    # first snapshot column >= idx (log position)
    return min(int(np.searchsorted(snap_idx, idx)), COLS - 1)


next_snap = 0
for idx, (t, a, b, oldc, newc) in enumerate(events):
    while next_snap < COLS and idx >= snap_idx[next_snap]:
        pop[:, next_snap] = counts
        snap_t[next_snap] = t
        next_snap += 1
    counts[oldc] -= 1
    counts[newc] += 1
    if counts[oldc] == 0:
        death_col[oldc] = col_of_event(idx)
while next_snap < COLS:
    pop[:, next_snap] = counts
    snap_t[next_snap] = events[-1][0]
    next_snap += 1

winner = h["winner"]
death_col[winner] = COLS
order = np.argsort(death_col)                    # first death first
rank_of = np.empty(n, dtype=np.int64)
rank_of[order] = np.arange(n)

# ---- thread field at (ROWS, COLS)
lum = np.where(pop > 0, np.power(np.log2(np.maximum(pop, 1)) + 1.0, 1.35), 0.0)
lum = lum / lum.max()
field = lum[order]                                # row r = rank r

# hues: muted dusk cycle by original colour id; winner overridden to gold
GOLD = np.array([1.00, 0.80, 0.34])
palette_angles = (np.arange(n) * 0.61803398875) % 1.0


def dusk(hfrac):
    """cyclic palette: richer twilight — ember/rose/steel/teal/moss."""
    a = 2 * np.pi * hfrac
    r = 0.55 + 0.42 * np.cos(a)
    g = 0.48 + 0.36 * np.cos(a - 2.1)
    b = 0.56 + 0.42 * np.cos(a - 4.0)
    return np.stack([r, g, b], -1)


col_rgb = dusk(palette_angles)                    # (n,3)
col_rgb = np.clip(0.16 + 0.92 * col_rgb / col_rgb.max(1, keepdims=True), 0, 1.1)
col_rgb[winner] = GOLD

# ---- paint to canvas
H = W = S
img = np.zeros((H, W, 3), np.float32)
y_lo, y_hi = 0.075 * H, 0.870 * H
x_lo, x_hi = 0.060 * W, 0.955 * W
row_y = np.linspace(y_lo, y_hi, ROWS)
col_x = np.linspace(x_lo, x_hi, COLS)

# vector paint: for each row draw its alive segment as small gaussian rows
acc = np.zeros((H, W, 3), np.float32)
xpix = np.clip(np.round(np.interp(np.arange(W), col_x, np.arange(COLS),
                                  left=0, right=COLS - 1)).astype(int), 0, COLS - 1)
# build (ROWS, W) luminance by sampling columns
fw = field[:, xpix]                                # (ROWS, W)
rgb_rows = col_rgb[order]                          # (ROWS,3)
# mask before x_lo / after x_hi
xmask = ((np.arange(W) >= x_lo) & (np.arange(W) <= x_hi)).astype(np.float32)
fw *= xmask[None, :]

sigma_y = 1.35 * rs
for r in range(ROWS):
    y = row_y[r]
    iy = int(round(y))
    w = fw[r]
    if w.max() <= 0:
        continue
    for dy in range(-3, 4):
        g = np.exp(-0.5 * (dy / sigma_y) ** 2)
        if 0 <= iy + dy < H:
            acc[iy + dy] += (w * g)[:, None] * rgb_rows[r][None, :] * 2.2

# death sparks
spark = np.zeros((H, W), np.float32)
rng = np.random.default_rng(3)
for c in range(n):
    if c == winner:
        continue
    dc = death_col[c]
    x = col_x[dc]
    y = row_y[rank_of[c]]
    th = rng.normal(size=(2, 300))
    xs = x + th[0] * 1.6 * rs
    ys = y + th[1] * 1.6 * rs
    ix = np.clip(np.round(xs).astype(int), 0, W - 1)
    iy = np.clip(np.round(ys).astype(int), 0, H - 1)
    np.add.at(spark, (iy, ix), 0.028)

# theory curve: k(t) = 1/(1-(1-1/n)exp(-t/(n(n-1)))), clipped to [1,n]
tgrid = snap_t
kk = 1.0 / (1.0 - (1.0 - 1.0 / n) * np.exp(-tgrid / (n * (n - 1.0))))
kk = np.clip(kk, 1, n)
# alive k -> wedge boundary row = n - k  (threads sorted by death)
yb = np.interp(n - kk, np.arange(ROWS), row_y)
xb = col_x
curve = np.zeros((H, W), np.float32)
pts = np.linspace(0, COLS - 1, 6000)
cx = np.interp(pts, np.arange(COLS), xb)
cy = np.interp(pts, np.arange(COLS), yb) - 5.0 * rs
ix = np.clip(np.round(cx).astype(int), 0, W - 1)
iy = np.clip(np.round(cy).astype(int), 0, H - 1)
np.add.at(curve, (iy, ix), 0.012)
curve = gaussian_filter(curve, 1.1 * rs)

# compose
img = acc.copy()
img[..., 0] += np.clip(spark, 0, None) * 26 * 0.95
img[..., 1] += np.clip(spark, 0, None) * 26 * 0.98
img[..., 2] += np.clip(spark, 0, None) * 26 * 1.05
CYAN = np.array([0.45, 0.85, 1.0])
img += curve[..., None] * CYAN * 9

# winner thread glow boost: re-add its row brighter + bloom later
wr = rank_of[winner]
iy = int(round(row_y[wr]))
wwin = fw[wr]
for dy in range(-4, 5):
    g = np.exp(-0.5 * (dy / (2.0 * rs)) ** 2)
    if 0 <= iy + dy < H:
        img[iy + dy] += (wwin * g)[:, None] * GOLD[None, :] * 2.2

# filmic tone
img = 1 - np.exp(-1.15 * img)
img = np.power(np.clip(img, 0, 1), 0.66)

# bloom
lumi = img.sum(2)
thr = np.percentile(lumi, 99.0)
mask = np.clip(lumi - thr, 0, None)[..., None] * img / (lumi[..., None] + 1e-9)
ds = 4
small = mask[::ds, ::ds]
bl = gaussian_filter(small, (10 * rs / ds, 10 * rs / ds, 0))
bloom = zoom(bl, (mask.shape[0] / small.shape[0],
                  mask.shape[1] / small.shape[1], 1), order=1)[:H, :W]
img += 0.8 * np.clip(bloom, 0, None)
img = np.clip(img, 0, 1)

rngd = np.random.default_rng(1)
img = np.clip(img + (rngd.random(img.shape) - 0.5) / 255.0, 0, 1)
out = Image.fromarray((img * 255).astype(np.uint8))

if S >= 2048:
    fs1 = int(S * 0.0135)
    fs2 = int(S * 0.0088)
    f1 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", fs1)
    f2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", fs2)
    dr = ImageDraw.Draw(out)
    y = int(0.905 * S)
    dr.text((int(0.06 * S), y), "THE LAST COLOUR", fill=(235, 208, 152), font=f1)
    cap = ("pick two balls, paint the second with the first's colour; repeat (MO 41939)  ·  n = 512 colours, one run: "
           f"T = {h['T']:,} steps to consensus")
    dr.text((int(0.06 * S), y + int(fs1 * 1.6)), cap, fill=(150, 152, 158), font=f2)
    cap2 = (f"E[T] = (n−1)² = {(n-1)**2:,} — exact by Markov solve for n ≤ 8; ensembles n = 32: 969 ± 9 (961), n = 128: 16,295 ± 224 (16,129)  ·  "
            "E[T] = n(n−1)·Σₖ 1/k(k−1)")
    dr.text((int(0.06 * S), y + int(fs1 * 2.55)), cap2, fill=(150, 152, 158), font=f2)
    cap3 = ("threads = colours sorted by extinction; brightness = log population; x = event-time (log)  ·  "
            "cyan: coalescent mean-field k(t) = [1−(1−1/n)e^(−t/n(n−1))]⁻¹  ·  every colour dies but one — consensus, not truth")
    dr.text((int(0.06 * S), y + int(fs1 * 3.5)), cap3, fill=(150, 152, 158), font=f2)
out.save(f"colors_{S}.png")
print("saved", f"colors_{S}.png")
