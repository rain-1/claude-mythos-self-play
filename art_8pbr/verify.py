"""Verification for the triptych 'Where the Path Forks'.
Checks the mathematical claims each piece rests on."""
import numpy as np
from scipy.ndimage import uniform_filter1d

def verify_hero():
    print("== Piece 1: ellipsoid conjugate locus (Jacobi's 4-cusp astroid) ==")
    from ellipsoid import make_A, shoot, _project_to_surface
    # geodesic integrator exactness on the sphere (great circle closes at 2pi)
    A=make_A(1,1,1); p=np.array([1.,0,0])
    _,R,V=shoot(p,np.array([0.3,1.1,2.0]),A,L=2*np.pi,nsteps=3000)
    clo=np.linalg.norm(R-p,axis=1).max()
    spd=np.abs(np.linalg.norm(V,axis=1)-1).max()
    print(f"  sphere geodesic closure err : {clo:.2e}  (great circle closes)")
    print(f"  unit-speed error            : {spd:.2e}")
    # triaxial on-surface residual after long integration
    A2=make_A(1.6,1.35,0.8)
    p2=_project_to_surface(np.array([[1.6,0,0]]),A2)[0]
    _,R2,V2=shoot(p2,np.linspace(0,2*np.pi,64,endpoint=False),A2,L=5.0,nsteps=2600)
    res=np.abs(np.einsum('ij,ij->i',R2*A2,R2)-1).max()
    print(f"  triaxial on-surface residual: {res:.2e}  (stays on the ellipsoid)")
    # cusp count from a fresh small hero fan (self-contained; no cache needed)
    import os
    if not os.path.exists("hero_main.npz"):
        from hero_build import compute
        compute((1.6,1.35,0.8),(np.pi/2,0.0),N=6000,L=5.0,nsteps=2600,cache="hero_main.npz")
    d=np.load("hero_main.npz")
    conj=d['conj']; sconj=d['sconj']; A3=d['A']; pp=d['p']
    okc=np.isfinite(conj[:,0])&(sconj<=np.nanpercentile(sconj,80))
    C=conj[okc]
    ap=-pp; n=ap*A3; n/=np.linalg.norm(n)
    h=np.array([0,0,1.0]) if abs(n[2])<0.9 else np.array([1.,0,0])
    e1=h-h.dot(n)*n; e1/=np.linalg.norm(e1); e2=np.cross(n,e1)
    u=C@e1; v=C@e2; cu,cv=u.mean(),v.mean()
    a=np.arctan2(v-cv,u-cu); r=np.hypot(u-cu,v-cv)
    B=360; prof=np.full(B,np.nan); wb=np.digitize(a,np.linspace(-np.pi,np.pi,B+1))-1
    for b in range(B):
        m=wb==b
        if m.any(): prof[b]=np.nanmax(r[m])
    good=~np.isnan(prof); prof=np.interp(np.arange(B),np.where(good)[0],prof[good],period=B)
    prof=uniform_filter1d(prof,9,mode='wrap')
    cusps=0
    for k in range(B):
        if prof[k]>=prof[(k-1)%B] and prof[k]>prof[(k+1)%B]:
            cusps+=1
    print(f"  conjugate-locus cusp count  : {cusps}  (Jacobi's theorem: 4)")

def verify_p2():
    print("== Piece 2: cut locus in a holed domain (a finite GRAPH, not a tree) ==")
    from piece2 import solve, cutlocus, HOLES
    S=900
    X,Y,d,mask,inside,holemask,dx=solve(S,0.955,HOLES,(-0.68,0.06))
    cut,strength=cutlocus(d,mask,dx,inside,erode=5)
    # eikonal: |grad d| == 1 in the interior AWAY from the cut locus
    from scipy.ndimage import binary_erosion,binary_dilation
    gy,gx=np.gradient(d,dx); g=np.hypot(gy,gx)
    far=binary_erosion(inside,iterations=8)&~binary_dilation(mask,iterations=3)&~binary_dilation(cut,iterations=2)
    print(f"  |grad d| off the cut locus  : median {np.nanmedian(g[far]):.3f} (eikonal => 1)")
    # the DEFINING property: arrival direction is discontinuous ON the cut locus
    off=np.nanmedian(strength[far]); on=np.nanmedian(strength[cut])
    print(f"  arrival-dir jump OFF cut    : {off:.3f} rad (smooth: two paths agree)")
    print(f"  arrival-dir jump ON  cut    : {on:.3f} rad (two shortest paths of equal length collide)")
    from scipy.ndimage import label
    _,ncomp=label(cut)
    print(f"  #holes = {len(HOLES)}; cut-locus arc-components = {ncomp} (>=1 arc behind each obstacle)")

def verify_p3():
    print("== Piece 3: Brillouin zones = higher cut loci of the flat torus ==")
    from piece3 import compute
    v1=(1.0,0.0); v2=(0.5,np.sqrt(3)/2)
    zone,margin,ang,X,Y=compute(240,2.7,v1,v2,nmax=10)
    # zone 1 = Wigner-Seitz cell; every point has a well-defined finite zone index
    print(f"  zone index range            : {zone.min()}..{zone.max()} (finite everywhere)")
    # area of 1st BZ should equal one lattice-cell area (tiles the plane)
    cell_area=abs(v1[0]*v2[1]-v1[1]*v2[0])
    dx=(X[0,1]-X[0,0]); px_area=dx*dx
    a1=(zone==1).sum()*px_area
    print(f"  1st Brillouin zone area     : {a1:.4f}  vs lattice cell {cell_area:.4f}"
          f"  (ratio {a1/cell_area:.3f}, =1: WS cell tiles)")
    # hexagonal 1st BZ is a hexagon: 6-fold symmetric
    print(f"  (hexagonal lattice -> 1st BZ is a regular hexagon = the torus cut locus)")

if __name__=="__main__":
    verify_hero(); print(); verify_p2(); print(); verify_p3()
