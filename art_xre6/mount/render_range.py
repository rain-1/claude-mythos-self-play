"""Mirror ranges: every symmetric primitive Dyck path of area n as a folded-paper mountain.

Row n (back = large n, many mountains, small unit; front = small n, few mountains, big unit) so the
counts d(n) themselves make the perspective. Each step of a path is one fold: rising steps catch the
sun, falling steps are in the paper's shade. Snow above a height, mist between rows, a lake that
mirrors everything (each mountain is its own left-right mirror; the lake adds the up-down one).
"""
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy.ndimage import gaussian_filter, map_coordinates
from dyck import sym_prim

W, H = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (2048, 1280)
OUT = sys.argv[3] if len(sys.argv) > 3 else 'range.png'
SS = 2
w, h = W * SS, H * SS
ROWS = [int(v) for v in (sys.argv[4] if len(sys.argv) > 4 else '47,41,35,29,23').split(',')]   # back to front
paths = sym_prim(max(ROWS))

def hexc(s): s = s.lstrip('#'); return np.array([int(s[i:i + 2], 16) for i in (0, 2, 4)]) / 255.0
SKY_TOP, SKY_MID, SKY_LOW = hexc('#b9c6f2'), hexc('#f4c9dc'), hexc('#ffe9c4')
# row colours back→front: periwinkle → lilac → rose → peach → apricot → mint → sea
ROWCOL = [hexc(c) for c in ['#c9d0f4', '#cfc6f0', '#d8bfea', '#e3bde0', '#edbccf', '#f4bfc0', '#f7c6b0',
                            '#f6d0a6', '#e8d7a0', '#cfe0a8', '#b2e0b8', '#9ad8c4', '#8fcfd0', '#86c3d8']]
WATERLINE = 0.66   # fraction of height
wl = int(h * WATERLINE)

yy = np.linspace(0, 1, h)[:, None, None]
img = np.ones((h, w, 3))
t = np.clip(yy / WATERLINE, 0, 1)
sky = np.where(t < 0.55, SKY_TOP * (1 - t / 0.55) + SKY_MID * (t / 0.55), SKY_MID * (1 - (t - 0.55) / 0.45) + SKY_LOW * ((t - 0.55) / 0.45))
img[:] = sky
# sun: soft disc low behind the ranges
sx, sy, sr = 0.5 * w, 0.43 * h, 0.055 * h
X, Y = np.meshgrid(np.arange(w), np.arange(h))
dd = np.hypot(X - sx, Y - sy)
glow = np.exp(-(dd / (sr * 5)) ** 2) * 0.35
img = img * (1 - glow[..., None]) + hexc('#fff6e0') * glow[..., None]
disc = np.clip((sr - dd) / 3 + 0.5, 0, 1)
img = img * (1 - disc[..., None]) + hexc('#fff3d6') * disc[..., None]

nrows = len(ROWS)
# base line of each row (back rows higher), front row base at the waterline
def unit_of(n):
    tot = sum(len(p) - 1 for p in paths[n]) + (len(paths[n]) + 1) * (float(sys.argv[6]) if len(sys.argv) > 6 else 0.0)
    return min((w - 0.06 * w) / tot, 0.03 * w)
bases = [0] * nrows; b = wl
for i in range(nrows - 1, -1, -1):
    bases[i] = b; b -= float(sys.argv[5] if len(sys.argv) > 5 else 2.6) * unit_of(ROWS[i])
for i, n in enumerate(ROWS):
    P = sorted(paths[n], key=lambda p: (max(p), len(p)))
    # symmetric arrangement: tallest in the centre, alternate outward
    arr = []
    for k, p in enumerate(P):
        if k % 2 == 0: arr.insert(0, p)
        else: arr.append(p)
    gapu = float(sys.argv[6]) if len(sys.argv) > 6 else 0.0
    total = sum(len(p) - 1 for p in arr) + gapu * (len(arr) + 1)
    margin = 0.03 * w
    u = (w - 2 * margin) / total
    u = min(u, 0.03 * w)
    x = (w - u * total) / 2 + gapu * u
    base = bases[i]
    col = ROWCOL[int(round(i * (len(ROWCOL) - 1) / max(1, nrows - 1)))]
    depth = (nrows - 1 - i) / max(1, nrows - 1)       # 1 = farthest
    haze = 0.55 * depth ** 1.2
    lay = Image.new('L', (w, h), 0); lit = Image.new('L', (w, h), 0); snow = Image.new('L', (w, h), 0)
    dl, dli, ds = ImageDraw.Draw(lay), ImageDraw.Draw(lit), ImageDraw.Draw(snow)
    vu = u * 1.0   # vertical unit = horizontal unit (true 45° slopes)
    for p in arr:
        m = len(p) - 1; pk = max(p)
        pts = [(x + j * u, base - p[j] * vu) for j in range(m + 1)]
        dl.polygon(pts + [(pts[-1][0], base + 2), (pts[0][0], base + 2)], fill=255)
        dl.rectangle([pts[0][0] - (gapu+0.5) * u, base, pts[-1][0] + (gapu+0.5) * u, wl], fill=255)
        # rising steps lit: strip polygon under each rising edge
        half = m // 2
        dli.polygon(pts[:half + 1] + [(pts[half][0], base + 2), (pts[0][0], base + 2)], fill=255)
        # snow: above 70% of the tallest in the row (only peaks)
        sl = max(2, int(0.72 * max(max(q) for q in arr)))
        if pk > sl:
            ycut = base - (sl + 0.25) * vu
            poly = pts
            # snow polygon = mountain clipped above ycut (approximate with the mountain polygon, cut later)
            ds.polygon(pts + [(pts[-1][0], base + 2), (pts[0][0], base + 2)], fill=255)
        x += (m + gapu) * u
    L = np.asarray(lay, float) / 255; Li = np.asarray(lit, float) / 255 * L; Sn = np.asarray(snow, float) / 255
    sl = max(2, int(0.72 * max(max(q) for q in arr)))
    ycut = base - (sl + 0.25) * vu
    Sn = Sn * L * np.clip((ycut - Y) / (1.5 * SS) + 0.5, 0, 1)
    # drop shadow of this row onto what is behind (soft, offset up-right since sun is behind: shadow falls toward viewer, so a mist band instead)
    sh = gaussian_filter(L, 10 * SS) * 0.10
    img = img * (1 - sh[..., None] * np.array([0.5, 0.45, 0.25]))
    # body colour: lit vs shade strips, vertical gradient to mist at the base
    shade = col * 0.86 + np.array([0.02, 0.0, 0.06])
    litc = np.minimum(1, col * 1.06 + 0.04)
    body = shade[None, None, :] * (1 - Li[..., None]) + litc[None, None, :] * Li[..., None]
    snowc = np.array([1.0, 0.985, 0.975]) * 0.97 + 0.03 * litc
    snowc_sh = np.array([0.90, 0.90, 0.98])
    snowcol = snowc_sh[None, None, :] * (1 - Li[..., None]) + snowc[None, None, :] * Li[..., None]
    body = body * (1 - Sn[..., None]) + snowcol * Sn[..., None]
    # mist toward base and haze toward sky colour for distant rows
    mist = np.clip((Y - (base - 2.6 * vu)) / (2.6 * vu + 1e-6), 0, 1) ** 1.6 * 0.55
    hazec = sky
    body = body * (1 - haze) + hazec * haze
    body = body * (1 - mist[..., None]) + np.array([1.0, 0.97, 0.96]) * mist[..., None]
    # thin rim light along the ridge (sun behind): edges of the mask lit
    edge = np.clip(L - np.roll(L, 2 * SS, axis=0), 0, 1)
    body = body + edge[..., None] * 0.18
    img = img * (1 - L[..., None]) + body * L[..., None]

# lake: mirror of everything above the waterline, rippled, tinted toward sky blue, glitter path under the sun
ys = np.arange(wl, h)
src_y = 2 * wl - ys
k = (ys - wl) / (h - wl)
amp = (0.6 + 6 * k) * SS
rip = amp[:, None] * np.sin(X[wl:] * (0.004 / SS) * (1 + 3 * k[:, None]) + (ys[:, None] ** 1.15) * 0.09 / SS ** 1.15) \
    + 0.5 * amp[:, None] * np.sin(X[wl:] * 0.0113 / SS + ys[:, None] * 0.21 / SS)
sy_ = np.clip(src_y[:, None] + 0 * X[wl:] + 0.3 * rip, 0, wl - 1)
sx_ = np.clip(X[wl:] + rip, 0, w - 1)
refl = np.stack([map_coordinates(img[..., c], [sy_, sx_], order=1) for c in range(3)], -1)
water = hexc('#a9d3ea')
tint = 0.18 + 0.25 * k[:, None, None]
refl = refl * (1 - tint) + water * tint
# glitter: thin horizontal streaks near the sun column
rng = np.random.default_rng(3)
gl = np.zeros((h - wl, w))
for _ in range(int(900 * (w / 4096))):
    yy0 = int(rng.uniform(0, 1) ** 1.6 * (h - wl - 4))
    spread = (0.03 + 0.25 * yy0 / (h - wl)) * w
    xx0 = int(sx + rng.normal(0, spread * 0.35))
    ln = int((4 + 30 * yy0 / (h - wl)) * SS)
    if 0 <= xx0 < w - ln: gl[yy0, xx0:xx0 + ln] += rng.uniform(0.3, 1.0)
gl = gaussian_filter(gl, (0.6 * SS, 1.2 * SS)) * 2.2
refl = refl + gl[..., None] * np.array([1.0, 0.97, 0.88])
img[wl:] = refl
# waterline glow
wlg = np.exp(-((Y - wl) / (1.5 * SS)) ** 2) * 0.35
img = img * (1 - wlg[..., None]) + np.array([1, 0.99, 0.96]) * wlg[..., None]

img = np.clip(img, 0, 1)
im = Image.fromarray((img * 255 + 0.5).astype(np.uint8)).resize((W, H), Image.LANCZOS)
im.save(OUT)
print('rows', [(n, len(paths[n])) for n in ROWS])
