# uncovered components inside the window vs N, at raster resolution (same RNG as lightbox.py)
import sys, numpy as np
from scipy.ndimage import label
S=int(sys.argv[1]); Nmax=int(sys.argv[2]); seed=int(sys.argv[3])
R=0.40*S; cx=cy=S/2
rng=np.random.default_rng(seed); u=rng.random(10**6)[:Nmax]; th=rng.random(10**6)[:Nmax]*2*np.pi
X=np.sqrt(u)*np.cos(th); Y=np.sqrt(u)*np.sin(th); r=1/np.sqrt(np.arange(1,Nmax+1))
yy,xx=np.mgrid[0:S,0:S].astype(np.float32)
unc=(np.hypot(xx-cx,yy-cy)<R)
marks=set(int(v) for v in np.unique(np.round(np.logspace(1,np.log10(Nmax),40))))
for n in range(Nmax):
    rp=r[n]*R; px=cx+X[n]*R; py=cy+Y[n]*R
    x0=max(int(px-rp-1),0);x1=min(int(px+rp+2),S);y0=max(int(py-rp-1),0);y1=min(int(py+rp+2),S)
    if x1>x0 and y1>y0:
        unc[y0:y1,x0:x1]&=~(np.hypot(xx[y0:y1,x0:x1]-px,yy[y0:y1,x0:x1]-py)<rp)
    if n+1 in marks:
        lab,k=label(unc); 
        cs=[] 
        if k:
            idx=np.argwhere(unc); rr=np.hypot(idx[:,1]-cx,idx[:,0]-cy)/R
            cs=[round(float(rr.min()),3),round(float(rr.max()),3)]
        print(n+1,k,int(unc.sum()),cs,flush=True)
        if k==0: break
