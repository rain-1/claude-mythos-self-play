"""HALF OF THEM HOLD THE CENTRE — P(p) for random triangles on three tangent circles, as layered paper."""
import numpy as np, sys, math
from scipy.ndimage import zoom, gaussian_filter, shift as nd_shift
from PIL import Image
from sorbet import PIG, WHEEL, wheel_tint, Sheet, lines, discs, text_mask
fn = sys.argv[1]; S = int(sys.argv[2]); OUT = sys.argv[3]; NL = int(sys.argv[4]) if len(sys.argv) > 4 else 20
title = sys.argv[5] if len(sys.argv) > 5 else 'Half of Them Hold the Centre'
d = np.load(fn); F = d['F'][::-1]; C = d['C'] - np.array([float(d['cx']), float(d['cy'])]); R = d['R']; ext = float(d['half'])
Ic = -np.array([float(d['cx']), float(d['cy'])])   # flip so +y is up
n = F.shape[0]
F = gaussian_filter(F, 2.2)
# drawing box
side = int(S * 0.84); ox = (S - side) // 2; oy = int(S * 0.045)
Fz = zoom(F, side / n, order=3)[:side, :side]
Fz = np.clip(Fz, 0, None)
H = S; W = S
def to_px(x, y):
    return ox + (x + ext) / (2 * ext) * (side - 1), oy + (ext - y) / (2 * ext) * (side - 1)
levels = [0.5 * (k + 0.5) / NL for k in range(NL)] # P levels
levels[0] = 0.006
lv = np.array(levels)
# per-pixel layer count with antialias: smooth step across each level
g = np.gradient(Fz); gm = np.hypot(*g) + 1e-9
layers = []
from scipy.spatial import ConvexHull
from PIL import ImageDraw
th = np.linspace(0, 2 * np.pi, 4000)
pts = np.concatenate([np.column_stack(to_px(cx + r * np.cos(th), cy + r * np.sin(th))) for (cx, cy), r in zip(C, R)]) - np.array([ox, oy])
hv = pts[ConvexHull(pts).vertices]
him = Image.new('L', (side * 4, side * 4), 0); ImageDraw.Draw(him).polygon([tuple(p * 4) for p in hv], fill=255)
hull = np.asarray(him.resize((side, side), Image.LANCZOS), np.float32) / 255
for k, L in enumerate(lv):
    m = np.clip(0.5 + (Fz - L) / gm, 0, 1)
    layers.append(hull if k == 0 else m * hull)
# colour: paper-cut stack; top layer tint at each pixel by wheel position
rgb = np.ones((side, side, 3)) * 0.992
light = np.array([-0.6, -0.8])   # light from upper-left (screen coords dx, dy)
sh_off = side / 520.0
for k, m in enumerate(layers):
    t = k / (NL - 1)
    # strawberry (outer) -> lilac (centre)
    tint = np.array(wheel_tint(0.0 + t * 7.0 / 9.0))
    col = 0.992 * tint ** (0.95 + 0.25 * math.sin(math.pi * t))
    # drop shadow this layer casts on what is below
    sh = gaussian_filter(nd_shift(m, (sh_off * 2.6, sh_off * 1.8), order=1), side / 420)
    shadow = np.clip(sh - m, 0, 1) * 0.30
    rgb *= (1 - shadow[..., None])
    # rim light on the edge facing the light
    edge = gaussian_filter(m, side / 900) - gaussian_filter(nd_shift(m, (-sh_off * 1.2, -sh_off * 0.9), order=1), side / 900)
    rim = np.clip(-edge, 0, 1) * 0.55
    # paper fibre shading: very gentle vignette inside each layer
    rgb = rgb * (1 - m[..., None]) + m[..., None] * (col[None, None, :] * (1 - shadow[..., None]))
    rgb = rgb + (1 - rgb) * rim[..., None]
# fine grain
canvas = np.ones((H, W, 3)) * np.array([0.992, 0.987, 0.978])
canvas[oy:oy + side, ox:ox + side] = rgb * (np.array([0.992, 0.987, 0.978]) / 0.992)
# ink: the three circles (thin plum), the incircle (coral dashed), the centre pearl
lw = max(2, S // 900)
poly = []
for (cx, cy), r in zip(C, R):
    th = np.linspace(0, 2 * np.pi, 1400)
    xs, ys = to_px(cx + r * np.cos(th), cy + r * np.sin(th)); poly.append(np.column_stack([xs, ys]))
inkd = lines(W, H, poly, lw * 1.6, sigma=0.7)
# incircle of centres triangle (radius rho: tangent length from I)
rho = math.sqrt((C[0, 0] - Ic[0]) ** 2 + (C[0, 1] - Ic[1]) ** 2 - R[0] ** 2)
dash = []
th = np.linspace(0, 2 * np.pi, 145)
for a, b in zip(th[:-1:2], th[1::2]):
    tt = np.linspace(a, b, 8); xs, ys = to_px(Ic[0] + rho * np.cos(tt), Ic[1] + rho * np.sin(tt)); dash.append(np.column_stack([xs, ys]))
cord = lines(W, H, dash, lw * 1.2, sigma=0.6)
px, py = to_px(Ic[0], Ic[1])
pearl = discs(W, H, [px], [py], [S * 0.0065], sigma=1.0)
A = inkd[..., None] * np.array([1.05, 1.25, 0.95]) * 0.7 + cord[..., None] * (-np.log(np.array(PIG['coral']))) * 0.9 \
    + pearl[..., None] * (-np.log(np.array(PIG['coral']))) * 1.6
canvas = canvas * np.exp(-A)
rng = np.random.default_rng(3)
canvas *= (1 + 0.010 * gaussian_filter(rng.standard_normal((H, W)), 0.8) / 0.35)[..., None]
# pearl highlight
hl = discs(W, H, [px - S * 0.002], [py - S * 0.002], [S * 0.0018], sigma=1.2)
canvas = canvas + (1 - canvas) * hl[..., None] * 0.8
srgb = np.where(canvas <= 0.0031308, 12.92 * canvas, 1.055 * np.clip(canvas, 0, None) ** (1 / 2.4) - 0.055)
cy0 = oy + side + int(S * 0.03)
items = [(title, S / 2, cy0, S * 0.03, 'serif_bold', 'mt'),
         ('one point chosen at random on each of three touching circles: the chance that their triangle covers the spot', S / 2, cy0 + S * 0.043, S * 0.0165, 'italic', 'mt'),
         ('one paper layer per 1/40 of chance, strawberry ≈ 0 → lilac ≈ ½ · the coral pearl is the incentre, where it is exactly ½ and highest · dashed: the circle crossing all three at right angles', S / 2, cy0 + S * 0.07, S * 0.0118, 'italic', 'mt')]
tm = text_mask(W, H, items)
srgb = srgb * (1 - tm[..., None]) + tm[..., None] * np.array([0.40, 0.31, 0.44])
Image.fromarray((np.clip(srgb, 0, 1) * 255 + 0.5).astype(np.uint8)).save(OUT, optimize=True)
