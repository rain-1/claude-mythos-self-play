import numpy as np
from sim import ring_from
W=10007
x0=np.ones(W)
_,_,_,xh=ring_from(0.15,x0,20000,3,1000)   # high-phase state
for p in [0.06,0.08,0.085,0.09,0.095,0.10,0.11]:
    T=1000000 if p<0.1 else 300000
    for lab,xi in [('ones',x0),('high',xh)]:
        lS,lM,zf,_=ring_from(p,xi,T,5,5000)
        n=np.arange(len(lM))*5000
        h=len(lM)//2
        g=np.polyfit(n[h:],lM[h:],1)[0]
        print(f"p={p:.3f} init={lab} lnMax every 100k: "+' '.join(f'{v:.1f}' for v in lM[::20])+f" | slope2nd={g:.2e} zf_end={zf[-1]:.3f}",flush=True)
