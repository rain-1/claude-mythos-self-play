"""
hero.py — 01: THE AMOEBA and its tropical spine.
The log-modulus shadow of a complex plane curve, three-fold symmetric,
with the piecewise-linear tropical curve (the 'straightened' skeleton) overlaid.
Concept: the logarithm turns a curved analytic object (the amoeba flesh) into a
combinatorial one (the tropical spine).  Tentacles = the ends / 'sides' the number
line grows toward; holes = bounded complement components (Newton-polygon interior
lattice points).
"""
import numpy as np
from tropical import sample_curve
from PIL import Image
from scipy import ndimage

# symmetric embedding: tentacle dirs (-1,0),(0,-1),(1,1) -> 120 apart
SQ3 = np.sqrt(3)
A = np.array([[0.0, SQ3/2],[-1.0, 0.5]])

def curve(d, lam):
    C=np.zeros((d+1,d+1),complex)
    val={}
    for i in range(d+1):
        for j in range(d+1):
            if i+j<=d:
                k=d-i-j; q=i*i+j*j+k*k
                val[(i,j)]=-lam*q
                C[i,j]=((-1)**(i+j))*np.exp(-lam*q)
    return C, val

def tropical_field(val, d, cu, cv, half, S):
    """Rasterise the tropical curve (corner locus of max term) in embedded UV.
    Returns a float mask in [0,1] that is bright ON the spine."""
    # grid in UV
    us=np.linspace(cu-half,cu+half,S); vs=np.linspace(cv-half,cv+half,S)
    UU,VV=np.meshgrid(us,vs);
    # invert embed: (x,y) = A^{-1} (u,v)
    Ainv=np.linalg.inv(A)
    XY=Ainv@np.vstack([UU.ravel(),VV.ravel()])
    Xg=XY[0]; Yg=XY[1]
    top1=np.full(Xg.shape,-1e30); top2=np.full(Xg.shape,-1e30)
    for (i,j),v in val.items():
        t=v+i*Xg+j*Yg
        newtop=t>top1
        top2=np.where(newtop,top1,np.maximum(top2,t))
        top1=np.where(newtop,t,top1)
    gap=(top1-top2).reshape(S,S)
    return gap, (us,vs)

def autoframe(U,V,frac=0.18,pad=0.16):
    Hc,ue,ve=np.histogram2d(U,V,bins=240)
    uc=0.5*(ue[:-1]+ue[1:]); vc=0.5*(ve[:-1]+ve[1:])
    body=Hc>frac*Hc.max()
    # true symmetry center = centroid of the body mass
    UU,VV=np.meshgrid(uc,vc,indexing='ij')
    cu=UU[body].mean(); cv=VV[body].mean()
    # span = max distance from center to a body cell (covers holes+near tentacle bases)
    ui=np.where(body.any(1))[0]; vi=np.where(body.any(0))[0]
    s=max(ue[ui[-1]+1]-ue[ui[0]], ve[vi[-1]+1]-ve[vi[0]])
    return cu,cv,s*(0.5+pad)

def d3_group():
    """The 6 exact 2x2 matrices of D3 acting on embedded UV coords."""
    R=np.array([[np.cos(2*np.pi/3),-np.sin(2*np.pi/3)],
                [np.sin(2*np.pi/3), np.cos(2*np.pi/3)]])
    Swap=np.array([[0.,1.],[1.,0.]])
    M=A@Swap@np.linalg.inv(A)          # the amoeba's true mirror (i<->j)
    els=[np.eye(2),R,R@R]
    els+=[M,M@R,M@R@R]
    return els

def d3_orbit(U, V, cu, cv):
    """Apply the 6 elements of D3 to points about (cu,cv); return stacked U,V."""
    du,dv=U-cu,V-cv
    Us=[]; Vs=[]
    for G in d3_group():
        ru=G[0,0]*du+G[0,1]*dv; rv=G[1,0]*du+G[1,1]*dv
        Us.append(cu+ru); Vs.append(cv+rv)
    return np.concatenate(Us), np.concatenate(Vs)

def build(d, lam, S=1100, Nx=2200, Nth=3000, dens_gamma=1.0, tag='hero_dev'):
    C,val=curve(d,lam)
    zr=(-lam*d*3-2, lam*d*3+2)
    X,Y,TH,PH=sample_curve(C,zr,Nx,Nth)
    m=np.isfinite(Y)&np.isfinite(X); X,Y=X[m],Y[m]
    P=A@np.vstack([X,Y]); U,V=P[0],P[1]
    cu,cv,half=autoframe(U,V)
    U,V=d3_orbit(U,V,cu,cv)   # symmetrize the point cloud (crisp)
    H,_,_=np.histogram2d(U,V,bins=S,range=[[cu-half,cu+half],[cv-half,cv+half]])
    H=H.T[::-1]
    dens=np.log1p(H)
    dens/=dens.max()+1e-9
    # tropical spine
    gap,_=tropical_field(val,d,cu,cv,half,S)
    gap=gap[::-1]  # match image orientation (V axis flipped)
    np.save(f'{tag}_dens.npy',dens); np.save(f'{tag}_gap.npy',gap)
    np.savez(f'{tag}_meta.npz',cu=cu,cv=cv,half=half,S=S,d=d,lam=lam)
    prev=(255*np.clip(dens**0.8,0,1)).astype(np.uint8)
    Image.fromarray(prev).save(f'{tag}_dens.png')
    print(tag,'built. shape',dens.shape,'half',round(half,2))
    return dens,gap,(cu,cv,half)

if __name__=='__main__':
    import sys
    d=int(sys.argv[1]); lam=float(sys.argv[2]); tag=sys.argv[3]
    S=int(sys.argv[4]) if len(sys.argv)>4 else 1100
    Nx=int(sys.argv[5]) if len(sys.argv)>5 else 2200
    Nth=int(sys.argv[6]) if len(sys.argv)>6 else 3000
    build(d,lam,S=S,Nx=Nx,Nth=Nth,tag=tag)
