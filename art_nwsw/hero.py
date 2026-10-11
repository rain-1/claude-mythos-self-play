"""Hero: 'A Half and Two Sixths' - the five-sixths plate at finite N, leftover wedge on the cloth."""
import numpy as np, sys, time
from render import Canvas, wheel, hexc, CORAL, PLUM, FONT, FONT_I, FONT_M, cutter
from pizza import five_sixths, check, strict_check
from PIL import Image, ImageDraw, ImageFont

W = int(sys.argv[1]); N = int(sys.argv[2]); eps = float(sys.argv[3]); out = sys.argv[4]
k = W / 4096
t0 = time.time()
S = five_sixths(N, eps)
ok, o, v = check(S, 1 - eps)
print("on plate", len(S), "of", 2 * N, ok, strict_check(S, 1 - eps, 400), f"{time.time()-t0:.1f}s", flush=True)
ph = np.pi / (2 * N)
d = np.sqrt(1 - (1 - eps) ** 2)
big = sorted([s for s in S if abs(s[1]) < 1e-9], key=lambda s: s[2])
top = sorted([s for s in S if s[1] > 1e-9], key=lambda s: s[2])
bot = sorted([s for s in S if s[1] < -1e-9], key=lambda s: -s[2])
nleft = 2 * N - len(S)
order = big + bot + [None] * nleft + top[::-1]          # position in the original pizza
HOFF = 0.02
cv = Canvas(W, W, seed=2)
cv.cloth(dot_r=30 * k, spacing=300 * k, tint=0.55)
cx, cy, U = 1440 * k, 1640 * k, 1040 * k
cv.plate(cx, cy, (1 - eps) * U, 1.30 * U, base_h=10 * k, rim_h=36 * k)
def P(x, y): return cx + U * x, cy - U * y
for i, s in enumerate(order):
    if s is None: continue
    ax, ay = P(s[0], s[1])
    cv.slice(ax, ay, -s[2], ph, U, wheel(i / (2 * N) + HOFF), 10 * k, T=15 * k, bevel=3.0 * k, gap=0.7 * k,
             sprinkles=3.0, sp_seed=1000 + i)
lo = [i for i, s in enumerate(order) if s is None]
apx, apy = 4050 * k, 1700 * k
for j, i in enumerate(lo):
    th = np.pi + (2 * (j - (nleft - 1) / 2)) * ph
    cv.slice(apx, apy, th, ph, U, wheel(i / (2 * N) + HOFF), 0.0, T=15 * k, bevel=3.0 * k, gap=0.7 * k,
             sprinkles=3.0, sp_seed=1000 + i)
rs = np.random.default_rng(77)
spal = [hexc("#ffffff"), hexc("#ff8fa3"), hexc("#ffd98a"), hexc("#9fe3c0"), hexc("#8fd3f4"), hexc("#c7a4ff")]
for q in range(46):
    rr = U * (1.08 + 0.25 * rs.random() ** 1.5); aa = np.pi + rs.normal(0, 0.45)
    px, py = apx + rr * np.cos(aa), apy + rr * np.sin(aa)
    cv.sprinkle(px, py, rs.uniform(0, np.pi), 0.013 * U + 6 * k, 0.0045 * U + 2.2 * k, spal[rs.integers(6)])
cutter(cv, 3200 * k, 2700 * k, np.radians(28), 170 * k)
for (x, y) in [(d, 0.0), (top[0][0], top[0][1]), (bot[0][0], bot[0][1])]:
    px, py = P(x, y)
    cv.bead(px, py, 12 * k, CORAL, height=30 * k)
t1 = time.time()
cv.shade(shadow_len=300 * k)
print("shade", f"{time.time()-t1:.1f}s", flush=True)
im = Image.fromarray((cv.img * 255 + 0.5).astype(np.uint8))

# ---- legend: the pizza before, flat, leftover slices pulled out (supersampled) ----
SS = 3
lc = (3430 * k, 470 * k); lr = 300 * k
box = (int(lc[0] - 1.45 * lr), int(lc[1] - 1.3 * lr), int(lc[0] + 1.45 * lr), int(lc[1] + 1.35 * lr))
bw, bh = box[2] - box[0], box[3] - box[1]
pane = im.crop(box).resize((bw * SS, bh * SS), Image.LANCZOS)
dr = ImageDraw.Draw(pane)
def toS(x, y): return ((x - box[0]) * SS, (y - box[1]) * SS)
for i in range(2 * N):
    a0 = np.pi / 2 + i * 2 * ph * -1 * -1           # original pizza: slice i at angle  (ccw from fan1 start)
    # slice i of the original pizza sits at angle pi - W + (2i+1)ph  (math), i.e. continuing ccw
    W1 = len(big) * ph
    th = np.pi - W1 + (2 * i + 1) * ph
    pull = 0.16 * lr if order[i] is None else 0.0
    ox, oy = lc[0] + pull * np.cos(th), lc[1] - pull * np.sin(th)
    angs = np.linspace(th - ph, th + ph, 12)
    pts = [toS(ox, oy)] + [toS(ox + lr * np.cos(a), oy - lr * np.sin(a)) for a in angs]
    c = wheel(i / (2 * N) + HOFF) ** 1.35
    fill = tuple(int(255 * x) for x in c)
    dr.polygon(pts, fill=fill, outline=(255, 255, 255), width=max(1, int(0.8 * k * SS)))
    if order[i] is None:
        pass
# crust ring
cc = tuple(int(255 * x) for x in hexc("#f6dca8"))
for i in range(2 * N):
    W1 = len(big) * ph
    th = np.pi - W1 + (2 * i + 1) * ph
    pull = 0.16 * lr if order[i] is None else 0.0
    ox, oy = lc[0] + pull * np.cos(th), lc[1] - pull * np.sin(th)
    bb = [*toS(ox - lr, oy - lr), *toS(ox + lr, oy + lr)]
    dr.arc(bb, start=np.degrees(-th - ph) + 0.6, end=np.degrees(-th + ph) - 0.6, fill=cc, width=int(0.07 * lr * SS))
pane = pane.resize((bw, bh), Image.LANCZOS)
im.paste(pane, box[:2])
D = ImageDraw.Draw(im)
fI = ImageFont.truetype(FONT_I, int(46 * k)); fM = ImageFont.truetype(FONT_M, int(34 * k))
plum = tuple(int(255 * x) for x in PLUM)
D.text((lc[0], lc[1] + 1.22 * lr), "the pizza, before:", font=fI, fill=plum, anchor="ms")
D.text((lc[0], lc[1] + 1.22 * lr + 46 * k), "hue = where each slice was", font=fM, fill=plum, anchor="ms")

# ---- caption ----
x0, y0 = 150 * k, 3330 * k
fT = ImageFont.truetype(FONT, int(118 * k))
f2 = ImageFont.truetype(FONT_I, int(62 * k))
f3 = ImageFont.truetype(FONT_M, int(37 * k))
coral = tuple(int(255 * x) for x in CORAL)
D.text((x0, y0), "A Half and Two Sixths", font=fT, fill=plum)
y = y0 + 160 * k
D.text((x0, y), f"A pizza of radius 1 cut into {2*N} slices; a plate of radius 0.99999. {len(S)} slices fit.", font=f2, fill=plum)
y += 80 * k
D.text((x0, y), "Half the pizza slides √(2ε) off-centre, and two sixty-degree fans hang from the rim.", font=f2, fill=plum)
y += 104 * k
D.text((x0, y), f"MathOverflow 515908 · as the slices thin out this fills 5/6 − O(√ε) of the pizza (best posted: 3√3/2π ≈ 0.827)", font=f3, fill=plum)
y += 52 * k
D.text((x0, y), "●", font=f3, fill=coral)
D.text((x0 + 36 * k, y), f"the three apexes  ·  {nleft} slices are left over, and some always will be: π(1−ε)² < π", font=f3, fill=plum)
im.save(out)
print("done", f"{time.time()-t0:.1f}s")
