import numpy as np, sys, time
from PIL import Image
from scipy.ndimage import gaussian_filter

# Only Three Distances — the Steinhaus three-gap theorem as polar growth-rings.
# radius = time n (rings grow outward); angle = position x on the circle [0,1) the
# golden rotation acts on. Ring n is the partition of the circle by {k*alpha mod1 : k<=n};
# Steinhaus: at most THREE distinct gap-lengths exist at every n -> exactly 3 colours.
phi=(1+5**0.5)/2; alpha=phi-1
N    = int(sys.argv[1]) if len(sys.argv)>1 else 610   # number of growth rings
S    = int(sys.argv[2]) if len(sys.argv)>2 else 2048
SS   = int(sys.argv[3]) if len(sys.argv)>3 else 2
tag  = sys.argv[4] if len(sys.argv)>4 else ""
W=S*SS
t0=time.time()
cx=cy=W/2
r0=0.013*W; r1=0.478*W
yy,xx=np.mgrid[0:W,0:W]
dx=xx-cx; dy=yy-cy
rad=np.hypot(dx,dy); ang=(np.arctan2(dy,dx)/(2*np.pi))%1.0
nfloat=(rad-r0)/(r1-r0)*(N-1)
nidx=np.round(nfloat).astype(int)
valid=(rad>=r0)&(rad<=r1)
ringw=(r1-r0)/(N-1)
# class field (0,1,2) and "is this the smallest gap" highlight field
cls=np.full((W,W),-1,np.int16)
small=np.zeros((W,W),np.float32)   # 1 where gap is the smallest class (spiral arms)
gapnorm=np.zeros((W,W),np.float32) # gap length / max, for subtle shading
# precompute per-n breakpoints
ksum=(np.arange(N)*alpha)%1.0
for n in range(N):
    pts=np.sort(ksum[:n+1])
    gp=np.diff(np.concatenate([pts,[pts[0]+1]]))
    u=np.unique(np.round(gp,9)); su=sorted(u)
    rank={v:i for i,v in enumerate(su)}
    gc=np.array([min(rank[round(g,9)],2) for g in gp])
    m=valid&(nidx==n)
    if not m.any(): continue
    a=ang[m]
    idx=np.searchsorted(pts,a,side='right')-1
    idx[idx<0]=len(pts)-1
    cls[m]=gc[idx]
    small[m]=(gc[idx]==0).astype(np.float32)
    gapnorm[m]=(gp[idx]/gp.max()).astype(np.float32)
print("classified rings in",round(time.time()-t0,1),"s")

# build colour — cohesive jewel palette, smallest gap blazes, largest recedes
COL=np.array([[252,214,116],   # class0 smallest gap -> warm gold (the spiral arms)
              [58,160,182],     # class1 -> teal
              [86,52,120]],float)   # class2 largest gap -> deep violet (recedes)
img=np.zeros((W,W,3),float)
for c in range(3):
    img[cls==c]=COL[c]
# gentle radial depth: everything a touch brighter near centre (the seed)
rfac=(0.86+0.14*(1-(rad-r0)/(r1-r0)))[...,None]
img*=rfac
# void outside / centre seed
void=~valid
img[void]=np.array([6,8,14])
# glow on the gold spiral arms (smallest-gap class)
goldmask=(cls==0).astype(np.float32)
glow=gaussian_filter(goldmask,sigma=1.6*SS)
img+= (glow[...,None])*np.array([255,228,150])*0.22
# bright seed point at the very centre (the origin 0 of the rotation)
seed=np.exp(-(rad/(0.02*W))**2)
img+= seed[...,None]*np.array([255,240,210])*0.9
img=np.clip(img,0,255)
im=Image.fromarray(img.astype(np.uint8)).resize((S,S),Image.LANCZOS)
im.save(f"/home/user/claude-mythos-self-play/art_oua4/gap{tag}.png")
print("saved", f"gap{tag}.png", "in", round(time.time()-t0,1),"s")
