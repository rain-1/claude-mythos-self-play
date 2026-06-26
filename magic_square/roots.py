"""Root systems of F4, E6, E7, E8 and their Coxeter-plane projections."""
import numpy as np, sys, itertools
sys.path.insert(0,'e8')
import e8 as E8

def _key(v): return tuple(np.round(v,6))

def gen_roots(simple):
    simple=[np.array(s,float) for s in simple]
    roots={_key(s):s for s in simple}
    changed=True
    while changed:
        changed=False
        cur=list(roots.values())
        for r in cur:
            for s in simple:
                rr=r-2*np.dot(r,s)/np.dot(s,s)*s
                k=_key(rr)
                if k not in roots:
                    roots[k]=rr; changed=True
    return np.array(list(roots.values()))

def f4_simple():
    e=np.eye(4)
    return [e[1]-e[2], e[2]-e[3], e[3], 0.5*(e[0]-e[1]-e[2]-e[3])]

def base_of(roots, seed=0):
    rng=np.random.default_rng(seed); g=rng.standard_normal(roots.shape[1])
    pos=[r for r in roots if np.dot(r,g)>1e-9]
    simple=[]
    for r in pos:
        decomp=False
        for s in pos:
            for t in pos:
                if np.allclose(s+t,r): decomp=True; break
            if decomp: break
        if not decomp: simple.append(r)
    return simple

def coxeter_plane(simple, h, dim):
    simple=[np.array(s,float) for s in simple]
    C=np.eye(dim)
    for s in simple:
        R=np.eye(dim)-2*np.outer(s,s)/np.dot(s,s)
        C=R@C
    w,v=np.linalg.eig(C)
    target=np.exp(2j*np.pi/h)
    k=int(np.argmin(np.abs(w-target)))
    z=v[:,k]; u=np.real(z); t=np.imag(z)
    u=u/np.linalg.norm(u); t=t-np.dot(t,u)*u; t=t/np.linalg.norm(t)
    return u,t

def system(name):
    if name=="F4":
        R=gen_roots(f4_simple()); simple=f4_simple(); h=12; dim=4
    elif name=="E8":
        R=E8.roots(); simple=list(E8.simple_roots()); h=30; dim=8
    elif name=="E7":
        allR=E8.roots(); r0=allR[0]
        R=np.array([r for r in allR if abs(np.dot(r,r0))<1e-9]); simple=base_of(R); h=18; dim=8
    elif name=="E6":
        allR=E8.roots(); r0=allR[0]
        # second root making A2 with r0 (dot = -1) and take common orthogonal
        r1=next(r for r in allR if abs(np.dot(r,r0)+1)<1e-9)
        R=np.array([r for r in allR if abs(np.dot(r,r0))<1e-9 and abs(np.dot(r,r1))<1e-9])
        simple=base_of(R); h=12; dim=8
    u,t=coxeter_plane(simple,h,dim)
    P=np.stack([R@u, R@t],1)
    return R,P

if __name__=="__main__":
    for nm,exp in [("F4",48),("E6",72),("E7",126),("E8",240)]:
        R,P=system(nm)
        rad=np.round(np.linalg.norm(P,axis=1),3)
        import collections
        rings=collections.Counter(rad.tolist())
        print(f"{nm}: {len(R)} roots (expect {exp})  ·  {len(rings)} rings  sizes={sorted(set(rings.values()))}")
