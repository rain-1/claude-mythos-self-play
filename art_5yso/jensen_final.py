import numpy as np, pickle
from PIL import Image
from scipy.ndimage import gaussian_filter
from numpy.polynomial.hermite import hermgauss

data=pickle.load(open("jensen_roots.pkl","rb"))
D=32; K=62
W,H=2100,2400
jac=np.zeros((H,W)); gold=np.zeros((H,W)); line_acc=np.zeros((H,W))
cx=W*0.5; smax=np.sqrt(2*D); pscale=0.46*W/smax
def Yd(d): return (H-1)-((d-1)/(D-1))*(H-1)*0.9-0.05*H
def splat(acc,x,y,s,amp):
    i0=int(max(0,y-4*s));i1=int(min(H,y+4*s));j0=int(max(0,x-4*s));j1=int(min(W,x+4*s))
    if i1<=i0 or j1<=j0:return
    yy=np.arange(i0,i1)[:,None];xx=np.arange(j0,j1)[None,:]
    g=amp*np.exp(-((xx-x)**2+(yy-y)**2)/(2*s*s))
    acc[i0:i1,j0:j1]=np.maximum(acc[i0:i1,j0:j1],g)   # max-composite: no additive streak

hyperbolic_all=True
for d in range(1,D+1):
    ns=[n for n in range(0,K-d+1) if (d,n) in data and np.all(np.isfinite(data[(d,n)]))]
    if not ns: continue
    n=ns[-1]
    r=np.sort(data[(d,n)]); rz=(r-r.mean())/(r.std()+1e-12)
    hzs=np.sort(hermgauss(d)[0]); hsd=hzs.std(); jx=rz*hsd
    y=Yd(d)
    amp=0.9
    for v in jx: splat(jac,cx+v*pscale,y,2.2,amp)
    for h in hzs: splat(gold,cx+h*pscale,y,1.8,0.7)
    # faint horizontal "reality line" for this row (all roots lie on the real axis)
    x0=int(cx+jx.min()*pscale); x1=int(cx+jx.max()*pscale); iy=int(y)
    if 0<=iy<H:
        xa,xb=max(0,x0),min(W,x1+1)
        line_acc[iy, xa:xb]=np.maximum(line_acc[iy,xa:xb],0.16)

jac=np.clip(jac,0,1); gold=np.clip(gold,0,1)
img=np.zeros((H,W,3))
img+=line_acc[...,None]*np.array([0.20,0.34,0.42])
img+=jac[...,None]*np.array([0.45,0.9,1.0])*1.35
img+=gold[...,None]*np.array([0.95,0.7,0.25])*0.72
glow=np.stack([gaussian_filter(img[...,c],5) for c in range(3)],-1)
img=img+glow*0.6
img=np.clip(img,0,1)**(1/1.5)
Image.fromarray((img*255).astype(np.uint8)).save("02_the_hermite_chalice.png")
print("saved 02_the_hermite_chalice.png")
