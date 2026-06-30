import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter
import sys,time

def chaos(W, total_chains, T, burn, seed=1, batch=250000):
    dens=np.zeros(W*W,np.float64); ysum=np.zeros(W*W,np.float64)
    rng=np.random.default_rng(seed); done=0; t0=time.time()
    while done<total_chains:
        nb=min(batch,total_chains-done); done+=nb
        x=rng.random(nb); y=rng.random(nb)
        for t in range(T):
            m=rng.random(nb)<0.5
            x=np.where(m,x/(1.0+x),1.0/(2.0-x))
            y=np.where(m,y/2.0,(1.0+y)/2.0)
            if t>=burn:
                fx=x*(W-1); fy=(1.0-y)*(W-1)
                ix=np.clip(np.floor(fx).astype(np.int64),0,W-2); iy=np.clip(np.floor(fy).astype(np.int64),0,W-2)
                dx=fx-ix; dy=fy-iy
                for ox,oy,wx,wy in [(0,0,1-dx,1-dy),(1,0,dx,1-dy),(0,1,1-dx,dy),(1,1,dx,dy)]:
                    idx=(iy+oy)*W+(ix+ox); w=wx*wy
                    np.add.at(dens,idx,w); np.add.at(ysum,idx,w*y)
        print("  batch done=%d t=%.1f"%(done,time.time()-t0)); sys.stdout.flush()
    return dens.reshape(W,W),ysum.reshape(W,W)

def sb_boxes(depth):
    out=[]
    def rec(aL,aQ,bL,bQ,lvl):
        if lvl>depth: return
        out.append((lvl,aL[0]/aL[1],bL[0]/bL[1],aQ,bQ))
        mp=aL[0]+bL[0]; mq=aL[1]+bL[1]; mQ=(aQ+bQ)/2
        rec(aL,aQ,(mp,mq),mQ,lvl+1); rec((mp,mq),mQ,bL,bQ,lvl+1)
    rec((0,1),0.0,(1,1),1.0,1); return out

def render(S=2048, chains=900000, fname="04_singular_staircase.png"):
    W=S; t0=time.time()
    dens,ysum=chaos(W,chains,240,40)
    print("chaos t=%.1f"%(time.time()-t0))
    nz=dens>0; ld=np.log1p(dens); eq=np.zeros_like(ld)
    flat=ld[nz]; order=np.argsort(flat); ranks=np.empty_like(flat); ranks[order]=np.arange(len(flat))
    eq[nz]=ranks/max(1,len(flat)-1)
    my=np.zeros_like(dens); my[nz]=ysum[nz]/dens[nz]
    cs=np.array([[0.62,0.20,0.66],[0.24,0.40,0.95],[0.10,0.82,0.82],[1.0,0.86,0.34]]); pos=np.array([0,0.4,0.7,1.0])
    curve=np.stack([np.interp(np.clip(my,0,1),pos,cs[:,k]) for k in range(3)],-1)*eq[...,None]
    box=Image.new("RGB",(W,W),(0,0,0)); db=ImageDraw.Draw(box)
    for lvl,x0,x1,y0,y1 in sb_boxes(7):
        f=0.64**lvl; c=(int(235*f),int(150*f),int(80*f))
        db.rectangle([x0*(W-1),(1-y1)*(W-1),x1*(W-1),(1-y0)*(W-1)],outline=c,width=1)
    boxarr=gaussian_filter(np.asarray(box).astype(np.float64)/255,sigma=(0.7,0.7,0))
    img=boxarr*0.95+curve
    for k in range(3): img[...,k]+=0.6*gaussian_filter(curve[...,k],sigma=2.0)+0.28*gaussian_filter(curve[...,k],sigma=7.0)
    img=np.clip(img,0,1)
    Image.fromarray((img*255).astype(np.uint8)).save(fname); print("SAVED",fname,(W,W),"t=%.1f"%(time.time()-t0))

if __name__=="__main__":
    S=int(sys.argv[1]) if len(sys.argv)>1 else 2048
    ch=int(sys.argv[2]) if len(sys.argv)>2 else 900000
    render(S,ch)
