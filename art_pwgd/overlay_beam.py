"""overlay_beam.py lin.npy out.png [key=val] — tone-map the marble render and lay the coral ray over it."""
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.ndimage import gaussian_filter
from grin import project, hit_sphere, nrm
from beam import trace
ARG = dict(a.split('=', 1) for a in sys.argv[3:] if '=' in a)
def P(k, d): return type(d)(ARG.get(k, d))
img = np.load(sys.argv[1]).astype(np.float64); H, W = img.shape[:2]
POS = [tuple(map(float, P(f'b{i}', dflt).split(','))) for i, dflt in enumerate(['-2.4,0.6', '0.1,-1.5', '2.2,0.9'])]
balls = [dict(c=np.array([*POS[0], 1.0]), r=1.0, kind='lune'), dict(c=np.array([*POS[1], 1.0]), r=1.0, kind='fish'),
         dict(c=np.array([*POS[2], 1.0]), r=1.0, kind='eaton')]
eye = np.array([P('ex', -1.0), P('ey', -10.0), P('ez', 4.2)]); look = np.array([P('lx', 0.0), P('ly', 0.0), P('lz', 0.8)]); fov = P('fov', 0.36)
y0, ang = P('by0', 0.74), P('bang', 0.13)
segs, seq = trace(balls, np.array([-14.0, y0 - 5 * np.tan(ang), 1.0]), np.array([np.cos(ang), np.sin(ang), 0]), far=P('far', 14.0))
print('sequence', seq)
SS = 2
core = Image.new('F', (W * SS, H * SS), 0.0); dr = ImageDraw.Draw(core)
lw = P('lw', 0.0016) * W * SS
for s in segs:
    pts = s[1]
    # resample densely
    t = np.linspace(0, 1, max(2, int(np.linalg.norm(pts[-1] - pts[0]) * 60) + len(pts) * 3))
    seg = np.array([np.interp(t, np.linspace(0, 1, len(pts)), pts[:, k]) for k in range(3)]).T
    xy, z = project(seg, W, H, eye, look, fov)
    # visibility: camera ray to point blocked by a ball in front?  (glass -> dim, not hide)
    dvec = seg - eye; dist = np.linalg.norm(dvec, axis=1); dn = dvec / dist[:, None]
    vis = np.ones(len(seg))
    for B in balls:
        th = hit_sphere(np.broadcast_to(eye, dn.shape), dn, B['c'], B['r'])
        vis = np.where(th < dist - 1e-4, vis * P('dim', 0.55), vis)
    for k in range(len(seg) - 1):
        dr.line([tuple(xy[k] * SS), tuple(xy[k + 1] * SS)], fill=float(min(vis[k], vis[k + 1])), width=max(1, int(round(lw))))
c = np.asarray(core, np.float32).copy()
c = np.asarray(Image.fromarray(c).resize((W, H), Image.LANCZOS), np.float32)
glow = gaussian_filter(c, P('gs', 0.006) * W) * P('gk', 7.0) + gaussian_filter(c, 0.0015 * W) * 1.2
CORAL = np.array([1.0, 0.42, 0.36])
a = np.clip(c * P('ca', 0.92), 0, 1)[..., None]
g = np.clip(glow * P('glk', 0.06), 0, 0.5)[..., None]
img = img * (1 - g) + g * img * CORAL ** 0.6          # soft coral haze around the thread
img = img * (1 - a) + a * CORAL * P('cbr', 1.05)         # the thread itself, opaque coral
img = img + np.clip(c - 0.5, 0, 1)[..., None] * 0.25    # hot core
ex = P('expo', 0.9)
if P('tone', 'exp') == 'rh':       # extended Reinhard: whiter paper, gentle shoulder
    x = ex * img; w = P('white', 1.25)
    v = x * (1 + x / (w * w)) / (1 + x)
else:
    v = 1 - np.exp(-ex * 1.6 * img)
srgb = np.where(v <= 0.0031308, 12.92 * v, 1.055 * np.power(np.clip(v, 0, 1), 1 / 2.4) - 0.055)
Image.fromarray((np.clip(srgb, 0, 1) * 255 + 0.5).astype(np.uint8)).save(sys.argv[2])
