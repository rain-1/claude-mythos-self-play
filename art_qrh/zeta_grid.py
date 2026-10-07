import numpy as np, sys
from zeta import zeta
W,H=int(sys.argv[1]),int(sys.argv[2]); s0,s1,t0,t1=[float(x) for x in sys.argv[3:7]]
sig=np.linspace(s0,s1,W); t=np.linspace(t0,t1,H)
S=sig[None,:]+1j*t[:,None]
Z=np.empty(S.shape,complex)
for r in range(0,H,64):
    Z[r:r+64]=zeta(S[r:r+64]); 
np.savez_compressed(sys.argv[7],Z=Z.astype(np.complex64),sig=sig,t=t); print('ok',Z.shape)
