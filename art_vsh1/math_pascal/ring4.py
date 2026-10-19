import numpy as np
from sim import ring_from
W=100003
x0=np.ones(W)
_,_,_,xh=ring_from(0.15,x0,20000,3,1000)   # high-phase state
np.save('xh.npy',xh)
for p in [0.08,0.0825,0.075]:
    T=400000
    lS,lM,zf,_=ring_from(p,xh,T,9,2000)
    np.save(f'ring4_{p}.npy',np.array([lS,lM,zf]))
    n=np.arange(len(lM))*2000
    h=len(lM)//2
    g=np.polyfit(n[h:],lM[h:],1)[0]
    print(f"W={W} p={p:.4f} init=high lnMax every 40k: "+' '.join(f'{v:.1f}' for v in lM[::20])+f" | slope2nd={g:.2e} zf: "+' '.join(f'{v:.2f}' for v in zf[::20]),flush=True)
