import numpy as np, math, sys
from geom import *; import sim
V,F=prism(5,1.62)
vol=mass_props(V,F)[0]; V=V*(2.2/vol)**(1/3)
Vb,Nb,Ii=sim.prepare(V,F)
for seed in range(40):
    rng=np.random.default_rng(seed); u=rng.random(9)
    q0=sim.rand_quat(u[0],u[1],u[2])
    rec=np.zeros((20000,7))
    f,t,n=sim.throw(Vb,Nb,Ii,np.array([0,0,2.6]),q0,np.array([3.2,0,0.8]),np.array([1.5*(2*u[6]-1),9*(2*u[7]-1),2*(2*u[8]-1)]),0.45,0.35,2e-4,15.0,25,rec)
    P=rec[:n,:3]; d=np.abs(P[-1,:2]-P[0,:2])
    # count bounces: local minima of z near the floor
    z=P[:,2]; mins=((z[1:-1]<z[:-2])&(z[1:-1]<z[2:])&(z[1:-1]<1.2)).sum()
    print(seed,f,round(t,2),n,P[-1].round(2),'bounces',mins, 'ymax', P[:,1].ptp().round(2) if hasattr(P,'ptp') else np.ptp(P[:,1]).round(2))
