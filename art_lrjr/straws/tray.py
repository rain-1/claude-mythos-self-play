"""ONE IN SIXTY: every way to string six paper straws through the six corners of one (twisted) octahedron.
Tray of 60 cells sorted by how many straws cut through the inside; the single trefoil framed in coral.
usage: python3 tray.py OUT.png CELLPX SPP
"""
import sys, numpy as np
sys_argv = sys.argv[:]
sys.argv = ['x']
from anti import anti
sys.argv = sys_argv
from cell import render, camera
from knot import ham_cycles, determinant
from PIL import Image, ImageDraw, ImageFont, ImageFilter

out, CP, SPP = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
V = anti(28)
anti_of = {}
for i in range(6):
    anti_of[i] = int(np.argmax(np.linalg.norm(V - V[i], axis=1)))
cycles = ham_cycles()
def ndiag(c):
    return sum(anti_of[c[i]] == c[(i + 1) % 6] for i in range(6))
dets = {c: determinant(V[list(c)]) for c in cycles}
tref = [c for c in cycles if dets[c] == 3]
assert len(tref) == 1, tref
tref = tref[0]
cls = sorted(cycles, key=lambda c: (ndiag(c), c))
# put the trefoil in the middle of its class
c3 = [c for c in cls if ndiag(c) == 3]
c3.remove(tref); c3.insert(len(c3) // 2, tref)
order = [c for c in cls if ndiag(c) < 3] + c3

CLASS = {  # stripe, ground tile
    0: ('3fc48f', 'cdeedd'),
    1: ('48aef0', 'cfe6f8'),
    2: ('9579ec', 'e0d8f8'),
    3: ('ff9a52', 'fde0cc'),
}
cam = camera(elev=78, azim=-90)
cols, rows = 10, 6
gut = int(CP * 0.06)
mx = int(CP * 0.45)
Wc = mx * 2 + cols * CP + (cols - 1) * gut
top = int(CP * 0.42)
capH = int(CP * 1.45)
Hc = top + rows * CP + (rows - 1) * gut + capH
canvas = np.ones((Hc, Wc, 3), np.float32) * (np.array([0.985, 0.975, 0.965]) ** 2.2)
shadow = np.zeros((Hc, Wc), np.float32)
tiles = []
for k, c in enumerate(order):
    r, q = divmod(k, cols)
    x0 = mx + q * (CP + gut); y0 = top + r * (CP + gut)
    d = ndiag(c)
    stripe, ground = CLASS[d]
    if c == tref:
        stripe, ground = 'f5455a', 'ffd6da'
    img, al = render(c, CP, 'fffaf6', stripe, 'ffeccc', ground, V=V, spp=SPP, zpad=0.3,
                     sun=(-0.25, -0.35, 1.0), cam=cam, fov=0.235, seed=k * 1000 + 1)
    tiles.append((x0, y0, img, c == tref))
    print('cell', k, d, c, flush=True)

# tile drop shadows (soft, offset down-right) then tiles with rounded corners
rad = int(CP * 0.07)
mask = Image.new('L', (CP, CP), 0)
ImageDraw.Draw(mask).rounded_rectangle([0, 0, CP - 1, CP - 1], rad, fill=255)
m = np.asarray(mask, np.float32) / 255
sh = Image.new('L', (Wc, Hc), 0)
for x0, y0, img, t in tiles:
    sh.paste(mask, (x0 + int(CP * 0.012), y0 + int(CP * 0.02)))
sh = np.asarray(sh.filter(ImageFilter.GaussianBlur(CP * 0.025)), np.float32) / 255
canvas *= (1 - 0.22 * sh)[..., None]
for x0, y0, img, t in tiles:
    reg = canvas[y0:y0 + CP, x0:x0 + CP]
    reg[:] = reg * (1 - m[..., None]) + img * m[..., None]
img = canvas / (1 + canvas / 4) * 1.25
srgb = (np.clip(img, 0, 1) ** (1 / 2.2) * 255 + 0.5).astype(np.uint8)
pic = Image.fromarray(srgb)
dr = ImageDraw.Draw(pic)
# coral frame round the trefoil
for x0, y0, img, t in tiles:
    if t:
        w = max(3, CP // 60)
        dr.rounded_rectangle([x0 - 3 * w, y0 - 3 * w, x0 + CP + 3 * w, y0 + CP + 3 * w], rad + 3 * w,
                             outline=(250, 104, 96), width=w)
# class labels in the gutter: small dots legend in caption
F = '/usr/share/fonts/truetype/freefont/'
s = CP / 370
fT = ImageFont.truetype(F + 'FreeSerifBold.ttf', int(84 * s))
fI = ImageFont.truetype(F + 'FreeSerifItalic.ttf', int(44 * s))
fS = ImageFont.truetype(F + 'FreeSerif.ttf', int(36 * s))
ink = (92, 77, 102)
y = top + rows * CP + (rows - 1) * gut + int(CP * 0.30)
dr.text((mx, y), 'One Way in Sixty', font=fT, fill=ink)
y += int(100 * s)
dr.text((mx, y), 'Six paper straws, six pearls on the corners of one octahedron, and every order in which to string them:'
        , font=fI, fill=ink)
y += int(56 * s)
dr.text((mx, y), '(6 − 1)!/2 = 60 closed hexagons. Fifty-nine can be shaken loose into a circle. One is a trefoil knot.',
        font=fI, fill=ink)
y += int(70 * s)
xx = mx
labels = [(0, 'all six straws on the surface (16)'), (1, 'one through the middle (24)'),
          (2, 'two (12)'), (3, 'three (8)')]
for d, lab in labels:
    col = tuple(int(255 * (int(CLASS[d][0][i:i + 2], 16) / 255)) for i in (0, 2, 4))
    rr = int(16 * s)
    dr.ellipse([xx, y + int(10 * s), xx + 2 * rr, y + int(10 * s) + 2 * rr], fill=col)
    xx += 2 * rr + int(12 * s)
    dr.text((xx, y), lab, font=fS, fill=ink)
    xx += int(dr.textlength(lab, font=fS)) + int(40 * s)
dr.ellipse([xx, y + int(10 * s), xx + 2 * rr, y + int(10 * s) + 2 * rr], fill=(255, 111, 125))
xx += 2 * rr + int(12 * s)
dr.text((xx, y), 'the trefoil', font=fS, fill=ink)
y += int(56 * s)
dr.text((mx, y), 'Six random points on a sphere make this octahedron with probability 15/(4π²); exactly one of the sixty orders knots, '
        'so a random six-stick knot is a trefoil with probability 1/(16π²) ≈ 0.0063.  (MO 54919)', font=fS, fill=ink)
pic.save(out)
