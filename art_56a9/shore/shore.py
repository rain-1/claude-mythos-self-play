# Storybook waterfront of the 1-D city-building sequence (OEIS A400000): a(n) = least h with exactly h earlier
# rooftops visible from height h. Chosen houses string bunting to every rooftop they can see.
import numpy as np, math, sys, json
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy import ndimage as ndi

cfg = json.load(open(sys.argv[1])); out = sys.argv[2]
W, H, SS = cfg['W'], cfg['H'], cfg.get('SS', 2)
A = np.load(cfg['city'])[0, :cfg['n']].astype(int)
n = len(A)
w = W / (n + 2 * cfg.get('pad', 0.6))         # house width in final px
x0 = w * cfg.get('pad', 0.6)
yq = H * cfg['quay']                          # quay line
fh = cfg['floor'] * w                         # floor height
cw, ch = W * SS, H * SS
S = SS
U = W / 1600.0

def hexf(c): return tuple(int(round(255 * v)) for v in c)

FAC = [[1.00, 0.80, 0.62], [0.99, 0.70, 0.72], [0.95, 0.70, 0.90], [0.80, 0.74, 0.99], [0.66, 0.82, 0.99],
       [0.62, 0.92, 0.86], [0.80, 0.94, 0.62], [1.00, 0.90, 0.60], [0.98, 0.76, 0.84], [0.72, 0.90, 0.96]]
SHUT = [[0.55, 0.78, 0.70], [0.60, 0.72, 0.92], [0.98, 0.98, 0.97], [0.86, 0.68, 0.86]]
rng = np.random.default_rng(cfg.get('seed', 3))

img = Image.new('RGB', (cw, ch))
# sky gradient
yy = np.linspace(0, 1, ch)[:, None]
top = np.array(cfg.get('sky_top', [0.66, 0.79, 1.0])); hor = np.array(cfg.get('sky_hor', [1.0, 0.86, 0.83]))
t = np.clip(yy / (yq * S / ch), 0, 1) ** 1.4
sky = top[None, :] * (1 - t[..., None]) + hor[None, :] * t[..., None]
sky = np.repeat(sky, cw, axis=1)
# sun glow
sx, sy = cfg['sun'][0] * cw, cfg['sun'][1] * ch
X = np.arange(cw)[None, :]; Y = np.arange(ch)[:, None]
r = np.hypot(X - sx, Y - sy) / S
glow = np.exp(-r / (200.0 * U)) * 0.22 + np.exp(-r / (40 * U)) * 0.22
sky = sky + glow[..., None] * np.array([1.0, 0.92, 0.75])
disc = np.clip((26 * U - r) / 1.5, 0, 1)
sky = sky * (1 - disc[..., None]) + disc[..., None] * np.array([1.0, 0.97, 0.86])
img = Image.fromarray((np.clip(sky, 0, 1) * 255).astype(np.uint8))
del sky, glow, r
# clouds: soft piles of circles
cl = Image.new('L', (cw, ch), 0); dc = ImageDraw.Draw(cl)
for (cx, cy, s) in cfg['clouds']:
    s = s * U
    for k in range(16):
        ox = rng.uniform(-1.6, 1.6) * s; oy = -abs(rng.normal(0, 0.35)) * s * (1.6 - abs(ox / s)) / 1.6
        rr = s * rng.uniform(0.45, 0.8) * (1.2 - 0.4 * abs(ox / s) / 1.6)
        dc.ellipse([(cx * W + ox - rr) * S, (cy * H + oy - rr) * S, (cx * W + ox + rr) * S, (cy * H + oy + rr) * S], fill=255)
    dc.rectangle([(cx * W - 3 * s) * S, (cy * H) * S, (cx * W + 3 * s) * S, (cy * H + 3 * s) * S], fill=0)
cl = cl.filter(ImageFilter.GaussianBlur(2.5 * S * U))
img.paste((255, 251, 247), (0, 0), cl.point(lambda v: int(v * 0.85)))
# distant lagoon island silhouettes on the horizon behind houses
d = ImageDraw.Draw(img)
xs_ = np.linspace(0, cw, 400)
hill = (yq - 0.035 * H - 0.025 * H * np.clip(np.sin(xs_ / cw * 9.0 + 1.0) + 0.6 * np.sin(xs_ / cw * 23.0), 0, None)) * S
d.polygon([(0, yq * S)] + list(zip(xs_.tolist(), hill.tolist())) + [(cw, yq * S)], fill=hexf([0.84, 0.84, 0.95]))
# houses
shadow = Image.new('L', (cw, ch), 0); dsh = ImageDraw.Draw(shadow)
roofs = []; prevc = None
for i in range(n):
    a = A[i]
    L = (x0 + i * w) * S; R = (x0 + (i + 1) * w) * S
    top_ = (yq - a * fh) * S
    roofs.append(((x0 + (i + .5) * w), yq - a * fh - 0.10 * fh))
    if a == 0:
        # a garden with a round tree
        d.rectangle([L, (yq - 0.18 * fh) * S, R, yq * S], fill=hexf([0.74, 0.90, 0.72]))
        cxp = (L + R) / 2; rr = 0.42 * w * S
        d.rectangle([cxp - 0.05 * w * S, (yq - 0.9 * fh) * S, cxp + 0.05 * w * S, yq * S], fill=hexf([0.80, 0.66, 0.60]))
        d.ellipse([cxp - rr, (yq - 1.05 * fh) * S - rr, cxp + rr, (yq - 1.05 * fh) * S + rr], fill=hexf([0.66, 0.88, 0.66]))
        continue
    c = FAC[(i * 7 + a * 3) % len(FAC)] if i else FAC[0]
    c = FAC[int(rng.integers(len(FAC)))] if cfg.get('random_col') else c
    if i > 0 and c == prevc: c = FAC[(FAC.index(c) + 3) % len(FAC)]
    prevc = c
    d.rectangle([L, top_, R, yq * S], fill=hexf(c))
    # cornice + string courses
    d.rectangle([L, top_ - 0.10 * fh * S, R, top_ + 0.02 * fh * S], fill=hexf([0.99, 0.98, 0.96]))
    d.rectangle([L - 0.03 * w * S, top_ - 0.12 * fh * S, R + 0.03 * w * S, top_ - 0.08 * fh * S], fill=hexf([0.99, 0.98, 0.96]))
    sh_c = SHUT[(i * 5 + a) % len(SHUT)]
    for f in range(a):
        fy0 = (yq - (f + 1) * fh) * S; fy1 = (yq - f * fh) * S
        if f > 0:
            d.rectangle([L, fy1 - 0.025 * fh * S, R, fy1], fill=hexf([0.99, 0.98, 0.96]))
        if f == 0:
            # door + window
            dx0 = L + 0.14 * w * S; dx1 = L + 0.42 * w * S
            d.rectangle([dx0, fy0 + 0.30 * fh * S, dx1, fy1], fill=hexf([0.99, 0.98, 0.96]))
            d.rectangle([dx0 + 0.03 * w * S, fy0 + 0.34 * fh * S, dx1 - 0.03 * w * S, fy1], fill=hexf(sh_c))
            d.ellipse([dx0, fy0 + 0.22 * fh * S, dx1, fy0 + 0.46 * fh * S], fill=hexf([0.99, 0.98, 0.96]))
            d.ellipse([dx0 + 0.03 * w * S, fy0 + 0.25 * fh * S, dx1 - 0.03 * w * S, fy0 + 0.49 * fh * S], fill=hexf(sh_c))
            wx0, wx1 = L + 0.56 * w * S, L + 0.84 * w * S
            d.rectangle([wx0, fy0 + 0.30 * fh * S, wx1, fy0 + 0.66 * fh * S], fill=hexf([0.99, 0.98, 0.96]))
            d.rectangle([wx0 + 0.025 * w * S, fy0 + 0.33 * fh * S, wx1 - 0.025 * w * S, fy0 + 0.63 * fh * S], fill=hexf([0.78, 0.88, 0.98]))
            continue
        for (u0, u1) in ((0.16, 0.42), (0.58, 0.84)):
            wx0, wx1 = L + u0 * w * S, L + u1 * w * S
            # shutters
            sw_ = 0.075 * w * S
            d.rectangle([wx0 - sw_, fy0 + 0.24 * fh * S, wx0, fy0 + 0.72 * fh * S], fill=hexf(sh_c))
            d.rectangle([wx1, fy0 + 0.24 * fh * S, wx1 + sw_, fy0 + 0.72 * fh * S], fill=hexf(sh_c))
            d.rectangle([wx0, fy0 + 0.22 * fh * S, wx1, fy0 + 0.74 * fh * S], fill=hexf([0.99, 0.98, 0.96]))
            d.rectangle([wx0 + 0.025 * w * S, fy0 + 0.25 * fh * S, wx1 - 0.025 * w * S, fy0 + 0.71 * fh * S], fill=hexf([0.78, 0.88, 0.98]))
            d.rectangle([wx0 + 0.025 * w * S, fy0 + 0.47 * fh * S, wx1 - 0.025 * w * S, fy0 + 0.49 * fh * S], fill=hexf([0.99, 0.98, 0.96]))
            # flower box
            if (i + f) % 3 == 0:
                d.rectangle([wx0 - 0.02 * w * S, fy0 + 0.74 * fh * S, wx1 + 0.02 * w * S, fy0 + 0.80 * fh * S], fill=hexf([0.92, 0.72, 0.62]))
                for k in range(5):
                    fx = wx0 + (k + 0.5) / 5 * (wx1 - wx0); rr = 0.035 * w * S
                    d.ellipse([fx - rr, fy0 + 0.72 * fh * S - rr, fx + rr, fy0 + 0.72 * fh * S + rr],
                              fill=hexf([1.0, 0.62, 0.70] if k % 2 else [1.0, 0.95, 0.70]))
    # side shading strip (right edge) for depth
    dsh.rectangle([R - 0.07 * w * S, top_, R, yq * S], fill=60)
img.paste((90, 70, 110), (0, 0), shadow.filter(ImageFilter.GaussianBlur(2 * S * U)))
# quay
d.rectangle([0, yq * S, cw, (yq + 0.05 * fh) * S], fill=hexf([0.95, 0.90, 0.84]))
d.rectangle([0, (yq + 0.05 * fh) * S, cw, (yq + 0.09 * fh) * S], fill=hexf([0.84, 0.78, 0.80]))
yw = yq + 0.09 * fh

def visible(i):
    out = []; best = -1e300; h = A[i]
    for k in range(i - 1, -1, -1):
        s = (A[k] - h) / (i - k)
        if s >= best - 1e-12: out.append(k)
        best = max(best, s)
    return out

# bunting
FL = [[1.0, 0.55, 0.50], [1.0, 0.86, 0.50], [0.62, 0.86, 0.98], [0.70, 0.92, 0.72], [0.92, 0.66, 0.92], [0.99, 0.99, 0.98]]
ink = hexf([0.36, 0.30, 0.40])
for fi_, i in enumerate(cfg['focus']):
    vs = visible(i)
    assert len(vs) == A[i], (i, len(vs), A[i])
    pal = cfg['flag_pal'][fi_]
    for j in vs:
        (xa, ya), (xb, yb) = roofs[i], roofs[j]
        Lg = math.hypot(xb - xa, yb - ya); sag = cfg.get('sag', 0.012) * Lg
        m = int(Lg / 2) + 2
        pts = []
        for q in range(m + 1):
            u = q / m
            pts.append((xa + (xb - xa) * u, ya + (yb - ya) * u + sag * 4 * u * (1 - u)))
        d.line([(p[0] * S, p[1] * S) for p in pts], fill=ink, width=max(1, int(1.3 * S * U)))
        fl = cfg.get('flag', 15.0) * U; nfl = int(Lg / (fl * 1.35))
        for q in range(1, nfl):
            u = q / nfl
            px_ = xa + (xb - xa) * u; py_ = ya + (yb - ya) * u + sag * 4 * u * (1 - u)
            u2 = min(1, u + 0.5 * fl / Lg)
            px2 = xa + (xb - xa) * u2; py2 = ya + (yb - ya) * u2 + sag * 4 * u2 * (1 - u2)
            col = pal[(q + j) % len(pal)]
            mxp, myp = (px_ + px2) / 2, (py_ + py2) / 2
            d.polygon([(px_ * S, py_ * S), (px2 * S, py2 * S), (mxp * S, (myp + fl * 1.15) * S)], fill=hexf(col))
    # rooftop flagpole on the focus house
    xa, ya = roofs[i]
    d.line([(xa * S, (ya + 0.1 * fh) * S), (xa * S, (ya - 0.55 * fh) * S)], fill=ink, width=int(2 * S * U))
    d.polygon([(xa * S, (ya - 0.55 * fh) * S), ((xa + 0.5 * w) * S, (ya - 0.45 * fh) * S), (xa * S, (ya - 0.35 * fh) * S)], fill=hexf(pal[0]))
# moored boats
for (bx, bc) in cfg['boats']:
    cx_ = (x0 + bx * w) * S; by = (yw + 0.02 * fh) * S; bl = 0.95 * w * S; bh = 0.22 * fh * S
    d.chord([cx_ - bl, by - bh, cx_ + bl, by + bh], 0, 180, fill=hexf(FAC[bc]))
    d.rectangle([cx_ - bl, by - 0.12 * bh, cx_ + bl, by + 0.06 * bh], fill=hexf([0.99, 0.98, 0.96]))
# reflection
arr = np.asarray(img).astype(np.float32) / 255
yws = int(yw * S)
water = np.array(cfg.get('water', [0.62, 0.84, 0.92]))
for y in range(yws, ch):
    dy = y - yws
    src = yws - 1 - int(dy * 1.0)
    if src < 0: src = 0
    amp = (2.0 * U * S + 0.012 * dy) * 0.6
    sh_ = int(amp * math.sin(dy / (5.0 * S * U) + 0.3 * math.sin(dy / (37.0 * S * U))))
    row = np.roll(arr[src], sh_, axis=0)
    k = min(1.0, 0.30 + dy / (ch - yws) * 0.35)
    arr[y] = row * (1 - k) + water * k
    if (dy // max(1, int(3 * S * U))) % 11 == 0 and dy > 6 * S * U:
        arr[y] = arr[y] * 0.9 + 0.1
img = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)
# caption
d = ImageDraw.Draw(img)
fb = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf', int(H * 0.040))
fi = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeSerifItalic.ttf', int(H * 0.021))
fs = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeSerif.ttf', int(H * 0.0175))
tx, ty = int(W * cfg['cap'][0]), int(H * cfg['cap'][1])
inkc = (92, 77, 102)
d.text((tx, ty), cfg['title'], font=fb, fill=inkc); ty += int(H * 0.056)
for k, line in enumerate(cfg['lines']):
    d.text((tx, ty), line, font=fi if k == 0 else fs, fill=inkc); ty += int(H * (0.031 if k == 0 else 0.026))
img.save(out)
