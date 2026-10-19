import numpy as np
from sim import ring_from2
W=100003
xh=np.load('xh.npy')
xi=np.round(xh*1e12)   # exact integers < 2^53: float arithmetic is exact while max<9e15
print('init: max',xi.max(),'zeros',(xi==0).mean(),'mean ln',np.log(xi[xi>0]).mean(),flush=True)
for p in [0.05,0.065,0.08]:
    T=300000
    lS,lM,zf,lG,fs,_=ring_from2(p,xi,T,21,2000)
    np.save(f'ring6_{p}.npy',np.array([lS,lM,zf,lG,fs]))
    print(f"p={p:.3f} exact-int init | every 30k lnMax: "+' '.join(f'{v:.1f}' for v in lM[::15])+"\n   meanln: "+' '.join(f'{v:.1f}' for v in lG[::15])+"\n   zf: "+' '.join(f'{v:.2f}' for v in zf[::15])+f"\n   (exact while lnMax<36.7)",flush=True)
