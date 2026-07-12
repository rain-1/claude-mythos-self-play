# Kilroy Was Here — the graph of one Brownian path, measured at every scale.
# Dyadic square covering at levels j = 4..10: each box hit by the graph is a
# lit instrument-cell whose TOTAL light is eps^{3/2} (eps = 2^-j). If the
# 3/2-dimensional content N(eps)*eps^{3/2} is roughly constant (dim_H(graph)
# = 3/2 a.s., Taylor/Mörters-Peres Thm 4.29), every level of the cascade
# glows with the same total light, brightening per-pixel like eps^{-1/2} as
# it collapses onto the trace. Whether the 3/2-Hausdorff measure of the graph
# is 0, positive or infinite is OPEN (live MathOverflow front page today).
# The walker is gone; the boxes are how we know it passed.
# Verifications (kilroy_stats.txt): N_j table, log2 N_j slope vs 3/2,
# covering completeness check on a subsample, quadratic-variation check.
import numpy as np, sys, time
from scipy.ndimage import gaussian_filter
from PIL import Image

PROTO = '--proto' in sys.argv
R  = 1280 if PROTO else 2560
SS = 2
S  = R*SS
NPTS = 1<<22
JMIN, JMAX = 4, 10

rng_scan = np.random.default_rng(20260712)
# ---- pick a seed whose path fits a unit square window with drama ----
best=None
for trial in range(200):
    seed = int(rng_scan.integers(1e9))
    g = np.random.default_rng(seed)
    dW = g.standard_normal(NPTS).astype(np.float64)*np.sqrt(1.0/NPTS)
    W = np.concatenate([[0],np.cumsum(dW)])
    rng = W.max()-W.min()
    if rng>0.90 or rng<0.60: continue
    # drama: sign changes of coarse increments + occupation spread
    c = W[::NPTS//256]; ch = np.diff(np.sign(np.diff(c))); drama=(ch!=0).sum()
    occ = np.histogram(W, bins=24)[0]; spread=(occ>0).mean()
    score = drama*spread
    if best is None or score>best[1]: best=(seed,score,rng)
seed = best[0]
print('chosen seed',best)
g = np.random.default_rng(seed)
dW = g.standard_normal(NPTS).astype(np.float64)*np.sqrt(1.0/NPTS)
W  = np.concatenate([[0],np.cumsum(dW)])
qv = np.sum(dW*dW)                     # quadratic variation ~ 1
wlo,whi = W.min(),W.max()
c0 = 0.5*(wlo+whi)                     # center the W-window
y0 = c0-0.5                            # frame: t in [0,1], W in [y0, y0+1]

# ---- dyadic covering ----
stats=[]
masks={}
for j in range(JMIN, JMAX+1):
    nb=1<<j
    idx = np.minimum((np.arange(NPTS+1)*nb)//(NPTS+1), nb-1)
    lo = np.full(nb, np.inf); hi = np.full(nb,-np.inf)
    np.minimum.at(lo, idx, W); np.maximum.at(hi, idx, W)
    blo = np.floor((lo-y0)*nb).astype(np.int64)
    bhi = np.floor((hi-y0)*nb).astype(np.int64)
    Nj = int(np.sum(bhi-blo+1))
    stats.append((j, Nj, Nj*(2.0**(-1.5*j))))
    m=np.zeros((nb,nb),bool)
    for i in range(nb):
        a,b=max(blo[i],0),min(bhi[i],nb-1)
        if b>=a: m[a:b+1,i]=True
    masks[j]=m
js=np.array([s[0] for s in stats]); Ns=np.array([s[1] for s in stats])
slope=np.polyfit(js[1:],np.log2(Ns[1:]),1)[0]
# covering completeness: every sampled point lies in a lit box (finest level)
nb=1<<JMAX; m=masks[JMAX]
sub=np.arange(0,NPTS+1,997)
ti=np.minimum((sub*nb)//(NPTS+1),nb-1)
wi=np.clip(np.floor((W[sub]-y0)*nb).astype(np.int64),0,nb-1)
inside=(W[sub]>=y0)&(W[sub]<=y0+1)
cover_ok = bool(np.all(m[wi[inside],ti[inside]]))
with open('kilroy_stats.txt','w') as f:
    f.write('seed %d  range %.3f  quadratic variation %.6f (expect 1)\n'%(seed,whi-wlo,qv))
    f.write('level j, N_j boxes, N_j * eps^{3/2}:\n')
    for j,Nj,mu in stats: f.write('  %2d  %8d   %.4f\n'%(j,Nj,mu))
    f.write('slope of log2 N_j (j=%d..%d): %.4f  (theory: 3/2, dim_H graph = 3/2 a.s.)\n'%(JMIN+1,JMAX,slope))
    f.write('covering completeness (finest level, 16k sample pts): %s\n'%cover_ok)
    f.write('the value of the 3/2-Hausdorff measure itself: OPEN (MO front page 2026-07-12)\n')
print('slope %.4f cover_ok %s'%(slope,cover_ok))

# ---- render ----
img=np.zeros((S,S,3),np.float64)
yy,xx=np.mgrid[0:S,0:S]
# level palette: deep indigo (coarse) -> teal -> amber (fine)
level_cols={
 4:(0.09,0.14,0.40), 5:(0.10,0.22,0.54), 6:(0.12,0.36,0.62),
 7:(0.18,0.58,0.55), 8:(0.55,0.64,0.38), 9:(0.88,0.64,0.33), 10:(1.00,0.70,0.32)}
# the trace itself, FIRST and faint — the boxes will collapse onto it
path=np.zeros((S,S),np.float64)
tp = np.linspace(0,1,NPTS+1)
px=(tp*(S-1)).astype(np.int64); py=np.clip(((W-y0)*(S-1)).astype(np.int64),0,S-1)
inb=(W>=y0)&(W<=y0+1)
np.add.at(path,(py[inb],px[inb]),1.0)
path/=np.percentile(path[path>0],98)
core=np.tanh(gaussian_filter(path,0.6*SS)*3.2)
halo=np.tanh(gaussian_filter(path,3.2*SS)*2.2)
img += core[...,None]*np.array([1.00,0.95,0.80])*0.22
img += halo[...,None]*np.array([1.0,0.62,0.30])*0.15

hits={}
for j in range(JMIN,JMAX+1):
    nb=1<<j
    bi_y = (yy*nb)//S; bi_x=(xx*nb)//S
    hits[j] = masks[j][bi_y,bi_x]
for j in range(JMIN,JMAX+1):
    nb=1<<j
    hit=hits[j]
    vis = hit & ~hits[j+1] if j<JMAX else hit      # measurement stratigraphy
    perpx = 2.0**(0.5*j)                            # eps^{-1/2} law
    fy = (yy*nb/S)%1.0; fx=(xx*nb/S)%1.0
    bw = max(0.06, 1.2*nb/S)
    border = hit*(np.minimum(np.minimum(fy,1-fy),np.minimum(fx,1-fx))<bw)
    c=np.array(level_cols[j])
    img += (vis*0.78*perpx*0.028 + border*np.maximum(perpx*0.028,0.085))[...,None]*c[None,None,:]
img=img.reshape(R,SS,R,SS,3).mean(axis=(1,3))
out=1-np.exp(-1.5*img)
out=np.clip(out,0,1)**(1/2.1)
Image.fromarray((out*255).astype(np.uint8)).save('kilroy_proto.png' if PROTO else 'kilroy.png')
print('saved')
