"""WHERE THE MOON GETS THROUGH — hero.  Cut-paper moonset over a lagoon of posts.

Mian-Chowla sequence A = 1, 2, 4, 8, 13, 21, 31, 45, ... (greedy Sidon set).  Every pair a<b in A is one
post: it stands b-a lanes to the right of the jetty (lane 0) at depth z = 1 + K*sqrt(a+b).  The moon sets
straight ahead, so each post throws its shadow down its own lane to the quay.  Sidon = no lane holds two
posts.  The quay is moonlit exactly at the differences that do not occur; the first is 33.
usage: moon.py W out.png [DR]"""
import sys, json, numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image, ImageDraw, ImageFont
W = int(sys.argv[1]); OUT = sys.argv[2]; DR = float(sys.argv[3]) if len(sys.argv) > 3 else 136.5
S = W / 1024.0; rng = np.random.default_rng(14)
A = np.array([int(l.split()[1]) for l in open('math_absent/b005282.txt') if l.strip() and l[0] != '#'], dtype=np.int64)
KZ, GAM = 0.14, 0.5
MM = 1 << 17
ZP = np.zeros(MM + 2, np.float32); SUM = np.zeros(MM + 2, np.int64)
for i in range(1, len(A)):
    j0 = np.searchsorted(A, A[i] - MM, 'left'); d = A[i] - A[j0:i]; s = A[i] + A[j0:i]
    ZP[d] = 1 + KZ * s.astype(np.float64) ** GAM; SUM[d] = s
ZP[0] = 0  # lane 0 is the jetty, drawn separately

# ---------- geometry ----------
M = int(0.085 * W); MB = int(0.150 * W)
x0, x1, y0, y1 = M, W - M, M, W - MB; ww = x1 - x0; wh = y1 - y0
DL = -4.5; DV = 33.0                       # lanes at the quay edge: DL..DR ; vanishing point above lane DV
S1 = ww / (DR - DL)                        # px per lane at z = 1
yh = y0 + 0.335 * wh; yq = y0 + 0.875 * wh
xv = x0 + (DV - DL) * S1
def scr(d, z): return xv + (d - DV) * S1 / z, yh + (yq - yh) / z
yy, xx = np.mgrid[0:W, 0:W].astype(np.float32)
def noise(shape, sig, seed):
    r = np.random.default_rng(seed).standard_normal(shape).astype(np.float32); r = gaussian_filter(r, sig, mode='wrap'); return r / r.std()
def hexc(s): return np.array([int(s[i:i + 2], 16) for i in (1, 3, 5)], np.float32) / 255
INK = dict(night=hexc('#0d1230'), deep=hexc('#151c46'), ind=hexc('#232d66'), dusk=hexc('#4a4a86'), mauve=hexc('#8a6f9c'),
           rose=hexc('#d79a9a'), peach=hexc('#f0c3a0'), cream=hexc('#f6ecd2'), red=hexc('#d8362b'), mat=hexc('#efe6d0'),
           pencil=hexc('#4b4a55'), slate=hexc('#6f7aa8'), pale=hexc('#c9c6d8'), stone=hexc('#b7b0bd'))
img = np.zeros((W, W, 3), np.float32)

# ---------- sky: torn bands, darkest on top, warm at the horizon ----------
t = (yy - y0) / (yh - y0)
img[:] = INK['night']
bands = [(0.24, 'deep'), (0.46, 'ind'), (0.63, 'dusk'), (0.77, 'mauve'), (0.875, 'rose'), (0.945, 'peach')]
for i, (lv, nm) in enumerate(bands):
    edge = lv + 0.020 * noise((W,), 40 * S, 100 + i)[None, :] + 0.004 * noise((W,), 4 * S, 200 + i)[None, :] \
        - 0.10 * np.exp(-((xx - xv) / (0.30 * ww)) ** 2) * (0.4 + 0.12 * i)        # bands lift over the moon
    a = np.clip((t - edge) * (yh - y0) / 1.2 + 0.5, 0, 1)
    sh = np.clip(1 - np.abs((t - edge) * (yh - y0) - 3 * S) / (5 * S), 0, 1) * 0.18 * a
    lip = np.clip(1 - np.abs((t - edge) * (yh - y0) + 0.2 * S) / (1.3 * S), 0, 1) * 0.35
    img = img * (1 - a[..., None]) + INK[nm] * a[..., None]
    img = img * (1 - sh[..., None]); img = img + (INK['cream'] - img) * lip[..., None] * 0.5
# stars (decorative, upper sky only)
ns = 260; sx = rng.uniform(x0, x1, ns); sy = y0 + (yh - y0) * rng.uniform(0, 1, ns) ** 1.5 * 0.55
star = np.zeros((W, W), np.float32)
for a_, b_, r_ in zip(sx, sy, rng.uniform(0.5, 1.15, ns) * S):
    ia, ib = int(a_), int(b_); R = int(3 * r_) + 2
    sl = (slice(ib - R, ib + R + 1), slice(ia - R, ia + R + 1))
    star[sl] += np.exp(-((xx[sl] - a_) ** 2 + (yy[sl] - b_) ** 2) / (2 * r_ * r_)) * rng.uniform(0.35, 1.0)
img = img + (INK['cream'] - img) * np.clip(star, 0, 1)[..., None] * 0.85
# moon: large, low, straight ahead
mr = 0.052 * ww; mx, my = xv, yh - 1.55 * mr
dm = np.hypot(xx - mx, yy - my)
halo = np.exp(-np.maximum(dm - mr, 0) / (0.09 * ww)) * 0.22; img = img + (INK['cream'] - img) * (halo * (dm > mr))[..., None]
img *= (1 - 0.30 * np.clip(1 - (np.hypot(xx - mx - 5 * S, yy - my - 7 * S) - mr) / (9 * S), 0, 1) * (dm > mr))[..., None]
am = np.clip((mr - dm) / 1.2 + 0.5, 0, 1)
mcol = INK['cream'][None, None, :] * (0.985 + 0.02 * noise((W, W), 7 * S, 5)[..., None])
img = img + (mcol - img) * am[..., None]
# two cloud strips (paper), one crossing the moon's lower limb
for i, (cy, cxc, clen, cth, nm) in enumerate([(my + 0.52 * mr, xv + 0.05 * ww, 0.30 * ww, 5.5 * S, 'dusk'), (my - 1.9 * mr, xv - 0.33 * ww, 0.22 * ww, 4.0 * S, 'ind'),
                                               (my - 0.2 * mr, xv + 0.45 * ww, 0.16 * ww, 3.6 * S, 'mauve')]):
    prof = cth * np.clip(1 - ((xx[0] - cxc) / clen) ** 2, 0, 1) ** 0.6 * (1 + 0.35 * noise((W,), 14 * S, 300 + i))
    cyl = cy + 2.0 * S * noise((W,), 50 * S, 310 + i)
    a = np.clip((prof[None, :] - np.abs(yy - cyl[None, :])) / 1.2 + 0.5, 0, 1) * (prof[None, :] > 0.3)
    sh = np.clip((prof[None, :] - np.abs(yy - 4 * S - cyl[None, :])) / (3 * S) + 0.5, 0, 1) * (prof[None, :] > 0.3) * 0.22
    img = img * (1 - sh[..., None]); img = img + (INK[nm] - img) * a[..., None]

# ---------- the water and the quay: one ground plane ----------
below = yy > yh
z = np.where(below, (yq - yh) / np.maximum(yy - yh, 1e-3), 1e6).astype(np.float32)
dzdy = z / np.maximum(yy - yh, 1e-3)                    # |dz/dy| per pixel
K = 6; shade = np.zeros((W, W), np.float32)
for k in range(K):
    off = (k + 0.5) / K - 0.5
    d = DV + (xx + off - xv) * z / S1
    m = np.floor(np.abs(d) + 0.5).astype(np.int64)
    zp = np.where(m <= MM, ZP[np.clip(m, 0, MM)], 0)
    shade += np.clip((zp - z) / np.maximum(dzdy, 1e-6) + 0.5, 0, 1)
shade /= K; shade *= below
dlat = DV + (xx - xv) * z / S1
jet = (np.abs(dlat) < 0.5) & below                       # lane 0: the jetty (every post paired with itself)
haze = np.exp(-(np.maximum(z, 1) - 1) / 8.0)            # 1 near, 0 far
glit = np.exp(-((xx - xv) / (0.16 * ww + 0.9 * (yy - yh))) ** 2)
near = np.clip((yy - yh) / (yq - yh), 0, 1.3)
nn = np.clip(1 - near, 0, 1)[..., None] ** 1.6
lit = INK['peach'][None, None, :] * nn + INK['pale'][None, None, :] * (1 - nn)
lit = lit + (INK['cream'] - lit) * (0.55 * glit * (1 - 0.45 * near))[..., None]
dark = INK['ind'][None, None, :] * (1 - near[..., None]) + INK['deep'][None, None, :] * near[..., None]
dark = dark + (INK['mauve'] - dark) * ((1 - haze) * 0.80)[..., None]         # far shadows dissolve in haze
ground = lit + (dark - lit) * shade[..., None]
# shadow strips are laid paper: a faint darker rim at the foot of every strip, a paler one at lit edges
gx = np.abs(np.gradient(shade, axis=1)); ground *= (1 - 0.10 * np.clip(gx * 2, 0, 1) * haze)[..., None]
# ripples (short horizontal torn nicks) on the water only
water = below & (yy < yq)
rip = noise((W, W), (0.7 * S, 7 * S), 21) * np.clip(near, 0.15, 1)
ground *= (1 + 0.035 * rip * water)[..., None]
img = np.where(below[..., None], ground, img)

# far shore: thin paper hills at the horizon, with a gap under the moon
for i, (amp, nm, sd, lo_, hi_) in enumerate([(0.020, 'dusk', 31, 0.50, 1.0), (0.014, 'ind', 32, 0.0, 0.26), (0.011, 'dusk', 33, 0.62, 1.0)]):
    xr = (xx[0] - x0) / ww
    env = np.clip((xr - lo_) / 0.07, 0, 1) * np.clip((hi_ - xr) / 0.05 + 1, 0, 1)
    prof = yh + 2 * S - wh * amp * env * np.clip(0.55 + 0.5 * noise((W,), (60 - 12 * i) * S, sd), 0.05, None) ** 1.3
    a = np.clip((yy - prof[None, :]) / 1.2 + 0.5, 0, 1) * np.clip((yh + 2.5 * S - yy) / 1.2 + 0.5, 0, 1) * np.clip(env[None, :] * 6, 0, 1)
    img = img + (INK[nm] - img) * a[..., None]
    lip = np.clip(1 - np.abs(yy - prof[None, :] - 0.8 * S) / (1.0 * S), 0, 1) * 0.25 * np.clip(env[None, :] * 6, 0, 1) * (yy < yh + 2 * S)
    img = img + (INK['cream'] - img) * lip[..., None]

# ---------- quay: stone seen from above (z < 1) ----------
quay = yy >= yq
stone_l = INK['stone'] * 1.04; stone_d = hexc('#262b55')
qcol = stone_l[None, None, :] + (stone_d - stone_l)[None, None, :] * shade[..., None]
# courses of paving (lines of equal z) and joints along the lanes every few lanes
zc = np.log(np.maximum(z, 1e-3)) / np.log(1.085)
course = np.clip(1 - np.abs(zc - np.round(zc)) * (np.log(1.085) * z / np.maximum(dzdy, 1e-6)) / (0.9 * S), 0, 1)
row = np.round(zc).astype(np.int64)
dj = (dlat + 3.7 * (row % 2) + 0.5) / 7.0
joint = np.clip(1 - np.abs(dj - np.round(dj)) * 7.0 * S1 / np.maximum(z, 1e-3) / (0.9 * S), 0, 1)
qcol = qcol * (1 - 0.22 * np.maximum(course, joint))[..., None]
qcol = qcol * (1 + 0.05 * noise((W, W), 1.4 * S, 51)[..., None] + 0.04 * noise((W, W), 22 * S, 52)[..., None])
img = np.where(quay[..., None], qcol, img)
# coping: a pale lip and the dark face of the wall just above it
face = (yy >= yq - 5 * S) & (yy < yq)
img = np.where(face[..., None], (INK['night'] * 0.9)[None, None, :] + (INK['ind'] * 0.9 - INK['night'] * 0.9)[None, None, :] * (1 - shade[..., None]), img)
lipq = np.clip(1 - np.abs(yy - yq - 1.2 * S) / (1.3 * S), 0, 1); img = img + (INK['cream'] - img) * (lipq * (0.25 + 0.6 * (1 - shade)))[..., None]

# ---------- jetty (lane 0) ----------
jcol = INK['slate'] * 0.80 + (INK['mauve'] - INK['slate'] * 0.80) * np.clip(1 - haze, 0, 1)[..., None] * 0.8
zj = np.log(np.maximum(z, 1e-3)) / np.log(1.03)
plank = np.clip(1 - np.abs(zj - np.round(zj)) * (np.log(1.03) * z / np.maximum(dzdy, 1e-6)) / (0.6 * S), 0, 1)
jcol = jcol * (1 - 0.3 * plank[..., None])
ja = np.clip((0.5 - np.abs(dlat)) * S1 / np.maximum(z, 1e-3) + 0.5, 0, 1) * below * (yy < yq)
img = img + (jcol - img) * ja[..., None]
edge_l = np.clip(1 - np.abs((dlat + 0.5) * S1 / np.maximum(z, 1e-3)) / (0.8 * S), 0, 1) * below * (yy < yq)
img = img + (INK['cream'] - img) * (edge_l * 0.35 * haze)[..., None]

# ---------- posts: one per pair, far to near ----------
HP = 8.5                                        # post height in lanes
ds = np.nonzero(ZP[:MM] > 0)[0]
cand = np.concatenate([ds, -ds]); zc_ = np.concatenate([ZP[ds], ZP[ds]])
px, py = scr(cand.astype(np.float64), zc_.astype(np.float64))
wpx = S1 / zc_
ok = (px > x0 - 40 * S) & (px < x1 + 40 * S) & (py < yq + 1) & (zc_ < 400)
cand, zc_, px, py, wpx = cand[ok], zc_[ok], px[ok], py[ok], wpx[ok]
order = np.argsort(-zc_); nposts = 0
for o in order:
    zc0 = float(zc_[o]); w = float(wpx[o]); hgt = HP * S1 / zc0 * (0.86 + 0.28 * ((int(cand[o]) * 2654435761) % 1000) / 1000.0)
    xa, xb = px[o] - w / 2, px[o] + w / 2; yb = float(py[o]); ya = yb - hgt
    if xb < x0 or xa > x1: continue
    nposts += 1
    X0, X1 = int(np.floor(xa)) - 1, int(np.ceil(xb)) + 2; Y0, Y1 = int(np.floor(ya)) - 3, int(np.ceil(yb)) + 2
    X0 = max(X0, 0); X1 = min(X1, W); Y0 = max(Y0, 0); Y1 = min(Y1, W)
    xs = np.arange(X0, X1); ys = np.arange(Y0, Y1)
    cx = np.clip(np.minimum(xs + 1, xb) - np.maximum(xs, xa), 0, 1)
    if w < 1: cx = cx                                             # sub-pixel posts keep their true coverage
    cyv = np.clip(np.minimum(ys + 1, yb) - np.maximum(ys, ya), 0, 1)
    a = (cyv[:, None] * cx[None, :]).astype(np.float32)
    hz = float(np.exp(-(zc0 - 1) / 22.0))
    col = INK['night'] * 0.85 * hz + INK['dusk'] * (1 - hz)
    blk = img[Y0:Y1, X0:X1]
    # the moon side of a near post catches a thin pale edge (towards xv)
    if w > 2.5 * S:
        side = 1 if xv > px[o] else -1
        ex = xb - 0.9 * S if side > 0 else xa
        rim = np.clip(np.minimum(xs + 1, ex + 0.9 * S) - np.maximum(xs, ex), 0, 1)[None, :] * cyv[:, None]
        nearw = float(np.clip((w - 2.5 * S) / (5 * S), 0, 1))
        colm = np.broadcast_to(col, blk.shape).copy(); colm = colm + (INK['pale'] - colm) * (rim * 0.55 * nearw)[..., None]
        # a pale cap
        capm = (np.clip(np.minimum(ys + 1, ya + 0.16 * w + 1.2 * S) - np.maximum(ys, ya), 0, 1)[:, None] * cx[None, :])
        colm = colm + (INK['slate'] - colm) * (capm * 0.55 * nearw)[..., None]
        blk[:] = blk * (1 - a[..., None]) + colm * a[..., None]
    else:
        blk[:] = blk * (1 - a[..., None]) + col * a[..., None]

# ---------- the red figure: someone standing on the quay where lane 33 comes ashore ----------
zf = 0.905; fx, fy = scr(33.0, zf); fh = 0.062 * wh
def cap(ax, ay, bx, by, r):
    pax = xx - ax; pay = yy - ay; bax = bx - ax; bay = by - ay; hh = np.clip((pax * bax + pay * bay) / (bax * bax + bay * bay), 0, 1)
    return np.clip((r - np.hypot(pax - bax * hh, pay - bay * hh)) / 1.2 + 0.5, 0, 1)
# shadow of the figure, running towards us along the lane (ray from the vanishing point)
ux, uy = fx - xv, fy - yh; un = np.hypot(ux, uy); ux, uy = ux / un, uy / un
shf = cap(fx, fy, fx + ux * 3.0 * fh, fy + uy * 3.0 * fh, 0.105 * fh) * quay
img = img + (stone_d - img) * (shf * 0.92)[..., None]
def blob(mask, col):
    global img
    img = img + (col - img) * np.clip(mask, 0, 1)[..., None]
nightc = INK['night'] * 0.8
blob(np.maximum(cap(fx - 0.06 * fh, fy, fx - 0.05 * fh, fy - 0.42 * fh, 0.050 * fh), cap(fx + 0.07 * fh, fy, fx + 0.05 * fh, fy - 0.42 * fh, 0.050 * fh)), nightc)   # legs
coat = np.maximum(cap(fx, fy - 0.36 * fh, fx, fy - 0.78 * fh, 0.135 * fh), cap(fx, fy - 0.30 * fh, fx, fy - 0.36 * fh, 0.165 * fh))
blob(coat, INK['red'])
blob(coat * np.clip((xx - fx - 0.02 * fh) / (0.05 * fh), 0, 1), INK['red'] * 0.72)                 # the side away from... the moon is behind: front in shade
blob(np.clip((0.085 * fh - np.hypot(xx - fx, yy - fy + 0.925 * fh)) / 1.2 + 0.5, 0, 1), nightc)   # head
rimf = np.clip((0.092 * fh - np.hypot(xx - fx, yy - fy + 0.925 * fh)) / 1.2 + 0.5, 0, 1) * np.clip((fy - 0.93 * fh - yy) / (0.05 * fh), 0, 1)
blob(rimf * 0.7, INK['cream'])                                                                  # moonlit crown of the head

# ---------- numbers painted on the quay: the lanes where the moon comes ashore ----------
im_t = Image.new('L', (W, W), 0); dt = ImageDraw.Draw(im_t)
fnt = ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf', max(6, int(4.6 * S)))
absent = [int(d) for d in range(1, int(DR) + 1) if ZP[d] == 0]
for d_ in absent:
    tx, ty = scr(float(d_), 0.955)
    if d_ == 33: continue
    dt.text((tx, ty), str(d_), font=fnt, fill=255, anchor='mm')
tm = np.asarray(im_t, np.float32) / 255
img = img + (INK['night'] - img) * (tm * 0.62)[..., None]
im_t = Image.new('L', (W, W), 0); dt = ImageDraw.Draw(im_t)
tx, ty = scr(33.0, 0.972)
dt.text((tx + 0.19 * fh + 5 * S, ty - 2 * S), '33', font=ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf', int(8.5 * S)), fill=255, anchor='lm')
img = img + (INK['red'] - img) * (np.asarray(im_t, np.float32) / 255 * 0.95)[..., None]

# ---------- paper grain, mat, captions ----------
img *= (1 + 0.020 * noise((W, W), 0.8 * S, 9))[..., None]
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
dr.text((x0, y1 + int(20 * S)), 'Where the Moon Gets Through', font=F('Regular', 34), fill=pc)
dr.text((x0, y1 + int(62 * S)), 'Drive posts into a lagoon, always at the nearest spot that keeps every pair of posts a different distance apart. Give each pair',
        font=F('Italic', 15.2), fill=pc)
dr.text((x0, y1 + int(82 * S)), 'a marker as far right of the jetty as the two are apart. No marker stands in another’s shadow; the moon comes ashore where none stands.',
        font=F('Italic', 15.2), fill=pc)
n_abs = len(absent)
cap2 = (f'Mian\u2013Chowla sequence 1, 2, 4, 8, 13, 21, 31, 45, \u2026 (10,000 terms).  Pair a<b: lane b\u2212a, depth 1+\u221a(a+b)/7.  '
        f'{nposts:,} markers; {n_abs} of lanes 1\u2013{int(DR)} moonlit.')
dr.text((x0, y1 + int(110 * S)), cap2, font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf', int(10.6 * S)), fill=pc)
t2 = 'red: someone waiting at 33'
tw = dr.textlength(t2, font=F('Italic', 12.2))
dr.text((x1 - tw, y1 + int(26 * S)), t2, font=F('Italic', 12.2), fill=rc)
im.save(OUT)
json.dump(dict(posts=nposts, absent=absent), open(OUT.replace('.png', '.json'), 'w'))
print('saved', OUT, 'posts', nposts, 'absent', absent)
