"""fingerprint.py — 'Two Fingers, One Smudge'   (engraved line on a record card; Fable 5.2, day 9)
For a lattice stair w with corners p_0..p_23 put  P_w(s,t) = sum_k exp(i(a_k s + b_k t)).
The bag of corner-to-corner separations (the tossprint) is exactly |P_w|^2.  Each print is drawn in
ridges: a ridge is a level line of the PHASE of P_w (plus a common carrier), its width is the
MODULUS.  For the two stairs of the valley the moduli agree everywhere, the phases do not:
P_w = A.Q and P_w' = conj(A).Q up to a monomial, A = 1 + Y + XY in X = s+... (see RESULTS.md).
Red rings: the 8 zeros of A on the torus, where the two prints fork opposite ways.
usage: fingerprint.py SIZE out.png"""
import sys, numpy as np
from scipy import ndimage as ndi
from PIL import Image, ImageDraw, ImageFont
from cyano import fbm
SERIF = '/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf'
SERIF_I = '/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf'
WA = "11011100110110111010101"; WB = "11001101110110101011101"
def pts(w):
    p = [(0, 0)]
    for c in w: p.append((p[-1][0] + (c == '0'), p[-1][1] + (c == '1')))
    return np.array(p, float)
S = int(sys.argv[1]); out = sys.argv[2]; u = S / 2048.0
rng = np.random.default_rng(5)
paper = np.array([0.955, 0.940, 0.895], np.float32)
img = np.empty((S, S, 3), np.float32); img[:] = paper
img *= (1 + 0.020 * fbm((S, S), 3 * u, rng, 2) + 0.022 * fbm((S, S), 240 * u, rng, 3))[..., None]
INK = np.array([0.075, 0.105, 0.285], np.float32); RED = np.array([0.80, 0.22, 0.15], np.float32)
def put(cov, col):
    global img
    a = np.clip(cov, 0, 1)[..., None]; img = img * (1 - a) + col * a

CAR = np.array([10.0, 31.0])          # carrier: the common ridge direction and count
def field(w, W, H, sx, sy):
    """P_w on a W x H window covering s in [-sx*pi, sx*pi], t in [-sy*pi, sy*pi]; origin = centroid"""
    P = pts(w); P = P - P.mean(0)
    s = np.linspace(-sx * np.pi, sx * np.pi, W, dtype=np.float32)[None, :]
    t = np.linspace(sy * np.pi, -sy * np.pi, H, dtype=np.float32)[:, None]
    F = np.zeros((H, W), np.complex64)
    for a, b in P: F += np.exp(1j * (a * s + b * t)).astype(np.complex64)
    return F, s, t
def print_(w, cx, cy, W, H, ridges=True, seed=0):
    r = np.random.default_rng(seed)
    F, s, t = field(w, W, H, 1.0, 1.0 * H / W)
    mod = np.abs(F) / 24.0
    T = np.clip(mod, 0, 1) ** 0.55
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    ex, ey = (xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2)
    rad = np.sqrt(ex ** 2 + ey ** 2) + 0.035 * fbm((H, W), 90 * u, r, 3)
    press = np.clip((1.0 - rad) / 0.16, 0, 1) ** 0.7                  # pressure of the finger pad
    if ridges:
        E = (F / np.maximum(np.abs(F), 1e-6)) * np.exp(1j * (4.0 * s + 33.0 * t + 8.5 * s * s + 0 * t))
        Ex = np.roll(E, -1, 1) * np.conj(np.roll(E, 1, 1)); Ey = np.roll(E, -1, 0) * np.conj(np.roll(E, 1, 0))
        gx, gy = np.angle(Ex) / 2, np.angle(Ey) / 2                    # radians per pixel
        g = np.maximum(np.hypot(gx, gy), 1e-4)
        d = np.abs(np.angle(E)) / g                                    # px to the ridge centre line
        pitch = 2 * np.pi / g
        wd = np.clip((0.15 + 0.72 * T) * pitch, 0.9 * u, None) * (pitch < 70 * u)
        cov = np.clip(wd / 2 - d + 0.5, 0, 1)
        pores = fbm((H, W), 2.2 * u, r, 1) > 0.63                     # sweat pores: pin-holes in the ridges
        grain = np.clip(0.86 + 0.30 * fbm((H, W), 5 * u, r, 2), 0, 1)
        cov = cov * (1 - 0.75 * pores) * grain
    else:
        # the smudge: the same darkness with no ridges (a rubbed pad), tone = area fraction of the ridges
        cov = (0.15 + 0.72 * T) * np.clip(0.80 + 0.5 * fbm((H, W), 4 * u, r, 2), 0, 1.1) * 0.92
        cov = ndi.gaussian_filter(cov, 1.5 * u)
    cov = cov * press * 0.97
    x0, y0 = int(cx - W / 2), int(cy - H / 2)
    a = np.clip(cov, 0, 1)[..., None]
    img[y0:y0 + H, x0:x0 + W] = img[y0:y0 + H, x0:x0 + W] * (1 - a) + INK * a
    return x0, y0
def text(items, col=INK, alpha=0.9):
    im = Image.new('L', (S, S), 0); d = ImageDraw.Draw(im)
    for x, y, tt, fp, px, an in items:
        d.text((x * u, y * u), tt, font=ImageFont.truetype(fp, int(round(px * u))), fill=255, anchor=an)
    put(np.asarray(im, np.float32) / 255 * alpha, col)
def rule(x0, y0, x1, y1, wd=2.2, alpha=0.75):
    im = Image.new('L', (S, S), 0); d = ImageDraw.Draw(im)
    d.line([(x0 * u, y0 * u), (x1 * u, y1 * u)], fill=255, width=max(1, int(round(wd * u))))
    put(np.asarray(im, np.float32) / 255 * alpha, INK)
# ---------------- the card ------------------------------------------------------------------
W1, H1 = int(760 * u), int(940 * u)
cxa, cxb, cy1 = 560 * u, 1488 * u, 640 * u
for bx in (cxa, cxb):       # printed frames
    x0, x1, y0, y1 = bx / u - 420, bx / u + 420, 120, 1160
    for a, b, c, d_ in ((x0, y0, x1, y0), (x1, y0, x1, y1), (x1, y1, x0, y1), (x0, y1, x0, y0)): rule(a, b, c, d_, 2.4, 0.55)
xa, ya = print_(WA, cxa, cy1, W1, H1, True, 1)
xb, yb = print_(WB, cxb, cy1, W1, H1, True, 2)
W2, H2 = int(500 * u), int(618 * u)
cx3, cy3 = 1024 * u, 1512 * u
x0, x1, y0, y1 = 1024 - 285, 1024 + 285, 1180, 1846
for a, b, c, d_ in ((x0, y0, x1, y0), (x1, y0, x1, y1), (x1, y1, x0, y1), (x0, y1, x0, y0)): rule(a, b, c, d_, 2.4, 0.55)
print_(WA, cx3, cy3, W2, H2, False, 3)
# ---------------- red rings on the zeros of the flipped factor ---------------------------------
# A = 1 + Y + XY vanishes on the torus at (X,Y) = (w,w),(w^2,w^2), w = exp(2 pi i/3);  X = 2s+2t, Y = s+3t (angles)
zs = []
for k in (1, 2):
    for m in range(-6, 7):
        for n_ in range(-6, 7):
            th1 = 2 * np.pi * k / 3 + 2 * np.pi * m; th2 = 2 * np.pi * k / 3 + 2 * np.pi * n_
            s_, t_ = np.linalg.solve(np.array([[2.0, 2.0], [1.0, 3.0]]), np.array([th1, th2]))
            zs.append((s_, t_))
ring = np.zeros((S, S), np.float32); yy, xx = np.mgrid[0:S, 0:S].astype(np.float32); nring = 0
FA, sA, tA = field(WA, 64, 64, 1, 1)
for (cx, x0p) in ((cxa, xa), (cxb, xb)):
    for s_, t_ in zs:
        px = cx + s_ / np.pi * W1 / 2; py = cy1 - t_ / np.pi * W1 / 2
        if ((px - cx) / (W1 / 2)) ** 2 + ((py - cy1) / (H1 / 2)) ** 2 < 0.80 ** 2:
            dd = np.abs(np.hypot(xx - px, yy - py) - 17 * u)
            ring = np.maximum(ring, np.clip(2.1 * u - dd + 0.5, 0, 1)); nring += 1
put(ring * 0.9, RED)
print('rings', nring)
# sanity: the two moduli agree, and the rings sit on zeros of P
Fa, s, t = field(WA, 256, 256, 1, 1); Fb, _, _ = field(WB, 256, 256, 1, 1)
print('max | |Pa| - |Pb| | =', float(np.abs(np.abs(Fa) - np.abs(Fb)).max()))
Pa = pts(WA); Pa -= Pa.mean(0)
print('|P| at the rings:', max(abs(np.exp(1j * (Pa[:, 0] * s_ + Pa[:, 1] * t_)).sum()) for s_, t_ in zs))
# ---------------- lettering -------------------------------------------------------------------
text([(cxa / u, 1128, "LEFT SLOPE   1101 1 1001 1 0110 · 1 · 1101 1 1010 1 0101"[:0] + "LEFT SLOPE", SERIF, 26, 'mm'),
      (cxb / u, 1128, "RIGHT SLOPE", SERIF, 26, 'mm'),
      (1024, 1818, "EITHER, RUBBED", SERIF, 24, 'mm'),
      (150, 1260, "Two Fingers,", SERIF, 62, 'la'), (150, 1334, "One Smudge", SERIF, 62, 'la'),
      (150, 1440, "Each stair of the valley is inked and pressed:", SERIF_I, 27, 'la'),
      (150, 1478, "a ridge follows the phase of the stair's wave,", SERIF_I, 27, 'la'),
      (150, 1516, "its weight is the wave's strength. The bag of", SERIF_I, 27, 'la'),
      (150, 1554, "276 slips records the strength and nothing else.", SERIF_I, 27, 'la'),
      (150, 1630, "So the two prints are equally dark at every", SERIF_I, 27, 'la'),
      (150, 1668, "point, ridge for ridge different, and rub", SERIF_I, 27, 'la'),
      (150, 1706, "down to one smudge.", SERIF_I, 27, 'la'),
      (1350, 1440, "At the red rings the ink runs out in both", SERIF_I, 27, 'la'),
      (1350, 1478, "prints and a ridge ends. There the two", SERIF_I, 27, 'la'),
      (1350, 1516, "prints fork in opposite senses: that is", SERIF_I, 27, 'la'),
      (1350, 1554, "the one factor the bag cannot orient.", SERIF_I, 27, 'la'),
      (1350, 1630, "P = Σ exp i(a·s + b·t) over the 24 corners (a, b);", SERIF, 23, 'la'),
      (1350, 1664, "ridges: arg P + (one shared arch) ≡ 0 mod 2π;  weight: |P|.", SERIF, 23, 'la'),
      (1350, 1698, "left P = A·Q,  right P = Ā·Q,  A = 1 + Y + XY.", SERIF, 23, 'la'),
      (1024, 1930, "engraved line on a record card  ·  the same two stairs as the valley and the sun print  ·  MO 516996", SERIF, 22, 'mm')], alpha=0.86)
Image.fromarray((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)).save(out)
