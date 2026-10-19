import numpy as np
from sim import ring
W=4096; T=200000
for p in [0.02,0.04,0.06,0.08,0.10,0.12,0.15,0.2,0.3]:
    for init in [0,1]:
        lS,lM,zf=ring(p,W,T,7,init,1000)
        g1=(lM[-1]-lM[len(lM)//2])/(T/2)
        print(f"p={p:.2f} init={init} lnMax: "+' '.join(f'{v:.1f}' for v in lM[::40])+f"  rate2ndhalf={g1:.2e} zf={zf[-1]:.3f}",flush=True)
