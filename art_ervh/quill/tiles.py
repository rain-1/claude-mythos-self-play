"""Build quilled tiles: unit square frame + unit-side polygon + coil-filled regions."""
import numpy as np
from scipy import ndimage as ndi
from matplotlib.path import Path
import quill as Q

def zigzag(n, eps=0.02):
    """odd n=2k+1: k teeth between left and right walls, closed by one edge (MO's construction)."""
    k=(n-1)//2
    # vertices along bottom row at x=0..1, apexes up; we build: chain of 2k unit edges zig-zagging
    # between y=a and y=b with horizontal advance 1/k per tooth, closed by the unit edge on y=a.
    dx=1.0/(2*k)
    dy=np.sqrt(1-dx*dx)
    pts=[]
    for i in range(2*k+1):
        x=i*dx; y=eps if i%2==0 else eps+dy
        pts.append((x,y))
    # chain from (0,eps) to (1,eps) has 2k edges; close with the bottom edge back (unit) -> 2k+1 sides
    return np.array(pts)

WARM=[(1.0,0.66,0.62),(1.0,0.74,0.58),(1.0,0.86,0.56),(1.0,0.70,0.80),(0.98,0.64,0.72)]
COOL=[(0.62,0.84,1.0),(0.66,0.92,0.80),(0.76,0.74,1.0),(0.86,0.72,0.98),(0.62,0.90,0.92),(0.78,0.92,0.66)]
PAPER=np.array([0.985,0.982,0.978])

def card(N, seed=0):
    rng=np.random.default_rng(seed)
    A=np.ones((N[0],N[1],3),np.float32)*PAPER
    A*= (1-0.025*ndi.gaussian_filter(rng.random(N),0.8)[...,None]).astype(np.float32)
    return np.zeros(N,np.float32), A

def tile(H, A, poly, ox, oy, S, warm, cools, frame_col=(0.97,0.95,0.90), poly_col=None,
         hgt=24.0, wall=3.2, pitch=22, sw=2.3, exception=False, flipy=True, smooth=8, Sy=None, G=None):
    Sy = S if Sy is None else Sy
    """draw one tile with the unit square at (ox,oy) size S px. poly in unit coords."""
    sq=np.array([[0,0],[1,0],[1,1],[0,1]],float)
    def tr(p):
        p=np.asarray(p,float).copy()
        q=np.empty_like(p); q[:,0]=ox+p[:,0]*S; q[:,1]=oy+(1-p[:,1])*Sy if flipy else oy+p[:,1]*Sy
        return q
    P=tr(poly); SQ=tr(sq)
    pad=int(hgt*2)
    x0,y0=int(ox-pad),int(oy-pad); x1,y1=int(ox+S+pad),int(oy+Sy+pad)
    Hs=H[y0:y1,x0:x1]; As=A[y0:y1,x0:x1]
    off=np.array([x0,y0])
    shp=Hs.shape
    d_sq=Q.seg_dist(Q.poly_segs(SQ-off),shp)
    d_p=Q.seg_dist(Q.poly_segs(P-off),shp) if not exception else d_sq
    yy,xx=np.mgrid[0:shp[0],0:shp[1]]; pts=np.c_[xx.ravel()+.5,yy.ravel()+.5]
    in_sq=Path(SQ-off).contains_points(pts).reshape(shp)
    in_p=Path(P-off).contains_points(pts).reshape(shp)
    gap=wall/2+2.0
    free=(d_sq>gap)&(d_p>gap)&in_sq
    lab,nr=ndi.label(free)
    ci=0
    sizes=ndi.sum(free,lab,range(1,nr+1))
    order=np.argsort(-sizes)
    for r in order+1:
        msk=lab==r
        if msk.sum()<30: continue
        ins=in_p[msk].mean()>.5
        c=warm if ins else cools[ci%len(cools)]
        if not ins: ci+=1
        Q.coil(Hs,As,msk,pitch=pitch,width=sw,height=hgt*0.78,col=c,smooth=smooth)
    if not exception:
        pc=poly_col if poly_col is not None else tuple(np.array(warm)**1.6*0.97)
        prof=Q.wall_profile(d_p,wall*1.5)
        Q.put(Hs,As,prof,hgt*1.12,pc)
        # gilded top edge: a thin bright band only on the strip's top (marks the polygon)
        if G is not None:
            gild=np.clip(1.3-d_p/(wall*0.75),0,1)
            Gs=G[y0:y1,x0:x1]; np.maximum(Gs,gild.astype(np.float32),out=Gs)
    Q.put(Hs,As,Q.wall_profile(d_sq,wall*1.15),hgt*1.04,frame_col)
    # the card itself: a slightly raised white board under the tile
    return d_sq
