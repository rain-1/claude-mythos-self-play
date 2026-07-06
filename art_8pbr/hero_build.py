"""Hero builder: geodesic fan + fold-density caustic + exact conjugate locus.
Cached to .npz so the colormap can be iterated fast."""
import numpy as np
from ellipsoid import make_A, shoot, _project_to_surface

def p_on(abc, th, ph):
    a,b,c=abc
    A=make_A(a,b,c)
    return _project_to_surface(np.array([[a*np.sin(th)*np.cos(ph),
                                          b*np.sin(th)*np.sin(ph),
                                          c*np.cos(th)]]),A)[0]

def compute(abc, p_ang, N, L, nsteps, cache):
    a,b,c=abc; A=make_A(a,b,c)
    p=p_on(abc,*p_ang)
    thetas=np.linspace(0,2*np.pi,N,endpoint=False)
    pos,R,V=shoot(p,thetas,A,L=L,nsteps=nsteps,record_every=1)
    T=pos.shape[0]; s_of_t=np.linspace(0,L,T)
    # perpendicular neighbour spreading, computed row-by-row to bound RAM
    spread=np.empty((T,N),np.float32)
    for t in range(T):
        cur=pos[t]
        nb=np.roll(cur,-1,axis=0)
        dvec=nb-cur
        tp=pos[min(t+1,T-1)]; tm=pos[max(t-1,0)]
        tang=tp-tm
        tn=tang/(np.linalg.norm(tang,axis=1,keepdims=True)+1e-12)
        dpar=np.einsum('nk,nk->n',dvec,tn)[:,None]*tn
        spread[t]=np.linalg.norm(dvec-dpar,axis=1)
    # first conjugate point per direction: first strong dip of spread (vectorised)
    conj=np.full((N,3),np.nan,np.float32); sconj=np.full(N,np.nan,np.float32)
    runmax=np.maximum.accumulate(spread,axis=0)
    locmin=np.zeros((T,N),bool)
    locmin[1:-1]=(spread[1:-1]<spread[:-2])&(spread[1:-1]<=spread[2:])
    cond=locmin&(spread<0.5*runmax)&(s_of_t[:,None]>1.2)
    has=cond.any(axis=0)
    tfirst=np.argmax(cond,axis=0)  # first True per column (0 if none, guarded by has)
    idx=np.where(has)[0]
    tt=tfirst[idx]
    conj[idx]=pos[tt,idx]
    sconj[idx]=s_of_t[tt]
    np.savez_compressed(cache, pos=pos.astype(np.float32), spread=spread,
                        conj=conj, sconj=sconj, A=A, p=p, abc=np.array(abc),
                        s_of_t=s_of_t.astype(np.float32))
    print("cached",cache,"T",T,"N",N,"conj found",np.isfinite(sconj).sum(),
          "s_conj range",np.nanmin(sconj),np.nanmax(sconj))

if __name__=="__main__":
    import sys
    abc=(1.7,1.15,0.78)
    compute(abc,(0.95,0.55),N=6000,L=4.6,nsteps=2400,cache="hero_cache.npz")
