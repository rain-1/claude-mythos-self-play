import numpy as np
from sim import run, ring
N=20000
print("triangle: A(n)=mean of all entries in rows 0..n ; row mean S_n/(n+1)  (8 seeds, N=20000)")
res={}
for p in [0.005,0.01,0.02,0.03,0.04,0.05,0.06,0.07]:
    A=[];R=[]
    for sd in range(8):
        lS,lM,zf,lC=run(p,N,500+sd,100)
        n=np.arange(len(lS))*100
        A.append(np.exp(lC-np.log((n+1)*(n+2)/2))); R.append(np.exp(lS)/(n+1))
    A=np.array(A);R=np.array(R); res[p]=(A,R)
    idx=[10,50,100,200]
    print(f"p={p:.3f} A(n) at n=1e3,5e3,1e4,2e4: "+' '.join(f'{A[:,i].mean():.3f}±{A[:,i].std()/np.sqrt(8):.3f}' for i in idx)+
          f" | rowmean(last 5000 rows avg)={R[:,150:].mean():.3f}±{R[:,150:].mean(1).std()/np.sqrt(8):.3f}",flush=True)
np.save('lowphase_tri.npy',res,allow_pickle=True)
print("ring W=10007 bulk (integer init all-ones), time-avg of row mean over t in [5e4,2e5]")
for p in [0.005,0.01,0.02,0.03,0.04,0.05,0.06,0.07,0.08]:
    ms=[]
    for sd in range(3):
        lS,lM,zf=ring(p,10007,200000,40+sd,0,100)
        ms.append(np.exp(lS[500:]).mean()/10007)
    print(f"p={p:.3f} ring bulk mean={np.mean(ms):.3f}±{np.std(ms)/np.sqrt(3):.3f}  zero frac={zf[500:].mean():.3f} max={np.exp(lM[500:].max()):.0f}",flush=True)
