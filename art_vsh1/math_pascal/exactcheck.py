# Compare float64 ring dynamics with exact Python-int dynamics using identical coins.
import numpy as np, math, random
def runs(p,W,T,seed):
    rng=np.random.default_rng(seed)
    xi=[1]*W; xf=np.ones(W)
    outi=[];outf=[]
    for t in range(1,T+1):
        c=rng.random(W)<p
        xi=[ (xi[k-1]+xi[k]) if c[k] else abs(xi[k-1]-xi[k]) for k in range(W)]
        a=np.roll(xf,1); xf=np.where(c,a+xf,np.abs(a-xf))
        m=xf.max(); 
        if m>1e100: xf/=m; outf.append(math.log(m)); 
        else: outf.append(0.0)
        if t%500==0:
            mi=max(xi); 
            Lf=sum(outf)+math.log(xf.max()) if xf.max()>0 else -1
            zi=sum(1 for v in xi if v==0)/W; zfl=(xf==0).mean()
            print(f"p={p} t={t} ln max exact={math.log(mi) if mi>0 else -1:.3f} float={Lf:.3f} zeros exact={zi:.3f} float={zfl:.3f}",flush=True)
for p in [0.1,0.15,0.3]:
    runs(p,1001,3000,1)
