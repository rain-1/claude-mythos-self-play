import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter
import time, sys

def glauber(a,b,c,sweeps,seed=0):
    rng=np.random.default_rng(seed)
    I,J=np.mgrid[0:a,0:b]
    h=np.clip(np.round(c*(1-(I+J)/(a+b-2+1e-9))),0,c).astype(np.int32)
    h=np.minimum.accumulate(h,axis=0); h=np.minimum.accumulate(h,axis=1)
    parity=(I+J)%2; t0=time.time()
    for s in range(sweeps):
        for p in (0,1):
            U=np.empty_like(h);U[1:,:]=h[:-1,:];U[0,:]=c
            L=np.empty_like(h);L[:,1:]=h[:,:-1];L[:,0]=c
            D=np.empty_like(h);D[:-1,:]=h[1:,:];D[-1,:]=0
            R=np.empty_like(h);R[:,:-1]=h[:,1:];R[:,-1]=0
            ci=(h+1<=U)&(h+1<=L)&(h+1<=c); cd=(h-1>=D)&(h-1>=R)&(h-1>=0)
            d=rng.integers(0,2,size=h.shape)*2-1; mask=(parity==p)
            h=h+(mask&(d==1)&ci).astype(np.int32)-(mask&(d==-1)&cd).astype(np.int32)
        if s%(sweeps//6)==0: print("  sweep",s,"t=%.1f"%(time.time()-t0)); sys.stdout.flush()
    ok=np.all(h[:-1,:]>=h[1:,:]) and np.all(h[:,:-1]>=h[:,1:]) and h.min()>=0 and h.max()<=c
    print("valid",ok,"vol frac",round(h.sum()/(a*b*c),4),"t=%.1f"%(time.time()-t0))
    return h

def render(h,a,b,c,u,ss,fname):
    t0=time.time()
    cos30=np.cos(np.pi/6)
    def P(x,y,z): return ((x-y)*cos30,(x+y)*0.5-z)
    pts=[(0,0,0),(b,0,0),(0,a,0),(b,a,0),(0,0,c),(b,0,c),(0,a,c),(b,a,c)]
    XY=[P(*p) for p in pts]; xs=[p[0] for p in XY]; ys=[p[1] for p in XY]
    minX,maxX,minY,maxY=min(xs),max(xs),min(ys),max(ys)
    W=int((maxX-minX)*u)+12; H=int((maxY-minY)*u)+12
    img=Image.new("RGB",(W*ss,H*ss),(4,5,12)); dr=ImageDraw.Draw(img)
    def sc(x,y,z):
        X,Y=P(x,y,z); return ((X-minX)*u*ss+6*ss,(Y-minY)*u*ss+6*ss)
    C_TOP=(255,201,84); C_FRONT=(34,166,182); C_RIGHT=(72,84,182)
    def shade(col,z):
        f=0.38+0.62*(z/c); return tuple(int(min(255,cc*f)) for cc in col)
    order=sorted([(i,j) for i in range(a) for j in range(b)],key=lambda t:(t[0]+t[1]))
    for (i,j) in order:
        x=j;y=i;ht=h[i,j]
        h_r=h[i,j+1] if j+1<b else 0
        h_d=h[i+1,j] if i+1<a else 0
        for k in range(h_r,ht):
            dr.polygon([sc(x+1,y,k),sc(x+1,y+1,k),sc(x+1,y+1,k+1),sc(x+1,y,k+1)],fill=shade(C_RIGHT,k+1))
        for k in range(h_d,ht):
            dr.polygon([sc(x,y+1,k),sc(x+1,y+1,k),sc(x+1,y+1,k+1),sc(x,y+1,k+1)],fill=shade(C_FRONT,k+1))
        dr.polygon([sc(x,y,ht),sc(x+1,y,ht),sc(x+1,y+1,ht),sc(x,y+1,ht)],fill=shade(C_TOP,ht))
    print("polys drawn t=%.1f"%(time.time()-t0))
    arr=np.asarray(img).astype(np.float32)/255
    lum=arr.mean(2); m=np.clip(lum-0.45,0,1)
    for k in range(3): arr[...,k]=np.clip(arr[...,k]+0.15*gaussian_filter(m*arr[...,k],sigma=ss*1.6),0,1)
    out=Image.fromarray((arr*255).astype(np.uint8))
    if ss>1: out=out.resize((W,H),Image.LANCZOS)
    out.save(fname); print("SAVED",fname,out.size,"t=%.1f"%(time.time()-t0))

if __name__=="__main__":
    a,b,c=300,216,198
    h=glauber(a,b,c,60000,seed=11)
    np.save("_loz_h.npy",h)
    render(h,a,b,c,u=5.6,ss=2,fname="02_arctic_ellipse.png")
