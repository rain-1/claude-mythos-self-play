import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
from cascade_core import cascade, verify_interlacing

z=np.load("zeta_zeros.npy")
lev=cascade(z)
N=len(lev)
assert verify_interlacing(lev)

S=2400
W=H=S
xmin,xmax=z.min()-4,z.max()+4
mgL,mgR,mgT,mgB=0.06,0.06,0.05,0.07
def X(x): return (mgL+ (x-xmin)/(xmax-xmin)*(1-mgL-mgR))*(W-1)
def Y(k): return (H-1)-(mgB+ (k/(N-1))*(1-mgT-mgB))*(H-1)

edge=np.zeros((H,W)); node=np.zeros((H,W)); nodeg=np.zeros((H,W))
def line(acc,x0,y0,x1,y1,amp):
    n=int(abs(x1-x0)+abs(y1-y0))+2
    xs=np.linspace(x0,x1,n); ys=np.linspace(y0,y1,n)
    ix=xs.astype(int); iy=ys.astype(int)
    m=(ix>=0)&(ix<W)&(iy>=0)&(iy<H)
    np.add.at(acc,(iy[m],ix[m]),amp)

# edges: interlacing lamination (each node connects down to its two brackets)
for k in range(N-1):
    a=lev[k]; b=lev[k+1]
    y0=Y(k); y1=Y(k+1)
    for j in range(len(b)):
        xb=X(b[j])
        line(edge,X(a[j]),y0,xb,y1,1.0)
        line(edge,X(a[j+1]),y0,xb,y1,1.0)

# nodes; base row (zeta zeros) get their own channel (gold), rest cool
def splat(acc,x,y,s,amp):
    i0=int(max(0,y-4*s));i1=int(min(H,y+4*s));j0=int(max(0,x-4*s));j1=int(min(W,x+4*s))
    if i1<=i0 or j1<=j0:return
    yy=np.arange(i0,i1)[:,None];xx=np.arange(j0,j1)[None,:]
    acc[i0:i1,j0:j1]+=amp*np.exp(-((xx-x)**2+(yy-y)**2)/(2*s*s))
for k in range(N):
    for x in lev[k]:
        splat(node,X(x),Y(k),1.6,1.0)
for x in lev[0]:
    splat(nodeg,X(x),Y(0),3.0,1.2)          # zeta zeros base, brighter gold
splat(nodeg,X(lev[-1][0]),Y(N-1),5.0,2.0)   # apex (the mean) blaze

# compose
edge/=np.percentile(edge[edge>0],99.7)+1e-9; edge=np.clip(edge,0,1)
node/=node.max()+1e-9; nodeg/=nodeg.max()+1e-9
img=np.zeros((H,W,3))
# level gradient tint on edges: cool indigo (top/apex) -> teal (base)
yy=np.linspace(0,1,H)[:,None]
tint=(1-yy)[...,None]*np.array([0.10,0.28,0.42])+yy[...,None]*np.array([0.16,0.20,0.48])
img+=edge[...,None]*tint*1.5
img+=node[...,None]*np.array([0.55,0.85,1.0])*0.8
img+=nodeg[...,None]*np.array([1.0,0.8,0.35])*1.2
glow=np.stack([gaussian_filter(img[...,c],5) for c in range(3)],-1)
img=img+glow*0.55
img=np.clip(img,0,1)**(1/1.6)
Image.fromarray((img*255).astype(np.uint8)).save("03_cascade_of_rolle.png")
print("saved 03_cascade_of_rolle.png interlacing:",verify_interlacing(lev),"levels",N)
