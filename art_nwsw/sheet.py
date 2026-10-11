"""Piece 3: best packings found for M slices of angle 2pi/M on a plate of radius 0.999."""
import numpy as np, sys, json, glob, time
from render import Canvas, wheel, hexc, CORAL, PLUM, FONT, FONT_I, FONT_M
from pizza import strict_check, check
from PIL import Image, ImageDraw, ImageFont
from fractions import Fraction

W = int(sys.argv[1]); out = sys.argv[2]
k = W / 4096
H = int(W * 4380 / 4096)
data = {}
for f in sorted(glob.glob("s2_M*.json")) + sorted(glob.glob("s3_M*.json")):
    d = json.load(open(f))
    if d['M'] not in data or d['best'] > data[d['M']]['best']:
        data[d['M']] = d
Ms = sorted(data)
print("M:", [(m, data[m]['best']) for m in Ms])
cv = Canvas(W, H, seed=11)
cv.cloth(dot_r=22 * k, spacing=240 * k, tint=0.5, seed=12)
cols = 4
U = 330 * k
cells = []
slot = 0
for M in Ms:
    r_, c_ = divmod(slot, cols)
    cx = 530 * k + c_ * 1012 * k; cy = 1080 * k + r_ * 1180 * k
    cells.append((M, cx, cy)); slot += 1
for idx, (M, cx, cy) in enumerate(cells):
    d = data[M]; eps = d['eps']; S = d['slices']; kk = len(S)
    ok, o, v = check([tuple(s) for s in S], 1 - eps); so, sv = strict_check([tuple(s) for s in S], 1 - eps, 2000)
    assert ok and so <= 0 and sv < 1e-7, (M, o, v, so, sv)
    # rotate so the configuration's 'heaviest' side points left (consistent look)
    cxm = np.mean([s[0] + 0.5 * np.cos(s[2]) for s in S]); cym = np.mean([s[1] + 0.5 * np.sin(s[2]) for s in S])
    rot = np.pi - np.arctan2(cym, cxm) if np.hypot(cxm, cym) > 0.03 else 0.0
    cr, sr = np.cos(rot), np.sin(rot)
    cv.plate(cx, cy, (1 - eps) * U, (1 - eps) * U + 0.30 * U, base_h=6 * k, rim_h=14 * k)
    base_hue = idx / len(cells)
    order = sorted(range(kk), key=lambda i: np.arctan2(S[i][1] + 0.5 * np.sin(S[i][2]), S[i][0] + 0.5 * np.cos(S[i][2])))
    for j, i in enumerate(order):
        ax, ay, th, ph = S[i]
        x2, y2 = ax * cr - ay * sr, ax * sr + ay * cr
        hue = base_hue + 0.10 * (j / max(1, kk - 1) - 0.5)
        cv.slice(cx + U * x2, cy - U * y2, -(th + rot), ph, U, wheel(hue + 0.02), 6 * k, T=10 * k,
                 bevel=3 * k, gap=0.8 * k, crust=0.085, sprinkles=4.0, sp_seed=M * 100 + j)
cv.shade(shadow_len=170 * k)
im = Image.fromarray((cv.img * 255 + 0.5).astype(np.uint8))
D = ImageDraw.Draw(im)
plum = tuple(int(255 * x) for x in PLUM); coral = tuple(int(255 * x) for x in CORAL)
fN = ImageFont.truetype(FONT, int(60 * k)); fS = ImageFont.truetype(FONT_I, int(46 * k))
for (M, cx, cy) in cells:
    kk = data[M]['best']; fr = Fraction(kk, M)
    hot = (M == 6 and kk > 3) or (M == 4 and kk > 1)
    D.text((cx, cy + 1.30 * U + 100 * k), f"{kk} of {M}", font=fN, fill=coral if hot else plum, anchor="ms")
    if hot:
        R = 1.30 * U + 18 * k
        for a in np.arange(0, 360, 4):
            D.arc([cx - R, cy - R, cx + R, cy + R], a, a + 2.2, fill=coral, width=max(1, int(4 * k)))
    D.text((cx, cy + 1.30 * U + 160 * k), f"slices of {360//M if 360 % M == 0 else round(360/M,1)}°", font=fS, fill=plum, anchor="ms")
fT = ImageFont.truetype(FONT, int(104 * k)); f2 = ImageFont.truetype(FONT_I, int(54 * k)); fM = ImageFont.truetype(FONT_M, int(33 * k))
x0, y0 = 130 * k, 150 * k
D.text((x0, y0), "How Many Still Fit", font=fT, fill=plum)
D.text((x0, y0 + 150 * k), "Cut a pizza into M equal slices and carry them to a plate a hair smaller than the pizza.", font=f2, fill=plum)
D.text((x0, y0 + 222 * k), "The best packing found for each M; the rest stay in the kitchen.", font=f2, fill=plum)
D.text((x0, y0 + 312 * k), "MathOverflow 515908 · plate radius 0.999 · L-BFGS from random and from fan-shaped starts · every packing re-checked (overlap area, sampled depth, exact radius) · best found, not proved", font=fM, fill=plum)
D.text((x0, y0 + 360 * k), "coral: more than the question's posted value (it guessed 3 of 6; four sixty-degree slices fit, their tips nudged apart around the centre)", font=fM, fill=coral)
im.save(out)
print("saved")
