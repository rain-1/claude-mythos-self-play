import numpy as np, time
from sim import cloning
res={}
for p in [0.04,0.06,0.07,0.08,0.09,0.10,0.12,0.15]:
    for P in [500,4000]:
        N=3000
        t=time.time()
        out=cloning(p,N,P,7)
        res[(p,P)]=out
        n=np.arange(N+1)
        h=N//2
        rate=(out[-1]-out[h])/(N-h)
        print(f"p={p} P={P} lnES at n=500,1000,2000,3000: {out[500]:.2f} {out[1000]:.2f} {out[2000]:.2f} {out[3000]:.2f}  ln(n)={np.log(3000):.2f} rate2nd={rate:.2e} ({time.time()-t:.0f}s)",flush=True)
np.save('clone2.npy',res,allow_pickle=True)
