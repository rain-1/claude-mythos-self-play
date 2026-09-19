"""render_sorites.py — TEN MINUTES AT A TIME.

Derived from render_potato.py: ONE body, the second pushed straight through it. The shared loop shrinks
moment by moment and is the same loop at every moment — until the tangency where it is a point (coral),
then nothing; on the far side a new loop is born at a second tangency. Morse theory answers the sorites:
the identity ends exactly at the tangency.

(original header follows)

Two potatoes side by side. B is pushed through A by pure translation along a path; at every step the
two surfaces cross in closed curves that lie on BOTH bodies. Each curve is drawn on A (where it was
made) and on B (the same curve, in B's own skin) in the same pigment; because the motion is a
translation and the camera orthographic, the two drawings of each curve are exact translates on the
page. Coral: the curve of the pictured moment; B's ghost is shown inside A at that moment.

usage: python3 render_potato.py FINAL out.png [sweep]
"""
import sys, time, json
import numpy as np
from scipy.ndimage import gaussian_filter, zoom, distance_transform_edt, binary_dilation
from PIL import Image, ImageDraw
from pastel import Sheet, PIG, absorb, text_density, text_width, ink_from_distance, finish, wrap
from potato import make_bodies, Chart, sph

FINAL = int(sys.argv[1]) if len(sys.argv) > 1 else 1024
out = sys.argv[2] if len(sys.argv) > 2 else f'cache/sorites_{FINAL}.png'
SWEEP = 'line'
SS = 2
W = H = FINAL * SS
rs = FINAL / 1024 * SS
t0 = time.time()

A, B = make_bodies()
# ---- layout (world units: A's mean radius ~ 1) ----
SCALE = 0.31 * W                    # px per world unit
cA = np.array([0.50 * W, 0.42 * H])   # screen centre of A (A's origin)
cB = None  # screen centre of B (B's origin), drawn in its own frame
VIEW_ROT = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], float)  # camera looks down -z; screen x right, y up


def to_screen(p, c):
    """world (x,y,z) about origin -> screen px, origin at c"""
    return np.stack([c[0] + SCALE * p[..., 0], c[1] - SCALE * p[..., 1]], axis=-1)


# ---- the sweep: pure translation of B through A ----
NT = int(sys.argv[3]) if len(sys.argv) > 3 else 96
if SWEEP == 'arc':
    # B's centre travels on a tilted circle around A's centre: partly inside all the way round
    ts = np.linspace(0, 1, NT, endpoint=False)
    ang = 2 * np.pi * ts
    e1 = np.array([1.0, 0.15, 0.35]); e1 /= np.linalg.norm(e1)
    e2 = np.array([-0.2, 1.0, 0.45]); e2 -= e1 * (e2 @ e1); e2 /= np.linalg.norm(e2)
    RARC = 0.78
    taus = RARC * (np.cos(ang)[:, None] * e1 + np.sin(ang)[:, None] * e2)
else:
    ts = np.linspace(0, 1, NT)
    taus = None   # set below from tau_of (one push direction for loops, tangencies and strip)
T_STAR = int(0.37 * NT)                  # the pictured moment

chart = Chart(A, 768, 1536)
chartB = Chart(B, 512, 1024)
v = -np.array([1.0, 0.35, 0.55]); v /= np.linalg.norm(v)
def tau_of(t):
    return (t - 0.5) * 3.4 * v
def crossing(t):
    g = chart.field(B, tau_of(t)); return g.min() < 0 < g.max(), g
# death: crossing -> none, between 0.42 and 0.46; rebirth: none -> crossing, between 0.54 and 0.58
def bisect(t_cross, t_none):
    for _ in range(40):
        tm = 0.5 * (t_cross + t_none)
        c, _ = crossing(tm)
        if c: t_cross = tm
        else: t_none = tm
    return t_cross
T_DEATH = bisect(0.42, 0.46); T_BIRTH = bisect(0.58, 0.54)
_, gd = crossing(T_DEATH); _, gb = crossing(T_BIRTH)
# the tangency points on A: where |g| is smallest at the tangency moment
def touch_point(g):
    i, j = np.unravel_index(np.argmin(np.abs(g)), g.shape); return chart.x[i, j], chart.n[i, j]
P_DEATH, N_DEATH = touch_point(gd); P_BIRTH, N_BIRTH = touch_point(gb)
taus = np.array([tau_of(t) for t in ts])
print('tangencies', T_DEATH, T_BIRTH, 'points', P_DEATH, P_BIRTH, 'visible', N_DEATH[2] > 0, N_BIRTH[2] > 0)
T_STAR = -1
print('charts', time.time() - t0)

# ---- shading by ray casting (at half the canvas, then upsampled) ----
def raycast(body, c, res_div=2):
    """front depth z and normal for body at screen centre c. Returns (mask, nrm) at full canvas res."""
    w2, h2 = W // res_div, H // res_div
    s = SCALE / res_div
    r_ext = 1.35 * body.axes.max()
    x0, x1 = int(c[0] / res_div - s * r_ext), int(c[0] / res_div + s * r_ext) + 1
    y0, y1 = int(c[1] / res_div - s * r_ext), int(c[1] / res_div + s * r_ext) + 1
    x0, y0 = max(x0, 0), max(y0, 0); x1, y1 = min(x1, w2), min(y1, h2)
    xs = (np.arange(x0, x1) + 0.5 - c[0] / res_div) / s
    ys = -(np.arange(y0, y1) + 0.5 - c[1] / res_div) / s
    X, Y = np.meshgrid(xs, ys)
    zs = np.linspace(r_ext, -r_ext, 40)
    zfront = np.full(X.shape, np.nan)
    prev = np.full(X.shape, np.nan)
    for z in zs:
        P = np.stack([X, Y, np.full_like(X, z)], -1)
        f = body.F(P)
        hit = (f < 0) & np.isnan(zfront)
        zfront[hit] = z; prev[hit] = z + (zs[0] - zs[1])
    m = ~np.isnan(zfront)
    # bisection between prev (outside) and zfront (inside)
    lo, hi = zfront[m].copy(), prev[m].copy()
    Xm, Ym = X[m], Y[m]
    for _ in range(14):
        mid = 0.5 * (lo + hi)
        f = body.F(np.stack([Xm, Ym, mid], -1))
        inside = f < 0
        lo = np.where(inside, mid, lo); hi = np.where(inside, hi, mid)
    zs_ = 0.5 * (lo + hi)
    pts = np.stack([Xm, Ym, zs_], -1)
    nrm = body.normal(pts)
    mask = np.zeros((h2, w2), np.float32); mask[y0:y1, x0:x1] = m
    N = np.zeros((h2, w2, 3), np.float32); N[y0:y1, x0:x1][m] = nrm
    Z = np.zeros((h2, w2), np.float32); Z[y0:y1, x0:x1][m] = zs_
    return mask, N, Z


def upsample(a, f):
    return zoom(a, f, order=1)


sh = Sheet(W, H, seed=5)
LIGHT = np.array([-0.6, 0.62, 0.38]); LIGHT /= np.linalg.norm(LIGHT)


def shade(body, c, pig_body, pig_shadow, strength):
    mask, N, Z = raycast(body, c, 2)
    L = np.clip(N @ LIGHT, 0, 1)
    dark = (1 - L) ** 1.0 * mask                  # 0 lit -> 1 away from the light
    rim = np.clip(1 - N[..., 2], 0, 1) ** 2.0 * mask   # silhouette darkening (contact tone)
    base = 0.06 * mask + 0.70 * dark + 0.25 * rim
    base = gaussian_filter(base, 1.2)
    base2 = upsample(base, 2)[:H, :W]
    sh.wash(strength * base2, pig_body, granulate=0.22, seed=11)
    sh.wash(strength * 0.55 * upsample(gaussian_filter(dark ** 1.5 * mask, 1.2), 2)[:H, :W], pig_shadow, granulate=0.2, seed=12)
    m2 = upsample(mask, 2)[:H, :W] > 0.5
    return m2, N, Z


maskA, NA, ZA = shade(A, cA, 'apricot', 'lavender', 0.95)

print('shaded', time.time() - t0)

# ink silhouettes
def outline(mask, w, weight):
    d_out = distance_transform_edt(~mask); d_in = distance_transform_edt(mask)
    d = np.where(mask, d_in, d_out)
    sh.wash(weight * ink_from_distance(d, w), 'ink')


outline(maskA, 1.5 * rs, 0.9)

# ---- curves ----
HUES = ['lemon', 'apricot', 'blush', 'orchid', 'lavender', 'cornflower', 'aqua', 'mint', 'pistachio']


WARM = ['lemon', 'apricot', 'blush', 'orchid']
COOL = ['lavender', 'cornflower', 'aqua', 'mint']


def tint_of(t):
    """entry family (before the death) walks the warm pigments over its own life; exit family the cool ones"""
    if t <= T_DEATH:
        hues, u = WARM, t / T_DEATH
    else:
        hues, u = COOL, (t - T_BIRTH) / max(1 - T_BIRTH, 1e-9)
    u = float(np.clip(u, 0, 1)); h = u * (len(hues) - 1)
    i = int(np.floor(h)) % len(hues); j = min(i + 1, len(hues) - 1); f = h - np.floor(h)
    return (1 - f) * absorb(PIG[hues[i]]) + f * absorb(PIG[hues[j]])


def draw_polyline_abs(pts, width, dens, absorb_vec, sigma=0.6):
    """draw a polyline (screen px) into the sheet's absorbance within its bbox"""
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


def split_runs(flag):
    """indices of maximal runs where flag is True"""
    runs = []; start = None
    for i, f in enumerate(flag):
        if f and start is None:
            start = i
        if (not f) and start is not None:
            runs.append((start, i)); start = None
    if start is not None:
        runs.append((start, len(flag)))
    return runs


curve_log = []
for k, tau in enumerate(taus):
    g = chart.field(B, tau)
    ncomp = chart.components(g)
    cs = chart.curves(g)
    t = ts[k]
    absv = tint_of(t)
    is_star = (k == T_STAR)
    if is_star:
        absv = absorb(PIG['coral'])
    dens_vis = 0.9 if not is_star else 1.3
    dens_hid = 0.07 if not is_star else 0.22
    wid = 3.6 * rs if not is_star else 5.5 * rs
    total_len = 0.0

    def draw_on(scr, nrm, vis):
        for a, b in split_runs(vis):
            # chunks with density and width following the normal's z (front-facing = fuller)
            idx = np.arange(a, b)
            for c0 in range(0, len(idx), 10):
                sl = idx[c0:c0 + 11]
                if len(sl) < 2:
                    continue
                nzm = float(np.clip(nrm[sl, 2].mean(), 0, 1))
                f = 0.30 + 0.70 * nzm
                draw_polyline_abs(scr[sl], wid * (0.55 + 0.45 * nzm), dens_vis * f, absv)
                draw_polyline_abs(scr[sl], 0.5 * rs, 0.18 * f, absorb(PIG['ink']), sigma=0.35)
        for a, b in split_runs(~vis):
            draw_polyline_abs(scr[a:b], wid * 0.7, dens_hid, absv)

    for p, n, c in cs:
        visA = n[:, 2] > 0.02
        sA = to_screen(p, cA)
        total_len += float(np.linalg.norm(np.diff(p, axis=0), axis=1).sum())
        draw_on(sA, n, visA)
    curve_log.append(dict(k=k, t=float(t), components=int(ncomp), pieces=len(cs), length=total_len))
    if k % 20 == 0:
        print('curve', k, ncomp, len(cs), round(time.time() - t0, 1))

# ---- the ghosts of B at the two tangencies, and the coral touch points ----
from skimage.measure import find_contours
nz = chartB.n[..., 2]
nzp = np.concatenate([nz, nz[:, :1]], axis=1)
sil = []
for c in find_contours(nzp, 0.0):
    ti, pi = c[:, 0], c[:, 1]
    i0 = np.clip(np.floor(ti).astype(int), 0, len(chartB.th) - 2); ft = ti - i0
    j0 = np.floor(pi).astype(int) % len(chartB.ph); j1 = (j0 + 1) % len(chartB.ph); fp = pi - np.floor(pi)
    x = chartB.x
    sil.append((1 - ft)[:, None] * ((1 - fp)[:, None] * x[i0, j0] + fp[:, None] * x[i0, j1]) +
               ft[:, None] * ((1 - fp)[:, None] * x[i0 + 1, j0] + fp[:, None] * x[i0 + 1, j1]))
for tt in (T_DEATH, T_BIRTH):
    tau = tau_of(tt)
    for pp in sil:
        s_ = to_screen(pp + tau, cA)
        seg = np.linalg.norm(np.diff(s_, axis=0), axis=1); arc = np.concatenate([[0], np.cumsum(seg)])
        on = ((arc // (14 * rs)) % 2) == 0
        for a, b in split_runs(on):
            draw_polyline_abs(s_[a:b], 1.3 * rs, 0.7, absorb(PIG['ink']), sigma=0.4)
for P, N in ((P_DEATH, N_DEATH), (P_BIRTH, N_BIRTH)):
    sp = to_screen(P, cA)
    im = Image.new('F', (W, H), 0.0); dr = ImageDraw.Draw(im)
    r = 12 * rs
    dr.ellipse([sp[0] - r, sp[1] - r, sp[0] + r, sp[1] + r], fill=1.0)
    r2 = 6.5 * rs
    dr.ellipse([sp[0] - r2, sp[1] - r2, sp[0] + r2, sp[1] + r2], fill=0.0)
    sh.wash(gaussian_filter(np.asarray(im, np.float32), 0.8 * rs) * (1.3 if N[2] > 0 else 0.35), 'coral')
    # a small glow
    im = Image.new('F', (W, H), 0.0); dr = ImageDraw.Draw(im)
    r3 = 30 * rs
    dr.ellipse([sp[0] - r3, sp[1] - r3, sp[0] + r3, sp[1] + r3], fill=1.0)
    sh.wash(gaussian_filter(np.asarray(im, np.float32), 10 * rs) * (0.18 if N[2] > 0 else 0.05), 'coral')
print('ghosts', time.time() - t0)

# ---- film strip: seven moments of the passage (ink silhouettes, the loop of the moment in its pigment) ----
def silhouette(chartX):
    nzX = chartX.n[..., 2]
    nzq = np.concatenate([nzX, nzX[:, :1]], axis=1)
    outl = []
    for c in find_contours(nzq, 0.0):
        ti, pi = c[:, 0], c[:, 1]
        i0 = np.clip(np.floor(ti).astype(int), 0, len(chartX.th) - 2); ft = ti - i0
        j0 = np.floor(pi).astype(int) % len(chartX.ph); j1 = (j0 + 1) % len(chartX.ph); fp = pi - np.floor(pi)
        x = chartX.x
        pp = ((1 - ft)[:, None] * ((1 - fp)[:, None] * x[i0, j0] + fp[:, None] * x[i0, j1]) +
              ft[:, None] * ((1 - fp)[:, None] * x[i0 + 1, j0] + fp[:, None] * x[i0 + 1, j1]))
        outl.append(pp)
    return outl

silA = silhouette(chart); silB = silhouette(chartB)
NF = 9
frame_ts = [0.0, 0.12, 0.25, 0.36, T_DEATH, 0.5, T_BIRTH, 0.72, 0.88]
fscale = 0.030 * W                    # px per world unit in the strip
fy = 0.815 * H
for fi, ft_ in enumerate(frame_ts):
    fx = W * (0.5 + (fi - (NF - 1) / 2) * 0.105)
    cF = np.array([fx, fy])
    def tsc(pp):
        return np.stack([cF[0] + fscale * pp[..., 0], cF[1] - fscale * pp[..., 1]], axis=-1)
    for pp in silA:
        draw_polyline_abs(tsc(pp), 1.2 * rs, 0.8, absorb(PIG['ink']), sigma=0.4)
    tau = tau_of(ft_)
    for pp in silB:
        s = tsc(pp + tau)
        seg = np.linalg.norm(np.diff(s, axis=0), axis=1); arc = np.concatenate([[0], np.cumsum(seg)])
        on = ((arc // (6 * rs)) % 2) == 0
        for a, b in split_runs(on):
            draw_polyline_abs(s[a:b], 1.0 * rs, 0.6, absorb(PIG['ink']), sigma=0.4)
    g = chart.field(B, tau)
    absv = absorb(PIG['coral']) if ft_ in (T_DEATH, T_BIRTH) else tint_of(ft_)
    if ft_ in (T_DEATH, T_BIRTH):
        P = P_DEATH if ft_ == T_DEATH else P_BIRTH
        sp = tsc(P[None])[0]
        im = Image.new('F', (W, H), 0.0); ImageDraw.Draw(im).ellipse([sp[0] - 3 * rs, sp[1] - 3 * rs, sp[0] + 3 * rs, sp[1] + 3 * rs], fill=1.0)
        sh.wash(gaussian_filter(np.asarray(im, np.float32), 0.6 * rs) * 1.2, 'coral')
    for pp, n, c in chart.curves(g):
        vis = n[:, 2] > 0.02
        s = tsc(pp)
        for a, b in split_runs(vis):
            draw_polyline_abs(s[a:b], 2.2 * rs, 1.0, absv, sigma=0.5)
        for a, b in split_runs(~vis):
            draw_polyline_abs(s[a:b], 1.6 * rs, 0.25, absv, sigma=0.5)
print('strip', time.time() - t0)

# ---- caption ----
sh.caption_strip(0.90, 0.985, 0.62)
title = 'Ten Minutes at a Time'
sub = ('A second body pushed straight through the first. The curve their skins share shrinks moment by moment and at every moment is still the same curve — '
       'until it is a point, and then nothing (coral, t = %.3f). On the far side a new curve is born at a second tangency (t = %.3f). Morse answers the sorites: the identity ends at the tangency, not somewhere along the way.' % (T_DEATH, T_BIRTH))
items = [(title, W * 0.5, H * 0.925, 30 * rs, 'serif_bold', 'mm')]
lines = wrap(sub, 15.5 * rs, 'italic', 0.80 * W)
for i, ln in enumerate(lines):
    items.append((ln, W * 0.5, H * (0.952 + 0.020 * i), 15.5 * rs, 'italic', 'mm'))
sh.wash(text_density(W, H, items) * 0.95, 'ink')
img = sh.develop()
finish(img, (FINAL, FINAL), out)
json.dump(dict(NT=NT, T_DEATH=T_DEATH, T_BIRTH=T_BIRTH, P_DEATH=P_DEATH.tolist(), P_BIRTH=P_BIRTH.tolist(), curves=curve_log), open('cache/sorites_curves.json', 'w'))
print('done', time.time() - t0)
