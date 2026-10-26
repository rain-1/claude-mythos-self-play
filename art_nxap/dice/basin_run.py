import numpy as np, sys, time
from geom import *; from sim import *
n=int(sys.argv[1]); L=float(sys.argv[2]); N=int(sys.argv[3]); W=float(sys.argv[4]); h=float(sys.argv[5]); e=float(sys.argv[6]); out=sys.argv[7]
V,F=prism(n,L); Vb,Nb,Ii=prepare(V,F)
q0=rand_quat(0.3,0.15,0.7)
wa=np.linspace(-W,W,N); wb=np.linspace(-W,W,N)
t=time.time()
B=basin(Vb,Nb,Ii,q0,np.array([0,0,h]),np.array([0.0,0,0]),wa,wb,e,0.4,2e-4,15.0)
print(time.time()-t, np.bincount(np.where(B<0,-1-B,B).ravel())/B.size, (B<0).mean())
np.save(out,B)
