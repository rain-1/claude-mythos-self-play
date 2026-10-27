"""Sphere-sweep tube splatter with z-buffer: points (x,y,z,r,rgb) -> colour + normal + depth buffers."""
import numpy as np, numba as nb
@nb.njit(cache=True)
def splat(X,Y,Z,Rr,CI,W,H,zb,nb_,ib,ub):
    # zb: depth (larger = closer to viewer), nb_: normals (H,W,3), ib: colour index, ub: per-point param
    for k in range(X.shape[0]):
        x=X[k]; y=Y[k]; r=Rr[k]
        x0=max(0,int(x-r-1)); x1=min(W-1,int(x+r+1)); y0=max(0,int(y-r-1)); y1=min(H-1,int(y+r+1))
        for py in range(y0,y1+1):
            for px in range(x0,x1+1):
                dx=(px+0.5-x)/r; dy=(py+0.5-y)/r; d2=dx*dx+dy*dy
                if d2<1.0:
                    nz=np.sqrt(1.0-d2); z=Z[k]+nz*r
                    if z>zb[py,px]:
                        zb[py,px]=z; nb_[py,px,0]=dx; nb_[py,px,1]=dy; nb_[py,px,2]=nz; ib[py,px]=CI[k]; ub[py,px]=k
@nb.njit(cache=True)
def splat_mask(X,Y,Rr,W,H,M,val):
    for k in range(X.shape[0]):
        x=X[k]; y=Y[k]; r=Rr[k]
        x0=max(0,int(x-r-1)); x1=min(W-1,int(x+r+1)); y0=max(0,int(y-r-1)); y1=min(H-1,int(y+r+1))
        for py in range(y0,y1+1):
            for px in range(x0,x1+1):
                dx=(px+0.5-x); dy=(py+0.5-y)
                if dx*dx+dy*dy<r*r: M[py,px]=max(M[py,px],val[k])
def resample(P,step):
    """resample a polyline (K,d) at arc-length spacing 'step' (in the first two coords)"""
    seg=np.hypot(np.diff(P[:,0]),np.diff(P[:,1])); s=np.concatenate([[0],np.cumsum(seg)])
    t=np.arange(0,s[-1],step)
    return np.stack([np.interp(t,s,P[:,i]) for i in range(P.shape[1])],1)
