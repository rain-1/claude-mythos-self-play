import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
from vkls import plancherel_shape, profile, Omega
import sys,time

UMAX=2.5; WMAX=2.62

def prof_on(xs,n,seed):
    lam=plancherel_shape(n,seed); sn=np.sqrt(n)
    ru,rphi=profile(lam); ru=ru/sn; rphi=rphi/sn
    return np.maximum(np.interp(xs,ru,rphi),np.abs(xs)), lam, sn

def line_buf(xs,ph,Wpx,Hpx,width):
    yp=(WMAX-ph)/WMAX*(Hpx-1); buf=np.zeros((Hpx,Wpx))
    for i in range(Wpx-1):
        a,b=yp[i],yp[i+1]; lo,hi=int(min(a,b)),int(max(a,b)); buf[max(0,lo):min(Hpx,hi+1),i]=1
    return gaussian_filter(buf,width)

def render(Wpx=2048, nhero=5200, fname="05_limit_shape.png"):
    Hpx=int(Wpx*WMAX/(2*UMAX)); t0=time.time()
    xs=np.linspace(-UMAX,UMAX,Wpx); ws=np.linspace(WMAX,0,Hpx)
    RU,RW=np.meshgrid(xs,ws)
    img=np.zeros((Hpx,Wpx,3))
    # hero diagram cells (content bands + grout)
    lam=plancherel_shape(nhero,seed=7); sn=np.sqrt(nhero)
    r=len(lam); lam_arr=np.array(lam)
    U=RU*sn; W=RW*sn                       # unscaled russian coords
    i_idx=np.round((W-U-1)/2).astype(np.int64)
    j_idx=np.round((U+W-1)/2).astype(np.int64)
    valid=(i_idx>=0)&(i_idx<r)
    ii=np.clip(i_idx,0,r-1)
    rowlen=lam_arr[ii]
    present=valid&(j_idx>=0)&(j_idx<rowlen)
    content=(j_idx-i_idx)/(2*np.sqrt(nhero))+0.5   # normalized content 0..1
    cs=np.array([[0.85,0.28,0.55],[0.42,0.30,0.85],[0.12,0.55,0.85],[0.10,0.78,0.72],[0.95,0.78,0.32]])
    pos=np.array([0,0.3,0.5,0.7,1.0])
    cs=cs*0.88+(cs@np.array([0.299,0.587,0.114]))[:,None]*0.12   # deepen/desaturate for set cohesion
    col=np.stack([np.interp(np.clip(content,0,1),pos,cs[:,k]) for k in range(3)],-1)
    # depth: brighter higher up the stack (w), subtle
    depth=0.45+0.55*np.clip(W/ (np.interp(RU,xs,prof_on(xs,nhero,7)[0])*sn+1e-6),0,1)
    cell=col*depth[...,None]
    # grout: diamond edges where frac of rotated lattice near 0.5
    fu=np.abs(((U+W)/2)%1-0.5); fv=np.abs(((W-U)/2)%1-0.5)
    grout=np.minimum(fu,fv)
    grm=np.clip((grout-0.18)/0.32,0,1)     # 1 in cell interior, ->0 at edge
    cell*=(0.45+0.55*grm)[...,None]
    img+=np.where(present[...,None],cell,0.0)
    print("cells t=%.1f"%(time.time()-t0))
    # ghost convergence curves (small + medium n)
    for k,(n,c) in enumerate([(110,[0.95,0.35,0.6]),(900,[0.4,0.6,0.95])]):
        ph,_,_=prof_on(xs,n,30+k)
        img+=line_buf(xs,ph,Wpx,Hpx,1.0)[...,None]*np.array(c)*0.5
    # hero jagged boundary (bright)
    phh,_,_=prof_on(xs,nhero,7)
    img+=line_buf(xs,phh,Wpx,Hpx,1.0)[...,None]*np.array([0.6,0.9,1.0])*0.6
    # smooth Omega gold
    img+=line_buf(xs,Omega(xs),Wpx,Hpx,1.8)[...,None]*np.array([1.0,0.86,0.42])*1.35
    for c in range(3): img[...,c]+=0.28*gaussian_filter(img[...,c],sigma=2.6)
    img=np.clip(img,0,1)
    Image.fromarray((img*255).astype(np.uint8)).save(fname)
    print("SAVED",fname,(Wpx,Hpx),"t=%.1f"%(time.time()-t0))

if __name__=="__main__":
    render(int(sys.argv[1]) if len(sys.argv)>1 else 2048)
