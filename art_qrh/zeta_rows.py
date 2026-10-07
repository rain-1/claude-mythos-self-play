"""zeta on a long isotropic ribbon: sigma in [s0,s1] (Hs samples), t in [0,T] (Wt samples) -> saved as (Hs,Wt)."""
import numpy as np, sys
from zeta import zeta
Hs,Wt=int(sys.argv[1]),int(sys.argv[2]); s0,s1,T=[float(x) for x in sys.argv[3:6]]
sig=np.linspace(s0,s1,Hs); t=np.linspace(0,T,Wt)
Z=np.empty((Hs,Wt),np.complex64)
for c in range(0,Wt,512):
    S=sig[:,None]+1j*t[None,c:c+512]
    Z[:,c:c+512]=zeta(S)
np.savez_compressed(sys.argv[6],Z=Z,sig=sig,t=t); print('ok',Z.shape)
