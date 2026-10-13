"""Mirror ranges, take 2: rows of symmetric primitive Dyck mountains at dawn.

Row for area n = all d(n) mountains side by side, shortest in the middle, tallest at the ends (so every row is
a valley that frames the sun). Unit shrinks geometrically with depth; each mountain is folded paper: the left
half (toward the light) pale, the right half in shade, the fold on its mirror axis. Mist between rows, a thin
lake mirror at the bottom.
"""
import sys, numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter, map_coordinates
from dyck import sym_prim

W, H = int(sys.argv[1]), int(sys.argv[2]); OUT = sys.argv[3]
ROWS = [int(v) for v in sys.argv[4].split(',')]          # back → front
U0 = float(sys.argv[5]) if len(sys.argv) > 5 else 0.022   # front unit, fraction of W
SHR = float(sys.argv[6]) if len(sys.argv) > 6 else 0.72   # unit ratio per row step back
SS = 2; w, h = W * SS, H * SS
paths = sym_prim(max(ROWS))
def hx(s): s = s.lstrip('#'); return np.array([int(s[i:i + 2], 16) for i in (0, 2, 4)]) / 255.0
WL = int(h * float(sys.argv[7]) if len(sys.argv) > 7 else h * 0.80)
Y, X = np.mgrid[0:h, 0:w].astype(np.float32)
t = np.clip(Y / WL, 0, 1)[..., None]
c0, c1, c2, c3 = hx('#aebdf0'), hx('#d9c4ee'), hx('#f8c8d6'), hx('#ffe6c2')
sky = np.where(t < 0.4, c0 + (c1 - c0) * (t / 0.4), np.where(t < 0.75, c1 + (c2 - c1) * ((t - 0.4) / 0.35), c2 + (c3 - c2) * ((t - 0.75) / 0.25)))
img = sky.copy()
sx, sy, sr = 0.5 * w, float(sys.argv[9]) * h if len(sys.argv) > 9 else 0.5 * h, 0.05 * h
d = np.hypot(X - sx, Y - sy)
g = (np.exp(-(d / (sr * 6)) ** 2) * 0.45)[..., None]
img = img * (1 - g) + hx('#fff4dc') * g
disc = np.clip((sr - d) / 2.5 + 0.5, 0, 1)[..., None]
img = img * (1 - disc) + hx('#fff6e2') * disc
# row colours back → front (periwinkle, lilac, orchid, rose, apricot, mint, teal)
PAL = [hx(c) for c in ['#c7cdf2', '#cdbfee', '#d9b7e4', '#e8b3cf', '#f2b8b4', '#f3c9a6', '#bfe0b4', '#93d2c2', '#7cc0c8']]
nr = len(ROWS)
units = [w / sum(len(p) - 1 for p in paths[n]) for n in ROWS] if U0 <= 0 else [U0 * w * SHR ** (nr - 1 - i) for i in range(nr)]
bases = [0.0] * nr; b = WL
for i in range(nr - 1, -1, -1):
    bases[i] = b; b -= float(sys.argv[8] if len(sys.argv) > 8 else 2.2) * units[i]
for i, n in enumerate(ROWS):
    u = units[i]; base = bases[i]
    P = sorted(paths[n], key=lambda p: (max(p), -len(p), p))
    arr = []
    for k, p in enumerate(P):
        (arr.insert(0, p) if k % 2 == 0 else arr.append(p))
    # mirror the arrangement order so the row is as symmetric as the data allows
    total = sum(len(p) - 1 for p in arr) * u
    x = (w - total) / 2
    lay = Image.new('L', (w, h), 0); lit = Image.new('L', (w, h), 0); snow = Image.new('L', (w, h), 0)
    dl, dli, dsn = ImageDraw.Draw(lay), ImageDraw.Draw(lit), ImageDraw.Draw(snow)
    hmax = max(max(p) for p in arr)
    for p in arr:
        m = len(p) - 1
        pts = [(x + j * u, base - p[j] * u) for j in range(m + 1)]
        dl.polygon(pts + [(pts[-1][0], h), (pts[0][0], h)], fill=255)
        hf = m // 2
        dli.polygon(pts[:hf + 1] + [(pts[hf][0], h), (pts[0][0], h)], fill=255)
        # snow cap: the part of the mountain above (peak - 1.6) units, only on tall ones
        if max(p) >= max(3, hmax - 2):
            yc = base - (max(p) - 1.5) * u
            poly = []
            dsn.polygon(pts + [(pts[-1][0], h), (pts[0][0], h)], fill=255)
            snow_y = yc
        x += m * u
    L = np.asarray(lay, np.float32) / 255; Li = np.asarray(lit, np.float32) / 255
    Sn = np.asarray(snow, np.float32) / 255
    # snow only above a per-row line, wavy
    snowline = base - (hmax - 1.6) * u + 0.25 * u * np.sin(X / (0.7 * u))
    Sn = Sn * np.clip((snowline - Y) / 1.5 + 0.5, 0, 1)
    depth = (nr - 1 - i) / max(1, nr - 1)
    col = PAL[int(round((1 - depth) * (len(PAL) - 1)))] if nr > 1 else PAL[-1]
    litc = np.minimum(1, col * 1.05 + 0.06); shc = col * 0.84 + np.array([0.0, 0.0, 0.05])
    body = shc * (1 - Li[..., None]) + litc * Li[..., None]
    snl, sns = np.array([1.0, 0.99, 0.985]), np.array([0.88, 0.89, 0.98])
    body = body * (1 - Sn[..., None]) + (sns * (1 - Li[..., None]) + snl * Li[..., None]) * Sn[..., None]
    # atmospheric haze toward the sky colour, plus mist rising from below the base
    hz = 0.5 * depth ** 1.3
    body = body * (1 - hz) + sky * hz
    mist = (np.clip((Y - (base - 1.2 * u)) / (2.4 * u), 0, 1) ** 1.3 * 0.75)[..., None]
    body = body * (1 - mist) + np.array([1.0, 0.975, 0.965]) * mist
    # rim light on the ridge line
    edge = np.clip(L - np.roll(L, int(1.5 * SS), axis=0), 0, 1)[..., None]
    body = body + edge * 0.22
    # soft contact shadow of this row on the row behind (tiny downward offset is invisible, so a glow halo instead)
    halo = gaussian_filter(L, 6 * SS)[..., None] * 0.06
    img = img * (1 - halo) + np.array([1, 1, 1]) * halo
    img = img * (1 - L[..., None]) + body * L[..., None]
# lake
ys = np.arange(WL, h); k = (ys - WL) / max(1, h - WL)
amp = (0.5 + 5 * k) * SS
rip = amp[:, None] * np.sin(X[WL:] * (0.006 / SS) * (1 + 2 * k[:, None]) + ys[:, None] * 0.35 / SS)
sy_ = np.clip(2 * WL - ys[:, None] + 0.4 * rip, 0, WL - 1); sx_ = np.clip(X[WL:] + rip, 0, w - 1)
refl = np.stack([map_coordinates(img[..., c], [sy_, sx_], order=1) for c in range(3)], -1)
tint = (0.22 + 0.2 * k)[:, None, None]
refl = refl * (1 - tint) + hx('#b8dcee') * tint
rng = np.random.default_rng(5); gl = np.zeros((h - WL, w), np.float32)
for _ in range(int(500 * W / 4096) + 60):
    yy = int(rng.uniform(0, 1) ** 1.4 * (h - WL - 3)); spread = (0.02 + 0.12 * yy / (h - WL)) * w
    xx = int(sx + rng.normal(0, spread * 0.4)); ln = int((3 + 22 * yy / (h - WL)) * SS)
    if 0 <= xx < w - ln: gl[yy, xx:xx + ln] += rng.uniform(0.3, 0.9)
refl = refl + (gaussian_filter(gl, (0.5 * SS, 1.0 * SS)) * 1.8)[..., None] * np.array([1, 0.97, 0.9])
img[WL:] = refl
img = np.clip(img, 0, 1)
Image.fromarray((img * 255 + 0.5).astype(np.uint8)).resize((W, H), Image.LANCZOS).save(OUT)
print([(n, len(paths[n])) for n in ROWS])
