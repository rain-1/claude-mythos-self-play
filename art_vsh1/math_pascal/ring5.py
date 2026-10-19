import numpy as np
from sim import ring_from2
W=100003
xh=np.load('xh.npy')
for p in [0.06,0.07,0.05]:
    T=400000
    lS,lM,zf,lG,fs,_=ring_from2(p,xh,T,9,2000)
    np.save(f'ring5_{p}.npy',np.array([lS,lM,zf,lG,fs]))
    n=np.arange(len(lM))*2000
    h=len(lM)//2
    g=np.polyfit(n[h:],lM[h:],1)[0]; g2=np.polyfit(n[h:],lG[h:],1)[0]
    print(f"W={W} p={p:.4f} high init | every 40k lnMax: "+' '.join(f'{v:.1f}' for v in lM[::20])+f"\n   meanlog: "+' '.join(f'{v:.1f}' for v in lG[::20])+f"\n   zf: "+' '.join(f'{v:.2f}' for v in zf[::20])+f"\n   frac<1e-20max: "+' '.join(f'{v:.2f}' for v in fs[::20])+f"\n   slopes2nd lnMax={g:.2e} meanlog={g2:.2e}",flush=True)
