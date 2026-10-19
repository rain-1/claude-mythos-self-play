import numpy as np, time
from sim import cloning
import sys
for p,N,P in [(1.0,200,50),(0.5,400,200),(0.3,600,400),(0.2,600,400),(0.1,600,400),(0.05,600,400)]:
    t=time.time()
    out=cloning(p,N,P,1)
    lam_mo = p*p+np.sqrt(p**4+4*p*(1-p))
    h=N//2
    rate=(out[-1]-out[h])/(N-h)
    print(f"p={p} lnE S_N={out[-1]:.2f} rate(2nd half)={rate:.4f} MO lower ln(lambda)={np.log(lam_mo):.4f}  lnES at N/4,N/2,3N/4: {out[N//4]:.1f} {out[h]:.1f} {out[3*N//4]:.1f} ({time.time()-t:.1f}s)",flush=True)
