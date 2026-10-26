import numpy as np, time, sys
from geom import *; from sim import *
rng=np.random.default_rng(1)
V,F=platonic('cube'); Vb,Nb,Ii=prepare(V,F)
U=rng.random((200,9)); t=time.time()
o=monte_carlo(Vb,Nb,Ii,U,0.5,0.4,2e-4,12.0,3.0,1.0,15.0); print('jit+200',time.time()-t)
U=rng.random((20000,9)); t=time.time()
o=monte_carlo(Vb,Nb,Ii,U,0.5,0.4,2e-4,12.0,3.0,1.0,15.0); print('20000',time.time()-t)
print(np.bincount(o[o>=0],minlength=6)/len(o), (o<0).sum())
