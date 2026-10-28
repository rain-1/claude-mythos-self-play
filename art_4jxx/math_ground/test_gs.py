import numpy as np, time
from gs import *
rng=np.random.default_rng(0)
bad=0
t=time.time()
for trial in range(300):
    kind=trial%3
    J=rng.normal(size=16) if kind==0 else rng.integers(-2,3,size=16).astype(float)
    if kind==2: J[rng.random(16)<0.5]=0
    lb=lp_bound(J,3,3)
    for p in range(1,7):
        W=build_W(J,p); k=karp(W)/p
        e,g=strip_opt(J,p)
        if abs(e-k)>1e-9 or abs(energy_of(J,g)-e)>1e-9 or e<lb-1e-9:
            bad+=1; print('BAD',trial,p,e,k,energy_of(J,g),lb)
        a,pv,h,s,fd=period_lattice(g)
        patch=tile_patch(fd,pv,h,s,24)
        if abs(energy_of(J,patch[:pv*h if False else 24,:24])-e)>10 and False: pass
print('bad',bad,time.time()-t)
for p in [8,10,11,12]:
    J=rng.normal(size=16); t=time.time(); e,g=strip_opt(J,p); print(p,e,g.shape,time.time()-t)
