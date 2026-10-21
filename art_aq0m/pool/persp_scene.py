"""EVERY WAVE GETS ITS SHARE, seen from the edge: perspective render of the basin."""
import sys, json, time
import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import pool, persp, scene

kw = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
Wd = kw.get('W', 1024); Hd = kw.get('H', Wd)
ss = kw.get('ss', 2)
out = kw.get('out', 'persp_proto.png')
lam = kw.get('lam', 0.07); A = kw.get('A', 0.0040); depth = kw.get('depth', 0.11)
el, az = kw.get('sun', (0.50, 0.75))
R = 0.5; rimw = 0.055; cope = 0.02
probs = (0.4090311, 0.2646657, 0.1742928, 0.0984137, 0.0535967)
t0 = time.time()
K, phi, ang = pool.waves(3, lam, 0.18, None)
a = pool.AMP
L = np.array([np.sin(el) * np.cos(az), np.sin(el) * np.sin(az), -np.cos(el)])   # sunlight travel direction
sun = -L
# floor maps (top-down grid)
Wf = kw.get('Wf', 2048); fx0 = -0.52; fx1 = 0.52; fpx = (fx1 - fx0) / Wf
caus = np.stack([pool.caustic(Wf, fx0, fx1, K, phi, a, A, depth, L[0], L[1], L[2], 1.0 / n, kw.get('css', 4), R, cope, 17 + c)
                 for c, n in enumerate((1.329, 1.334, 1.341))], -1)
caus = gaussian_filter(caus, (0.7 * Wf / 2048, 0.7 * Wf / 2048, 0))
icap = kw.get('icap', 4.0)
caus = kw.get('sunk', 0.55) * caus / (1 + caus / icap)
cols = [scene.lin([1.0, 0.78, 0.80]), scene.lin([1.0, 0.91, 0.70]), scene.lin([0.76, 0.95, 0.84]), scene.lin([0.74, 0.86, 1.0]), scene.lin([0.88, 0.80, 1.0])]
alb = scene.mosaic_rings(Wf, fx0, fx1, 0.024, probs, cols, R)
print('floor maps', time.time() - t0)
# camera
eye = np.array(kw.get('eye', (0.0, 1.20, 0.80)))
look = np.array(kw.get('look', (0.0, 0.06, -0.08)))
fwd = look - eye; fwd /= np.linalg.norm(fwd)
right = np.cross(fwd, [0, 0, 1.0]); right /= np.linalg.norm(right)
up = np.cross(right, fwd)
fov = kw.get('fov', 0.80)
img, wmask = persp.trace(Wd, Hd, eye, fwd, right, up, fov, K, phi, a, A, depth, R, rimw, cope, 1.0 / 1.334,
                         alb, caus, fx0, fpx, sun, ss, 1)
print('trace', time.time() - t0)


def project(p):
    v = p - eye
    z = v @ fwd
    x = (v @ right) / z; y = (v @ up) / z
    tanf = np.tan(fov / 2)
    return ((x / (tanf * Wd / Hd) + 1) * Wd / 2, (1 - y / tanf) * Hd / 2, z)

# boats: storybook sprites standing on the water, each on its own sector, with a soft reflection
BOATC = [[1.0, 0.62, 0.66], [1.0, 0.84, 0.46], [0.52, 0.88, 0.70], [0.55, 0.74, 1.0], [0.78, 0.64, 1.0]]
e = np.concatenate([[0], np.cumsum(probs)]); e /= e[-1]
boats = []
for k in range(5):
    tm = np.pi / 2 + 2 * np.pi * (e[k] + e[k + 1]) / 2
    rad = 0.33 if k else 0.30
    boats.append((rad * np.cos(tm), rad * np.sin(tm), 0.13 * (0.6 + 0.4 * a[k] / a[0]), ang[k], BOATC[k]))
SS = 3
lay = Image.new('RGBA', (Wd * SS, Hd * SS), (0, 0, 0, 0))
refl = Image.new('RGBA', (Wd * SS, Hd * SS), (0, 0, 0, 0))
shad = Image.new('L', (Wd * SS, Hd * SS), 0)
order = sorted(range(5), key=lambda k: -project(np.array([boats[k][0], boats[k][1], 0]))[2])
for k in order:
    cx, cy, Lb, hd, rgb = boats[k]
    sx, sy, z = project(np.array([cx, cy, 0.0]))
    s2, _, _ = project(np.array([cx + Lb, cy, 0.0]))
    Lp = abs(s2 - sx) * SS
    # facing: show the bow on the side of the screen the heading points to
    hx = np.cos(hd) * right[0] + np.sin(hd) * right[1]
    f = 1.0 if hx >= 0 else -1.0
    X0, Y0 = sx * SS, sy * SS
    h = 0.26
    faces = [([(-0.5, 0), (0.5, 0), (0.42, -0.07), (-0.42, -0.07)], 0.74),
             ([(-0.5, 0), (0.5, 0), (0.27, h), (-0.27, h)], 0.97),
             ([(-0.5, 0), (-0.27, h), (-0.20, h * 0.55)], 0.86),
             ([(0.5, 0), (0.27, h), (0.20, h * 0.55)], 0.88),
             ([(-0.26, -0.035), (0.0, -0.035), (0.0, -0.60)], 1.05),
             ([(0.0, -0.035), (0.26, -0.035), (0.0, -0.60)], 0.84)]
    sink = h * 0.75   # the hull sits in the water up to here
    d = ImageDraw.Draw(lay); dr = ImageDraw.Draw(refl)
    for pts, sh in faces:
        c = tuple(int(255 * min(1, v * sh * 0.96 + 0.03)) for v in rgb) + (255,)
        P = [(X0 + f * x * Lp, Y0 + (y - sink) * Lp) for x, y in pts]
        d.polygon(P, fill=c)
        Pr = [(X0 + f * x * Lp, Y0 + (-(y - sink)) * Lp * 0.9) for x, y in pts]
        dr.polygon(Pr, fill=c[:3] + (150,))
    ImageDraw.Draw(shad).ellipse([X0 - 0.62 * Lp, Y0 - 0.05 * Lp, X0 + 0.62 * Lp, Y0 + 0.16 * Lp], fill=150)
lay = lay.resize((Wd, Hd), Image.LANCZOS)
refl = refl.resize((Wd, Hd), Image.LANCZOS).filter(ImageFilter.GaussianBlur(1.5 * Wd / 1024))
shad = np.asarray(shad.resize((Wd, Hd), Image.LANCZOS).filter(ImageFilter.GaussianBlur(3 * Wd / 1024)), np.float32) / 255
# wobble the reflection by the surface slope would be ideal; a soft vertical smear is enough at this size
ra = np.asarray(refl, np.float32) / 255
la = np.asarray(lay, np.float32) / 255
img = img * (1 - 0.25 * shad[..., None] * wmask[..., None])
img = img * (1 - ra[..., 3:] * 0.45 * wmask[..., None]) + scene.lin(ra[..., :3]) * ra[..., 3:] * 0.45 * wmask[..., None] * 0.9
lin_b = scene.lin(la[..., :3]) * 1.0
img = img * (1 - la[..., 3:]) + lin_b * la[..., 3:]
rgb = scene.srgb(scene.tonemap(img * kw.get('expo', 1.0), 1.5))
rgb = rgb + np.random.default_rng(0).uniform(-0.5, 0.5, rgb.shape) / 255
im = Image.fromarray((np.clip(rgb, 0, 1) * 255 + 0.5).astype(np.uint8))
im.save(out)
np.save(out.replace('.png', '_lin.npy'), img.astype(np.float32)) if kw.get('savelin') else None
print('done', out, time.time() - t0)

if kw.get('caption'):
    N = Wd
    a_ = np.asarray(im).astype(np.float32) / 255
    y = np.arange(Hd)[:, None]
    band = np.clip((y / Hd - 0.875) / 0.03, 0, 1)
    paper = np.array([0.99, 0.975, 0.962])
    a_ = a_ * (1 - 0.88 * band[..., None]) + paper * 0.88 * band[..., None]
    im = Image.fromarray((np.clip(a_, 0, 1) * 255 + 0.5).astype(np.uint8))
    d = ImageDraw.Draw(im)
    s = N / 4096
    ink = (92, 77, 102)
    F = '/usr/share/fonts/truetype/freefont/'
    ft = ImageFont.truetype(F + 'FreeSerifBold.ttf', int(92 * s))
    fi = ImageFont.truetype(F + 'FreeSerifItalic.ttf', int(50 * s))
    fm = ImageFont.truetype(F + 'FreeSerif.ttf', int(44 * s))
    x = int(150 * s); y0 = int(0.905 * Hd)
    d.text((x, y0), 'Every Wave Gets Its Share', font=ft, fill=ink)
    d.text((x, y0 + int(118 * s)), 'Five waves of heights 1, .85, .7, .55, .4 cross a round basin; each paper boat rides its own wave. Floor sector k is the chance that wave k carries the sum.', font=fi, fill=ink)
    d.text((x, y0 + int(186 * s)), '40.9% + 26.5% + 17.4% + 9.8% + 5.4% = 1 exactly (Weyl, 1938), although the five events overlap and nearly four points in ten belong to none. The light on the floor is the same five waves, refracted.', font=fm, fill=ink)
    im.save(out)
    print('captioned', out)
