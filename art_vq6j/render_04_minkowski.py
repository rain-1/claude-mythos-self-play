import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
from qvec import Q_vec
import sys,time

def chaos(W,H,chains,T,burn,seed=1,batch=250000):
    dens=np.zeros(H*W); hsum=np.zeros(H*W); rng=np.random.default_rng(seed); done=0; t0=time.time()
    while done<chains:
        nb=min(batch,chains-done); done+=nb
        x=rng.random(nb); y=rng.random(nb)
        for t in range(T):
            m=rng.random(nb)<0.5
            x=np.where(m,x/(1+x),1/(2-x)); y=np.where(m,y/2,(1+y)/2)
            if t>=burn:
                fx=x*(W-1); fy=(1-y)*(H-1)
                ix=np.clip(np.floor(fx).astype(int),0,W-2); iy=np.clip(np.floor(fy).astype(int),0,H-2)
                dx=fx-ix; dy=fy-iy
                for ox,oy,wt in [(0,0,(1-dx)*(1-dy)),(1,0,dx*(1-dy)),(0,1,(1-dx)*dy),(1,1,dx*dy)]:
                    idx=(iy+oy)*W+(ix+ox); np.add.at(dens,idx,wt); np.add.at(hsum,idx,wt*y)
        print("  batch",done,"t=%.1f"%(time.time()-t0)); sys.stdout.flush()
    return dens.reshape(H,W),hsum.reshape(H,W)

def render(S=2048, fname="04_singular_staircase.png", seed=1):
    W=H=S; t0=time.time()
    dens,hsum=chaos(W,H,1000000,220,40,seed)
    print("chaos t=%.1f"%(time.time()-t0))
    nz=dens>0; ld=np.log1p(dens); eq=np.zeros_like(ld)
    f=ld[nz]; o=np.argsort(f); rk=np.empty_like(f); rk[o]=np.arange(len(f)); eq[nz]=rk/max(1,len(f)-1)
    inten=eq
    # ANALYTIC column height profile (exact ?(x), gap-free) — image row of the curve
    xs=np.linspace(0,1,W); qx=Q_vec(xs)
    prof=(1-qx)*(H-1)
    rowidx=np.arange(H)[:,None]; below=(rowidx>prof[None,:]).astype(float)
    # ---- background: dawn gradient + faint nebula veil from the ?-warp ----
    yy=np.linspace(0,1,H)
    bg=np.zeros((H,W,3))
    top=np.array([0.045,0.045,0.11]); mid=np.array([0.12,0.06,0.15]); bot=np.array([0.02,0.02,0.055])
    for k in range(3): bg[...,k]=np.interp(yy,[0,0.55,1],[top[k],mid[k],bot[k]])[:,None]
    QX,QY=np.meshgrid(qx,Q_vec(np.linspace(0,1,H)))
    veil=0.5+0.5*np.sin(2*np.pi*2*QX+1.4*np.sin(2*np.pi*1.5*QY))
    veil=gaussian_filter(veil,22)
    bg+= (veil[...,None]-0.5)*np.array([0.035,0.022,0.05])
    img=np.clip(bg,0,1)
    # ---- under-curve valley glow ----
    bodyglow=gaussian_filter(below,(10,10))
    img+= bodyglow[...,None]*np.array([0.16,0.06,0.15])*0.7
    # ---- luminous curve, warm, multi-scale bloom ----
    t=np.clip(hsum/np.maximum(dens,1e-9),0,1)
    cs=np.array([[0.92,0.22,0.42],[1.0,0.5,0.22],[1.0,0.86,0.55]]); pos=np.array([0,0.5,1.0])
    ccol=np.stack([np.interp(t,pos,cs[:,k]) for k in range(3)],-1)
    core=(inten[...,None])*ccol
    soft=np.zeros_like(core)
    for s,a in [(1.5,0.8),(4,0.55),(11,0.32),(26,0.20)]:
        for k in range(3): soft[...,k]+=a*gaussian_filter(core[...,k],s)
    img+= core*1.15 + soft
    # soft warm 'lanterns' where the simplest rationals rest on the curve (self-similar step centres)
    from mink import Q_cf
    XX,YY=np.meshgrid(np.arange(W),np.arange(H))
    for p,q in [(1,2),(1,3),(2,3),(1,4),(3,4),(2,5),(3,5)]:
        xc=p/q*(W-1); yc=(1-Q_cf(p/q))*(H-1); sg=W*0.018*(1+0.4*q)
        blob=np.exp(-(((XX-xc)**2+(YY-yc)**2)/(2*sg*sg)))
        img+= blob[...,None]*np.array([1.0,0.72,0.42])*(0.10/q)
    img=np.clip(img,0,1)
    Image.fromarray((img*255).astype(np.uint8)).save(fname)
    print("SAVED",fname,(W,H),"t=%.1f"%(time.time()-t0))

if __name__=="__main__":
    render(int(sys.argv[1]) if len(sys.argv)>1 else 2048)
