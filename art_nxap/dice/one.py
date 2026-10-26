import numpy as np, time
from geom import *; from sim import *
V,F=platonic('cube'); Vb,Nb,Ii=prepare(V,F)
rec=np.zeros((100000,7))
for s in range(5):
    rng=np.random.default_rng(s); u=rng.random(9)
    q0=rand_quat(u[0],u[1],u[2]); 
    t=time.time(); f,tr,n=throw(Vb,Nb,Ii,np.array([0,0,3.0]),q0,np.array([1.0,0,0]),15*(2*u[6:9]-1),0.5,0.4,2e-4,12.0,100,rec)
    print(f,tr,n,time.time()-t, rec[n-1,:3])
