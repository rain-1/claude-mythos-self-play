"""Base picture for the Droste twist: the balloon lake seen from a little jetty,
where an easel holds a canvas that shows exactly this picture.
usage: python3 compose.py view_raw.npy base.npy base_preview.png
"""
import sys, json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, '../balloons')
from post import tone

view = np.load(sys.argv[1]); N = view.shape[0]
V = json.loads(sys.argv[4]) if len(sys.argv) > 4 else {}
base = tone(view, 1.0)  # sRGB float
SS = 2
M = N * SS
over = Image.new('RGBA', (M, M), (0, 0, 0, 0))
sh = Image.new('L', (M, M), 0)
d = ImageDraw.Draw(over); ds = ImageDraw.Draw(sh)
P = lambda x, y: (x * M, y * M)

# canvas square (the recursion window) — x0, y0, side as fractions
cx0, cy0, cs = V.get('canvas', [0.35, 0.40, 0.30])
cb = cy0 + cs

# ---------------- jetty: perspective planks from the bottom edge toward the lake
jt = V.get('jetty_top', 0.70)
xl0, xr0 = 0.18, 0.82   # bottom edge
xl1, xr1 = 0.40, 0.60   # far end
def jx(t, side):  # t 0 bottom .. 1 far end
    return (xl0 + (xl1 - xl0) * t) if side == 0 else (xr0 + (xr1 - xr0) * t)
def jy(t):
    return 1.0 + (jt - 1.0) * t
wood = [(233, 214, 236), (240, 222, 236), (226, 210, 234), (238, 226, 240)]
# planks with perspective spacing (uniform in 1/z)
nplank = 26
zs = np.linspace(1.0, 3.2, nplank + 1)  # depth multiples
ts = (1 - 1 / zs) / (1 - 1 / zs[-1])
for k in range(nplank):
    t0, t1 = ts[k], ts[k + 1]
    poly = [P(jx(t0, 0), jy(t0)), P(jx(t0, 1), jy(t0)), P(jx(t1, 1), jy(t1)), P(jx(t1, 0), jy(t1))]
    d.polygon(poly, fill=wood[k % 4] + (255,))
    d.line([P(jx(t1, 0), jy(t1)), P(jx(t1, 1), jy(t1))], fill=(205, 186, 214, 255), width=max(1, int(0.0016 * M / (1 + 2 * t1))))
# side beam
for side in (0, 1):
    pts = [P(jx(0, side), 1.0), P(jx(1, side), jt)]
    d.line(pts, fill=(200, 180, 212, 255), width=int(0.006 * M))
# posts into the water at the far end
for side in (0, 1):
    x = jx(1, side); y = jt
    d.rectangle([P(x - 0.004, y - 0.03), P(x + 0.004, y + 0.03)], fill=(214, 196, 224, 255))
    d.rectangle([P(x - 0.004, y - 0.03), P(x + 0.004, y - 0.026)], fill=(240, 230, 244, 255))

# ---------------- easel (three legs) + shadow
honey = (240, 208, 160, 255); honey_d = (214, 176, 132, 255); honey_l = (250, 228, 190, 255)
foot_l = (cx0 + 0.02, 0.965); foot_r = (cx0 + cs - 0.02, 0.965); apex = (cx0 + cs / 2, cy0 - 0.075)
foot_b = (cx0 + cs / 2, 0.90)
lw = 0.012
def leg(a, b, w, col, col_l):
    ax, ay = a; bx, by = b
    nx, ny = by - ay, -(bx - ax); n = (nx * nx + ny * ny) ** 0.5; nx, ny = nx / n * w / 2, ny / n * w / 2
    d.polygon([P(ax - nx, ay - ny), P(ax + nx, ay + ny), P(bx + nx, by + ny), P(bx - nx, by - ny)], fill=col)
    d.polygon([P(ax - nx, ay - ny), P(ax - nx * 0.2, ay - ny * 0.2), P(bx - nx * 0.2, by - ny * 0.2), P(bx - nx, by - ny)], fill=col_l)
# shadows (sun from the left -> shadows fall right and toward us)
shx, shy = 0.10, 0.012
for a in (foot_l, foot_r, foot_b):
    ds.line([P(*a), P(a[0] + shx * 0.9, a[1] + shy)], fill=150, width=int(0.010 * M))
ds.polygon([P(cx0 + 0.04 + shx * 0.5, 0.955 + shy * 0.5), P(cx0 + cs - 0.04 + shx, 0.955 + shy), P(cx0 + cs + shx * 0.9 - 0.06, 0.975), P(cx0 + 0.04 + shx * 0.4, 0.972)], fill=90)
leg(apex, foot_b, lw * 0.9, honey_d, honey_d)
leg(apex, foot_l, lw, honey, honey_l)
leg(apex, foot_r, lw, honey, honey_l)
# ledge under the canvas
d.rectangle([P(cx0 - 0.03, cb + 0.004), P(cx0 + cs + 0.03, cb + 0.022)], fill=honey)
d.rectangle([P(cx0 - 0.03, cb + 0.004), P(cx0 + cs + 0.03, cb + 0.009)], fill=honey_l)
d.rectangle([P(cx0 - 0.03, cb + 0.019), P(cx0 + cs + 0.03, cb + 0.022)], fill=honey_d)
# top clamp
d.rectangle([P(cx0 + cs / 2 - 0.035, cy0 - 0.03), P(cx0 + cs / 2 + 0.035, cy0 - 0.008)], fill=honey)
d.rectangle([P(cx0 + cs / 2 - 0.035, cy0 - 0.03), P(cx0 + cs / 2 + 0.035, cy0 - 0.025)], fill=honey_l)
# ---------------- frame around the canvas (cream-gold with a bevel)
fw = V.get('frame', 0.016)
fr = [(250, 236, 206, 255), (240, 220, 180, 255), (226, 202, 160, 255), (252, 244, 226, 255)]
x0, y0, x1, y1 = cx0, cy0, cx0 + cs, cb
d.polygon([P(x0 - fw, y0 - fw), P(x1 + fw, y0 - fw), P(x1, y0), P(x0, y0)], fill=fr[0])  # top (lit)
d.polygon([P(x0 - fw, y0 - fw), P(x0, y0), P(x0, y1), P(x0 - fw, y1 + fw)], fill=fr[3])  # left (lit)
d.polygon([P(x1 + fw, y0 - fw), P(x1 + fw, y1 + fw), P(x1, y1), P(x1, y0)], fill=fr[1])  # right
d.polygon([P(x0 - fw, y1 + fw), P(x0, y1), P(x1, y1), P(x1 + fw, y1 + fw)], fill=fr[2])  # bottom
# little bouquet of paintbrushes in a jar on the jetty, left
jx0, jy0 = cx0 - 0.09, 0.93
d.rounded_rectangle([P(jx0 - 0.018, jy0 - 0.045), P(jx0 + 0.018, jy0)], radius=int(0.006 * M), fill=(200, 232, 236, 230))
for k, (ang, col) in enumerate(zip((-0.35, -0.12, 0.08, 0.3), [(247, 161, 215), (148, 205, 246), (203, 232, 137), (255, 191, 148)])):
    bx = jx0 + 0.004 * (k - 1.5); by = jy0 - 0.04
    tx, ty = bx + 0.09 * np.sin(ang), by - 0.09 * np.cos(ang)
    d.line([P(bx, by), P(tx, ty)], fill=(236, 214, 170, 255), width=int(0.004 * M))
    d.ellipse([P(tx - 0.006, ty - 0.012), P(tx + 0.006, ty + 0.006)], fill=col + (255,))
ds.ellipse([P(jx0 - 0.02 + 0.03, jy0 - 0.006), P(jx0 + 0.07, jy0 + 0.008)], fill=110)

over = over.resize((N, N), Image.LANCZOS)
sh = sh.resize((N, N), Image.LANCZOS).filter(ImageFilter.GaussianBlur(N * 0.004))
o = np.asarray(over).astype(np.float32) / 255
s = np.asarray(sh).astype(np.float32) / 255
img = base * (1 - o[..., 3:]) + o[..., :3] * o[..., 3:]
# shadow only where there is jetty
jet = np.zeros((N, N), np.float32)
yy, xx = np.mgrid[0:N, 0:N] / N
t = (1 - yy) / (1 - jt)
inside = (t >= 0) & (t <= 1) & (xx >= xl0 + (xl1 - xl0) * t) & (xx <= xr0 + (xr1 - xr0) * t)
shadow_col = np.array([0.62, 0.55, 0.72], np.float32)
a = (s * inside * 0.55)[..., None]
img = img * (1 - a) + img * shadow_col * a
np.save(sys.argv[2], img.astype(np.float32))
Image.fromarray((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)).save(sys.argv[3])
json.dump(dict(canvas=[cx0 * N, cy0 * N, cs * N]), open(sys.argv[2] + '.json', 'w'))
