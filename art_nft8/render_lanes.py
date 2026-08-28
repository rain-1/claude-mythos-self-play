#!/usr/bin/env python3
"""Piece 3, 2560^2 — 'THE SIX FERTILE LANES' (MO 514700)

a -> a + digitsum(a). Since ds(a) ≡ a (mod 9), the lane a mod 9 DOUBLES
each step: three castes, forever — the fixed point {0}, the 2-cycle
{3,6}, and the 6-cycle {1,2,4,8,7,5}. Only the 6-cycle can carry primes.
The river from 1 walked 2,081,679,312 steps to 10^11 and met 136,932,755
primes — drawn here as gold weather on six lanes ordered by the doubling
cycle; the sterile castes lie below, cold and unlit. The lanes trade
their luck decade by decade (lane 7: richest at 10^5, poorest at 10^10),
and the drift is EXACTLY the river's own (mod 9 × mod 10) occupancy
drift: the bottom register shows observed prime shares (gold) against
the parity•5 occupancy prediction (cyan rings) — four-decimal agreement,
while the 11-decade aggregate inverts the ranking (Simpson's paradox).
"""
import numpy as np, math
from collections import defaultdict

FINAL = 2560; SS = 2; S = FINAL*SS
rs = FINAL/1024.0
acc = np.zeros((S, S, 3), np.float32)

NB = 2750
XLO, XHI = 0.4, 11.0
mx = 0.055*S
X0, X1 = mx, S-mx
def px_of_bin(b):  # bin center -> canvas x
    lx = (b+0.5)/NB*11.0
    return X0 + (X1-X0)*(lx-XLO)/(XHI-XLO)
def px_of_logn(lx):
    return X0 + (X1-X0)*(lx-XLO)/(XHI-XLO)

# lane band layout (top to bottom)
order = [1,2,4,8,7,5, 3,6, 0]
ytop = 0.115*S
BH  = 0.0555*S      # band height
GAP = 0.0135*S
BIGGAP = 0.040*S
lane_y = {}
y = ytop
for i, l in enumerate(order):
    if i == 6: y += BIGGAP
    if i == 8: y += BIGGAP
    lane_y[l] = y
    y += BH + GAP
print("bands end at", y/S)

# ---------- data ----------
occ = np.zeros((3, NB, 9)); cop = np.zeros((3, NB, 9))
for line in open('occup_fine.txt'):
    r, b, m, o, c = line.split()
    occ[int(r), int(b), int(m)] = float(o)
    cop[int(r), int(b), int(m)] = float(c)
pb = np.zeros((NB, 9))
for line in open('prime_bins.txt'):
    k, v = line.split()
    b, l = k.split('_')
    pb[int(b), int(l)] = float(v)

FERT = [1,2,4,8,7,5]
from scipy.ndimage import gaussian_filter1d
pbs = gaussian_filter1d(pb, 14, axis=0)
tot_by_bin = pbs[:, FERT].sum(1)                      # primes per bin (smoothed)
share = np.zeros((NB, 9))
nzb = tot_by_bin > 1.5
for l in FERT:
    share[nzb, l] = pbs[nzb, l]/tot_by_bin[nzb]

# ---------- draw lane bands ----------
xs = px_of_bin(np.arange(NB))
COL_BASE = np.array([0.30, 0.42, 0.62], np.float32)
COL_GOLD = np.array([1.00, 0.76, 0.30], np.float32)
COL_COLD = np.array([0.28, 0.40, 0.60], np.float32)

yy = np.arange(S, dtype=np.float32)
xcol = np.zeros(S, np.float32)
binw = (X1-X0)/NB
xi = np.clip(((np.arange(S)-X0)/binw).astype(int), 0, NB-1)
inplot = (np.arange(S) >= X0) & (np.arange(S) <= X1)

def band_profile(yc):
    prof = np.exp(-0.5*((yy-yc)/(0.36*BH))**4)        # soft-edged flat band
    return prof

for l in order:
    yc = lane_y[l] + BH/2
    prof = band_profile(yc)                           # (S,)
    if l in FERT:
        occ_l = np.maximum.accumulate(gaussian_filter1d(occ[0, :, l], 6))
        base = np.where(occ_l[xi] > 0, 1.0, 0.0)*inplot
        # occupancy fog (constant along fertile river: honest dim silver)
        A = 0.16*base
        # gold: relative fertility (share*6), windowed 0.75..1.25 -> 0..1
        rel = np.clip((share[xi, l]*6 - 0.72)/0.56, 0, 1.35)*base
        # absolute prime-density falloff (keeps late decades honest): ~1/ln n
        lx = (xi+0.5)/NB*11.0
        dens = 1.0/np.maximum(lx, 1.0)**0.18
        ramp = np.clip((lx-4.4)/1.8, 0, 1)
        ramp = ramp*ramp*(3-2*ramp)
        G = 0.55*rel*dens*ramp
        col = (A[:, None]*COL_BASE[None, :] + G[:, None]*COL_GOLD[None, :])
    else:
        r = 1 if l in (3, 6) else 2
        occ_l = np.maximum.accumulate(gaussian_filter1d(occ[r, :, l], 6))
        on = np.where(occ_l[xi] > 0, 1.0, 0.0)*inplot
        col = 0.13*on[:, None]*COL_COLD[None, :]
    acc += prof[:, None, None]*col[None, :, :]

# ---------- early primes as stars ----------
COL_STAR = np.array([1.0, 0.9, 0.62], np.float32)
for line in open('early_primes.txt'):
    p = line.split()
    n = int(p[1]); l = int(p[3].split('=')[1])
    if n < 2: continue
    lx = math.log10(n)
    if lx < XLO: lx = XLO
    if lx > 5.3: continue
    x0 = px_of_logn(lx); y0 = lane_y[l] + BH/2
    rad = (3.4 - 2.3*min(lx/5.0, 1.0))*rs
    b = int(5*rad)
    xg = np.arange(max(0, int(x0)-b), min(S, int(x0)+b+1))
    yg = np.arange(max(0, int(y0)-b), min(S, int(y0)+b+1))
    if xg.size == 0 or yg.size == 0: continue
    dx = xg[None, :]-x0; dyy = (yg[:, None]-y0)
    amp_s = 0.75 - 0.45*min(lx/5.0, 1.0)
    gau = np.exp(-(dx*dx+dyy*dyy)/(2*rad*rad))*amp_s
    acc[yg[0]:yg[-1]+1, xg[0]:xg[-1]+1, :] += gau[..., None]*COL_STAR

# ---------- doubling-cycle emblem (top right) ----------
cx0, cy0, R = 0.905*S, 0.062*S, 0.030*S
ang = {l: -math.pi/2 + i*math.pi/3 for i, l in enumerate([1,2,4,8,7,5])}
for i, l in enumerate([1,2,4,8,7,5]):
    a0 = ang[l]; a1 = ang[[1,2,4,8,7,5][(i+1) % 6]]
    tt = np.linspace(0, 1, 240)
    da = (a1-a0) % (2*math.pi)
    aa = a0 + da*tt
    xs_ = cx0 + R*np.cos(aa); ys_ = cy0 + R*np.sin(aa)
    xi_ = xs_.astype(int); yi_ = ys_.astype(int)
    ok = (xi_ >= 0) & (xi_ < S) & (yi_ >= 0) & (yi_ < S)
    acc[yi_[ok], xi_[ok], :] += 0.35*np.array([0.85, 0.9, 1.0])*rs*0.35
for l in [1,2,4,8,7,5]:
    x0 = cx0 + R*math.cos(ang[l]); y0 = cy0 + R*math.sin(ang[l])
    b = int(6*rs)
    xg = np.arange(max(0, int(x0)-b), min(S, int(x0)+b+1))
    yg = np.arange(max(0, int(y0)-b), min(S, int(y0)+b+1))
    dx = xg[None, :]-x0; dyy = yg[:, None]-y0
    gau = np.exp(-(dx*dx+dyy*dyy)/(2*(1.7*rs)**2))*0.85
    acc[yg[0]:yg[-1]+1, xg[0]:xg[-1]+1, :] += gau[..., None]*COL_GOLD

# ---------- bottom register: obs vs predicted shares by decade ----------
# recompute from pb + cop (river 0)
yr0, yr1 = 0.845*S, 0.968*S
xr0, xr1 = X0, X1
decs = [5, 6, 7, 8, 9, 10]
obs = {}; pred = {}
lxall = (np.arange(NB)+0.5)/NB*11.0
for d in decs:
    sel = (lxall >= d) & (lxall < d+1)
    tp = pb[sel][:, FERT].sum()
    tc = cop[0][sel][:, FERT].sum()
    for l in FERT:
        obs[(d, l)] = pb[sel][:, l].sum()/tp
        pred[(d, l)] = cop[0][sel][:, l].sum()/tc
sh0, sh1 = 0.135, 0.215
def ry(v): return yr1 - (yr1-yr0)*np.clip((v-sh0)/(sh1-sh0), 0, 1)
def rx(d): return xr0 + (xr1-xr0)*(d-4.6)/(10.4-4.6+0.4)
LANEC = {1: (0.85, 0.80, 0.75), 2: (1.0, 0.72, 0.25), 4: (0.95, 0.85, 0.45),
         8: (0.80, 0.72, 0.55), 7: (0.55, 0.70, 0.95), 5: (0.95, 0.62, 0.45)}
for l in FERT:
    pts = [(rx(d), ry(obs[(d, l)])) for d in decs]
    colL = np.array(LANEC[l], np.float32)
    for i in range(len(pts)-1):
        x0c, y0c = pts[i]; x1c, y1c = pts[i+1]
        n = int(max(abs(x1c-x0c), abs(y1c-y0c)))+2
        tt = np.linspace(0, 1, n)
        xi_ = (x0c+(x1c-x0c)*tt).astype(int); yi_ = (y0c+(y1c-y0c)*tt).astype(int)
        ok = (xi_ >= 0) & (xi_ < S) & (yi_ >= 0) & (yi_ < S)
        for off in range(-int(rs*0.6), int(rs*0.6)+1):
            acc[np.clip(yi_[ok]+off, 0, S-1), xi_[ok], :] += 0.22*colL[None, :]
    for d in decs:                      # observed dot (filled)
        x0c, y0c = rx(d), ry(obs[(d, l)])
        b = int(6*rs)
        xg = np.arange(max(0, int(x0c)-b), min(S, int(x0c)+b+1))
        yg = np.arange(max(0, int(y0c)-b), min(S, int(y0c)+b+1))
        dx = xg[None, :]-x0c; dyy = yg[:, None]-y0c
        gau = np.exp(-(dx*dx+dyy*dyy)/(2*(1.6*rs)**2))*0.9
        acc[yg[0]:yg[-1]+1, xg[0]:xg[-1]+1, :] += gau[..., None]*colL
    for d in decs:                      # predicted ring (cyan)
        x0c, y0c = rx(d), ry(pred[(d, l)])
        rr = 3.4*rs
        th = np.linspace(0, 2*math.pi, 200)
        xi_ = (x0c+rr*np.cos(th)).astype(int); yi_ = (y0c+rr*np.sin(th)).astype(int)
        ok = (xi_ >= 0) & (xi_ < S) & (yi_ >= 0) & (yi_ < S)
        for off in range(0, max(1, int(rs*0.5))):
            acc[np.clip(yi_[ok]+off, 0, S-1), xi_[ok], :] += 0.5*np.array([0.45, 0.95, 1.0])

# ---------- bloom + tone ----------
from scipy.ndimage import gaussian_filter, zoom as ndzoom
def wide_bloom(img, sigma):
    ds = max(1, int(sigma/6))
    if ds > 1:
        small = img[::ds, ::ds].copy()
        small = gaussian_filter(small, sigma/ds, axes=(0, 1))
        big = ndzoom(small, (ds, ds, 1), order=1)
        out = np.zeros_like(img)
        h = min(big.shape[0], S); w = min(big.shape[1], S)
        out[:h, :w] = big[:h, :w]
        return out
    return gaussian_filter(img, sigma, axes=(0, 1))

lum = acc.sum(2); nz = lum[lum > 0]
hi = np.percentile(nz, 99.4) if nz.size else 1.0
hot = np.clip(lum-hi, 0, None)[..., None]*np.where(lum[..., None] > 0,
                                                   acc/(lum[..., None]+1e-9), 0)
acc += 0.45*wide_bloom(hot.astype(np.float32), 8*rs)
acc += 0.25*wide_bloom(acc, 2.0*rs)

k = 1.15
img = 1.0 - np.exp(-k*acc)
img = np.clip(img, 0, 1)**(1/1.9)
bgc = np.array([0.012, 0.016, 0.028], np.float32)
img = np.maximum(img, bgc[None, None, :])
img += (np.random.default_rng(3).random((S, S, 1)).astype(np.float32)-0.5)/255.0
img = np.clip(img, 0, 1)

from PIL import Image, ImageDraw, ImageFont
im = Image.fromarray((img*255).astype(np.uint8), 'RGB')
im = im.resize((FINAL, FINAL), Image.LANCZOS)
dr = ImageDraw.Draw(im)
def F(sz):
    try: return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', sz)
    except Exception: return ImageFont.load_default()
fb, fs, ft = F(int(20*rs)), F(int(11.5*rs)), F(int(9.5*rs))
cA, cB, cC = (216, 226, 240), (152, 164, 186), (114, 126, 150)
xt, yt = int(0.055*FINAL), int(0.030*FINAL)
dr.text((xt, yt), "THE SIX FERTILE LANES", font=fb, fill=cA)
dr.text((xt, yt+int(27*rs)),
        "a → a + digitsum(a):  the lane a mod 9 doubles each step — three castes, fixed at birth: {0}, {3,6}, and the six-cycle 1→2→4→8→7→5",
        font=fs, fill=cB)
dr.text((xt, yt+int(44*rs)),
        "the river from 1: 2,081,679,312 steps to 10¹¹, 136,932,755 primes — all in the six lanes; gold = each lane's share of the primes (MO 514700)",
        font=ft, fill=cC)
# lane labels
tot = {1: '21.3M', 2: '25.6M', 4: '23.9M', 8: '22.3M', 7: '19.9M', 5: '24.0M'}
for l in order:
    yl = int((lane_y[l]+BH*0.5)/SS/1.0)/1*1  # canvas SS -> final
    yl = int((lane_y[l]+BH*0.5)/S*FINAL)-int(6*rs)
    if l in FERT:
        dr.text((int(0.018*FINAL), yl), f"lane {l}", font=fs, fill=cB)
        dr.text((int(0.952*FINAL), yl), tot[l], font=ft, fill=(190, 160, 100))
    else:
        dr.text((int(0.018*FINAL), yl), f"lane {l}", font=fs, fill=(90, 100, 122))
        dr.text((int(0.905*FINAL), yl), "no prime, ever", font=ft, fill=(90, 100, 122))
yl = int(0.826*FINAL)
dr.text((xt, yl),
        "the lanes trade their luck: observed prime share per decade (dots) vs the river's own odd·non-5 occupancy share (cyan rings) — they agree to 4 decimals",
        font=ft, fill=cC)
dr.text((xt, yl+int(12*rs)),
        "lane 7 (blue): richest at 10⁵, poorest at 10¹⁰ — aggregated over all decades the sieve ranking inverts: Simpson's paradox on a river of digits",
        font=ft, fill=cC)
for d in decs:
    dr.text((int(rx(d)/S*FINAL)-int(8*rs), int(0.970*FINAL)), f"10^{d}", font=ft, fill=cC)
for l in (2, 7):
    yv = ry(obs[(10, l)])/S*FINAL
    dr.text((int(rx(10)/S*FINAL)+int(12*rs), int(yv)-int(5*rs)), f"lane {l}",
            font=ft, fill=tuple(int(c*255) for c in LANEC[l]))
im.save('lanes_2560.png')
print("saved lanes")
