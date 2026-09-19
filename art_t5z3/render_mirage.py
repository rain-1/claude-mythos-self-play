"""render_mirage.py — THE WATER THAT IS ONLY SKY (landscape, 4096 x 2304).

Side view: hot ground (warm band), a tower at the left, an eye at the right (coral). A fan of rays from the
tower's top point: pigment by launch angle (warm for rays that reach the eye's side going up, cool for rays
that dipped and turned), rays that hit the ground fade out. Ink: the fold caustic (envelope of the fan) —
inside the fold the eye sees the tower twice. Inset (right): what the eye sees — the tower erect above,
inverted below, the lowest part missing, and beneath the vanishing line only sky (aqua): the water.

usage: python3 render_mirage.py FINAL_W out.png
"""
import sys, time, json
import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image, ImageDraw
from pastel import Sheet, PIG, absorb, text_density, finish, wrap
import mirage as M

FW = int(sys.argv[1]) if len(sys.argv) > 1 else 1024
out = sys.argv[2] if len(sys.argv) > 2 else f'cache/mirage_{FW}.png'
SS = 2
W = FW * SS; H = int(W * 0.5625)
rs = FW / 1024 * SS
t0 = time.time()
M.EPS, M.HSC, M.L = 0.05, 0.30, 12.0
L = M.L
Z_EYE = 1.1
TOWER = (0.30, 1.70)          # the tower's foot and top
Z_SRC = 1.62                  # the fan's source point (near the top)

sh = Sheet(W, H, seed=44)
# ---- side-view window: x in [-0.6, L + 0.8], z in [-0.25, 2.55] mapped to the left 74 % of the sheet, upper 80 %
X0, X1 = -0.6, L + 0.9
Z0, Z1 = -0.22, 2.55
px_w = 0.74 * W; px_h = 0.80 * H
sx = px_w / (X1 - X0); sz = px_h / (Z1 - Z0)
sz = min(sz, sx * 2.6)        # vertical exaggeration at most 2.6x
def to_px(x, z):
    return np.stack([0.03 * W + (np.asarray(x) - X0) * sx, 0.04 * H + (Z1 - np.asarray(z)) * sz], -1)


def draw_polyline_abs(pts, width, dens, absorb_vec, sigma=0.6):
    pts = np.asarray(pts, float)
    pts = pts[~np.isnan(pts).any(1)]
    if len(pts) < 2:
        return
    pad = int(width * 3 + 4)
    x0 = int(max(0, pts[:, 0].min() - pad)); x1 = int(min(W, pts[:, 0].max() + pad))
    y0 = int(max(0, pts[:, 1].min() - pad)); y1 = int(min(H, pts[:, 1].max() + pad))
    if x1 - x0 < 2 or y1 - y0 < 2:
        return
    im = Image.new('F', (x1 - x0, y1 - y0), 0.0)
    ImageDraw.Draw(im).line([(float(x - x0), float(y - y0)) for x, y in pts], fill=1.0, width=int(max(1, round(width))), joint='curve')
    a = np.asarray(im, np.float32)
    if sigma:
        a = gaussian_filter(a, sigma)
    sh.A[y0:y1, x0:x1] += (dens * a)[..., None] * absorb_vec[None, None, :]


# ---- the hot ground: a warm band whose density follows the index gradient (the hot layer) ----
zz = np.linspace(Z1, Z0, H)
prof = np.exp(-np.maximum(zz, 0) / M.HSC) * (zz >= 0) + (zz < 0) * 1.0
band = np.zeros((H, W), np.float32)
band[:, :] = prof[:, None]
xmask = np.zeros(W, np.float32); c0, c1 = to_px(X0, 0)[0], to_px(X1, 0)[0]
xmask[int(c0):int(c1)] = 1
band *= xmask[None, :]
rowmask = (np.arange(H) >= to_px(0, Z1)[1] - 1) & (np.arange(H) <= to_px(0, Z0)[1] + 1)
band *= rowmask[:, None].astype(np.float32)
sh.wash(gaussian_filter(band, 1.5 * rs) * 1.1, 'apricot', granulate=0.3, seed=3)
sh.wash(gaussian_filter(band ** 3, 1.5 * rs) * 0.8, 'coral', granulate=0.2, seed=4)
# ground line
gl = to_px(np.array([X0, X1]), np.array([0, 0]))
draw_polyline_abs(gl, 2.0 * rs, 0.9, absorb(PIG['ink']))

# ---- the fan of rays from the tower's top ----
NR = 260 if FW >= 2048 else 140
th = np.linspace(-0.40, 0.16, NR)
X, Z = M.trace(0.0, Z_SRC, th, ds=0.01)
xs = np.linspace(0, L, 600)
Zg = M.resample(X, Z, xs)
# classify: hit the ground (ends before L), turned (minimum z above 0 and final direction upward), direct
ends = np.array([np.nanmax(X[i]) if np.any(~np.isnan(X[i])) else 0 for i in range(NR)])
hit = ends < L - 1e-6
turned = np.zeros(NR, bool)
for i in range(NR):
    m = ~np.isnan(Z[i])
    if m.sum() > 5:
        zi = Z[i, m]
        turned[i] = (np.argmin(zi) > 5) and (np.argmin(zi) < m.sum() - 5) and not hit[i]
WARM = ['lemon', 'apricot', 'blush']; COOL = ['lavender', 'cornflower', 'aqua', 'mint']


def walk(hues, u):
    u = float(np.clip(u, 0, 1)); h = u * (len(hues) - 1)
    i = int(np.floor(h)) % len(hues); j = min(i + 1, len(hues) - 1); f = h - np.floor(h)
    return (1 - f) * absorb(PIG[hues[i]]) + f * absorb(PIG[hues[j]])


for i in range(NR):
    m = ~np.isnan(X[i])
    if m.sum() < 2:
        continue
    pts = to_px(X[i, m], Z[i, m])
    if hit[i]:
        # fades into the ground: draw in segments with decaying density
        k = len(pts); nseg = 6
        for s in range(nseg):
            a, b = int(k * s / nseg), int(k * (s + 1) / nseg) + 1
            draw_polyline_abs(pts[a:b], 1.4 * rs, 0.22 * (1 - s / nseg), absorb(PIG['sepia']))
    elif turned[i]:
        u = (th[i] - th[turned].min()) / max(th[turned].max() - th[turned].min(), 1e-9)
        draw_polyline_abs(pts, 1.8 * rs, 0.62, walk(COOL, u))
    else:
        u = (th[i] - th[~turned & ~hit].min()) / max(th[~turned & ~hit].max() - th[~turned & ~hit].min(), 1e-9)
        draw_polyline_abs(pts, 1.8 * rs, 0.55, walk(WARM, u))
print('rays', NR, 'hit', hit.sum(), 'turned', turned.sum(), round(time.time() - t0, 1))

# ---- the caustic (fold) in ink: the envelope of the turned family = its lower boundary at every x ----
c = M.caustic(Zg, xs)
Zt = Zg[turned]
env = np.nanmin(np.where(np.isnan(Zt), np.inf, Zt), axis=0) if turned.any() else np.full(len(xs), np.nan)
env[~np.isfinite(env)] = np.nan
# the fold begins where the turned rays start to cross (first caustic point); before that the boundary is just the last ray
x_fold0 = c[:, 0].min() if len(c) else xs[0]
mask_env = (xs >= x_fold0) & ~np.isnan(env)
if mask_env.sum() > 4:
    draw_polyline_abs(to_px(xs[mask_env], env[mask_env]), 3.8 * rs, 1.15, absorb(PIG['ink']), sigma=0.7)
print('caustic points', len(c), 'fold from x =', x_fold0, 'env pts', int(mask_env.sum()), 'turned', int(turned.sum()))

# ---- the tower (ink) and the eye (coral) ----
tw = 0.22
tower_pts = to_px(np.array([0, 0, -tw / 2, 0, tw / 2, 0]), np.array([0, TOWER[1], TOWER[1], TOWER[1] + 0.12, TOWER[1], TOWER[1]]))
draw_polyline_abs(to_px(np.array([0, 0]), np.array([0, TOWER[1]])), 5.0 * rs, 1.0, absorb(PIG['ink']))
draw_polyline_abs(to_px(np.array([-tw / 2, 0, tw / 2]), np.array([TOWER[1], TOWER[1] + 0.14, TOWER[1]])), 3.0 * rs, 1.0, absorb(PIG['ink']))
# a ladder of tower heights as tick marks, tinted by height (the same tints the inset uses)
TZ = np.linspace(TOWER[0], TOWER[1], 15)
TOW = ['pistachio', 'mint', 'aqua', 'cornflower', 'lavender', 'orchid', 'blush', 'apricot', 'lemon']
for zt in TZ:
    u = (zt - TOWER[0]) / (TOWER[1] - TOWER[0])
    draw_polyline_abs(to_px(np.array([-0.16, 0.16]), np.array([zt, zt])), 3.2 * rs, 1.0, walk(TOW, u))
eye = to_px(L, Z_EYE)
im = Image.new('F', (W, H), 0.0); dr = ImageDraw.Draw(im)
r = 9 * rs; dr.ellipse([eye[0] - r, eye[1] - r, eye[0] + r, eye[1] + r], fill=1.0)
r2 = 4 * rs; dr.ellipse([eye[0] - r2, eye[1] - r2, eye[0] + r2, eye[1] + r2], fill=0.0)
sh.wash(gaussian_filter(np.asarray(im, np.float32), 0.7 * rs) * 1.3, 'coral')

# ---- the inset: what the eye sees ----
TZD = np.linspace(TOWER[0], TOWER[1], 48 if FW >= 2048 else 30)
NANG = 1400 if FW >= 2048 else 700
seen0 = M.view(Z_EYE, TZD, nang=NANG, th_range=(-0.45, 0.2))
vis = np.array([np.any(seen0[:, 0] == z_) for z_ in TZD]) if len(seen0) else np.zeros(len(TZD), bool)
# the fold: bisection on the tower height between the highest invisible and the lowest visible point
if vis.any() and (~vis).any() and np.argmax(vis) > 0:
    lo, hi = TZD[np.argmax(vis) - 1], TZD[np.argmax(vis)]
    for _ in range(18):
        mid = 0.5 * (lo + hi)
        if len(M.view(Z_EYE, [mid], nang=NANG, th_range=(-0.45, 0.2))):
            hi = mid
        else:
            lo = mid
    z_fold = hi
    extra = z_fold + (TZD[np.argmax(vis)] - z_fold) * np.linspace(0, 1, 9)[1:-1] ** 2
    TZD = np.sort(np.concatenate([TZD, extra]))
else:
    z_fold = None
seen = M.view(Z_EYE, TZD, nang=NANG, th_range=(-0.45, 0.2))
print('fold height', z_fold)
print('seen', len(seen), round(time.time() - t0, 1))
ix0, ix1 = 0.80 * W, 0.97 * W
iy0, iy1 = 0.06 * H, 0.84 * H
e_lo, e_hi = -0.07, 0.30
def to_inset(elev):
    return iy1 - (np.asarray(elev) - e_lo) / (e_hi - e_lo) * (iy1 - iy0)
frame = np.zeros((H, W), np.float32)
frame[int(iy0):int(iy1), int(ix0):int(ix1)] = 1
yy = np.arange(H)
horizon_y = to_inset(0.0)
sh.wash(frame * np.clip((iy1 - yy[:, None]) / (iy1 - iy0), 0, 1) * 0.08, 'aqua')     # sky, paler toward the horizon
vanish = None
if len(seen):
    # erect vs inverted: sign of d(elevation)/d(tower height) along each branch (launch angle separates the branches)
    zt, el, th0 = seen[:, 0], seen[:, 1], seen[:, 2]
    direct = th0 > np.median(th0[zt == zt.max()]) - 1e-9 if False else None
    # branch by launch angle: the turned rays leave below a threshold; take the two arrivals per point ordered by elevation
    erect = np.zeros(len(seen), bool)
    for z_ in np.unique(zt):
        idx = np.where(zt == z_)[0]
        if len(idx) >= 2:
            erect[idx[np.argmax(el[idx])]] = True
        else:
            erect[idx] = True
    lowest_visible = zt.min()
    fold_el = float(np.mean(el[zt == lowest_visible]))       # the join: both images of the lowest visible point (found by bisection above)
    vanish = float(el.min())                                    # the inverted top: below it only sky
    water = frame * (yy[:, None] > to_inset(vanish)) * 0.55
    sh.wash(gaussian_filter(water, 1.0 * rs), 'aqua', granulate=0.25, seed=9)
    xm = 0.5 * (ix0 + ix1); hw = 0.09 * (ix1 - ix0)
    for k in range(len(seen)):
        u = (zt[k] - TOWER[0]) / (TOWER[1] - TOWER[0])
        y = to_inset(el[k])
        draw_polyline_abs(np.array([[xm - hw, y], [xm + hw, y]]), 3.4 * rs, 1.0, walk(TOW, u))
    draw_polyline_abs(np.array([[ix0, horizon_y], [ix1, horizon_y]]), 0.8 * rs, 0.5, absorb(PIG['ink']))
    fy = to_inset(fold_el)
    draw_polyline_abs(np.array([[ix0, fy], [ix1, fy]]), 2.2 * rs, 1.1, absorb(PIG['coral']))
    labs = [('erect', ix1 - 4 * rs, min(to_inset(el[erect].mean()), iy1 - 20 * rs), 9.5 * rs, 'italic', 'rm'),
            ('inverted', ix1 - 4 * rs, to_inset(el[~erect].mean()), 9.5 * rs, 'italic', 'rm'),
            ('sky', ix1 - 4 * rs, 0.5 * (to_inset(vanish) + iy1), 9.5 * rs, 'italic', 'rm')]
    sh.wash(text_density(W, H, labs) * 0.8, 'ink')
# inset frame
draw_polyline_abs(np.array([[ix0, iy0], [ix1, iy0], [ix1, iy1], [ix0, iy1], [ix0, iy0]]), 1.6 * rs, 0.9, absorb(PIG['ink']))
lab = [('what the eye sees', 0.5 * (ix0 + ix1), iy0 - 9 * rs, 11 * rs, 'italic', 'mm')]
sh.wash(text_density(W, H, lab) * 0.9, 'ink')

# ---- caption ----
sh.caption_strip(0.855, 0.985, 0.62)
title = 'The Water That Is Only Sky'
sub = ('Hot ground, cooler air above: light bends upward. Rays from the tower that dip toward the ground turn back before touching it and reach the eye from below, '
       'so the eye sees the tower a second time, inverted, and the two images join at the fold (coral) and beneath the inverted top it sees the sky and calls it water. '
       'Ink: the fold caustic of the fan — inside the fold there are two images, outside one. A state with the look of water and none of its function.')
items = [(title, W * 0.5, H * 0.885, 30 * rs, 'serif_bold', 'mm')]
lines = wrap(sub, 14.5 * rs, 'italic', 0.86 * W)
for i, ln in enumerate(lines):
    items.append((ln, W * 0.5, H * (0.925 + 0.026 * i), 14.5 * rs, 'italic', 'mm'))
sh.wash(text_density(W, H, items) * 0.95, 'ink')
img = sh.develop()
finish(img, (FW, H // SS), out)
json.dump(dict(eps=M.EPS, h=M.HSC, L=L, z_eye=Z_EYE, tower=TOWER, z_src=Z_SRC, rays=int(NR), hit=int(hit.sum()), turned=int(turned.sum()),
               caustic_points=int(len(c)), caustic_z=(float(c[:, 1].min()), float(c[:, 1].max())) if len(c) else None,
               vanishing_elevation=vanish, fold_elevation=(fold_el if len(seen) else None), fold_height=z_fold,
               images_per_tower_point={str(round(float(z_), 3)): int(np.sum(seen[:, 0] == z_)) for z_ in TZD} if len(seen) else {}),
          open('cache/mirage_cert.json', 'w'), indent=1)
print('done', round(time.time() - t0, 1))
