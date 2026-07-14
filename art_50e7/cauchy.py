"""Companion 2 — 'Cauchy's Cage': a CONVEX triangulated polyhedron is rigid
(Cauchy 1813). Same 9 vertices as Steffen, but convex => the flex-kernel of the
rigidity matrix is exactly the 6 trivial rigid motions (no nontrivial flex).
Rendered as a still, solid, luminous crystal: solidity == rigidity.
"""
import numpy as np
from scipy.spatial import ConvexHull

def spread_points(n, iters=4000, seed=3):
    """n points spread on unit sphere by repulsion (Fibonacci start + relax)."""
    rng=np.random.default_rng(seed)
    i=np.arange(n)+0.5
    phi=np.arccos(1-2*i/n); th=np.pi*(1+5**0.5)*i
    P=np.stack([np.sin(phi)*np.cos(th),np.sin(phi)*np.sin(th),np.cos(phi)],1)
    for _ in range(iters):
        D=P[:,None,:]-P[None,:,:]
        d2=(D**2).sum(2)+np.eye(n)*1e9
        F=(D/ (d2[...,None]**1.5)).sum(1)
        P=P+0.02*F; P/=np.linalg.norm(P,axis=1,keepdims=True)
    return P

def rigidity_matrix(P, edges):
    n=len(P); R=np.zeros((len(edges),3*n))
    for k,(a,b) in enumerate(edges):
        d=P[a]-P[b]
        R[k,3*a:3*a+3]=d; R[k,3*b:3*b+3]=-d
    return R

def flex_analysis(P, edges):
    R=rigidity_matrix(P,edges)
    U,s,Vt=np.linalg.svd(R)
    # kernel dim = 3n - rank ; trivial rigid motions = 6 (generic 3D)
    tol=1e-9*s.max()
    rank=int((s>tol).sum())
    ker=3*len(P)-rank
    # smallest NONtrivial singular value: infinitesimal stiffness beyond rigid motions
    nz=s[s>tol]
    return dict(nedge=len(edges),ndof=3*len(P),rank=rank,kernel=ker,
                min_stiff=nz.min() if len(nz) else 0.0)

if __name__=='__main__':
    for n in (9,12,16):
        P=spread_points(n)
        h=ConvexHull(P)
        faces=[tuple(f) for f in h.simplices]
        eset=set()
        for f in faces:
            for a,b in [(f[0],f[1]),(f[1],f[2]),(f[2],f[0])]:
                eset.add((min(a,b),max(a,b)))
        edges=sorted(eset)
        fa=flex_analysis(P,edges)
        V,E,F=n,len(edges),len(faces)
        print("n=%2d  V-E+F=%d  E=%d F=%d  kernel=%d (rigid<=>6)  min_stiffness=%.4f"%(
            n,V-E+F,E,F,fa['kernel'],fa['min_stiff']))
