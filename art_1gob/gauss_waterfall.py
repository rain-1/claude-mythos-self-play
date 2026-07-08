"""Piece I — The Waterfall That Forgets  (v4: ropes of measure)
Backward cascade G^{-n}(A) of a golden interval A ∋ 1/phi under the Gauss map.
Every cylinder-piece is fed by a rope from its parent; rope brightness = Gauss-
mass flux / width (constant flux), so conservation is literally visible.
Sub-pixel children pour into a mist that keeps cascading via exact mu-transfer
weights.  Total mass mu(A) at every level, verified.  The all-ones corridor
(fixed point 1/phi) survives longest.
"""
import sys, numpy as np
from scipy.ndimage import gaussian_filter
from kit import filmic, bloom, save

PROTO = '--proto' in sys.argv
S  = 1280 if PROTO else 4096
SS = 2
W = H = S*SS
NLEV = 11
LN2 = np.log(2.0); PHI=(1+np.sqrt(5))/2; X0=1/PHI
def mu(a,b): return (np.log1p(b)-np.log1p(a))/LN2

# ---------- cascade ----------
A0, B0 = X0-0.055, X0+0.055
EPS = 0.5/W
levels = [[(A0,B0)]]
ropes  = []                 # (lev, pa,pb, s0,s1 cumfrac in parent, ca,cb, mass, is_dust)
newdust = [[] for _ in range(NLEV)]
for n in range(NLEV-1):
    nxt = []
    for (a,b) in levels[n]:
        mpar = mu(a,b); pc=0.5*(a+b)
        emitted = 0.0; cum = 0.0; k = 1
        while True:
            ca, cb = 1.0/(k+b), 1.0/(k+a)
            m = mu(ca,cb)
            if cb-ca < EPS and not (k==1 and cb-ca > EPS/48): break
            nxt.append((ca,cb))
            fr = m/mpar
            ropes.append((n, a,b, cum, cum+fr, ca,cb, m, 0))
            cum += fr; emitted += m; k += 1
        kk, dust_here = k, []
        while kk < k+160:
            ca2, cb2 = 1.0/(kk+b), 1.0/(kk+a)
            m2 = mu(ca2,cb2)
            if m2 < 1e-15: break
            dust_here.append((0.5*(ca2+cb2), m2)); emitted += m2; kk += 1
        rem = mu(a,b)-emitted
        if rem > 0: dust_here.append((0.5/(kk+pc), rem))
        dm = sum(m for _,m in dust_here)
        if dm > 0:
            ca, cb = 0.3/(k+pc), 1.0/(k+a)   # dust fan target zone
            ropes.append((n, a,b, cum, 1.0, ca,cb, dm, 1))
        newdust[n+1].extend(dust_here)
    levels.append(nxt)

# mist evolution (exact mu-transfer split)
MB = 16384
xb = (np.arange(MB)+0.5)/MB
gb = 1.0/(LN2*(1+xb))
def deposit(grid, xs, ms):
    p = np.asarray(xs)*MB-0.5
    j0 = np.clip(np.floor(p).astype(np.int64),0,MB-2); f = np.clip(p-j0,0,1)
    np.add.at(grid, j0, np.asarray(ms)*(1-f)); np.add.at(grid, j0+1, np.asarray(ms)*f)
K = 1200
u_k, w_k = [], []
ssum = np.zeros(MB)
for k in range(1, K+1):
    u = 1.0/(k+xb)
    w = (1.0/gb)*(1.0/(LN2*(1+u)))/(k+xb)**2
    u_k.append(u); w_k.append(w); ssum += w
wrem = np.maximum(1-ssum, 0)
def mist_step(m):
    out = np.zeros(MB)
    for u,w in zip(u_k,w_k): deposit(out, u, m*w)
    deposit(out, np.full(MB, 0.5/K), m*wrem)
    return out
mist = [np.zeros(MB) for _ in range(NLEV)]
for n in range(1, NLEV):
    m = mist_step(mist[n-1])
    if newdust[n]:
        dd = np.array(newdust[n]); deposit(m, dd[:,0], dd[:,1])
    mist[n] = m
m0 = mu(A0,B0)
print(f"mu(A) = {m0:.6f}, ropes={len(ropes)}")
for n in range(NLEV):
    mp = sum(mu(a,b) for a,b in levels[n]); mm = mist[n].sum()
    print(f"  level {n:2d}: pieces={len(levels[n]):5d} piece-mass={mp:.6f} mist={mm:.6f} total={mp+mm:.6f}")

# ---------- Stern-Brocot mesh ----------
seen = {}
def rec(pm,qm,p,q,depth):
    for (pp,qq) in ((p,q),(p+pm,q+qm)):
        if qq and (pp,qq) not in seen: seen[(pp,qq)] = depth
    lo = p/q if q else 0.0; hi=(p+pm)/(q+qm)
    if lo>hi: lo,hi=hi,lo
    if depth>=NLEV-1 or (hi-lo)*W<0.5: return
    k=1
    while k<=400:
        p2,q2 = k*p+pm, k*q+qm
        if abs((p2+p)/(q2+q)-p2/q2)*W<0.5 and k>3: break
        rec(p,q,p2,q2,depth+1); k+=1
sys.setrecursionlimit(20000)
rec(1,0,0,1,0)

# ---------- paint ----------
Y0p, Y1p = 0.085*H, 0.985*H
BH = (Y1p-Y0p)/(NLEV-1)
def ylev(n): return Y0p+n*BH
KEYS = np.array([
 [1.00,0.82,0.38],[1.00,0.62,0.20],[1.00,0.44,0.16],[0.94,0.32,0.20],
 [0.80,0.24,0.28],[0.64,0.22,0.40],[0.55,0.28,0.58],[0.38,0.34,0.64],
 [0.28,0.44,0.64],[0.24,0.52,0.62],[0.22,0.58,0.60],[0.24,0.62,0.57],[0.26,0.65,0.55]])
def pal(tau):
    t = np.clip(tau,0,NLEV-1); i = np.minimum(t.astype(int),NLEV-2); f=(t-i)[...,None]
    return KEYS[i]*(1-f)+KEYS[i+1]*f

acc = np.zeros((H,W,3), np.float32)     # additive light
# mesh threads
thr = np.zeros((H,W), np.float32)
for (p,q),depth in seen.items():
    x = p/q*W-0.5; j0=int(np.floor(x)); a=x-j0
    yb = int(ylev(depth)); wgt=(1.0/q)**0.85*1.2
    if 0<=j0<W: thr[yb:,j0]+=wgt*(1-a)
    if 0<=j0+1<W: thr[yb:,j0+1]+=wgt*a
thr = gaussian_filter(thr,(0,SS*0.55))
acc += np.array([0.30,0.45,0.60])[None,None,:]*(1-np.exp(-1.2*thr))[...,None]*0.38

# ropes: constant-flux sheets
GAIN_R = 0.115
rope_buf = np.zeros((H,W,3), np.float32)
for (n, pa,pb, s0,s1, ca,cb, m, isd) in ropes:
    # top strip (right-to-left cumfrac) and bottom interval
    ta, tb = pb-(pb-pa)*s1, pb-(pb-pa)*s0
    y0, y1 = ylev(n), ylev(n+1)
    travel = abs(0.5*(ca+cb)-0.5*(ta+tb))*W
    ns = int(max(y1-y0, travel)*1.35)+8
    ts = np.linspace(0,1,ns)
    es = ts*ts*(3-2*ts)
    xa = (ta+(ca-ta)*es)*W; xbv = (tb+(cb-tb)*es)*W
    yv = y0+(y1-y0)*ts
    flux = (m/np.maximum(xbv-xa,0.7))*(W/m0)*GAIN_R*( (y1-y0)/ns )/1.0
    if isd: flux = flux*(1-0.75*es)          # dust rope fades into mist
    cols = pal(n+ts)
    iy = np.clip(yv.astype(int),0,H-1)
    for i in range(ns):
        j0 = int(np.floor(xa[i])); j1 = int(np.ceil(xbv[i]))
        j0c, j1c = max(j0,0), min(j1,W)
        if j1c<=j0c: continue
        rope_buf[iy[i], j0c:j1c] += flux[i]*cols[i]
for c in range(3):
    rope_buf[...,c] = gaussian_filter(rope_buf[...,c], SS*0.55)
acc += rope_buf

# mist: continuous vertical interpolation between levels
pxb = np.clip((xb*W).astype(np.int64),0,W-1)
mist_px = np.zeros((NLEV,W), np.float32)
for n in range(NLEV):
    tmp = np.zeros(W, np.float32)
    np.add.at(tmp, pxb, mist[n].astype(np.float32))
    mist_px[n] = gaussian_filter(tmp, SS*(0.6+0.5*n))*(W/m0)
GAIN_M = 0.15
rows = np.arange(H)
tau_r = np.clip((rows-Y0p)/BH, 0, NLEV-1-1e-6)
n_r = tau_r.astype(int); f_r = tau_r-n_r; f_r = f_r*f_r*(3-2*f_r)
mist_field = mist_px[n_r]*(1-f_r[:,None])+mist_px[np.minimum(n_r+1,NLEV-1)]*f_r[:,None]
mist_col = pal(tau_r)                       # (H,3)
acc += (1-np.exp(-GAIN_M*mist_field))[...,None]*mist_col[:,None,:]*0.85

# source pool + seed star + golden marker
X = np.arange(W, dtype=np.float32); Yv = np.arange(H, dtype=np.float32)
r2 = (X[None,:]-X0*W)**2 + (Yv[:,None]-0.052*H)**2
star = 1.5*np.exp(-r2/(2*(0.0055*H)**2))+0.55*np.exp(-r2/(2*(0.016*H)**2))
acc += np.array([1.0,0.82,0.36])[None,None,:]*star[...,None]
gl = np.exp(-0.5*((X-X0*W)/(SS*0.8))**2)*0.13
acc += np.array([1.0,0.80,0.35])[None,None,:]*(gl[None,:]*np.ones((H,1),np.float32))[...,None]
# pool: bright lens on [A0,B0] at Y0
poolx = np.clip(4*(X/W-A0)*(B0-X/W)/(B0-A0)**2,0,1)**0.5
pooly = np.exp(-0.5*((Yv-Y0p)/(0.008*H))**2)
acc += np.array([1.0,0.80,0.36])[None,None,:]*(pooly[:,None]*poolx[None,:]*1.1)[...,None]

# shoreline: the limit law g(x) drawn as a luminous horizon
gsh = 1.0/(LN2*(1+X/W))
gn = (gsh-gsh.min())/(gsh.max()-gsh.min())
ysh = 0.948*H - 0.088*H*gn
dsh = np.abs(Yv[:,None]-ysh[None,:])
crv = np.exp(-0.5*(dsh/(SS*0.9))**2)*0.55*(0.45+0.55*gn)
under = np.exp(-np.maximum(Yv[:,None]-ysh[None,:],0)/(0.012*H))*0.10*(Yv[:,None]>ysh[None,:])
acc += np.array([0.55,0.85,0.80])[None,None,:]*(crv+under)[...,None]

# background wash
yy = np.linspace(0,1,H)[:,None]
bg = np.zeros((H,W,3), np.float32)
for c,v in enumerate((0.026,0.028,0.048)): bg[...,c] = v*(0.55+0.45*yy)
out = bg+acc
out = bloom(out, mask_thresh=0.66, sigma=W/300, gain=0.5)
out = filmic(out, k=1.2, gamma=0.90)
save(out, ('proto/' if PROTO else 'out/')+'I_waterfall'+('_proto' if PROTO else '')+'.png', down=S)
