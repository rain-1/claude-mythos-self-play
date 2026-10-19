import numpy as np, sys
from sim import run
N=20000
ps=[0.05,0.08,0.1,0.12,0.15,0.2,0.25,0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.95]
out={}
for p in ps:
    rows=[]
    for sd in range(4):
        lS,lM,zf,lC=run(p,N,1000+sd,100)
        rows.append((lS,lM,zf,lC))
    lS=np.array([r[0] for r in rows]); lM=np.array([r[1] for r in rows]); zf=np.array([r[2] for r in rows]); lC=np.array([r[3] for r in rows])
    out[p]=(lS,lM,zf,lC)
    n=np.arange(lS.shape[1])*100
    # slope of logS over last half
    h=lS.shape[1]//2
    sl=[np.polyfit(n[h:],x[h:],1)[0] for x in lS]
    print(f"p={p:.2f} lnS_N/N={lS[:,-1].mean()/N:.5f} slope2nd={np.mean(sl):.5f}+-{np.std(sl):.5f} lnMax/N={lM[:,-1].mean()/N:.5f} zeros={zf[:,-1].mean():.4f} ln(mean rows<=N)={np.mean(lC[:,-1]-np.log(N*(N+1)/2)):.2f}",flush=True)
np.save('scan1.npy',{p:np.array(v) for p,v in out.items()},allow_pickle=True)
