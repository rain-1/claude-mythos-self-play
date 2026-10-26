import numpy as np, sys
from geom import *; import sim
V,F=prism(5,1.62); vol=mass_props(V,F)[0]; V=V*(2.2/vol)**(1/3)
Vb,Nb,Ii=sim.prepare(V,F)
for seed in range(60):
    rng=np.random.default_rng(seed); u=rng.random(9); q0=sim.rand_quat(u[0],u[1],u[2]); rec=np.zeros((40000,7))
    f,t,n=sim.throw(Vb,Nb,Ii,np.array([0,0,3.2]),q0,np.array([4.5,0,2.5]),np.array([1.5*(2*u[6]-1),9*(2*u[7]-1),2*(2*u[8]-1)]),0.45,0.35,2e-4,15.0,5,rec)
    P=rec[:n,:3]; idx=[0]
    for k in range(1,n):
        if np.linalg.norm(P[k]-P[idx[-1]])>=1.5: idx.append(k)
    print(seed,f,len(idx),P[-1].round(1),np.ptp(P[:,1]).round(2),P[:,2].max().round(1))
