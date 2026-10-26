import numpy as np, sys, time
from geom import *; from sim import *
N=int(sys.argv[1]); ax0,ax1,ay0,ay1=map(float,sys.argv[2:6]); out=sys.argv[6]
V,F=prism(5,1.62); Vb,Nb,Ii=prepare(V,F)
q0=rand_quat(0.3,0.15,0.7)
wa=np.linspace(ax0,ax1,N); wb=np.linspace(ay1,ay0,N)
t=time.time(); B=basin(Vb,Nb,Ii,q0,np.array([0,0,1.6]),np.zeros(3),wa,wb,0.3,0.4,2e-4,15.0); print(time.time()-t,flush=True)
np.save(out,B)
