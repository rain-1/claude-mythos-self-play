"""Piece 2: cross (rectangles of alternating slices) vs fans, plate radius 1 - eps for four eps."""
import numpy as np, sys, time, json
from render import Canvas, wheel, hexc, CORAL, PLUM, FONT, FONT_I, FONT_M
from pizza import five_sixths, cross, check, strict_check, fan_order
from PIL import Image, ImageDraw, ImageFont

W = int(sys.argv[1]); out = sys.argv[2]
N = 40
EPS = [1e-1, 1e-2, 1e-3, 1e-5]
LAB = ["ε = 0.1", "ε = 0.01", "ε = 0.001", "ε = 0.00001"]
k = W / 4096
H = int(W * 2900 / 4096)
ph = np.pi / (2 * N)
rows = []
t0 = time.time()
for e in EPS:
    A = cross(N, e); B = five_sixths(N, e)
    for S in (A, B):
        ok, o, v = check(S, 1 - e); so, sv = strict_check(S, 1 - e, 300)
        assert ok and so <= 1e-12 and sv < 1e-9, (e, o, v, so, sv)
    rows.append((A, B))
    print(e, len(A), len(B), f"{time.time()-t0:.0f}s", flush=True)
json.dump([[len(a), len(b)] for a, b in rows], open("tourney_counts.json", "w"))
cv = Canvas(W, H, seed=5)
cv.cloth(dot_r=22 * k, spacing=230 * k, tint=0.5, seed=8)
U = 345 * k
xs = [650 * k + j * 965 * k for j in range(4)]
ys = [700 * k, 1760 * k]
HOFF = 0.02
centres = []
for j, (A, B) in enumerate(rows):
    e = EPS[j]
    for i, S in enumerate((A, B)):
        cx, cy = xs[j], ys[i]
        centres.append((cx, cy))
        cv.plate(cx, cy, (1 - e) * U, (1 - e) * U + 0.30 * U, base_h=6 * k, rim_h=14 * k)
        seq = list(S) + [None] * (2 * N - len(S)) if i == 0 else fan_order(S, N)
        for q, s in enumerate(seq):
            if s is None: continue
            ax, ay = cx + U * s[0], cy - U * s[1]
            cv.slice(ax, ay, -s[2], ph, U, wheel(q / (2 * N) + HOFF), 6 * k,
                     T=9 * k, bevel=2.5 * k, gap=0.7 * k, crust=0.085, sprinkles=0)
print("slices", f"{time.time()-t0:.0f}s", flush=True)
cv.shade(shadow_len=160 * k)
im = Image.fromarray((cv.img * 255 + 0.5).astype(np.uint8))
D = ImageDraw.Draw(im)
plum = tuple(int(255 * x) for x in PLUM); coral = tuple(int(255 * x) for x in CORAL)
fL = ImageFont.truetype(FONT_I, int(54 * k)); fC = ImageFont.truetype(FONT, int(58 * k)); fM = ImageFont.truetype(FONT_M, int(34 * k))
for j, (A, B) in enumerate(rows):
    e = EPS[j]
    D.text((xs[j], 140 * k), LAB[j], font=fL, fill=plum, anchor="ms")
    for i, S in enumerate((A, B)):
        cx, cy = xs[j], ys[i]
        n = len(S); other = len(rows[j][1 - i])
        win = n > other
        # pizza outline (radius 1) as a dashed coral ring when it differs visibly from the well
        R = U
        for a in np.arange(0, 360, 5):
            D.arc([cx - R, cy - R, cx + R, cy + R], a, a + 3, fill=coral, width=max(1, int(2.2 * k)))
        txt = f"{n} of {2*N}"
        D.text((cx, cy + 1.30 * U + 92 * k), txt, font=fC, fill=coral if win else plum, anchor="ms")
for lab, yy in (("rectangles", ys[0]), ("fans", ys[1])):
    tw = int(D.textlength(lab, font=fL)) + 20; th_ = int(80 * k)
    tmp = Image.new("RGBA", (tw, th_), (0, 0, 0, 0))
    ImageDraw.Draw(tmp).text((10, th_ * 0.75), lab, font=fL, fill=plum + (255,), anchor="ls")
    tmp = tmp.rotate(90, expand=True)
    im.paste(tmp, (int(95 * k), int(yy - tw / 2)), tmp)
fT = ImageFont.truetype(FONT, int(100 * k)); f2 = ImageFont.truetype(FONT_I, int(54 * k))
y = 2390 * k
D.text((140 * k, y), "A Hair Decides Which Plate Wins", font=fT, fill=plum); y += 140 * k
D.text((140 * k, y), "The same eighty slices on plates of radius 1 − ε. Top: Jonathan Love's cross of rectangles, each slice beside a reversed twin.", font=f2, fill=plum); y += 70 * k
D.text((140 * k, y), "Bottom: half a pizza pushed √(2ε) aside, plus two sixty-degree fans. Rectangles lose ε; fans lose √ε, but start from 5/6.", font=f2, fill=plum); y += 84 * k
D.text((140 * k, y), "MathOverflow 515908 · dashed coral: the pizza's own radius · coral count: the winner · limits as slices thin: (2√3−1)/π ≈ 0.784 vs 5/6 ≈ 0.833", font=fM, fill=plum)
im.save(out)
print("done", f"{time.time()-t0:.0f}s")
