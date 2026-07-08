"""Piece III — The Ladder That Repeats  (v2: spine chart)
Chart: u = ln x, v = center ∓ scaled ln|y - x/sqrt2|.  The sqrt2 direction is a
central spine no integer point ever touches; each hyperbola x^2-2y^2 = n is a
straight rib converging on it; the unit eps^2 = 3+2sqrt2 beads each rib with
solutions at exactly even spacing 2 ln(1+sqrt2).  eps itself (norm -1) stitches
rib n to rib -n across the spine.  Ribs with |n| ≡ ±3 (mod 8) carry no beads:
locally forbidden ladders.  All points exact-verified.
"""
import sys, numpy as np
from scipy.ndimage import gaussian_filter
from kit import filmic, bloom, save

PROTO = '--proto' in sys.argv
S  = 1280 if PROTO else 2560
SS = 2
W = H = S*SS
NMAX_CURVE = 48
NMAX_PT    = 4000
XMAX       = 1.4e6
SQ2 = np.sqrt(2.0)

# ---------- integer points ----------
B = 3000
xs, ys = np.mgrid[0:B+1, 0:B+1]
xs = xs.ravel().astype(np.int64); ys = ys.ravel().astype(np.int64)
n = xs*xs - 2*ys*ys
m = (np.abs(n) <= NMAX_PT) & (xs>0) & (ys>0)
P = np.stack([xs[m], ys[m]], 1)
pts = set(map(tuple, P.tolist()))
cur = P
U2 = np.array([[3,2],[4,3]], dtype=np.int64)
while len(cur):
    nx = cur @ U2
    keep = (nx[:,0] <= XMAX*1.35) & (nx[:,1] <= XMAX*1.35)
    cur = nx[keep]
    new = [t for t in map(tuple, cur.tolist()) if t not in pts]
    pts.update(new)
    cur = np.array(new, dtype=np.int64).reshape(-1,2)
P = np.array(sorted(pts), dtype=np.int64)
NN = P[:,0]**2 - 2*P[:,1]**2
assert np.abs(NN).max() <= NMAX_PT
assert (((P@U2)[:,0]**2 - 2*(P@U2)[:,1]**2) == NN).all()
solv = sorted(set(int(v) for v in NN if abs(v)<=NMAX_CURVE))
print(f"points: {len(P)} (x,y>0), verified.")
print("solvable |n|<=48:", [v for v in solv if v>0])
print("bare (no beads) among 1..48:", [v for v in range(1,49) if v not in solv])

# ---------- chart ----------
UL, UR = -0.35, 14.35
WLO, WHI = -16.0, 2.3
VSPAN = 0.485
PEXP = 1.55
def chart(x, y):
    x = np.asarray(x, dtype=np.float64); y = np.asarray(y, dtype=np.float64)
    u = np.log(np.maximum(x, 1e-9))
    d = y - x/SQ2
    wv = np.clip(np.log(np.maximum(np.abs(d), 1e-9)), WLO, WHI)
    dist = ((wv-WLO)/(WHI-WLO))**PEXP*VSPAN
    v = 0.5 - np.sign(d)*dist          # d>0 (above asymptote, n<0) -> up
    px = (u-UL)/(UR-UL)*W
    py = v*H
    return px, py

acc = np.zeros((H,W,3), np.float32)
yy = np.linspace(0,1,H)[:,None]
for c,vv in enumerate((0.026,0.028,0.048)): acc[...,c] += vv*(0.70+0.30*np.abs(yy-0.5)*2)

def splat(xf, yf, wf, sigma):
    buf = np.zeros((H,W), np.float32)
    j0 = np.floor(xf).astype(np.int64); i0 = np.floor(yf).astype(np.int64)
    fx, fy = xf-j0, yf-i0
    for dj,di,wq in ((0,0,(1-fx)*(1-fy)),(1,0,fx*(1-fy)),(0,1,(1-fx)*fy),(1,1,fx*fy)):
        jj, ii = j0+dj, i0+di
        ok = (jj>=0)&(jj<W)&(ii>=0)&(ii<H)
        np.add.at(buf, (ii[ok],jj[ok]), (wf*wq)[ok])
    return gaussian_filter(buf, sigma*SS) if sigma else buf

WARM = np.array([1.00,0.60,0.20]); WARM2 = np.array([0.95,0.36,0.14])
COOLC= np.array([0.30,0.75,0.68]); COOL2 = np.array([0.22,0.48,0.72])
SPINE= np.array([1.00,0.94,0.80])

# ---------- ribs (hyperbola pencil) ----------
rib_w = np.zeros((H,W), np.float32); rib_c = np.zeros((H,W), np.float32)
for nv in list(range(1,NMAX_CURVE+1))+list(range(-NMAX_CURVE,0)):
    xlo = np.sqrt(abs(nv)) if nv>0 else np.sqrt(abs(nv)/2)*0.02+1e-3
    lx = np.linspace(np.log(max(xlo,1e-3)+1e-9), np.log(XMAX*1.35), 2600)
    x = np.exp(lx)
    if nv > 0:
        y = np.sqrt(np.maximum(x*x-nv,0))/SQ2
    else:
        y = np.sqrt((x*x-nv))/SQ2      # x^2-2y^2=n<0 -> y=sqrt((x^2-n)/2)
    px, py = chart(x, y)
    ok = (px>=0)&(px<W)&(py>=0)&(py<H)
    # weight ∝ 1/(pixel speed) for even line density
    dpx = np.hypot(np.gradient(px), np.gradient(py))
    wgt = np.clip(1.0/np.maximum(dpx,1e-6),0,4)* (2.6/abs(nv)**0.72)
    tgt = rib_w if nv>0 else rib_c
    boost = 1.25 if nv in solv else 0.5
    tgt += splat(px[ok], py[ok], wgt[ok]*boost, 0)
rib_w = gaussian_filter(rib_w, 0.65*SS); rib_c = gaussian_filter(rib_c, 0.65*SS)
acc += WARM[None,None,:]*(1-np.exp(-1.15*rib_w))[...,None]*0.85
acc += COOLC[None,None,:]*(1-np.exp(-1.15*rib_c))[...,None]*0.85

# ---------- the spine: unreachable sqrt2 ----------
Yv = np.arange(H, dtype=np.float32); Xg = np.arange(W, dtype=np.float32)
spine = np.exp(-0.5*((Yv-0.5*H)/(SS*1.1))**2)*0.55 + np.exp(-0.5*((Yv-0.5*H)/(SS*6.0))**2)*0.22
ramp = 0.35+0.65*(Xg/W)**1.2
acc += SPINE[None,None,:]*(spine[:,None]*ramp[None,:])[...,None]*0.28

# ---------- eps-stitch ----------
absn = np.abs(NN).astype(np.float64)
sel = absn <= 2
Ps = P[sel]
E1 = np.array([[1,1],[2,1]], dtype=np.int64)
Pe = Ps @ E1
assert ((Pe[:,0]**2-2*Pe[:,1]**2) == -(Ps[:,0]**2-2*Ps[:,1]**2)).all()
x0p, y0p = chart(Ps[:,0], Ps[:,1]); x1p, y1p = chart(Pe[:,0], Pe[:,1])
st = np.zeros((H,W), np.float32)
for i in range(len(Ps)):
    if x1p[i] > W+80: continue
    ln = max(np.hypot(x1p[i]-x0p[i], y1p[i]-y0p[i]), 4)
    ns = int(ln*0.8)+4
    tt = np.linspace(0,1,ns)
    xs_ = x0p[i]+(x1p[i]-x0p[i])*tt; ys_ = y0p[i]+(y1p[i]-y0p[i])*tt
    st += splat(xs_, ys_, np.full(ns, 0.14*ln/ns), 0)
st = gaussian_filter(st, 0.7*SS)
acc += np.array([0.80,0.72,0.98])[None,None,:]*(1-np.exp(-1.6*st))[...,None]*0.72

# forbidden wedge: |x^2-2y^2| >= 1 means nothing enters here, ever
ucol = UL + (np.arange(W)+0.5)/W*(UR-UL)
xcol = np.exp(ucol)
w1 = np.clip(np.log(1.0/(2*SQ2*xcol)), WLO, WHI)
dist1 = ((w1-WLO)/(WHI-WLO))**PEXP*VSPAN
vup = (0.5-dist1)*H; vdn = (0.5+dist1)*H
Ygrid = Yv[:,None]
inside = (Ygrid > vup[None,:]) & (Ygrid < vdn[None,:])
depthw = np.where(dist1[None,:]*H>1e-6,
                  np.clip((Ygrid-vup[None,:])*(vdn[None,:]-Ygrid),0,None)/np.maximum((dist1[None,:]*H)**2,1e-6),
                  0.0)
wedge = np.where(inside, depthw**0.8, 0.0).astype(np.float32)*np.float32(0.20)
wedge *= (0.35+0.65*(np.arange(W,dtype=np.float32)/W)**0.8)[None,:]
acc += np.array([0.30,0.24,0.55])[None,None,:]*wedge[...,None]

# ---------- beads ----------
Xf, Yf = P[:,0].astype(np.float64), P[:,1].astype(np.float64)
for fam, colA, colB in ((NN>0, WARM, WARM2), (NN<0, COOLC, COOL2)):
    s1 = fam & (absn<=NMAX_CURVE)
    px, py = chart(Xf[s1], Yf[s1])
    b = splat(px, py, (1.0/(absn[s1]+1)**0.5)*30.0, 1.15)
    acc += (colA*0.75+np.array([1,1,1])*0.25)[None,None,:]*(1-np.exp(-2.0*b))[...,None]*1.05
    s2 = fam & (absn>NMAX_CURVE)
    px, py = chart(Xf[s2], Yf[s2])
    b = splat(px, py, (1.0/(absn[s2]+1)**0.5)*16.0, 0.9)
    acc += (colB*0.9)[None,None,:]*(1-np.exp(-2.0*b))[...,None]*0.80

# fundamental solutions: the seed of each ladder
fund = []
for nv in solv:
    ss = NN==nv
    if ss.any():
        i = np.argmin(Xf[ss]); fund.append((Xf[ss][i], Yf[ss][i]))
fund = np.array(fund)
px, py = chart(fund[:,0], fund[:,1])
b = splat(px, py, np.full(len(fund), 55.0), 2.2)
acc += np.array([1.0,0.95,0.80])[None,None,:]*(1-np.exp(-1.2*b))[...,None]*0.5

# hero |n|=1,2 brighter
s1 = absn <= 2
px, py = chart(Xf[s1], Yf[s1])
b = splat(px, py, np.full(int(s1.sum()), 42.0), 1.5)
acc += np.array([1.0,0.86,0.50])[None,None,:]*(1-np.exp(-1.8*b))[...,None]*0.9

# seed star: (1,1) — the first strike of the unit (x,y>0 window)
px0, py0 = chart(np.array([1.0]), np.array([1.0]))
r2 = (Xg[None,:]-px0[0])**2+(Yv[:,None]-py0[0])**2
star = 1.5*np.exp(-r2/(2*(0.007*H)**2))+0.6*np.exp(-r2/(2*(0.02*H)**2))
acc += np.array([1.0,0.88,0.55])[None,None,:]*star[...,None]

acc = bloom(acc, mask_thresh=0.70, sigma=W/340, gain=0.5)
out = filmic(acc, k=1.95, gamma=0.90)
save(out, ('proto/' if PROTO else 'out/')+'III_ladder'+('_proto' if PROTO else '')+'.png', down=S)
