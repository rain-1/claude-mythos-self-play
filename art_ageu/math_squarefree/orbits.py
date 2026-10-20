import json, numpy as np, sys
from count_anti90 import run, squares
def full(n,mod):
    h=n//2; g=-np.ones((n,n),int)
    for r in range(n):
        for c in range(n):
            rr,cc,k=r,c,0
            while not (rr<h and cc<h): rr,cc=cc,n-1-rr; k+=1
            v=mod[rr*h+cc]>0
            g[r,c]=int(v) if k%2==0 else 1-int(v)
    return g
def ok(g):
    n=len(g)
    return all(len({g[r][c] for r,c in sq})>1 for sq in squares(n))
for n in map(int,sys.argv[1:]):
    cnt,dt,_=run(n)
    # re-enumerate all for orbit count
    from pysat.solvers import Cadical153
    import count_anti90 as C
    sols=[]
    # quick: rerun storing all
    def lit(r,c):
        k=0
        while not (r<n//2 and c<n//2): r,c=c,n-1-r; k+=1
        v=r*(n//2)+c+1; return v if k%2==0 else -v
    cls=set()
    for sq in squares(n):
        L=[lit(*p) for p in sq]
        if any(-x in L for x in L): continue
        cls.add(tuple(sorted(set(L)))); cls.add(tuple(sorted(set(-x for x in L))))
    s=Cadical153(bootstrap_with=[list(c) for c in cls]); m=(n//2)**2
    while s.solve():
        mod=s.get_model()[:m]; sols.append(full(n,mod)); s.add_clause([-x for x in mod])
    assert all(ok(g) for g in sols)
    keys=set()
    for g in sols:
        forms=[]
        for h in (g,g.T):
            for k in range(4):
                x=np.rot90(h,k)
                forms+= [x.tobytes(),(1-x).tobytes()]
        keys.add(min(forms))
    ones=sorted(set(int(g.sum()) for g in sols))
    fixedT=sum((g==g.T).all() or (g==1-g.T).all() for g in sols)
    print(n,len(sols),'orbits',len(keys),'ones',ones,'transpose-(anti)symmetric',fixedT)
    if n==14: np.save('anti90_14_all.npy',np.array(sols))
