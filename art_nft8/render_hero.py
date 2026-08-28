#!/usr/bin/env python3
"""HERO 4096^2 — 'The Shore Every Rhyme Must Touch'  (MO 514678)

Every consecutive triple (u,v,w) of every one of the 7,584 good
permutations of {-22..22} (the complete mirror ensemble at N=22,
exhaustively enumerated) IS a quadratic u x^2 + v x + w with a rational
root: its parabola cannot float — it must touch the real line, and it
must touch it at rational points. All distinct triples are drawn as
parabolas in an asinh-warped plane; the x-axis is the shore; every
crossing is a bead of certified rationality. LAWFUL triples
(v = +-(u+w), discriminant (u-+w)^2 — the meter) burn cold silver-cyan;
LUCKY triples (generic square discriminant) burn gold; disc = 0
parabolas kiss the shore in white.
Bottom register: the one deep poem (N=48) as a class-colored seismogram,
and the cold unresolved column at N=49.
"""
import numpy as np, math, sys
from collections import Counter

SS    = 2
FINAL = 4096 if len(sys.argv) < 2 else int(sys.argv[1])
S     = FINAL*SS
rs    = FINAL/1024.0

# ---------- data ----------
tripmult = Counter()
for line in open('ens22.txt'):
    b = [int(x) for x in line.split()]
    full = b + [0] + [-x for x in reversed(b)]
    for i in range(1, len(full)-1):
        tripmult[(full[i-1], full[i], full[i+1])] += 1
trips = np.array(list(tripmult.keys()), dtype=np.float64)
mult  = np.array([tripmult[tuple(t)] for t in trips.astype(int)], np.float64)
u, v, w = trips[:,0], trips[:,1], trips[:,2]
disc = v*v - 4*u*w
kroot = np.sqrt(disc)
lawful = (v == u+w) | (v == -(u+w))
geo = disc == 0
NTR = len(trips)
print("distinct triples:", NTR, " lawful:", lawful.sum(), " geo:", geo.sum())

# ---------- chart ----------
XR = 7.5                      # x in [-XR, XR]
YS = 5.0                      # asinh scale divisor
YR = math.asinh(200/YS)       # world y range mapped
mx, mtop, mbot = 0.045*S, 0.045*S, 0.185*S
X0, X1 = mx, S-mx
Y0, Y1 = mtop, S-mbot
ymid_frac = 0.52              # shore slightly below center of plot area
YSHORE = Y0 + (Y1-Y0)*ymid_frac
def px(x): return X0 + (X1-X0)*(x+XR)/(2*XR)
def pyw(y):                   # world y -> canvas
    z = np.arcsinh(y/YS)/YR   # -1..1 ish
    return YSHORE - z*(Y1-Y0)*0.5

acc = np.zeros((S, S, 3), np.float32)
def splat(xs, ys, wts, col):
    xi = np.floor(xs).astype(np.int64); yi = np.floor(ys).astype(np.int64)
    fx = (xs - xi).astype(np.float32); fy = (ys - yi).astype(np.float32)
    m = (xi >= 0) & (xi < S-1) & (yi >= 0) & (yi < S-1)
    xi, yi, fx, fy, wt = xi[m], yi[m], fx[m], fy[m], wts[m].astype(np.float32)
    flat = acc.reshape(-1, 3)
    for dx, dy, ww in ((0,0,(1-fx)*(1-fy)), (1,0,fx*(1-fy)),
                       (0,1,(1-fx)*fy), (1,1,fx*fy)):
        idx = (yi+dy)*S + (xi+dx)
        for c in range(3):
            np.add.at(flat[:, c], idx, wt*ww*col[c])

COL_LAW  = np.array([0.40, 0.66, 0.95], np.float32)
COL_LUCK = np.array([1.00, 0.72, 0.28], np.float32)
COL_GEO  = np.array([1.00, 1.00, 1.00], np.float32)

# ---------- parabola strokes ----------
NX = int(900*rs)
xs_world = np.linspace(-XR, XR, NX)
xs_can = px(xs_world).astype(np.float32)
ink = (mult**0.30).astype(np.float32)
AMP = 0.046
CH = 400
order = np.argsort(~lawful)   # draw lawful first, lucky over
for c0 in range(0, NTR, CH):
    ids = order[c0:c0+CH]
    Y = (u[ids,None]*xs_world[None,:]**2 + v[ids,None]*xs_world[None,:]
         + w[ids,None])
    Yc = pyw(Y).astype(np.float32)
    # arc-length compensation per segment (avoid dotted steep parts):
    # draw as dense polyline samples between consecutive x-samples
    inside = (Yc > Y0-40) & (Yc < Y1+40)
    for r in range(len(ids)):
        t = ids[r]
        col = COL_LAW if lawful[t] else COL_LUCK
        yr = Yc[r]; ok = inside[r]
        # subdivide by vertical jumps
        dy = np.abs(np.diff(yr))
        steps = np.clip((dy/ (1.6)).astype(np.int32), 1, 40)
        segs_x = []; segs_y = []
        idxs = np.nonzero(ok[:-1] & ok[1:])[0]
        if idxs.size == 0: continue
        for j in idxs:
            n = steps[j]
            tt = np.arange(n, dtype=np.float32)/n
            segs_x.append(xs_can[j] + (xs_can[j+1]-xs_can[j])*tt)
            segs_y.append(yr[j] + (yr[j+1]-yr[j])*tt)
        sx = np.concatenate(segs_x); sy = np.concatenate(segs_y)
        zfrac = np.clip(np.abs(sy - YSHORE)/(0.5*(Y1-Y0)), 0, 1)
        xfrac = np.clip((np.abs(sx - 0.5*(X0+X1))/(0.5*(X1-X0)) - 0.86)/0.14, 0, 1)
        fall = ((1.0 - 0.88*zfrac**2.3)*(1.0 - 0.85*xfrac**1.5)).astype(np.float32)
        wts = np.full(sx.size, AMP*ink[t]*NX/(sx.size+1), np.float32)*fall
        splat(sx, sy, wts, col)
    print("chunk", c0, flush=True)

# ---------- root beads on the shore ----------
rootmult = Counter()
ui, vi, wi = trips[:,0].astype(int), trips[:,1].astype(int), trips[:,2].astype(int)
ki = kroot.astype(int)
for t in range(NTR):
    if ui[t] == 0: continue
    for sgn in (+1, -1):
        num = -vi[t] + sgn*ki[t]; den = 2*ui[t]
        from math import gcd
        g = gcd(abs(num), abs(den)) or 1
        rootmult[(num//g, den//g)] += tripmult[(ui[t], vi[t], wi[t])]
rx, rm = [], []
for (p, q), m_ in rootmult.items():
    x = p/q
    if -XR < x < XR:
        rx.append(x); rm.append(m_)
rx = np.array(rx); rm = np.array(rm, np.float64)
print("distinct rational roots in frame:", len(rx))
bead_amp = 0.9*(rm**0.42)/ (rm.max()**0.42)
rad = 2.1*rs
for xw, amp in zip(rx, bead_amp):
    x0 = px(xw); y0 = YSHORE
    b = int(5*rad)
    xg = np.arange(max(0, int(x0)-b), min(S, int(x0)+b+1))
    yg = np.arange(max(0, int(y0)-b), min(S, int(y0)+b+1))
    dx = xg[None,:]-x0; dyy = yg[:,None]-y0
    gau = np.exp(-(dx*dx+dyy*dyy)/(2*rad*rad))*amp*0.72
    acc[yg[0]:yg[-1]+1, xg[0]:xg[-1]+1, :] += gau[..., None]*np.array([1.0,0.95,0.80],np.float32)

# shore hairline
yy = np.arange(S)
shore = np.exp(-((yy-YSHORE)**2)/(2*(0.9*rs)**2)).astype(np.float32)
xin = ((np.arange(S) >= X0) & (np.arange(S) <= X1)).astype(np.float32)
acc += 0.16*shore[:,None,None]*xin[None,:,None]*np.array([0.9,0.95,1.0],np.float32)[None,None,:]

# ---------- bottom register: deep poem N=48 + the wall at 49 ----------
try:
    txt = open('sols/sol_49.txt').read()
    deep = [int(x) for x in txt.split(':')[1].split()]
except Exception:
    deep = None
if deep:
    Ld = len(deep)
    yb0, yb1 = S-0.155*S, S-0.030*S
    xb = np.linspace(X0, X1*0.955, Ld)
    ymid = 0.5*(yb0+yb1); ysc = (yb1-yb0)/2/(max(abs(min(deep)), max(deep)))
    pts = ymid - np.array(deep)*ysc
    for i in range(Ld-1):
        lawf = (0 < i < Ld-1 and (deep[i] == deep[i-1]+deep[i+1]
                                  or deep[i] == -(deep[i-1]+deep[i+1])))
        col = (COL_LAW if lawf else COL_LUCK)*1.35
        x0c, y0c, x1c, y1c = xb[i], pts[i], xb[i+1], pts[i+1]
        n = int(max(abs(x1c-x0c), abs(y1c-y0c)))+2
        tt = np.linspace(0, 1, n, dtype=np.float32)
        for off in np.linspace(-0.45*rs, 0.45*rs, max(1, int(rs))):
            splat(x0c+(x1c-x0c)*tt, y0c+(y1c-y0c)*tt+off,
                  np.full(n, 0.16*rs/max(1, int(rs)), np.float32), col)
# cold wall at N=49
xw = X1*0.985
ww = np.exp(-((np.arange(S)-xw)**2)/(2*(2.6*rs)**2)).astype(np.float32)
grad = np.zeros(S, np.float32)
ys0 = int(S-0.175*S)
grad[ys0:] = np.linspace(0.15, 1.0, S-ys0)
acc += (ww[None,:]*grad[:,None])[:,:,None]*np.array([0.95,0.72,0.35],np.float32)[None,None,:]*0.75

# ---------- bloom + tone ----------
from scipy.ndimage import gaussian_filter, zoom as ndzoom
def wide_bloom(img, sigma):
    ds = max(1, int(sigma/6))
    if ds > 1:
        small = img[::ds, ::ds].copy()
        small = gaussian_filter(small, sigma/ds, axes=(0,1))
        big = ndzoom(small, (ds, ds, 1), order=1)
        out = np.zeros_like(img)
        out[:min(big.shape[0],S), :min(big.shape[1],S)] = big[:S,:S]
        return out
    return gaussian_filter(img, sigma, axes=(0,1))

lum = acc.sum(2)
nz = lum[lum > 0]
hi = np.percentile(nz, 99.3) if nz.size else 1.0
hot = np.clip((lum-hi), 0, None)[..., None] * np.where(
    lum[..., None] > 0, acc/(lum[..., None]+1e-9), 0)
acc += 0.50*wide_bloom(hot.astype(np.float32), 9*rs)
acc += 0.28*wide_bloom(acc, 2.0*rs)

k = 0.85
img = 1.0 - np.exp(-k*acc)
img = np.clip(img, 0, 1)**(1/1.9)
bgc = np.array([0.013, 0.017, 0.030], np.float32)
img = np.maximum(img, bgc[None, None, :])
img += (np.random.default_rng(7).random((S, S, 1)).astype(np.float32)-0.5)/255.0
img = np.clip(img, 0, 1)

from PIL import Image, ImageDraw, ImageFont
im = Image.fromarray((img*255).astype(np.uint8), 'RGB')
im = im.resize((FINAL, FINAL), Image.LANCZOS)
dr = ImageDraw.Draw(im)
def F(sz, path='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'):
    try: return ImageFont.truetype(path, sz)
    except Exception: return ImageFont.load_default()
fb = F(int(21*rs)); fs = F(int(12.5*rs)); ft = F(int(10.5*rs))
cA=(214,225,240); cB=(150,163,185); cC=(112,124,148)
x0t = int(0.049*FINAL); y0t = int(0.052*FINAL)
dr.text((x0t, y0t), "THE SHORE EVERY RHYME MUST TOUCH", font=fb, fill=cA)
dr.text((x0t, y0t+int(30*rs)),
  "all 7,584 rational-root permutations of {-22..22} — every consecutive triple drawn as its quadratic  u x² + v x + w",
  font=fs, fill=cB)
dr.text((x0t, y0t+int(48*rs)),
  "a permutation is good when every triple's discriminant v²−4uw is a perfect square: no parabola may float — each must touch the line, at rational points",
  font=ft, fill=cC)
dr.text((x0t, y0t+int(64*rs)),
  "silver: lawful rhymes v = ±(u+w), the meter whose pure poems die at N = 6  ·  gold: lucky squares  ·  beads: the 1,114 rational crossings  ·  MO 514678",
  font=ft, fill=cC)
yb = int((1-0.175)*FINAL)
dr.text((x0t, yb), "one deep poem: N = 49, the hardest door yet — 99 words, every triple certified; N ≤ 48 fell in seconds, this held for an hour", font=ft, fill=cC)
dr.text((int(0.845*FINAL), yb), "the door at N=49: 118 restarts →", font=ft, fill=(235,195,120))
im.save('hero_proto.png' if FINAL < 4096 else 'hero_4096.png')
print("saved", FINAL)
