import numpy as np
from sim import ring
T=200000
for W in [1000,3001,4099,10007]:
    for p in [0.04,0.08]:
        lS,lM,zf=ring(p,W,T,11,0,1000)
        g1=(lM[-1]-lM[len(lM)//2])/(T/2)
        print(f"W={W} p={p:.2f} lnMax: "+' '.join(f'{v:.1f}' for v in lM[::40])+f"  rate2ndhalf={g1:.2e} W*rate={W*g1:.3f} zf={zf[-1]:.3f}",flush=True)
