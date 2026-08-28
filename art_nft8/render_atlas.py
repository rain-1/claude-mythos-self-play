#!/usr/bin/env python3
"""Atlas piece 47, 2560^2 — 'THE GATE, PROVED; THE WEATHER, WATCHED'

Layers: (1) the 144-arch gate wall with the four product-gate classes lit
(94 fertile-gold; 103/110/119 sterile-amber) — now a THEOREM (2-adic to
2^26, 3-adic to 3^14, thin threads listed); observed l=4 populations as
bars under the lit arches. (2) the fence road 4e11→2.4e12: 8 historical
beacons, window-47 shaded, new fences or the ghost of the expected one.
(3) the hazard ladder r45|94 by window. Verdict per pre-commit."""
import numpy as np, math, json

FINAL = 2560; SS = 2; S = FINAL*SS
rs = FINAL/1024.0
acc = np.zeros((S, S, 3), np.float32)
R = json.load(open('atlas47_results.json'))

GOLD  = np.array([1.00, 0.74, 0.28], np.float32)
AMBER = np.array([0.80, 0.55, 0.22], np.float32)
BLUE  = np.array([0.30, 0.44, 0.66], np.float32)
CYAN  = np.array([0.45, 0.92, 1.00], np.float32)
WHITE = np.array([1.00, 1.00, 1.00], np.float32)

def gauss_patch(x0, y0, rad, amp, col):
    b = int(4*rad)+1
    xg = np.arange(max(0, int(x0)-b), min(S, int(x0)+b+1))
    yg = np.arange(max(0, int(y0)-b), min(S, int(y0)+b+1))
    if xg.size == 0 or yg.size == 0: return
    dx = xg[None, :]-x0; dy = yg[:, None]-y0
    g = np.exp(-(dx*dx+dy*dy)/(2*rad*rad))*amp
    acc[yg[0]:yg[-1]+1, xg[0]:xg[-1]+1, :] += g[..., None]*col

def line(x0, y0, x1, y1, w, amp, col):
    n = int(max(abs(x1-x0), abs(y1-y0)))+2
    tt = np.linspace(0, 1, n)
    xs = x0+(x1-x0)*tt; ys = y0+(y1-y0)*tt
    for off in np.linspace(-w/2, w/2, max(1, int(w))):
        xi = (xs+off*(y1-y0)/max(1e-9, math.hypot(x1-x0, y1-y0))).astype(int)
        yi = (ys-off*(x1-x0)/max(1e-9, math.hypot(x1-x0, y1-y0))).astype(int)
        ok = (xi >= 0) & (xi < S) & (yi >= 0) & (yi < S)
        acc[yi[ok], xi[ok], :] += amp/max(1, int(w))*col

# ---------------- (1) the gate wall ----------------
wall_y = 0.185*S; wall_h = 0.135*S
mx = 0.05*S
X0, X1 = mx, S-mx
gate = {94: ('fertile', GOLD, 1.0), 103: ('sterile', AMBER, 0.45),
        110: ('sterile', AMBER, 0.45), 119: ('sterile', AMBER, 0.45)}
cls_counts = {int(k): v for k, v in R['l4g25']['classes'].items()}
maxc = max(cls_counts.values()) if cls_counts else 1
line(X0, wall_y+wall_h, X1, wall_y+wall_h, 1.2*rs, 0.25, BLUE)
for c in range(144):
    xa = X0 + (X1-X0)*(c+0.5)/144
    if c in gate:
        _, col, ampf = gate[c]
        # a true arch: two legs + half-ellipse top
        aw = 0.010*S; hh = wall_h*0.92
        th = np.linspace(0, math.pi, 240)
        ax = xa + aw*np.cos(th); ay = wall_y+wall_h-hh + 0  - 0.30*hh*np.sin(th)
        for i2 in range(len(th)-1):
            line(ax[i2], ay[i2], ax[i2+1], ay[i2+1], 2.6*rs, 0.10*ampf*2.6, col)
        line(xa-aw, wall_y+wall_h, xa-aw, wall_y+wall_h-hh, 2.6*rs, 1.1*ampf, col)
        line(xa+aw, wall_y+wall_h, xa+aw, wall_y+wall_h-hh, 2.6*rs, 1.1*ampf, col)
        gauss_patch(xa, wall_y+wall_h-hh*0.55, 8.5*rs, 0.45*ampf, col)
        cnt = cls_counts.get(c, 0)
        bh = 0.050*S * cnt/maxc
        line(xa, wall_y+wall_h+0.016*S+bh, xa, wall_y+wall_h+0.016*S, 5.0*rs,
             0.85, col*0.9)
    else:
        line(xa, wall_y+wall_h, xa, wall_y+wall_h-0.22*wall_h, 1.6*rs, 0.22, BLUE)

# ---------------- (2) the fence road ----------------
road_y = 0.560*S
D0, D1 = 3.5e11, 2.45e12
def dx_(d): return X0 + (X1-X0)*(d-D0)/(D1-D0)
# base road
line(X0, road_y, X1, road_y, 1.4*rs, 0.55, BLUE*1.3)
# gold dust: every l=4 g=25 occurrence of this window, under the road
import random as _rd
_rd.seed(4)
for s4 in [int(x) for x in R.get('l4g25_starts', [])]:
    gauss_patch(dx_(s4), road_y + 0.016*S + 0.018*S*_rd.random(), 1.3*rs,
                0.55, GOLD*0.85)
fences = [458171603806, 615709112638, 830595732286, 862954027582,
          1158245890366, 1378555660606, 1890086207422, 1987781143486]
for f in fences:
    gauss_patch(dx_(f), road_y, 3.6*rs, 1.15, GOLD)
    line(dx_(f), road_y-0.010*S, dx_(f), road_y-0.030*S, 1.2*rs, 0.5, GOLD)
for f in R['fences25']['starts']:
    gauss_patch(dx_(f), road_y, 5.0*rs, 1.5, WHITE)
    line(dx_(f), road_y-0.010*S, dx_(f), road_y-0.038*S, 1.5*rs, 0.8, WHITE)
# window tint: soft-edged
xw0, xw1 = dx_(2.0e12), dx_(R['scanned_to'])
xxr = np.arange(S, dtype=np.float32)
tint = 1/(1+np.exp(-(xxr-xw0)/(3*rs))) * 1/(1+np.exp((xxr-xw1)/(3*rs)))
yyr = np.arange(S, dtype=np.float32)
vert = np.exp(-0.5*((yyr-road_y)/(0.030*S))**2)
acc += (tint[None,:]*vert[:,None])[...,None]*0.055*np.array([0.45,0.60,0.95],np.float32)
# ghost fence at expected position if none seen: E spacing ~ 2e11
if not R['fences25']['starts']:
    gx = dx_(2.0e12 + 2.0e11*0.5)
    if gx < xw1:  # only if the scan actually passed it
        th = np.linspace(0, 2*math.pi, 300)
        rr = 4.5*rs
        xi = (gx+rr*np.cos(th)).astype(int); yi = (road_y+rr*np.sin(th)).astype(int)
        ok = (xi >= 0) & (xi < S)
        acc[yi[ok], xi[ok], :] += 0.35*CYAN
# the long silence bracket [1378555660606, 1890086207422]
line(dx_(1378555660606), road_y+0.032*S, dx_(1890086207422), road_y+0.032*S,
     1.0*rs, 0.22, CYAN*0.8)
# sextets (ch-24, l=6) as six-bead constellations below the road
sext = [536462850079, 982614621929, 1666103585801, 1851647369129] + \
       sorted(set(R['sextets']['starts']))
for si, sx_ in enumerate(sext):
    xa = dx_(sx_)
    new = sx_ >= 2.0e12
    for b in range(6):
        gauss_patch(xa+(b-2.5)*2.6*rs, road_y+0.062*S, 1.5*rs,
                    1.0 if new else 0.55, CYAN if not new else WHITE)

# ---------------- (3) hazard ladder r45|94 ----------------
lad_y0, lad_y1 = 0.700*S, 0.850*S
lx0 = 0.10*S
windows = [('1.6-2.0e12', 2, 169), (f"2.0-{R['scanned_to']/1e12:.2f}e12",
            len(R['fences25']['starts']), R['l4g25']['fertile'])]
for i, (lab, k, n) in enumerate(windows):
    xa = lx0 + i*0.16*S
    rate = k/n if n else 0
    # candle: height ∝ rate, cap at 3e-2
    hh = (lad_y1-lad_y0)*min(rate/0.03, 1.0)
    if k > 0:
        line(xa, lad_y1, xa, lad_y1-hh, 6*rs, 1.0, GOLD)
    else:
        # empty candle: outline only
        line(xa, lad_y1, xa, lad_y1-(lad_y1-lad_y0)*0.4, 2*rs, 0.25, CYAN)
    # Poisson 68% band (Gehrels) as faint sleeve
    import math as _m
    up = (k+1)*(1-1/(9*(k+1))+1/(3*_m.sqrt(k+1)))**3
    hi_ = (lad_y1-lad_y0)*min((up/n if n else 0)/0.03, 1.0)
    line(xa+9*rs, lad_y1, xa+9*rs, lad_y1-hi_, 1.0*rs, 0.30, BLUE*1.4)
# dilution twin: raw r45 vs fertile (window 46)
xa = lx0 + 0.40*S
line(xa, lad_y1, xa, lad_y1-(lad_y1-lad_y0)*min(2.0e-3/0.03, 1)*1.0, 6*rs, 0.7, AMBER)
line(xa+0.05*S, lad_y1, xa+0.05*S, lad_y1-(lad_y1-lad_y0)*min(1.18e-2/0.03, 1),
     6*rs, 0.9, GOLD)

# ---------------- bloom + tone ----------------
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
hi = np.percentile(nz, 99.0) if nz.size else 1
hot = np.clip(lum-hi, 0, None)[..., None]*np.where(lum[..., None] > 0,
                                                   acc/(lum[..., None]+1e-9), 0)
acc += 0.55*wide_bloom(hot.astype(np.float32), 9*rs)
acc += 0.30*wide_bloom(acc, 2.2*rs)
img = 1.0 - np.exp(-1.05*acc)
img = np.clip(img, 0, 1)**(1/1.9)
img = np.maximum(img, np.array([0.012, 0.016, 0.028], np.float32)[None, None, :])
img += (np.random.default_rng(9).random((S, S, 1)).astype(np.float32)-0.5)/255.0
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
xt = int(0.055*FINAL)
dr.text((xt, int(0.030*FINAL)), "THE GATE, PROVED — THE WEATHER, WATCHED", font=fb, fill=cA)
dr.text((xt, int(0.030*FINAL)+int(27*rs)),
        "Atlas of AP obstructions, piece 47 — runs of equal gap 25 in S = {n = |x²−2y²|}, relay window [2.0, 2.4]·10¹²",
        font=fs, fill=cB)
dr.text((xt, int(0.030*FINAL)+int(44*rs)),
        "every 4-run start ≡ {94, 103, 110, 119} (mod 144) = {7,14} (mod 16) × {2,4} (mod 9) — this run: certified 2-adically to 2²⁶ and 3-adically to 3¹⁴",
        font=ft, fill=cC)
frac = R['l4g25']['fertile_frac']
dr.text((xt, int(0.030*FINAL)+int(58*rs)),
        f"observed {R['l4g25']['count']} four-runs, gate violations: {len(R['l4g25']['violations'])}; only class 94 is fertile — share {frac:.3f}",
        font=ft, fill=cC)
dr.text((xt, int(0.452*FINAL)),
        "the fence road: all known l=5 g=25 fences (gold), every one ≡ 94 (mod 144) — the silence of 511·10⁹ bracketed in cyan; sextets of gap 24 beneath",
        font=ft, fill=cC)
dr.text((xt, int(0.660*FINAL)),
        "the hazard ladder: fence rate conditional on the fertile class, window by window — and the 5.9× dilution the sterile classes hide (amber: raw, gold: fertile)",
        font=ft, fill=cC)
verd = open('atlas47_verdict.txt').read().strip() if __import__('os').path.exists('atlas47_verdict.txt') else ''
ytx = int(0.910*FINAL)
import textwrap
vls = []
for ln in verd.split('\n'):
    vls += textwrap.wrap(ln, 150) or ['']
for i, ln in enumerate(vls[:7]):
    dr.text((xt, ytx+i*int(11.5*rs)), ln, font=ft, fill=(170, 182, 205))
lly = int(lad_y1/S*FINAL)+int(6*rs)
dr.text((int((0.10*S)/S*FINAL)-int(10*rs), lly), "2/169", font=ft, fill=(190,160,100))
dr.text((int((0.10*S)/S*FINAL)-int(16*rs), lly+int(11*rs)), "window 46", font=ft, fill=(114,126,150))
dr.text((int((0.26*S)/S*FINAL)-int(8*rs), lly), "1/41", font=ft, fill=(230,200,140))
dr.text((int((0.26*S)/S*FINAL)-int(26*rs), lly+int(11*rs)), "window 47 (quarter)", font=ft, fill=(114,126,150))
dr.text((int((0.50*S)/S*FINAL)-int(30*rs), lly), "raw r45 vs fertile: the 5.9x dilution", font=ft, fill=(114,126,150))
im.save('atlas47_2560.png')
print("saved atlas")
