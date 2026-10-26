import numpy as np
from geom import *; import sim
V,F=prism(5,1.62); vol=mass_props(V,F)[0]; V=V*(2.2/vol)**(1/3)
Vb,Nb,Ii=sim.prepare(V,F)
for seed in range(80):
    rng=np.random.default_rng(seed); u=rng.random(9); q0=sim.rand_quat(u[0],u[1],u[2]); rec=np.zeros((40000,7))
    f,t,n=sim.throw(Vb,Nb,Ii,np.array([0,0,1.2]),q0,np.array([5.5,0,5.5]),np.array([1.5*(2*u[6]-1),9*(2*u[7]-1),2*(2*u[8]-1)]),0.5,0.35,2e-4,15.0,5,rec)
    P=rec[:n,:3]; z=P[:,2]
    # airborne hops: segments where lowest vertex > 0.05
    low=np.array([z[k]+(Vb@sim.qrot(rec[k,3:]).T)[:,2].min() for k in range(n)])
    air=low>0.08; hops=((~air[:-1])&air[1:]).sum()
    hmax=[]; 
    idx=[0]
    for k in range(1,n):
        if np.linalg.norm(P[k]-P[idx[-1]])>=2.0: idx.append(k)
    print(seed,f,n,'hops',hops,'x',P[-1,0].round(1),'y',np.ptp(P[:,1]).round(2),'cop',len(idx),'zmax',z.max().round(1))
