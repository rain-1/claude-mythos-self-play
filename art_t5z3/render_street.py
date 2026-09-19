"""render_street.py — THE EDDY IS NOT THE WATER (landscape 4096 x 2560).

A von Kármán vortex street (exact staggered point-vortex street, Krasny-regularised) drifts through
still-ish water in a free stream; dye is released continuously at fixed points upstream and every
particle is advected in the lab frame.  Pigment = the streaklines (the water, tinted by the height of
the source that released it: warm above the axis, cool below).  Ink = the streamlines of the street's
OWN frame, in which the flow is steady: the cat's-eyes that travel unchanged while the water inside
them is exchanged.  Coral = the vortex centres.  What persists is the pattern, not the stuff.

usage: python3 render_street.py FINAL_W out.png
"""
import sys, time, json
import numpy as np
from scipy.ndimage import gaussian_filter, distance_transform_edt
from PIL import Image, ImageDraw
from skimage.measure import find_contours
from pastel import Sheet, PIG, absorb, text_density, ink_from_distance, finish, wrap
import street as st

FW = int(sys.argv[1]) if len(sys.argv) > 1 else 1024
out = sys.argv[2] if len(sys.argv) > 2 else f'cache/street_{FW}.png'
SS = 2
W = FW * SS; H = int(W * 0.52)
rs = FW / 1024 * SS
t0 = time.time()

U = 1.0
Us = st.street_speed(); Uv = U - Us
# window in world units: the street lies along y = 0; show x from XL to XR
XL, XR = 0.55, 5.05
YC = -0.10
sx = W / (XR - XL)
YH = (H / sx)              # world height of the window
print('window', XL, XR, 'height', YH, 'Uv', Uv)


def to_px(P):
    return np.stack([(P[:, 0] - XL) * sx, H * 0.5 - (P[:, 1] - YC) * sx], 1)


# ---- the dye ----
NSRC = 30 if FW >= 2048 else 26
_u = np.linspace(-1, 1, NSRC)
ys = 0.62 * np.sign(_u) * np.abs(_u) ** 1.5
T = 11.0; dt = 0.004
release_every = 2
P, TR, J = st.streaklines(ys, U, T, dt, release_every, xsrc=-1.6)
print('particles', len(P), 'in', round(time.time() - t0, 1), 's')

sh = Sheet(W, H, seed=21)

# streaklines as polylines: for each source, particles ordered by release time (latest released = nearest the source)
HUES_TOP = ['lemon', 'apricot', 'blush', 'orchid']
HUES_BOT = ['pistachio', 'mint', 'aqua', 'cornflower']


def tint_for(j):
    """source index -> absorbance vector: warm above the axis (outer = lemon ... inner = orchid), cool below"""
    y = ys[j]
    f = min(abs(y) / 0.62, 1.0)          # 0 axis .. 1 outermost
    hues = HUES_TOP if y >= 0 else HUES_BOT
    h = (1 - f) * (len(hues) - 1)        # axis -> last (orchid/cornflower), outer -> first (lemon/pistachio)
    i = int(np.floor(h)); k = min(i + 1, len(hues) - 1); fr = h - i
    return (1 - fr) * absorb(PIG[hues[i]]) + fr * absorb(PIG[hues[k]])


def draw_polyline_abs(pts, width, dens, absorb_vec, sigma=0.6):
    if len(pts) < 2:
        return
    pad = int(width * 3 + 4)
    x0 = int(max(0, pts[:, 0].min() - pad)); x1 = int(min(W, pts[:, 0].max() + pad))
    y0 = int(max(0, pts[:, 1].min() - pad)); y1 = int(min(H, pts[:, 1].max() + pad))
    if x1 - x0 < 2 or y1 - y0 < 2:
        return
    im = Image.new('F', (x1 - x0, y1 - y0), 0.0)
    dr = ImageDraw.Draw(im)
    dr.line([(float(x - x0), float(y - y0)) for x, y in pts], fill=1.0, width=int(max(1, round(width))), joint='curve')
    a = np.asarray(im, np.float32)
    if sigma:
        a = gaussian_filter(a, sigma)
    sh.A[y0:y1, x0:x1] += (dens * a)[..., None] * absorb_vec[None, None, :]


for j in range(NSRC):
    sel = np.where(J == j)[0]
    order = sel[np.argsort(TR[sel])]
    pts = P[order]
    # break the streakline where consecutive particles are far apart (stretched past resolution)
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    # local stretch = spacing relative to the release spacing; density fades with stretch (dye thins)
    absv = tint_for(j)
    inner = 1 - min(abs(ys[j]) / 0.62, 1.0)
    base_w = (2.6 + 2.2 * inner) * rs
    chunk = 40
    for c0 in range(0, len(pts) - 1, chunk):
        sl = slice(c0, min(c0 + chunk + 1, len(pts)))
        p = pts[sl]
        s = seg[c0:min(c0 + chunk, len(seg))]
        stretch = float(np.median(s)) / (U * dt * release_every)
        if float(s.max()) > 0.12:
            # broken: draw sub-pieces
            pieces = np.split(np.arange(len(p)), np.where(s > 0.12)[0] + 1)
            for pc in pieces:
                if len(pc) > 1:
                    draw_polyline_abs(to_px(p[pc]), base_w / (1 + 0.25 * stretch) ** 0.4, 0.8 / (1 + 0.25 * stretch) ** 0.5, absv)
            continue
        draw_polyline_abs(to_px(p), base_w / (1 + 0.25 * stretch) ** 0.4, 0.8 / (1 + 0.25 * stretch) ** 0.5, absv)
print('dye drawn', round(time.time() - t0, 1))

# ---- ink: streamlines of the street frame at time T (the pattern) ----
xs = np.linspace(XL, XR, 1400); yy = np.linspace(-YH / 2, YH / 2, int(1400 * YH / (XR - XL)))
X, Y = np.meshgrid(xs, yy)
x0 = Uv * T                      # where the street's reference vortex sits at time T
psi = st.streamfunction_street_frame(X - x0, Y, U)
# separatrix level: the stagnation points of the street frame lie on the x-axis between vortices?  Take the
# level set through the saddle: find stagnation points numerically (|velocity| minima in the street frame)
u, v = st.velocity(X, Y, T, U); u = u - Uv
spd = np.hypot(u, v)
# levels: a ladder around the vortex-core values + the saddle level(s)
from scipy.ndimage import minimum_filter
mins = (spd == minimum_filter(spd, size=9)) & (spd < 0.05)
cand = np.stack([X[mins], Y[mins], psi[mins]], 1)
print('stagnation candidates', len(cand))
levels = []
if len(cand):
    for lv in np.unique(np.round(cand[:, 2], 4)):
        levels.append(float(lv))
# inner loops: between the saddle level and the core values; outer: two undulating streamlines just outside
sep = levels[0] if levels else float(np.median(psi))
core_hi = float(psi.max()); core_lo = float(psi.min())
inner = []
for frac in (0.025, 0.07, 0.15, 0.30):
    inner.append(sep + frac * (core_hi - sep) * 0.9)   # eyes of one sign
    inner.append(sep - frac * (sep - core_lo) * 0.9)   # eyes of the other sign
ladder = inner
ink_img = np.zeros((H, W), np.float32)
for lv in ladder + levels:
    is_sep = lv in levels
    for c in find_contours(psi, lv):
        pts = np.stack([xs[np.clip(c[:, 1].astype(int), 0, len(xs) - 1)] + (c[:, 1] % 1) * (xs[1] - xs[0]),
                        yy[np.clip(c[:, 0].astype(int), 0, len(yy) - 1)] + (c[:, 0] % 1) * (yy[1] - yy[0])], 1)
        if len(pts) < 3:
            continue
        draw_polyline_abs(to_px(pts), (1.2 if is_sep else 0.7) * rs, (0.6 if is_sep else 0.2), absorb(PIG['ink']), sigma=0.45)
print('ink drawn', round(time.time() - t0, 1))

# ---- coral: the vortex centres at time T ----
cx_top = x0 + st.A_SP * np.arange(-3, 12); cy_top = np.full_like(cx_top, st.H_ROW / 2)
cx_bot = x0 + st.A_SP / 2 + st.A_SP * np.arange(-3, 12); cy_bot = np.full_like(cx_bot, -st.H_ROW / 2)
cs = np.concatenate([np.stack([cx_top, cy_top], 1), np.stack([cx_bot, cy_bot], 1)])
im = Image.new('F', (W, H), 0.0); dr = ImageDraw.Draw(im)
for x, y in to_px(cs):
    r = 6.0 * rs
    dr.ellipse([x - r, y - r, x + r, y + r], fill=1.0)
    r2 = 4.2 * rs
    dr.ellipse([x - r2, y - r2, x + r2, y + r2], fill=0.0)
sh.wash(gaussian_filter(np.asarray(im, np.float32), 0.6 * rs) * 1.4, 'coral')

# ---- caption ----
sh.caption_strip(0.845, 0.985, 0.62)
title = 'The Eddy Is Not the Water'
sub = ('A vortex street drifts through the stream; dye released upstream is wound into it and left behind, tinted by where it entered. '
       'Ink: the streamlines of the street’s own frame, in which nothing changes while all the water is exchanged. Coral: the vortex centres.')
items = [(title, W * 0.5, H * 0.885, 30 * rs, 'serif_bold', 'mm')]
lines = wrap(sub, 15.5 * rs, 'italic', 0.84 * W)
for i, ln in enumerate(lines):
    items.append((ln, W * 0.5, H * (0.93 + 0.034 * i), 15.5 * rs, 'italic', 'mm'))
sh.wash(text_density(W, H, items) * 0.95, 'ink')
img = sh.develop()
finish(img, (FW, H // SS), out)
json.dump(dict(U=U, Us=Us, Uv=Uv, T=T, dt=dt, NSRC=NSRC, particles=int(len(P)), h_over_a=st.H_ROW / st.A_SP,
               delta=st.DELTA, stagnation=cand.tolist()[:40]), open('cache/street_cert.json', 'w'), indent=1)
print('done', round(time.time() - t0, 1))
