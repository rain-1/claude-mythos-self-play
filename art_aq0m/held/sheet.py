"""NINE POINTS, ONE CENTRE: three paper-cut discs (X = 0, typical, 30) over the exact distribution for n = 9."""
import numpy as np, json, sys, itertools
from PIL import Image, ImageDraw, ImageFont
import depth, paper

S = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0   # scale: 1.0 -> 4096 x 2600
out = sys.argv[2] if len(sys.argv) > 2 else 'nine_points_one_centre.png'
WW, HH = int(4096 * S), int(3000 * S)
n = 9
rng = np.random.default_rng(11)


def X_of(th):
    c = 0
    for i, j, k in itertools.combinations(range(len(th)), 3):
        a = np.sort([th[i], th[j], th[k]]); g = np.diff(np.r_[a, a[0] + 2 * np.pi])
        c += g.max() < np.pi
    return c

# three configurations
th0 = np.sort(rng.uniform(0.35, 2.95, n)) + 2.2
while True:   # a typical one: X = 24, the mode
    th1 = np.sort((np.arange(n) + 0.5 + 2.2 * rng.uniform(-0.5, 0.5, n)) * 2 * np.pi / n + rng.uniform(0, 6.3))
    if X_of(th1) == 24:
        break
th2 = np.sort((np.arange(n) + 0.5 + 0.35 * rng.uniform(-0.5, 0.5, n)) * 2 * np.pi / n + 0.4)
confs = [th0, th1, th2]
Xs = [X_of(t) for t in confs]
print('X', Xs)
MAXX = 30

D = np.full((HH, WW), -1, np.int32)        # -1 = bare paper
C = np.zeros((HH, WW))                      # colour index
rad = int(540 * S); cy = int(820 * S)
cxs = [int(720 * S), int(2048 * S), int(3376 * S)]
span = 1.0 / 0.94
for th, cx in zip(confs, cxs):
    w = 2 * rad
    d = depth.depth(w, -span, span, np.cos(th), np.sin(th))
    sl = (slice(cy - rad, cy + rad), slice(cx - rad, cx + rad))
    m = d >= 0
    D[sl][m] = d[m]
    C[sl][m] = (d[m] / MAXX) ** 0.85
# distribution: stacked paper tiles, one layer per configuration class (count out of 256)
dist = {int(k): v for k, v in json.load(open('../math_triangles/dist.json'))['9'].items()}
x0b, x1b = int(430 * S), int(3666 * S)
slot = (x1b - x0b) / (MAXX + 1)
base = int(2260 * S); unit = 12.0 * S; bw = int(slot * 0.64)
for X in range(MAXX + 1):
    cnt = dist.get(X, 0)
    xc = int(x0b + (X + 0.5) * slot)
    # a flat dot marks every X (also the impossible ones)
    yy, xx = np.ogrid[-int(9 * S):int(9 * S) + 1, -int(9 * S):int(9 * S) + 1]
    if cnt == 0:
        continue
    h = int(round(cnt * unit))
    # layers: every 'unit' rows is one sheet; draw as a slab whose depth steps by layer
    ys = np.arange(base - h, base)
    lay = ((base - ys) / unit).astype(int)            # 0..cnt-1
    sl = (slice(base - h, base), slice(xc - bw // 2, xc + bw // 2))
    # rounded top corners
    D[sl] = np.minimum(cnt, 6)                         # a slab: height capped so shadows stay short
    C[sl] = (X / MAXX) ** 0.85
    D[sl] = D[sl] + 0 * lay[:, None]
LAY = (np.arange(HH)[:, None] - base) / unit
img = paper.render(D, thick=2.6 * S, ss_px=S, cidx=C)
# tile seams inside the bars: a thin lighter line every 'unit' rows (one sheet per class of configurations)
seam = (np.abs(((base - np.arange(HH)[:, None]) / unit) % 1.0 - 0.0) < 0.14 / S) & (np.arange(HH)[:, None] < base)
bar = np.zeros((HH, WW), bool)
for X, cnt in dist.items():
    xc = int(x0b + (X + 0.5) * slot); h = int(round(cnt * unit))
    bar[base - h:base, xc - bw // 2:xc + bw // 2] = True
img = np.where((seam & bar)[..., None], img * 0.93, img)
rgb = paper.srgb(img)
im = Image.fromarray((np.clip(rgb, 0, 1) * 255 + 0.5).astype(np.uint8))
# supersampled overlay: gold ring, pearls, coral pins
SS = 2
ov = Image.new('RGBA', (WW * SS, HH * SS), (0, 0, 0, 0))
d = ImageDraw.Draw(ov)
gold = (214, 178, 96, 255); coral = (246, 120, 108, 255); ink = (92, 77, 102, 255)
R0 = rad / span
for th, cx in zip(confs, cxs):
    d.ellipse([(cx - R0) * SS, (cy - R0) * SS, (cx + R0) * SS, (cy + R0) * SS], outline=gold, width=int(5 * S * SS))
    for t in th:
        px_, py_ = cx + R0 * np.cos(t), cy + R0 * np.sin(t)
        pr = 17 * S
        d.ellipse([(px_ - pr + 3 * S) * SS, (py_ - pr + 5 * S) * SS, (px_ + pr + 3 * S) * SS, (py_ + pr + 5 * S) * SS], fill=(120, 110, 160, 70))
        d.ellipse([(px_ - pr) * SS, (py_ - pr) * SS, (px_ + pr) * SS, (py_ + pr) * SS], fill=(250, 246, 248, 255), outline=(220, 210, 225, 255), width=int(2 * S * SS))
        d.ellipse([(px_ - pr * 0.45 - 4 * S) * SS, (py_ - pr * 0.45 - 5 * S) * SS, (px_ + pr * 0.2 - 4 * S) * SS, (py_ + pr * 0.2 - 5 * S) * SS], fill=(255, 255, 255, 255))
    pr = 13 * S
    d.ellipse([(cx - pr) * SS, (cy - pr) * SS, (cx + pr) * SS, (cy + pr) * SS], fill=coral, outline=(255, 255, 255, 255), width=int(3 * S * SS))
ov = ov.resize((WW, HH), Image.LANCZOS)
im = Image.alpha_composite(im.convert('RGBA'), ov).convert('RGB')
d = ImageDraw.Draw(im)
F = '/usr/share/fonts/truetype/freefont/'
fl = ImageFont.truetype(F + 'FreeSerifItalic.ttf', int(54 * S))
fn = ImageFont.truetype(F + 'FreeSerif.ttf', int(34 * S))
fb = ImageFont.truetype(F + 'FreeSerifBold.ttf', int(40 * S))
labels = ['nobody holds it', 'the usual crowd', 'everyone takes turns']
for X, cx, lab in zip(Xs, cxs, labels):
    t = f'X = {X}  ·  {lab}'
    w = d.textlength(t, font=fl)
    d.text((cx - w / 2, cy + rad + int(28 * S)), t, font=fl, fill=ink[:3])
for X in range(MAXX + 1):
    xc = x0b + (X + 0.5) * slot
    cnt = dist.get(X, 0)
    t = str(X)
    f = fb if X in Xs else fn
    w = d.textlength(t, font=f)
    d.text((xc - w / 2, base + int(14 * S)), t, font=f, fill=(coral[:3] if X in Xs else ink[:3]) if cnt else (190, 180, 195))
    if cnt:
        c = str(cnt); w = d.textlength(c, font=fn)
        d.text((xc - w / 2, base - cnt * unit - int(44 * S)), c, font=fn, fill=(150, 135, 160))
ft = ImageFont.truetype(F + 'FreeSerifBold.ttf', int(84 * S))
fi = ImageFont.truetype(F + 'FreeSerifItalic.ttf', int(46 * S))
fm = ImageFont.truetype(F + 'FreeSerif.ttf', int(40 * S))
y0 = int(2420 * S); x = int(430 * S)
d.text((x, y0 - int(10 * S)), 'Nine Points, One Centre', font=ft, fill=ink[:3])
d.text((x, y0 + int(112 * S)), 'Over each disc, one sheet of paper for every triangle of its nine points; the coral pin counts the sheets over the centre.', font=fi, fill=ink[:3])
d.text((x, y0 + int(180 * S)), 'Below: how many of the 256 equally likely sign patterns give each count X. Exactly X = 31⅛ − ⅛ Σ Wₜ², with Wₜ the imbalance across the t-th line through the centre.', font=fm, fill=ink[:3])
d.text((x, y0 + int(236 * S)), 'X = 0 has chance 9/256 (Wendel); X = 30 only when the points alternate; 1, 2, …, 6, 8, 9, 10, 11, 13, 14, 18, 19, 22 never happen.', font=fm, fill=ink[:3])
im.save(out)
print('saved', out)
