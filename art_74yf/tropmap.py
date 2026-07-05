"""
tropmap.py — 02: THE ORDER MAP (the straightened skeleton).
The tropical curve is the corner locus of  T(x,y)=max_{(i,j)} (v_{ij}+i x+j y),
v_{ij}=log|c_{ij}|.  Away from it, ONE term wins; that winning lattice point (i,j) is
exactly grad(Ronkin N) there (Forsberg-Passare-Tsikh: the amoeba complement component
of order (i,j)).  So the plane divides into flat regions, each NAMED by a Newton-polygon
lattice point, stitched along the razor-straight tropical roads.  This is what the
soft luminous amoeba (01) becomes when the logarithm is pushed to its limit: pure
combinatorics.  (Region labels were cross-checked against the true Ronkin gradient.)
Rendered analytically -> crisp at any resolution.
"""
import numpy as np
from PIL import Image
from scipy import ndimage

A = np.array([[0.0, np.sqrt(3)/2],[-1.0, 0.5]])

def lattice(d):
    return [(i,j) for i in range(d+1) for j in range(d+1) if i+j<=d]

def bary_color(i,j,d):
    k=d-i-j; s=i+j+k
    a,b,c=i/s,j/s,k/s
    C_i=np.array([214,150,58.]); C_j=np.array([58,150,205.]); C_k=np.array([172,80,192.])
    return a*C_i+b*C_j+c*C_k

def tropical_center(d,lam):
    """Centroid (in UV) of the bounded (interior-lattice-point) tropical regions."""
    pts=lattice(d); v={(i,j):-lam*(i*i+j*j+(d-i-j)**2) for (i,j) in pts}
    W=60.0; g=np.linspace(-W,W,600); UU,VV=np.meshgrid(g,g)
    Ainv=np.linalg.inv(A); XY=Ainv@np.vstack([UU.ravel(),VV.ravel()]); Xg,Yg=XY[0],XY[1]
    top1=np.full(Xg.shape,-1e30); arg=np.zeros(Xg.shape,int)
    for idx,(i,j) in enumerate(pts):
        t=v[(i,j)]+i*Xg+j*Yg; nt=t>top1; arg=np.where(nt,idx,arg); top1=np.where(nt,t,top1)
    interior=[idx for idx,(i,j) in enumerate(pts) if 0<i and 0<j and i+j<d]
    msk=np.isin(arg,interior)
    return UU.ravel()[msk].mean(), VV.ravel()[msk].mean()

def build(d,lam,half,S=2048,linew=1.3,glow=0.5,tag='tropmap',cu=None,cv=None):
    if cu is None: cu,cv=tropical_center(d,lam)
    pts=lattice(d)
    v={(i,j):-lam*(i*i+j*j+(d-i-j)**2) for (i,j) in pts}
    us=np.linspace(cu-half,cu+half,S); vs=np.linspace(cv-half,cv+half,S)
    UU,VV=np.meshgrid(us,vs)                       # (S,S), row=v col=u  (indexing xy)
    Ainv=np.linalg.inv(A); XY=Ainv@np.vstack([UU.ravel(),VV.ravel()])
    Xg=XY[0]; Yg=XY[1]
    top1=np.full(Xg.shape,-1e30); top2=np.full(Xg.shape,-1e30)
    arg=np.zeros(Xg.shape,int)
    for idx,(i,j) in enumerate(pts):
        t=v[(i,j)]+i*Xg+j*Yg
        nt=t>top1
        top2=np.where(nt,top1,np.maximum(top2,t))
        arg=np.where(nt,idx,arg); top1=np.where(nt,t,top1)
    gap=(top1-top2)
    # region colours
    col=np.zeros((Xg.size,3))
    for idx,(i,j) in enumerate(pts):
        msk=arg==idx
        if msk.any(): col[msk]=bary_color(i,j,d)
    col=col.reshape(S,S,3)
    gap=gap.reshape(S,S)
    # bounded (hole) vs unbounded region: bounded = interior lattice points
    interior=set((i,j) for (i,j) in pts if 0<i and 0<j and i+j<d)
    isint=np.zeros((S,S),bool)
    for idx,(i,j) in enumerate(pts):
        if (i,j) in interior: isint|= (arg.reshape(S,S)==idx)
    # dim the big unbounded regions a touch so the honeycomb pops
    col=col*np.where(isint[...,None],1.0,0.82)
    # tropical roads: crisp dark line where gap ~ 0.  width in tropical units:
    px=2*half/S
    # gap grows ~ |slope difference| * distance from curve; normalise by local grad scale
    w=linew*px* (d*0.5)
    line=np.exp(-(gap/ w)**2)
    core=np.exp(-(gap/(w*0.42))**2)              # thin bright filament on the road
    # dark trough flanking the glowing road (gives the network relief)
    road_dark=np.clip(line*1.15,0,1)
    col=col*(1-0.78*road_dark[...,None])
    if glow>0:
        halo=ndimage.gaussian_filter(line,S/600)
        col=col+glow*halo[...,None]*np.array([46,150,175.])
        col=col+core[...,None]*np.array([150,224,236.])*0.95   # luminous cyan core
    # orient: flip rows so V increases upward
    out=col[::-1]
    Image.fromarray(np.clip(out,0,255).astype(np.uint8)).save(f'{tag}.png')
    print(tag,'saved  regions used=',len(set(arg.tolist()[:0]) or set(np.unique(arg))))

if __name__=='__main__':
    import sys
    d=int(sys.argv[1]); lam=float(sys.argv[2]); half=float(sys.argv[3])
    S=int(sys.argv[4]) if len(sys.argv)>4 else 2048
    build(d,lam,half,S=S,tag=sys.argv[5] if len(sys.argv)>5 else 'tropmap')
