"""EIGHTEEN FENCES, EACH TWICE AS LONG — engraving.  The long view: the distances thin out.

Fence k (k = 5..22, nearest first) is the stretch of whole numbers 2^k .. 2^(k+1)-1.  A paling stands for
one number (fences 5-9) or for 2^(k-9) consecutive numbers (fences 10-22); its height is the share of
those numbers that are a distance between two posts of the Mian-Chowla sequence (10,000 posts).
Ink width is tone: sky and water are ruled lines that swell; reflections are the swelling of the water lines.
usage: fences.py W out.png"""
import sys, json, numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image, ImageDraw, ImageFont
W = int(sys.argv[1]); OUT = sys.argv[2]; S = W / 2048.0
A = np.array([int(l.split()[1]) for l in open('math_absent/b005282.txt') if l.strip() and l[0] != '#'], dtype=np.int64)
K0, K1 = 5, 22; XM = 1 << (K1 + 1)
ds = []
for i in range(1, len(A)):
    j0 = np.searchsorted(A, A[i] - XM + 1, 'left'); ds.append(A[i] - A[j0:i])
D = np.sort(np.concatenate(ds)); assert len(np.unique(D)) == len(D)
rows = []
for k in range(K0, K1 + 1):
    lo = 1 << k; nb = min(lo, 512); per = lo // nb
    h = np.histogram(D[(D >= lo) & (D < 2 * lo)], bins=nb, range=(lo, 2 * lo))[0] / per
    rows.append(h)
dens = [float(r.mean()) for r in rows]
print('densities', ' '.join('%.3f' % d for d in dens))
def noise(shape, sig, seed):
    r = np.random.default_rng(seed).standard_normal(shape).astype(np.float32); r = gaussian_filter(r, sig, mode='wrap'); return r / r.std()
yy, xx = np.mgrid[0:W, 0:W].astype(np.float32)
ink = np.zeros((W, W), np.float32)
FX0, FX1 = 250 * S, 1800 * S; FW = FX1 - FX0
YB = 1570 * S; P0 = 118 * S; RR = 0.915
nrow = K1 - K0 + 1
base = [YB]
for i in range(1, nrow): base.append(base[-1] - P0 * RR ** (i - 1))
pitch = [P0 * RR ** i for i in range(nrow)]
yh = base[-1] - pitch[-1] * 0.9                       # horizon
def line_family(U, gradU, width):
    """ink of the level lines U = integer, with per-pixel width (px)"""
    d = np.abs(U - np.round(U)) / np.maximum(gradU, 1e-6)
    return np.clip(width / 2 - d + 0.5, 0, 1)
# ---------- water: ruled horizontals whose pitch follows the fences (perspective), width = tone ----------
# U(y): 16 lines per fence interval
yk = np.array(base[::-1] + [YB + P0 / RR, YB + P0 / RR + P0 / RR ** 2, YB + 4 * P0]); uk = np.arange(len(yk)) * 16.0
yk2 = np.concatenate([[yh], yk]); uk2 = np.concatenate([[-12.0], uk])
U = np.interp(yy[:, 0], yk2, uk2); dU = np.gradient(U)
Uw = U[:, None] + 0.10 * noise((W, W), (3 * S, 40 * S), 3) * 0.0; gU = np.broadcast_to(dU[:, None], (W, W))
tone = np.full((W, W), 0.16, np.float32)               # base tone of the water
refl = np.zeros((W, W), np.float32)
# ---------- fences ----------
fence = np.zeros((W, W), np.float32); cut = np.zeros((W, W), np.float32)
rng = np.random.default_rng(5)
float_xy = None
for i in range(nrow - 1, -1, -1):
    k = K0 + i; h = rows[i]; nb = len(h); bw = FW / nb; H = 0.56 * pitch[i]; yb = base[i]
    pw = bw * (0.46 if nb <= 64 else 0.56 if nb <= 256 else 0.68)
    y0i, y1i = int(yb - H - 3), int(yb + H * 1.25 + 3)
    sl = (slice(max(y0i, 0), min(y1i, W)), slice(0, W)); X = xx[sl]; Y = yy[sl]
    b = np.clip(np.floor((X - FX0) / bw), 0, nb - 1).astype(np.int64)
    cx = FX0 + (b + 0.5) * bw; hh = h[b] * H
    inx = np.clip(pw / 2 - np.abs(X - cx) + 0.5, 0, 1) * (X >= FX0) * (X < FX1)
    top = yb - hh
    m = inx * np.clip(Y - top + 0.5, 0, 1) * np.clip(yb - Y + 0.5, 0, 1) * (hh > 0.02 * H)
    if pw > 9 * S:      # near fences: a round post = solid on the shade side, two cut lines on the lit side, a rounded head
        u = (X - cx) / pw
        hl = (np.clip(1 - np.abs(u + 0.24) * pw / (0.9 * S), 0, 1) + 0.6 * np.clip(1 - np.abs(u + 0.02) * pw / (0.7 * S), 0, 1)) * (Y > top + 0.5 * pw)
        cut[sl] = np.maximum(cut[sl], hl * m * 0.95)
        m = m * np.clip((np.clip(Y - top, 0, None) / (0.35 * pw)) ** 0.5 * 0.5 - np.abs(u) + 0.02, 0, 1 / pw) * pw   # head: taper at the top
    fence[sl] = np.maximum(fence[sl], np.clip(m, 0, 1))
    # reflection: mirror below the waterline, wobbling sideways, fading with depth
    wob = (1.2 + 0.05 * pitch[i]) * noise((W, W), (2.2 * S, 5 * S), 100 + i)[sl] * np.clip((Y - yb) / (0.3 * H + 1), 0, 1)
    b2 = np.clip(np.floor((X + wob - FX0) / bw), 0, nb - 1).astype(np.int64)
    cx2 = FX0 + (b2 + 0.5) * bw; hh2 = h[b2] * H
    r = np.clip(pw / 2 - np.abs(X + wob - cx2) + 0.5, 0, 1) * (X >= FX0) * (X < FX1) * (Y > yb) * np.clip((yb + 1.15 * hh2 - Y) / (0.25 * H + 1), 0, 1)
    refl[sl] = np.maximum(refl[sl], r * (0.55 + 0.45 * np.clip(pw / (6 * S), 0, 1)))
    if k == 5:
        bb = 33 - 32; float_xy = (FX0 + (bb + 0.5) * bw, yb, bw, H)
tone = tone + 0.50 * refl
# a moon glitter: water lines thin out under the moon
MXc = FX0 + 0.30 * FW
glit = np.exp(-((xx - MXc) / (60 * S + 0.10 * (yy - yh))) ** 2) * (yy > yh)
tone = tone * (1 - 0.80 * glit * (1 - refl))
brk = (noise((W, W), (0.8 * S, 14 * S), 7) > -1.15).astype(np.float32)          # little breaks in the ruled lines
pitch_px = 1 / np.maximum(gU, 1e-6)
water = line_family(np.broadcast_to(U[:, None], (W, W)), gU, np.clip(tone, 0, 0.92) * pitch_px) * (yy > yh) * np.where(refl > 0.3, 1, brk)
ink = np.maximum(ink, water)
# ---------- sky: ruled horizontals, heavier at the top, clear round the moon ----------
MR = 58 * S; MYc = yh - 165 * S
dm = np.hypot(xx - MXc, yy - MYc)
sky_t = 0.14 + 0.50 * np.clip((yh - yy) / (yh - 120 * S), 0, 1) ** 1.6
sky_t = sky_t * (1 - 0.85 * np.exp(-np.maximum(dm - MR, 0) / (130 * S)))
cloud = np.clip(noise((W, W), (9 * S, 90 * S), 11) * 0.9 - 0.55, 0, 1) * np.clip((yh - yy) / (300 * S), 0, 1) * np.clip((yy - 160 * S) / (200 * S), 0, 1)
sky_t = sky_t + 0.30 * cloud
SP = 7.0 * S
sky = line_family(yy / SP, np.full((W, W), 1 / SP, np.float32), np.clip(sky_t, 0.05, 0.9) * SP) * (yy < yh) * (yy > 120 * S) * (dm > MR + 1.5 * S)
sky *= (xx > 120 * S) * (xx < W - 120 * S)
ink = np.maximum(ink, sky)
ring = np.clip(1 - np.abs(dm - MR) / (1.0 * S), 0, 1); ink = np.maximum(ink, ring * 0.9)
# far shore: a low ridge, hatched vertically
prof = yh - (5 * S + 15 * S * np.clip(0.5 + 0.5 * noise((W,), 60 * S, 21), 0, None) ** 1.2) * np.clip(1 - np.exp(-((xx[0] - MXc) / (260 * S)) ** 2), 0, 1)
hill = (yy > prof[None, :]) & (yy <= yh)
hat = line_family(xx / (3.2 * S), np.full((W, W), 1 / (3.2 * S), np.float32), 1.7 * S)
ink = np.where(hill & (xx > 120 * S) & (xx < W - 120 * S), np.maximum(hat, 0), ink)
water *= 1
ink = np.where((yy > yh) & ((xx < 120 * S) | (xx > W - 120 * S)), 0, ink)
ink = np.where(yy > YB + 1.05 * P0, 0, ink)
# horizon line
ink = np.maximum(ink, np.clip(1 - np.abs(yy - yh) / (0.8 * S), 0, 1) * (xx > 120 * S) * (xx < W - 120 * S))
# fences on top (solid ink) with their cut lines
ink = np.where(fence > 0, np.maximum(ink * (1 - fence), fence), ink)
ink = ink * (1 - cut)
# plate border
bx0, bx1, by0, by1 = 120 * S, W - 120 * S, 120 * S, YB + 1.05 * P0
bd = np.minimum(np.minimum(xx - bx0, bx1 - xx), np.minimum(yy - by0, by1 - yy))
ink = np.maximum(ink, np.clip(1 - np.abs(bd) / (1.3 * S), 0, 1)); ink = np.maximum(ink, np.clip(1 - np.abs(bd + 9 * S) / (0.6 * S), 0, 1))
ink = np.where(bd < -9.6 * S, 0, ink)
# ---------- print: indigo intaglio on cream ----------
paper = np.array([0.957, 0.937, 0.880], np.float32); indigo = np.array([0.075, 0.095, 0.26], np.float32)
img = paper[None, None, :] * (1 + 0.014 * noise((W, W), 0.9 * S, 1)[..., None] + 0.012 * noise((W, W), 50 * S, 2)[..., None])
ink = np.clip(gaussian_filter(ink, 0.45 * S) * (1 + 0.10 * noise((W, W), 1.0 * S, 4)), 0, 1)
img = img * (1 - ink[..., None]) + indigo[None, None, :] * ink[..., None]
# labels knocked out of the water need a cleared halo: draw text on a small paper patch
im = Image.fromarray((np.clip(img, 0, 1) * 255 + .5).astype(np.uint8)); dr = ImageDraw.Draw(im)
F = lambda nm, sz: ImageFont.truetype(f'/usr/share/fonts/truetype/liberation/LiberationSerif-{nm}.ttf', max(6, int(sz * S)))
pc = (38, 44, 92); rc = (205, 52, 42); pap = tuple(int(v * 255) for v in paper)
def label(x, y, t, f, anchor, fill=pc):
    bb = dr.textbbox((x, y), t, font=f, anchor=anchor); p = int(4 * S)
    dr.rectangle([bb[0] - p, bb[1] - p, bb[2] + p, bb[3] + p], fill=pap); dr.text((x, y), t, font=f, fill=fill, anchor=anchor)
for i in range(nrow):
    k = K0 + i; sz = float(np.clip(9 + 0.105 * pitch[i] / S, 10, 23))
    t = f'{1 << k:,}' if True else ''
    label(FX0 - 14 * S, base[i] - 0.25 * pitch[i], t, F('Regular', sz), 'rm')
    pct = dens[i] * 100
    label(FX1 + 14 * S, base[i] - 0.25 * pitch[i], (f'{pct:.0f} %' if pct >= 10 else f'{pct:.1f} %'), F('Italic', sz), 'lm')
# the one red: a float riding in the gap at 33, with its line
fxp, fyb, fbw, fH = float_xy
r0 = 11 * S
dr.ellipse([fxp - r0, fyb - 2.0 * r0, fxp + r0, fyb + 0.1 * r0], fill=rc)
dr.line([(fxp, fyb - 2.0 * r0), (fxp, fyb - 4.3 * r0)], fill=rc, width=max(1, int(2 * S)))
for q, wd in ((2.4, 1.6), (3.9, 1.2)):
    dr.arc([fxp - q * r0 * 1.9, fyb - q * r0 * 0.34, fxp + q * r0 * 1.9, fyb + q * r0 * 0.34], 0, 360, fill=pc, width=max(1, int(wd * S)))
label(fxp, fyb + 0.36 * fH, '33', F('Bold', 21), 'mt', rc)
ty = by1 + 40 * S
dr.text((bx0, ty), 'Eighteen Fences, Each Twice as Long', font=F('Regular', 54), fill=pc)
dr.text((bx0, ty + 70 * S), 'The nearest fence is the numbers 32 to 63, the next 64 to 127, and so on to eight million. A paling stands only where its number', font=F('Italic', 26), fill=pc)
dr.text((bx0, ty + 103 * S), 'is the distance between some two posts; from the sixth fence on, a paling speaks for 2, 4, 8, … numbers and is as tall as their share.', font=F('Italic', 26), fill=pc)
dr.text((bx0, ty + 144 * S), f'Mian–Chowla sequence, 10,000 posts. Shares fall by about a fifth per fence: {dens[0]*100:.0f} % → {dens[-1]*100:.1f} %. Posts still to come would raise every fence by about 0.4 of a point.'
        '  Red float: 33, the first gap.', font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf', int(15.5 * S)), fill=pc)
im.save(OUT); json.dump(dict(dens=dens), open(OUT.replace('.png', '.json'), 'w')); print('saved', OUT)
