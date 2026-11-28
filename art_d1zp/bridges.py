"""NO LAST BRIDGE — hero.  Cut-paper tunnel book: a canal at night, identical bridges one behind another.

The law that makes "one of four holds more than a third of the total" as likely as it can be
(MO 474916; exact supremum 0.400695..., a root of 16x^4+8x^3+99x^2-32x-4) is self-similar:
    X = eps^G * (1 - eps^U),   G geometric (go one level deeper with probability p* = 0.474346),
                               U uniform on (0,1),   eps -> 0.
Here that is a place.  Bridge number G stands at distance eps^-G, so it looks eps^G as tall; under every
bridge the lanterns hang at the same real heights 1 - eps^U.  X = how high a lantern looks from here.
One paper sheet per bridge; one lantern per draw.
usage: bridges.py W out.png [N] [seed]"""
import sys, json, numpy as np
from scipy.ndimage import gaussian_filter, zoom
from PIL import Image, ImageDraw, ImageFont
W = int(sys.argv[1]); OUT = sys.argv[2]
N = int(sys.argv[3]) if len(sys.argv) > 3 else 420
SEED = int(sys.argv[4]) if len(sys.argv) > 4 else 15
S = W / 1024.0; rng = np.random.default_rng(SEED)
EPS = 0.4; PSTAR = 0.47434645545490369
def noise(shape, sig, seed):
    r = np.random.default_rng(seed).standard_normal(shape).astype(np.float32); r = gaussian_filter(r, sig, mode='wrap'); return r / r.std()
def hexc(s): return np.array([int(s[i:i + 2], 16) for i in (1, 3, 5)], np.float32) / 255
INK = dict(night=hexc('#0d1230'), deep=hexc('#151c46'), ind=hexc('#232d66'), dusk=hexc('#4a4a86'), mauve=hexc('#8a6f9c'),
           rose=hexc('#d79a9a'), peach=hexc('#f0c3a0'), cream=hexc('#f6ecd2'), red=hexc('#d8362b'), mat=hexc('#efe6d0'),
           pencil=hexc('#4b4a55'), slate=hexc('#6f7aa8'), pale=hexc('#c9c6d8'), amber=hexc('#f0a94e'), gold=hexc('#f7d98a'))
SHEET = [hexc(c) for c in ('#080b20', '#161d4a', '#2c3577', '#535596', '#8a6fa6', '#bd8aa6', '#dba3a0', '#ecbba0', '#f0c3a0')]

# ---------- geometry ----------
M = int(0.085 * W); MB = int(0.150 * W)
x0, x1, y0, y1 = M, W - M, M, W - MB; ww = x1 - x0; wh = y1 - y0
yw = y0 + 0.665 * wh            # the waterline; the eye is at water level, so this is also the horizon
xv = x0 + 0.455 * ww            # straight ahead
R0 = 0.585 * wh                 # the near bridge: its vault nearly fills the window
yy, xx = np.mgrid[0:W, 0:W].astype(np.float32)
dx = xx - xv; hh = yw - yy
aa = lambda d, w=1.2: np.clip(d / w + 0.5, 0, 1)

# ---------- the draws ----------
G = rng.geometric(1 - PSTAR, N) - 1; U = rng.random(N)
X = EPS ** G * (1 - EPS ** U)                                  # apparent height, in units of the near vault
# one hand of four, in red: chosen as the first four consecutive draws with two tops (so two lions)
hand = None
for i in range(0, N - 3):
    g = G[i:i + 4]; x = X[i:i + 4]
    if (g == 0).sum() == 2 and (g == 1).sum() == 1 and (g == 2).sum() == 1 and (3 * x > x.sum()).sum() == 2 \
            and np.all(x[g == 0] > 0.34) and x[g == 1][0] > 0.12:
        hand = list(range(i, i + 4)); break
lions_all = 0
for i in range(0, N - 3, 4):
    x = X[i:i + 4]; lions_all += int((3 * x > x.sum()).sum())

# ---------- sky ----------
img = np.zeros((W, W, 3), np.float32); img[:] = INK['deep']
t = (yy - y0) / (yw - y0)
bands = [(0.20, 'ind'), (0.40, 'dusk'), (0.60, 'mauve'), (0.78, 'rose'), (0.90, 'peach'), (0.962, 'cream')]
INK['ind'] = hexc('#1d2658'); INK['dusk'] = hexc('#3a3d7c'); INK['mauve'] = hexc('#6b5c96'); INK['rose'] = hexc('#a97fa2'); INK['peach'] = hexc('#dfa59f'); 
for i, (lv, nm) in enumerate(bands):
    edge = lv + 0.018 * noise((W,), 40 * S, 100 + i)[None, :] + 0.004 * noise((W,), 4 * S, 200 + i)[None, :] \
        - 0.05 * np.exp(-(dx / (0.22 * ww)) ** 2) * (0.3 + 0.1 * i)
    a = aa((t - edge) * (yw - y0))
    lip = np.clip(1 - np.abs((t - edge) * (yw - y0) + 0.2 * S) / (1.3 * S), 0, 1) * 0.3
    sh = np.clip(1 - np.abs((t - edge) * (yw - y0) - 3 * S) / (5 * S), 0, 1) * 0.16 * a
    img = img * (1 - a[..., None]) + INK[nm] * a[..., None]
    img *= (1 - sh[..., None]); img += (INK['cream'] - img) * lip[..., None] * 0.5
ns = 420; sx = rng.uniform(x0, x1, ns); sy = y0 + (yw - y0) * rng.uniform(0, 1, ns) ** 1.3 * 0.62
star = np.zeros((W, W), np.float32)
for a_, b_, r_ in zip(sx, sy, rng.uniform(0.5, 1.2, ns) * S):
    ia, ib = int(a_), int(b_); Rr = int(3 * r_) + 2
    sl = (slice(ib - Rr, ib + Rr + 1), slice(ia - Rr, ia + Rr + 1))
    star[sl] += np.exp(-((xx[sl] - a_) ** 2 + (yy[sl] - b_) ** 2) / (2 * r_ * r_)) * rng.uniform(0.35, 1.0)
img += (INK['cream'] - img) * np.clip(star, 0, 1)[..., None] * 0.85
# the moon, rising at the far end of the canal: the point every bridge is on its way to
mr = R0 * EPS ** 3 * 0.80; mxc, myc = xv, yw - 0.42 * mr
dm = np.hypot(xx - mxc, yy - myc)
img += (INK['cream'] - img) * (0.50 * np.exp(-(dm / (3.4 * mr)) ** 2) + 0.22 * np.exp(-(dm / (9 * mr)) ** 2))[..., None] * (hh > 0)[..., None]
img += (np.array([1.0, 0.975, 0.90], np.float32) - img) * aa(mr - dm)[..., None]

# ---------- sheets, far to near ----------
def blur_big(a, sig):
    if sig < 3: return gaussian_filter(a, sig)
    f = max(1, int(sig / 3)); hh_, ww_ = (a.shape[0] // f) * f, (a.shape[1] // f) * f; small = a[:hh_, :ww_].reshape(hh_ // f, f, ww_ // f, f).mean((1, 3)); b = gaussian_filter(small, sig / f)
    if f == 1: return b
    up_ = zoom(b, f, order=1)[:a.shape[0], :a.shape[1]]
    if up_.shape != a.shape: up_ = np.pad(up_, ((0, a.shape[0] - up_.shape[0]), (0, a.shape[1] - up_.shape[1])), mode='edge')
    return up_
def sheet_mask(j):
    R = R0 * EPS ** j; r_ = np.random.default_rng(900 + j)
    arch = aa(R - np.hypot(dx, hh))
    deck = aa(1.27 * R - hh)
    # balustrade: a row of small cut-outs under the coping
    per = 0.085 * R; cell = np.abs(((dx / per) % 1.0) - 0.5) * per
    hole = aa(0.021 * R - cell) * aa(0.040 * R - np.abs(hh - 1.17 * R)) * (np.abs(dx) < 1.52 * R) * (j > 0)
    body = deck * (1 - hole)
    # houses on both banks: flat blocks with stepped roofs
    roof = np.zeros(W, np.float32)
    for side in (-1, 1):
        u = 1.60 * R
        while u < 12 * R and u < 2.2 * W:
            wd = r_.uniform(0.34, 0.72) * R; ht = r_.uniform(1.75, 2.75) * R
            if side < 0 and j == 1 and u < 2.2 * R: ht *= 0.82
            xa, xb = (xv + side * u, xv + side * (u + wd)) if side > 0 else (xv - (u + wd), xv - u)
            ia, ib = int(max(0, xa)), int(min(W, xb))
            if ib > ia: roof[ia:ib] = np.maximum(roof[ia:ib], ht)
            # a chimney or a gable step
            if r_.random() < 0.7:
                cxa = xa + r_.uniform(0.15, 0.6) * wd; ca, cb = int(max(0, cxa)), int(min(W, cxa + 0.09 * R))
                if cb > ca: roof[ca:cb] = np.maximum(roof[ca:cb], ht + 0.16 * R)
            u += wd + (0.0 if r_.random() < 0.8 else 0.10 * R)
    house = aa(roof[None, :] - hh) * (roof[None, :] > 0)
    m = np.maximum(body, house) * (1 - arch) * (hh > -1)
    # lit windows
    win = np.zeros((W, W), np.float32)
    nwin = 46
    for _ in range(nwin):
        side = -1 if r_.random() < 0.5 else 1
        wx = xv + side * r_.uniform(1.68, 5.0) * R; wy = r_.uniform(1.36, 2.55) * R
        if 0 <= int(wx) < W and roof[int(wx)] > wy + 0.16 * R and (wx - 0.06 * R >= 0) and roof[int(max(0, wx - 0.05 * R))] > wy + 0.1 * R and roof[int(min(W - 1, wx + 0.05 * R))] > wy + 0.1 * R:
            win = np.maximum(win, aa(0.030 * R - np.abs(xx - wx)) * aa(0.046 * R - np.abs(hh - wy)) * r_.uniform(0.45, 1.0))
    return m, win, R
def lantern(cx, cy, s, red, emis):
    """paper lantern of height s hanging with its centre at (cx, cy)"""
    a_, b_ = 0.37 * s, 0.50 * s; Rr = int(b_ * 1.6) + 3
    X0, X1 = max(int(cx) - Rr, 0), min(int(cx) + Rr + 1, W); Y0, Y1 = max(int(cy) - Rr, 0), min(int(cy) + Rr + 1, W)
    if X1 <= X0 or Y1 <= Y0: return
    lx = xx[Y0:Y1, X0:X1] - cx; ly = yy[Y0:Y1, X0:X1] - cy
    q = np.sqrt((lx / a_) ** 2 + (ly / b_) ** 2)
    if s < 2.2:                                                    # too far to have a shape: a counted spark
        m = np.exp(-(lx * lx + ly * ly) / (2 * max(0.45, 0.33 * s) ** 2)) * min(1.0, 0.5 + 0.3 * s)
        col = INK['red'] if red else INK['gold']
        img[Y0:Y1, X0:X1] += (col - img[Y0:Y1, X0:X1]) * m[..., None]
    else:
        m = aa((1 - q) * min(a_, b_), 1.0)
        core = INK['cream'] if not red else hexc('#ffc9a0'); rim = INK['amber'] if not red else INK['red']
        tt = np.clip(q, 0, 1)[..., None] ** 1.6
        col = core * (1 - tt) + rim * tt
        ribs = 0.5 + 0.5 * np.cos(ly / b_ * np.pi * 5.0)            # paper ribs
        col = col * (1 - 0.10 * ribs[..., None] * (s > 9))
        blk = img[Y0:Y1, X0:X1]; blk += (col - blk) * m[..., None]
        capm = aa(0.16 * s - np.abs(lx)) * (aa(0.045 * s - np.abs(ly + 0.50 * s)) + aa(0.045 * s - np.abs(ly - 0.50 * s)))
        blk += (SHEET[0] - blk) * np.clip(capm, 0, 1)[..., None]
        tas = aa(0.022 * s + 0.35 - np.abs(lx), 0.9) * ((ly > 0.5 * s) & (ly < 0.78 * s))
        blk += ((INK['red'] if red else INK['amber']) * 0.9 - blk) * np.clip(tas, 0, 1)[..., None] * 0.9
    emis.append((cx, cy, s, red))

JMAX = 9
cache = {}
levels_drawn = {}
for j in range(JMAX, -1, -1):
    m, win, R = sheet_mask(j)
    col = SHEET[min(j, len(SHEET) - 1)]
    # cast shadow on everything behind
    off = max(1.0, 7 * S * EPS ** (0.6 * j)); sg = max(0.8, 6 * S * EPS ** (0.6 * j))
    shm = np.roll(np.roll(m, int(round(off)), 0), int(round(off * 0.7)), 1)
    shm = blur_big(shm, sg)
    img *= (1 - 0.42 * shm * (hh > 0))[..., None]
    grain = 1 + 0.05 * noise((W, W), 0.9 * S, 300 + j) + 0.04 * noise((W, W), 30 * S, 400 + j)
    img += (col[None, None, :] * grain[..., None] - img) * m[..., None]
    # the cut edge of the sheet catches light
    gy, gx = np.gradient(m); edge = np.clip(np.hypot(gx, gy) * 1.6, 0, 1) * (hh > 0)
    img += (INK['pale'] - img) * (edge * (0.20 if j > 0 else 0.26))[..., None]
    wcol = INK['gold'] * 0.95
    img += (wcol - img) * (win * m * (0.85 if j > 0 else 0.0))[..., None]
    # lanterns under this bridge
    idx = np.where(G == j)[0]; emis = []
    s = 0.046 * R
    order = idx[np.argsort(-U[idx])]                               # lowest first, so higher ones overlap them
    pos = {}
    for i in idx:
        h = (1 - EPS ** U[i]) * R; c = np.sqrt(R * R - h * h) * 0.90
        lo, hi = max(xv - c, x0 + 0.6 * s), min(xv + c, x1 - 0.6 * s)
        if j >= 1:
            lo, hi = xv - c, xv + c
        pos[i] = (rng.uniform(lo, hi), yw - h)
    # strings
    strs = np.zeros((W, W), np.float32)
    for i in idx:
        cx, cy = pos[i]; ytop = yw - np.sqrt(max(R * R - (cx - xv) ** 2, 0)); wst = max(0.5, 0.55 * S * EPS ** (0.5 * j))
        if s < 2.2: continue
        Xa, Xb = max(int(cx - wst - 2), 0), min(int(cx + wst + 3), W); Ya, Yb = max(int(ytop), 0), min(int(cy - 0.5 * s) + 1, W)
        if Yb > Ya: strs[Ya:Yb, Xa:Xb] = np.maximum(strs[Ya:Yb, Xa:Xb], aa(wst - np.abs(xx[Ya:Yb, Xa:Xb] - cx), 0.9))
    img += (INK['pale'] - img) * (strs * 0.34)[..., None]
    # glow first (additive, lights whatever is behind), then the bodies
    E = np.zeros((W, W), np.float32); Er = np.zeros((W, W), np.float32)
    for i in idx:
        cx, cy = pos[i]
        if 0 <= int(cy) < W and 0 <= int(cx) < W:
            (Er if (hand and i in hand) else E)[int(cy), int(cx)] += 1.0
    for Em, gc in ((E, INK['amber']), (Er, INK['red'])):
        if Em.sum() == 0: continue
        sg1 = max(0.7, 0.62 * s); sg2 = max(1.2, 3.2 * s)
        gl = blur_big(Em, sg1) * (2 * np.pi * sg1 ** 2) * 0.26 + blur_big(Em, sg2) * (2 * np.pi * sg2 ** 2) * 0.014
        gl = 0.50 * (1 - np.exp(-gl / 0.50))
        img += (gc - img) * gl[..., None] * (hh > 0)[..., None]
    for i in order:
        cx, cy = pos[i]; lantern(cx, cy, s, bool(hand and i in hand), emis)
    levels_drawn[j] = len(idx)
    cache[j] = pos

# ---------- a boat between the first and second bridge ----------
def cap(ax, ay, bx, by, r):
    pax = xx - ax; pay = yy - ay; bax = bx - ax; bay = by - ay; h_ = np.clip((pax * bax + pay * bay) / (bax * bax + bay * bay), 0, 1)
    return aa(r - np.hypot(pax - bax * h_, pay - bay * h_))
bz = EPS ** 0.62; bxc = xv + 0.36 * R0 * bz * 2.1; bl = 0.50 * R0 * bz; fh = 0.30 * R0 * bz
hull = aa(0.030 * R0 * bz - np.abs(hh - 0.030 * R0 * bz + 0.05 * R0 * bz * ((xx - bxc) / (0.5 * bl)) ** 2 * -1)) * aa(0.5 * bl - np.abs(xx - bxc))
hull = np.clip(hull, 0, 1) * (hh > 0)
boatc = SHEET[0] * 0.9
img += (boatc - img) * hull[..., None]
fx = bxc - 0.22 * bl; fy = yw - 0.045 * R0 * bz
fig = np.maximum.reduce([cap(fx - 0.03 * fh, fy, fx - 0.02 * fh, fy - 0.45 * fh, 0.05 * fh), cap(fx + 0.05 * fh, fy, fx + 0.03 * fh, fy - 0.45 * fh, 0.05 * fh),
                         cap(fx, fy - 0.40 * fh, fx + 0.02 * fh, fy - 0.80 * fh, 0.115 * fh),
                         aa(0.082 * fh - np.hypot(xx - fx - 0.03 * fh, yy - fy + 0.95 * fh)),
                         cap(fx + 0.30 * fh, fy + 0.02 * fh, fx - 0.16 * fh, fy - 1.55 * fh, 0.016 * fh),   # the pole
                         cap(fx + 0.02 * fh, fy - 0.72 * fh, fx + 0.14 * fh, fy - 0.52 * fh, 0.04 * fh)]) * (hh > 0)
img += (boatc - img) * fig[..., None]
img += (INK['pale'] - img) * (fig * aa(0.092 * fh - np.hypot(xx - fx - 0.03 * fh, yy - fy + 0.95 * fh)) * np.clip((fy - 0.96 * fh - yy) / (0.05 * fh), 0, 1) * 0.5)[..., None]

# ---------- water: the same picture upside down, on torn strips ----------
iw = int(round(yw)); nrow = W - iw
up = img[iw - nrow:iw][::-1].copy() if iw - nrow >= 0 else None
d = np.arange(nrow, dtype=np.float32)
row_n = noise((nrow,), 1.1 * S, 71) * 1.0 + noise((nrow,), 4 * S, 72) * 0.5
n2 = noise((nrow, W), 9 * S, 73)
amp = (1.0 + 0.030 * d / S) * S * 0.75
shift = amp[:, None] * (row_n[:, None] * 1.3 + 0.45 * n2)
xs = np.clip(np.arange(W)[None, :] + shift, 0, W - 1)
xi = np.floor(xs).astype(np.int32); xf = (xs - xi)[..., None]; xi2 = np.minimum(xi + 1, W - 1)
rows = np.arange(nrow)[:, None]
refl = up[rows, xi] * (1 - xf) + up[rows, xi2] * xf
fade = np.exp(-d / (0.50 * wh))[:, None, None]
wcol = INK['night'] * 0.75
refl = wcol + (refl - wcol) * (0.80 * fade + 0.06)
# ripple strips: pale dashes, denser and finer towards the horizon
rip = np.zeros((nrow, W), np.float32)
r2 = np.random.default_rng(77)
for _ in range(900):
    dd = (r2.random() ** 2.2) * (y1 - iw); z = 1.0 / (0.06 + dd / (0.5 * wh)); ln = r2.uniform(16, 60) * S / z ** 0.55 + 2 * S
    cxr = r2.uniform(x0, x1); th = max(0.45, 0.9 * S / z ** 0.35)
    Ya, Yb = int(dd - th - 2), int(dd + th + 3); Xa, Xb = int(cxr - ln - 2), int(cxr + ln + 3)
    Ya, Yb, Xa, Xb = max(Ya, 0), min(Yb, nrow), max(Xa, 0), min(Xb, W)
    if Yb <= Ya or Xb <= Xa: continue
    lx = (np.arange(Xa, Xb) - cxr) / ln; ly = (np.arange(Ya, Yb) - dd)
    rip[Ya:Yb, Xa:Xb] = np.maximum(rip[Ya:Yb, Xa:Xb], np.clip((th * np.clip(1 - lx ** 2, 0, 1)[None, :] - np.abs(ly)[:, None]) / 0.8 + 0.5, 0, 1) * r2.uniform(0.25, 0.8))
lum = refl.max(-1)
refl += (INK['pale'] - refl) * (rip * (0.10 + 0.55 * np.clip(lum * 1.3, 0, 1)))[..., None]
# the moon's road
road = np.exp(-(dx[iw:] / (mr * (0.9 + d[:, None] / (3.5 * mr) * 0.55))) ** 2) * np.exp(-d[:, None] / (0.42 * wh)) * (0.35 + 0.65 * (noise((nrow, W), 1.2 * S, 78) * np.array([1.0])[None] > 0.2))
road *= (0.5 + 0.5 * np.sign(np.sin(d[:, None] / (1.3 * S) + 3 * row_n[:, None]))) * 0.75 + 0.25
refl += (INK['cream'] - refl) * np.clip(road * 0.55, 0, 1)[..., None]
img[iw:] = refl
# a thin bright seam on the waterline
seam = np.clip(1 - np.abs(yy - yw) / (0.9 * S), 0, 1) * 0.22
img += (INK['pale'] - img) * seam[..., None]

# ---------- paper grain, mat, captions ----------
img *= (1 + 0.018 * noise((W, W), 0.8 * S, 9))[..., None]
inwin = (xx >= x0) & (xx < x1) & (yy >= y0) & (yy < y1)
mat = INK['mat'][None, None, :] * (1 + 0.018 * noise((W, W), 1.0 * S, 60)[..., None] + 0.012 * noise((W, W), 40 * S, 61)[..., None])
dx_in = np.minimum(np.minimum(xx - x0, x1 - xx), np.minimum(yy - y0, y1 - yy))
img *= (1 - 0.55 * np.exp(-np.maximum(np.minimum(xx - x0, yy - y0), 0) / (10 * S)) * inwin)[..., None]
out = np.where(inwin[..., None], img, mat)
bev = (dx_in < 0) & (dx_in > -3.5 * S)
out = np.where(bev[..., None], out * 0.5 + 0.5 * np.array([1, 1, 0.97], np.float32) * np.where((xx < x0) | (yy < y0), 0.80, 1.03)[..., None], out)
im = Image.fromarray((np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8)); dr = ImageDraw.Draw(im)
F = lambda nm, sz: ImageFont.truetype(f'/usr/share/fonts/truetype/liberation/LiberationSerif-{nm}.ttf', int(sz * S))
pc = tuple(int(v * 255) for v in INK['pencil']); rc = tuple(int(v * 255) for v in INK['red'])
dr.text((x0, y1 + int(20 * S)), 'No Last Bridge', font=F('Regular', 34), fill=pc)
dr.text((x0, y1 + int(62 * S)), 'Four lanterns are lit at random. How often can one of them hang higher than a third of all four heights together?',
        font=F('Italic', 15.2), fill=pc)
dr.text((x0, y1 + int(82 * S)), 'Never more than 40.07% of the time — and only on a canal like this one, where under every bridge the whole canal begins again.',
        font=F('Italic', 15.2), fill=pc)
vis = ', '.join(str(levels_drawn[j]) for j in range(0, 7))
cap2 = (f'X = ε^G(1−ε^U): bridge G (one further with probability 0.4743), height 1−ε^U under it; here ε = 0.4.  '
        f'{N} lanterns: {vis}, … by bridge')
dr.text((x0, y1 + int(110 * S)), cap2, font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf', int(10.6 * S)), fill=pc)
t2 = 'red: one hand of four; two hold more than a third'
tw = dr.textlength(t2, font=F('Italic', 12.2))
dr.text((x1 - tw, y1 + int(26 * S)), t2, font=F('Italic', 12.2), fill=rc)
im.save(OUT)
info = dict(N=N, eps=EPS, p=PSTAR, per_bridge={int(k): int(v) for k, v in sorted(levels_drawn.items())}, deeper=int((G > JMAX).sum()),
            hand=None if hand is None else dict(idx=hand, G=[int(G[i]) for i in hand], X=[float(X[i]) for i in hand],
                                                lions=[bool(3 * X[i] > X[hand].sum()) for i in hand]),
            lions_in_consecutive_hands=lions_all, hands=N // 4)
json.dump(info, open(OUT.replace('.png', '.json'), 'w'), indent=1)
print('saved', OUT, info)
