import numpy as np, sys, time
from geom import *; from sim import *
N=int(sys.argv[1]); Wmax=float(sys.argv[2]); gam=float(sys.argv[3]); out=sys.argv[4]
V,F=prism(5,1.62); Vb,Nb,Ii=prepare(V,F)
q0=rand_quat(0.3,0.15,0.7)
y,x=np.mgrid[0:N,0:N]; u=(x+0.5)/N*2-1; v=1-(y+0.5)/N*2
r=np.hypot(u,v); m=r<=1.0
rr=r[m]; th=np.arctan2(v[m],u[m]); mag=Wmax*rr**gam
WP=np.stack([mag*np.cos(th),mag*np.sin(th),np.zeros_like(mag)],1)
# shuffle for load balance
perm=np.random.default_rng(0).permutation(len(WP))
t=time.time(); o=basin_pts(Vb,Nb,Ii,q0,np.array([0,0,1.6]),np.zeros(3),np.ascontiguousarray(WP[perm]),0.3,0.4,2e-4,15.0)
res=np.empty_like(o); res[perm]=o
B=np.full((N,N),-100,np.int64); B[m]=res
np.save(out,B); print(time.time()-t,flush=True)
