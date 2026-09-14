"""render_contour.py — THE CONTOUR THAT ISN'T THERE.
Kanizsa inducers (coral discs with a wedge missing) and the stochastic completion field of every pair of
edge ends: the pigment cloud is the probability that the eye's contour passes there; ink is the most
probable path of the strongest pairs; coral is what is actually on the page.

usage: python3 render_contour.py FINAL scene out_prefix [FIELD_N] [ntheta]
"""
import sys, json, time
import numpy as np
from scipy.ndimage import zoom, gaussian_filter, gaussian_filter1d, distance_transform_edt
from PIL import Image, ImageDraw
import pastel as P
from completion import greens, place, completion_all, completion_pair, ridge

FINAL = int(sys.argv[1]); SCENE = sys.argv[2]; OUT = sys.argv[3]
FN = int(sys.argv[4]) if len(sys.argv) > 4 else 512          # field resolution (canvas is FN x FN in field units)
NT = int(sys.argv[5]) if len(sys.argv) > 5 else 48
SS = 2; W = H = FINAL * SS; rs = FINAL / 1024.0 * SS
t0 = time.time()
rng = np.random.default_rng(3)

# ------------------------------------------------------------------ scene (all in field units, FN x FN)
def pacman(cx, cy, r, bis, opening):
    """returns dict with the two edge ends (x, y, heading outward)"""
    ends = []
    for s in (-1, 1):
        a = bis + s * opening / 2
        ends.append((cx + r * np.cos(a), cy + r * np.sin(a), a))
    return dict(c=(cx, cy), r=r, bis=bis, opening=opening, ends=ends)

def scene_polygon(n, R, r, cx, cy, bow=0.0, phase=0.0):
    """n pac-men on a circle of radius R; mouths face the centre; opening = the interior angle of the n-gon;
    bow rotates each mouth by `bow` (radians) so the illusory sides curve"""
    out = []
    interior = np.pi * (n - 2) / n
    for i in range(n):
        a = phase + 2 * np.pi * i / n
        x, y = cx + R * np.cos(a), cy + R * np.sin(a)
        out.append(pacman(x, y, r, a + np.pi + bow, interior))
    return out

def add_strays(pm, n, r0, r1):
    tries = 0
    while n > 0 and tries < 500:
        tries += 1
        a = rng.uniform(0, 2 * np.pi); rr = rng.uniform(r0, r1) * FN
        x, y = 0.5 * FN + rr * np.cos(a), 0.5 * FN + rr * np.sin(a)
        r = rng.uniform(0.028, 0.042) * FN
        if all(np.hypot(x - p['c'][0], y - p['c'][1]) > r + p['r'] + 0.035 * FN for p in pm) and 0.06 * FN < x < 0.94 * FN and 0.06 * FN < y < 0.86 * FN:
            pm.append(pacman(x, y, r, rng.uniform(0, 2 * np.pi), rng.uniform(0.9, 1.6))); n -= 1

def build_scene(name):
    pm = []
    if name == 'triangle':
        pm += scene_polygon(3, 0.30 * FN, 0.075 * FN, 0.5 * FN, 0.52 * FN, phase=-np.pi / 2)
    elif name == 'garden':
        pm += scene_polygon(5, 0.26 * FN, 0.055 * FN, 0.52 * FN, 0.50 * FN, bow=0.22, phase=-np.pi / 2 + 0.3)
        # strays
        add_strays(pm, 7, 0.38, 0.46)
    elif name == 'hepta':
        pm += scene_polygon(7, 0.27 * FN, 0.05 * FN, 0.50 * FN, 0.47 * FN, bow=0.30, phase=-np.pi / 2)
        add_strays(pm, 8, 0.40, 0.47)
    elif name == 'kite':
        # an irregular illusory shape: pac-men on an ellipse, mouths turned by varying bows
        n = 6; R1, R2 = 0.33 * FN, 0.22 * FN
        for i in range(n):
            a = -np.pi / 2 + 2 * np.pi * i / n + 0.15 * np.sin(3 * i)
            x, y = 0.5 * FN + R1 * np.cos(a), 0.48 * FN + R2 * np.sin(a)
            pm.append(pacman(x, y, (0.045 + 0.012 * np.cos(2 * i)) * FN, np.arctan2(0.48 * FN - y, 0.5 * FN - x) + 0.35 * np.sin(2.1 * i + 1), 1.4 + 0.5 * np.cos(1.7 * i)))
        add_strays(pm, 6, 0.42, 0.47)
    elif name == 'hero':
        n = 7; R1, R2 = 0.31 * FN, 0.245 * FN; ccx, ccy = 0.50 * FN, 0.465 * FN
        for i in range(n):
            a = -np.pi / 2 + 2 * np.pi * i / n + 0.12 * np.sin(2.3 * i)
            x, y = ccx + R1 * np.cos(a), ccy + R2 * np.sin(a)
            r = (0.052 + 0.012 * np.cos(1.3 * i + 0.4)) * FN
            bis = np.arctan2(ccy - y, ccx - x) + 0.30 * np.sin(1.7 * i + 0.5)
            pm.append(pacman(x, y, r, bis, 2.05 + 0.35 * np.cos(2.2 * i)))
        add_strays(pm, 11, 0.41, 0.47)
    elif name == 'square_bow':
        pm += scene_polygon(4, 0.30 * FN, 0.07 * FN, 0.5 * FN, 0.5 * FN, bow=0.35, phase=np.pi / 4)
    return pm

pm = build_scene(SCENE)
ends = [e for p in pm for e in p['ends']]
print('scene', SCENE, len(pm), 'inducers', len(ends), 'ends', flush=True)

# ------------------------------------------------------------------ fields
SIG = 0.045 * np.sqrt(512 / FN) ** 0   # heading diffusion per field px (scaled below)
TAU = 0.30 * FN
sigma = 0.11 / np.sqrt(FN / 512.0) * np.sqrt(512.0 / FN)    # keep the curvature scale ∝ size: sigma^2 * L const
sigma = 0.062 * np.sqrt(512.0 / FN)
print('sigma', sigma, 'tau', TAU, flush=True)
import os
os.makedirs('cache', exist_ok=True)
key = f'cache/{SCENE}_{FN}_{NT}'
if os.path.exists(key + '_G.npy'):
    G = np.load(key + '_G.npy'); S = np.load(key + '_S.npy'); C = np.load(key + '_C.npy')
    print('loaded cached fields', key, flush=True)
else:
    G = greens(FN, NT, sigma=sigma, tau=TAU, dt=max(1.0, FN / 512.0), T=5.0 * TAU)
    print('G done mass %.1f [%.0fs]' % (G.sum(), time.time() - t0), flush=True)
    np.save(key + '_G.npy', G)
    S = np.zeros((FN, FN, NT), np.float32)
    for (x, y, a) in ends:
        S += place(G, x, y, a, FN, FN)
    C = completion_all(S)
    np.save(key + '_S.npy', S); np.save(key + '_C.npy', C)
_cache = {}
def Pend(i):
    if i not in _cache:
        if len(_cache) > 6: _cache.clear()
        x, y, a = ends[i]; _cache[i] = place(G, x, y, a, FN, FN)
    return _cache[i]
print('all-pairs field done max %.3g [%.0fs]' % (C.max(), time.time() - t0), flush=True)

# pair strengths: designed pairs = consecutive inducers' facing ends
pairs = []
n_pm = len(pm)
for i in range(n_pm):
    for j in range(i + 1, n_pm):
        for a in range(2):
            for b in range(2):
                s, k = 2 * i + a, 2 * j + b
                # only pairs whose headings roughly face each other
                xs, ys, hs = ends[s]; xk, yk, hk = ends[k]
                d = np.array([xk - xs, yk - ys]); L = np.hypot(*d)
                if L < 1e-6: continue
                u = d / L
                if np.dot(u, [np.cos(hs), np.sin(hs)]) > 0.6 and np.dot(-u, [np.cos(hk), np.sin(hk)]) > 0.6 and L < 0.9 * FN:
                    Cp = completion_pair(Pend(s), Pend(k))
                    pairs.append((float(Cp.sum()), s, k, Cp.astype(np.float16)))
pairs.sort(key=lambda t: -t[0])
print('facing pairs', len(pairs), 'strengths', [round(float(p[0]), 4) for p in pairs[:12]], flush=True)

# ------------------------------------------------------------------ paint
sheet = P.Sheet(W, H, seed=11)
up = W / FN
Cz = zoom(C, up, order=3); Cz = np.clip(Cz, 0, None)
# log tone map keyed to the faint cloud level (90th percentile of the non-zero field), not to the hot spots at the ends
c0 = np.percentile(Cz[Cz > 0], 85.0)
dens = 0.85 * np.log1p(Cz / c0)
dens = dens / (1 + dens / 2.4)
del Cz
# the eye's search: every mouth edge emits a fan of possible continuations (the source field itself), faint and warm
Sm = S.sum(axis=2)
Smz = zoom(Sm, up, order=3); Smz = np.clip(Smz, 0, None)
s0 = np.percentile(Smz[Smz > 0], 80.0)
fan = 0.27 * np.log1p(Smz / s0); fan = fan / (1 + fan / 1.0)
sheet.wash(fan, 'apricot', granulate=0.10, seed=3)
del Smz, Sm
# two pigments by local contour orientation: heading of max-theta at each point (horizontal→aqua, vertical→lavender)
Spi = np.roll(S, NT // 2, axis=2); prod = S * Spi
th_idx = np.argmax(prod, axis=2); th = 2 * np.pi * th_idx / NT
orient = 0.5 * (1 - np.cos(2 * th))                    # 0 horizontal, 1 vertical
orient = zoom(orient.astype(np.float32), up, order=1)
orient = gaussian_filter(orient, 3 * rs)
sheet.wash(dens * (1 - orient), 'aqua', granulate=0.12, seed=1)
sheet.wash(dens * orient, 'lavender', granulate=0.12, seed=2)

# ink: most probable paths of the strongest pairs (weighted by strength)
if pairs:
    top = pairs[0][0]
    ink = np.zeros((H, W), np.float32)
    for (st, s, k, Cp) in pairs[:14]:
        if st < 0.22 * top: break
        xs, ys, _ = ends[s]; xk, yk, _ = ends[k]
        rp = ridge(gaussian_filter(Cp.astype(np.float32), 1.5), (xs, ys), (xk, yk), n=240, half=0.22 * np.hypot(xk - xs, yk - ys), lens=True)
        px = gaussian_filter1d(rp[:, 0], 8, mode='nearest'); py = gaussian_filter1d(rp[:, 1], 8, mode='nearest')
        px[0], py[0], px[-1], py[-1] = xs, ys, xk, yk
        pts = [(x * up, y * up) for x, y in zip(px, py)]
        w = 0.9 * rs * (0.5 + 0.5 * st / top)
        ink += (0.35 + 0.65 * st / top) * P.polyline_density(W, H, pts, w, sigma=0.4 * rs)
    sheet.wash(np.clip(ink, 0, 1) * 0.75, 'ink')

# pac-men in coral (disc minus wedge), rim ink
disc = np.zeros((H, W), np.float32)
for p in pm:
    cx, cy = p['c'][0] * up, p['c'][1] * up; r = p['r'] * up
    x0, x1 = int(max(0, cx - r - 4)), int(min(W, cx + r + 4)); y0, y1 = int(max(0, cy - r - 4)), int(min(H, cy + r + 4))
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    rr = np.hypot(xx - cx, yy - cy)
    da = np.arctan2(yy - cy, xx - cx) - p['bis']
    da = (da + np.pi) % (2 * np.pi) - np.pi
    disc[y0:y1, x0:x1] += (rr < r) & (np.abs(da) > p['opening'] / 2)
disc = gaussian_filter(disc, 0.8 * rs)
sheet.wash(1.25 * disc, 'coral', granulate=0.08, seed=5)
edt = distance_transform_edt(disc < 0.5)
sheet.wash(0.5 * P.ink_from_distance(edt, 0.7 * rs) * (disc < 0.5), 'ink')

title = "The Contour That Isn't There"
sub = ('Coral is all that is printed. The cloud is the probability that a contour the eye draws between two edges passes '
       'through each point (a particle whose heading wanders; Mumford, Williams–Jacobs); the ink is its most likely course.')
fs_t = int(0.036 * H); fs_s = int(0.0125 * H)
sheet.caption_strip(0.905, 0.995, 0.55)
items = [(title, 0.05 * W, 0.935 * H, fs_t, 'serif_bold', 'ls')]
for j, line in enumerate(P.wrap(sub, fs_s, 'italic', 0.90 * W)):
    items.append((line, 0.05 * W, (0.958 + 0.018 * j) * H, fs_s, 'italic', 'ls'))
sheet.wash(0.95 * P.text_density(W, H, items), 'ink')
img = sheet.develop()
P.finish(img, (FINAL, FINAL), OUT + f'_{FINAL}.png')
json.dump(dict(scene=SCENE, FN=FN, NT=NT, sigma=sigma, tau=TAU, G_mass=float(G.sum()), n_inducers=len(pm),
               pair_strengths=[(float(a), int(b), int(c)) for a, b, c, _ in pairs], seconds=time.time() - t0),
          open(OUT + f'_{FINAL}_cert.json', 'w'), indent=1)
print('done [%.0fs]' % (time.time() - t0))
