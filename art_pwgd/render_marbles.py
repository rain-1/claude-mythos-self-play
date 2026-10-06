"""render_marbles.py — WAKING, DREAMING, DEEP SLEEP: three gradient-index marbles on a gingham cloth.

usage: render_marbles.py W H out.png [key=val ...]
"""
import sys, time, numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
from grin import Scene, camera_rays, project, nrm

ARG = dict(a.split('=', 1) for a in sys.argv[4:] if '=' in a)
def P(k, d): return type(d)(ARG.get(k, d))

W, H, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]

# ---------- palette (linear transmission) ----------
PINK = np.array([1.00, 0.62, 0.72]); SKY = np.array([0.60, 0.84, 1.00]); BUTTER = np.array([1.0, 0.90, 0.55])
LILAC = np.array([0.80, 0.66, 1.00]); MINT = np.array([0.60, 0.94, 0.80]); PEACH = np.array([1.0, 0.76, 0.60])
absb = lambda t: -np.log(np.asarray(t, float))

def band(u, period, width, soft):
    f = np.abs(((u / period) % 1.0) - 0.5) * period        # distance to stripe centre
    return 1 / (1 + np.exp((f - width / 2) / soft))

PAT = P('pat', 'gingham')
def tex(x, y):
    paper = np.array([0.985, 0.975, 0.965])
    if PAT == 'gingham':
        per = P('per', 1.1)
        bx = band(x, per, per * 0.5, 0.025); by = band(y, per, per * 0.5, 0.025)
        # hue of the warm stripes walks slowly along y, cool along x (neighbouring hues only)
        A = (bx[:, None] * (0.55 * absb(PINK) + 0.0 * absb(PEACH))[None] +
             by[:, None] * 0.55 * absb(SKY)[None])
        return paper * np.exp(-P('gk', 1.0) * A)
    if PAT == 'plaid':
        per = P('per', 1.1)
        # warp: wide pink + thin butter;  weft: wide sky + thin mint  (neighbouring hues cross)
        A = (band(x, per, per * 0.42, 0.02)[:, None] * 0.55 * absb(PINK) +
             band(x - per / 2, per, per * 0.12, 0.012)[:, None] * 0.65 * absb(BUTTER) +
             band(y, per, per * 0.42, 0.02)[:, None] * 0.50 * absb(SKY) +
             band(y - per / 2, per, per * 0.12, 0.012)[:, None] * 0.55 * absb(LILAC))
        return paper * np.exp(-P('gk', 1.0) * A)
    if PAT == 'dots':
        per = P('per', 0.9)
        # hex lattice of sorbet dots, colour hashed per dot from a 9-hue wheel
        row = np.floor(y / (per * 0.866)).astype(int)
        cx = (x / per - 0.5 * (row % 2)); col = np.floor(cx + 0.5).astype(int)
        best = np.full(len(x), 1e9); hid = np.zeros(len(x), int)
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                r2 = row + dr; c2 = col + dc
                px = (c2 + 0.5 * (r2 % 2)) * per; py = (r2 + 0.5) * per * 0.866
                dd = np.hypot(x - px, y - py)
                m = dd < best; best = np.where(m, dd, best); hid = np.where(m, (r2 * 7919 + c2 * 104729) % 9973, hid)
        rad = P('drad', 0.17) * per
        cov = 1 / (1 + np.exp((best - rad) / 0.012))
        Ah = DOTPAL[hid % len(DOTPAL)]
        return paper * np.exp(-P('gk', 1.0) * cov[:, None] * Ah)
    return np.broadcast_to(paper, (len(x), 3)).copy()
_dw = [(1.00, 0.55, 0.65), (1.0, 0.72, 0.52), (1.0, 0.88, 0.45), (0.75, 0.94, 0.50), (0.52, 0.92, 0.78),
       (0.52, 0.82, 1.0), (0.64, 0.66, 1.0), (0.80, 0.60, 1.0), (1.0, 0.60, 0.90)]
DOTPAL = np.array([absb(c) for c in _dw])

# pastel cloud texture over (azimuth, elevation)
from scipy.ndimage import zoom as _zoom
_rng = np.random.default_rng(P('cseed', 7))
def _fbm(h, w):
    acc = np.zeros((h, w))
    for o in range(6):
        s = 2 ** o * 3
        n = _rng.standard_normal((s, 2 * s))
        n = np.concatenate([n, n[:, :1]], 1)
        acc += _zoom(n, (h / s, (w + w / (2 * s)) / (2 * s + 1)), order=3)[:h, :w] / 1.7 ** o
    return acc / acc.std()
CL = _fbm(256, 1024)
CL2 = _fbm(256, 1024)
SUN = nrm(np.array([P('sx', -0.45), P('sy', 0.75), P('sz', 0.55)]))
def sky(d):
    z = np.clip(d[:, 2], -1, 1)
    hor = np.array([1.00, 0.90, 0.88]); zen = np.array([0.66, 0.80, 1.00]); low = np.array([1.0, 0.94, 0.86])
    t = np.clip(z, 0, 1) ** 0.6
    c = hor * (1 - t[:, None]) + zen * t[:, None]
    az = (np.arctan2(d[:, 1], d[:, 0]) / (2 * np.pi)) % 1.0
    el = np.clip(z, 0, 1)
    iy = np.clip((el ** 0.7 * 255).astype(int), 0, 255); ix = (az * 1023).astype(int)
    cm = np.clip((CL[iy, ix] - P('cth', 0.35)) * 0.9, 0, 1) * np.clip(z * 6, 0, 1) * (1 - 0.5 * t)
    tint = np.where((CL2[iy, ix] > 0)[:, None], np.array([1.0, 0.86, 0.90]), np.array([1.0, 0.95, 0.88]))
    c = c * (1 - cm[:, None]) + cm[:, None] * tint * 1.08
    # pastel rainbow around the antisolar point (inside of the bow a little brighter)
    ang = np.degrees(np.arccos(np.clip(-(d @ SUN), -1, 1)))
    u = (ang - P('rb0', 39.0)) / P('rbw', 4.0)              # 0 = violet edge, 1 = red edge
    env = np.exp(-((u - 0.5) / 0.42) ** 8)
    hue = np.stack([np.interp(u, [0, .2, .4, .6, .8, 1], ch) for ch in
                    ([0.75, 0.55, 0.55, 0.85, 1.0, 1.0], [0.60, 0.75, 0.95, 0.95, 0.80, 0.55], [1.0, 1.0, 0.75, 0.55, 0.50, 0.60])], -1)
    rb = P('rbk', 0.55) * (env * np.clip(z * 8 + 0.3, 0, 1))[:, None]
    c = c * (1 - rb) + rb * hue * 1.15 + (0.06 * (u < 0) * np.clip(z * 8, 0, 1))[:, None]
    c = np.where(z[:, None] < 0, low, c)
    cs = d @ SUN
    c = c + P('sunk', 9.0) * np.exp(-(1 - cs) / 0.0009)[:, None] * np.array([1.0, 0.97, 0.9]) \
          + 0.25 * np.exp(-(1 - cs) / 0.02)[:, None] * np.array([1.0, 0.93, 0.85])
    return c * 1.05

R = 1.0
gap = P('gap', 2.75)
POS = [tuple(map(float, P(f'b{i}', dflt).split(','))) for i, dflt in enumerate(['-2.75,0', '0,0', '2.75,0'])]
balls = [dict(c=np.array([*POS[0], R]), r=R, kind=P('k0', 'lune'), absorb=absb(BUTTER) * 1.0, dens=P('dens', 0.55)),
         dict(c=np.array([*POS[1], R]), r=R, kind=P('k1', 'fish'), absorb=absb(LILAC), dens=P('dens', 0.55)),
         dict(c=np.array([*POS[2], R]), r=R, kind=P('k2', 'eaton'), absorb=absb(SKY), dens=P('dens', 0.55))]
if P('scene', 'trio') == 'necklace':
    # Eaton marbles spaced along the table conic where the line of sight is RB degrees from the sun
    rr_ = P('nr', 0.62); E_ = np.array([P('ex', 0.0), P('ey', -10.0), P('ez', 4.6)])
    cosA = np.cos(np.radians(P('rbdeg', 41.0)))
    xs_ = np.linspace(-P('nx', 4.6), P('nx', 4.6), 400); arc = []
    ys = np.linspace(-9, 12, 20001)
    for x in xs_:
        X = np.stack([np.full_like(ys, x), ys, np.full_like(ys, rr_)], 1)
        v = X - E_; v /= np.linalg.norm(v, axis=1, keepdims=True)
        f = v @ SUN - cosA; i = np.where(np.diff(np.sign(f)))[0][0]
        arc.append((x, ys[i]))
    arc = np.array(arc); seg = np.r_[0, np.cumsum(np.linalg.norm(np.diff(arc, axis=0), axis=1))]
    nb = P('nb', 7); tgt = np.linspace(0, seg[-1], nb)
    TINTS = [SKY, np.array([0.66, 0.74, 1.0]), LILAC, np.array([0.92, 0.66, 0.96]), PINK, PEACH, BUTTER, MINT]
    balls = []
    for q, tt in enumerate(tgt):
        x = np.interp(tt, seg, arc[:, 0]); y = np.interp(tt, seg, arc[:, 1])
        balls.append(dict(c=np.array([x, y, rr_]), r=rr_, kind='eaton', absorb=absb(TINTS[q % len(TINTS)]) * P('ntk', 1.0), dens=P('dens', 0.5)))
    print('necklace', [tuple(np.round(b['c'][:2], 2)) for b in balls])
sc = Scene(balls, SUN, sun_rad=P('sunrad', 0.04), tex=tex, sky=sky)
sc.ksun, sc.kamb = P('ksun', 0.78), P('kamb', 0.30)

t0 = time.time()
ext = (-9, 9, -8, 6)
if P('pmload', ''):
    E = np.load(P('pmload', ''))
else:
    sc.photon_map(ext, (P('pmy', 700), P('pmx', 900)), nph=P('nph', 600000), batches=P('pb', 4))
    E = sc.E[1]
    E = np.stack([gaussian_filter(E[..., c], P('pmsig', 1.2)) for c in range(3)], -1)
    if P('pmsave', ''):
        np.save(P('pmsave', ''), E.astype(np.float32)); print('saved photon map'); sys.exit(0)
sc.E = (ext, E)
print('photon map', time.time() - t0, 'max E', E.max(), flush=True)

eye = np.array([P('ex', 1.2), P('ey', -10.5), P('ez', 4.6)])
look = np.array([P('lx', 0.0), P('ly', 0.4), P('lz', 0.75)])
fov = P('fov', 0.30)
r0, r1 = P('r0', 0), P('r1', H)
acc = np.zeros(((r1 - r0) * W, 3))
npass = P('passes', 1)
rng = np.random.default_rng(3)
for k in range(npass):
    jit = (0.5, 0.5) if npass == 1 else tuple(rng.random(2))
    ap = P('ap', 0.0)
    if ap > 0 and npass > 1:     # stratified aperture samples (golden-angle spiral)
        rr = ap * np.sqrt((k + 0.5) / npass); th = k * 2.39996
        lens = (rr * np.cos(th), rr * np.sin(th))
    else:
        lens = (0.0, 0.0)
    o, d = camera_rays(W, H, eye, look, fov, jitter=jit, lens=lens, rows=(r0, r1), focus=P('focus', float(np.linalg.norm(look - eye))))
    for s in range(0, len(o), 400000):
        acc[s:s + 400000] += sc.shade(o[s:s + 400000], d[s:s + 400000])
    print('pass', k, time.time() - t0, flush=True)
img = (acc / npass).reshape(r1 - r0, W, 3)
np.save(out.replace('.png', '_lin.npy'), img.astype(np.float32))
if r1 - r0 != H: print('strip done', time.time() - t0); sys.exit(0)
ex = P('expo', 1.0)
v = 1 - np.exp(-ex * 1.6 * img)
srgb = np.where(v <= 0.0031308, 12.92 * v, 1.055 * np.power(np.clip(v, 0, 1), 1 / 2.4) - 0.055)
Image.fromarray((np.clip(srgb, 0, 1) * 255 + 0.5).astype(np.uint8)).save(out)
print('done', time.time() - t0)
