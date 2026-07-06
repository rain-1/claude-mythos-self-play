"""Cut locus of the source on the ellipsoid, from the geodesic fan.

A point is on the cut locus when two DISTINCT minimizing geodesics of equal
length reach it.  From the fan we rasterize, per screen cell, the direction i
of the shortest-arclength geodesic arriving there; the cut locus is the seam
where that direction field jumps discontinuously (two far-apart directions tie).
"""
import numpy as np

def cut_locus_field(pos, s_of_t, Rc, ext, S, A, cull=-0.05):
    T,N,_=pos.shape
    flat=pos.reshape(-1,3)
    P=flat@Rc.T
    nrm=flat*A; nrm/=np.linalg.norm(nrm,axis=1)[:,None]
    facing=(nrm@Rc.T)[:,2]>cull
    sx=((P[:,0]/ext)*0.5+0.5)*(S-1)
    sy=((-P[:,1]/ext)*0.5+0.5)*(S-1)
    ix=sx.astype(int); iy=sy.astype(int)
    sarr=np.repeat(s_of_t[:,None],N,axis=1).reshape(-1)
    iarr=np.repeat(np.arange(N)[None,:],T,axis=0).reshape(-1)
    m=facing&(ix>=0)&(ix<S)&(iy>=0)&(iy<S)
    cell=iy[m]*S+ix[m]; sM=sarr[m]; iM=iarr[m]
    # write direction of SMALLEST arclength per cell: sort by s DESCending, last write wins
    order=np.argsort(-sM)
    dirfield=np.full(S*S,-1,np.int32)
    mins=np.full(S*S,np.inf)
    dirfield[cell[order]]=iM[order]
    minsraw=np.full(S*S,np.inf)
    np.minimum.at(minsraw,cell,sM)
    dirfield=dirfield.reshape(S,S); minsraw=minsraw.reshape(S,S)
    # seam detection: angular distance between neighbor direction indices (mod N)
    dg=dirfield.astype(np.float32)
    def angdiff(a,b):
        d=np.abs(a-b); return np.minimum(d,N-d)
    valid=dirfield>=0
    seam=np.zeros((S,S),np.float32)
    for dy,dx in [(0,1),(1,0),(1,1),(1,-1)]:
        a=dirfield
        b=np.roll(np.roll(dirfield,dy,0),dx,1)
        vv=valid&np.roll(np.roll(valid,dy,0),dx,1)
        jump=angdiff(a.astype(np.float32),b.astype(np.float32))
        seam=np.maximum(seam,np.where(vv,jump,0))
    # cut locus: big direction jump (>~ N/8) between adjacent minimizing geodesics
    cut=(seam>N*0.06)&valid
    return cut, minsraw, dirfield
