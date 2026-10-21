"""THREE WAYS TO CATCH A CHORD: Bertrand's paradox as three dreamcatchers at dawn.
Threads longer than the side of the inscribed triangle are warm; shorter ones are cool."""
import numpy as np, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0
out = sys.argv[2] if len(sys.argv) > 2 else 'three_ways_to_catch_a_chord.png'
NCH = int(sys.argv[3]) if len(sys.argv) > 3 else 240
WW, HH = int(4096 * S), int(3072 * S)
SS = 2
W2, H2 = WW * SS, HH * SS
rng = np.random.default_rng(7)


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def grad3(stops, t):
    t = min(max(t, 0), 1) * (len(stops) - 1)
    i = min(int(t), len(stops) - 2)
    return lerp(stops[i], stops[i + 1], t - i)

# ------------------------------------------------------------------ sky
y = np.linspace(0, 1, HH)[:, None, None]
sky = np.array([[0.80, 0.84, 1.0], [0.93, 0.86, 0.98], [1.0, 0.89, 0.88], [1.0, 0.95, 0.84], [1.0, 0.98, 0.93]])
t = y[..., 0] * (len(sky) - 1)
i = np.minimum(t.astype(int), len(sky) - 2)
f = (t - i)[..., None]
bg = sky[i] * (1 - f) + sky[i + 1] * f
bg = np.broadcast_to(bg, (HH, WW, 3)).copy()
# soft sun glow low on the right
yy, xx = np.mgrid[0:HH, 0:WW]
g = np.exp(-(((xx - 0.78 * WW) / (0.30 * WW)) ** 2 + ((yy - 0.80 * HH) / (0.22 * HH)) ** 2))
bg = bg * (1 - 0.25 * g[..., None]) + np.array([1.0, 0.97, 0.88]) * 0.25 * g[..., None]
# distant hills (two pastel layers)
for k, (hy, amp, col) in enumerate([(0.86, 0.020, (0.86, 0.90, 0.96)), (0.91, 0.016, (0.80, 0.92, 0.86))]):
    xs = np.linspace(0, 1, WW)
    ridge = hy + amp * np.sin(xs * 6.1 + k * 2) + 0.6 * amp * np.sin(xs * 15.3 + k) + 0.3 * amp * np.sin(xs * 37 + 3 * k)
    m = (yy / HH) > ridge[None, :]
    bg[m] = bg[m] * 0.25 + np.array(col) * 0.75
im = Image.fromarray((np.clip(bg, 0, 1) * 255).astype(np.uint8)).convert('RGBA').resize((W2, H2), Image.BICUBIC)
L = Image.new('RGBA', (W2, H2), (0, 0, 0, 0))
d = ImageDraw.Draw(L)

# ------------------------------------------------------------------ the branch
bx = np.linspace(-0.05, 1.05, 300) * W2
by = (0.095 + 0.018 * np.sin(np.linspace(0, 3.1, 300)) + 0.01 * np.linspace(0, 1, 300)) * H2
d.line(list(zip(bx, by)), fill=(196, 160, 150, 255), width=int(34 * S * SS), joint='curve')
d.line(list(zip(bx, by - 8 * S * SS)), fill=(222, 192, 182, 255), width=int(10 * S * SS), joint='curve')
# blossom on the branch
for k in range(26):
    px = rng.uniform(0.02, 0.98) * W2; py = np.interp(px, bx, by) + rng.normal(0, 14) * S * SS
    for p in range(5):
        a = p * 2 * np.pi / 5 + rng.uniform(0, 1)
        r = 16 * S * SS
        cx, cy = px + np.cos(a) * r * 0.9, py + np.sin(a) * r * 0.9
        d.ellipse([cx - r * 0.75, cy - r * 0.75, cx + r * 0.75, cy + r * 0.75], fill=(255, 214, 226, 235))
    d.ellipse([px - 6 * S * SS, py - 6 * S * SS, px + 6 * S * SS, py + 6 * S * SS], fill=(255, 226, 150, 255))

COOL = [(120, 210, 178), (112, 196, 222), (128, 170, 238)]   # short: mint -> aqua -> sky
WARM = [(255, 170, 120), (246, 108, 118)]                   # long: peach -> coral
ROOT3 = np.sqrt(3)


def chords(method, N):
    if method == 'ends':
        a = rng.uniform(0, 2 * np.pi, N); b = rng.uniform(0, 2 * np.pi, N)
        return a, b
    if method == 'radius':
        phi = rng.uniform(0, 2 * np.pi, N); dist = rng.uniform(0, 1, N)
    else:  # midpoint uniform in the disc
        phi = rng.uniform(0, 2 * np.pi, N); dist = np.sqrt(rng.uniform(0, 1, N))
    h = np.arccos(dist)
    return phi - h, phi + h


def catcher(cx, cy, R, method, N, ribbon):
    a, b = chords(method, N)
    P = np.stack([np.cos(a), np.sin(a)], 1); Q = np.stack([np.cos(b), np.sin(b)], 1)
    ln = np.linalg.norm(P - Q, axis=1)
    long_ = ln > ROOT3
    # draw cool (short) first, warm (long) on top; within each, shortest first
    order = np.lexsort((ln, long_))
    lw = max(2, int(2.3 * S * SS))
    for k in order:
        if long_[k]:
            c = grad3(WARM, (ln[k] - ROOT3) / (2 - ROOT3))
        else:
            c = grad3(COOL, ln[k] / ROOT3)
        p = (cx + R * P[k, 0], cy + R * P[k, 1]); q = (cx + R * Q[k, 0], cy + R * Q[k, 1])
        d.line([p, q], fill=c + (225,), width=lw)
    # the inscribed triangle in gold, very fine
    tri = [(cx + R * np.cos(-np.pi / 2 + j * 2 * np.pi / 3), cy + R * np.sin(-np.pi / 2 + j * 2 * np.pi / 3)) for j in range(4)]
    d.line(tri, fill=(226, 190, 104, 230), width=int(5 * S * SS), joint='curve')
    # hoop wrapped in ribbon: a thick ring with diagonal wraps
    hw = 30 * S * SS
    d.ellipse([cx - R - hw / 2, cy - R - hw / 2, cx + R + hw / 2, cy + R + hw / 2], outline=ribbon + (255,), width=int(hw))
    nw = 120
    for j in range(nw):
        t0 = j * 2 * np.pi / nw
        p1 = (cx + (R - hw / 2) * np.cos(t0), cy + (R - hw / 2) * np.sin(t0))
        p2 = (cx + (R + hw / 2) * np.cos(t0 + 0.03), cy + (R + hw / 2) * np.sin(t0 + 0.03))
        d.line([p1, p2], fill=lerp(ribbon, (255, 255, 255), 0.45) + (255,), width=int(5 * S * SS))
    # highlight on the upper-left of the ring
    d.arc([cx - R - hw * 0.25, cy - R - hw * 0.25, cx + R + hw * 0.25, cy + R + hw * 0.25], 190, 260, fill=(255, 255, 255, 140), width=int(6 * S * SS))
    return long_.mean()


def feather(x, y, ln, ang, col):
    # quill + soft vane made of many short barbs
    ux, uy = np.sin(ang), np.cos(ang)
    vx, vy = uy, -ux
    for s in np.linspace(0.12, 1.0, 70):
        w = ln * 0.22 * np.sin(np.pi * min(1, s * 1.05)) ** 0.8
        px, py = x + ux * ln * s, y + uy * ln * s
        for side in (-1, 1):
            ex = px + side * vx * w + ux * w * 0.55; ey = py + side * vy * w + uy * w * 0.55
            d.line([(px, py), (ex, ey)], fill=lerp(col, (255, 255, 255), 0.05 + 0.22 * (side > 0) + 0.25 * (s < 0.3)) + (235,), width=int(4 * S * SS))
    # tip darker band
    d.line([(x, y), (x + ux * ln, y + uy * ln)], fill=(236, 226, 228, 255), width=int(5 * S * SS))

methods = [('ends', 'two random ends', (196, 220, 246)), ('radius', 'a random radius, then a point on it', (246, 214, 196)), ('mid', 'a random midpoint', (214, 236, 214))]
R = 560 * S * SS
xs = [0.18, 0.5, 0.82]; ys = [0.40, 0.44, 0.40]
fr = []
for (m, lab, rib), fx, fy in zip(methods, xs, ys):
    cx, cy = fx * W2, fy * H2
    # hanging string
    top = np.interp(cx, bx, by)
    d.line([(cx, top), (cx, cy - R - 15 * S * SS)], fill=(170, 150, 165, 255), width=int(4 * S * SS))
    fr.append(catcher(cx, cy, R, m, NCH, rib))
    # three feathers on strings, with beads
    for k, (dx, ln, col) in enumerate([(-0.55, 330, (250, 170, 186)), (0.0, 400, (160, 192, 248)), (0.55, 330, (252, 210, 130))]):
        sx = cx + dx * R * 0.8; sy = cy + np.sqrt(max(0, 1 - (dx * 0.8) ** 2)) * R + 12 * S * SS
        ey = sy + 150 * S * SS
        d.line([(sx, sy), (sx, ey)], fill=(170, 150, 165, 255), width=int(3 * S * SS))
        br = 15 * S * SS
        d.ellipse([sx - br, ey - br * 1.6, sx + br, ey + br * 0.4], fill=(250, 140, 130, 255))
        d.ellipse([sx - br * 0.5, ey - br * 1.3, sx - br * 0.0, ey - br * 0.8], fill=(255, 230, 225, 255))
        feather(sx, ey + br * 0.3, ln * S * SS, 0.10 * (k - 1), col)
print('fractions', fr)
im = Image.alpha_composite(im, L).resize((WW, HH), Image.LANCZOS).convert('RGB')
d2 = ImageDraw.Draw(im)
F = '/usr/share/fonts/truetype/freefont/'
ink = (92, 77, 102)
fl = ImageFont.truetype(F + 'FreeSerifBold.ttf', int(64 * S)); fs = ImageFont.truetype(F + 'FreeSerifItalic.ttf', int(42 * S))
for (m, lab, rib), fx, fy, p, ans in zip(methods, xs, ys, fr, ['1/3', '1/2', '1/4']):
    cx = fx * WW
    t = ans; w = d2.textlength(t, font=fl)
    yb = fy * HH + 560 * S + 560 * S
    d2.text((cx - w / 2, yb), t, font=fl, fill=ink)
    t = f'{lab}  ·  {p * 100:.1f}% of these {NCH} threads are long'
    w = d2.textlength(t, font=fs)
    d2.text((cx - w / 2, yb + 78 * S), t, font=fs, fill=ink)
ft = ImageFont.truetype(F + 'FreeSerifBold.ttf', int(92 * S))
fi = ImageFont.truetype(F + 'FreeSerifItalic.ttf', int(48 * S))
x = int(160 * S); y0 = int(2770 * S)
d2.text((x, y0), 'Three Ways to Catch a Chord', font=ft, fill=ink)
d2.text((x, y0 + 116 * S), 'One statement: “a random chord is longer than the side of the inscribed triangle” (gold). Three honest ways to choose the chord, three probabilities. Long threads warm, short threads cool (Bertrand, 1889).', font=fi, fill=ink)
im.save(out)
print('saved', out)
