"""Numerical search: maximise q = P[b*(X_1+..+X_{n-1}) < a*X_n] / (1 - P[tie]) over laws on {0..K}.
(the tie boost = nesting an independent infinitesimal copy; see RESULTS.md)
usage: search.py n a b K restarts seed"""
import sys, numpy as np
from scipy.optimize import minimize
n,a,b,K,R,seed=map(int,sys.argv[1:7])
def parts(m):
    c=np.array([1.0])
    for _ in range(n-1): c=np.convolve(c,m)          # law of the sum of n-1, support 0..(n-1)K
    F=np.cumsum(c)
    P=T=0.0
    for x in range(K+1):
        # b*s < a*x  <=> s < a*x/b
        t=a*x
        smax=(t-1)//b                                 # largest s with b*s < a*x
        if smax>=0: P+=m[x]*F[min(smax,len(F)-1)]
        if t%b==0 and t//b<len(c): T+=m[x]*c[t//b]
    return P,T
def obj(th):
    m=np.exp(th-th.max()); m/=m.sum(); P,T=parts(m); return -P/(1-T+1e-12)
rng=np.random.default_rng(seed); best=(0,None)
for r in range(R):
    th=rng.normal(0,2,K+1)
    if r%2: th-=0.15*np.arange(K+1)*rng.random()*3
    res=minimize(obj,th,method='L-BFGS-B',options={'maxiter':400})
    if -res.fun>best[0]:
        m=np.exp(res.x-res.x.max()); m/=m.sum(); best=(-res.fun,m)
        print(r,'q=%.6f'%best[0],'P,T=%.4f %.4f'%parts(m),' '.join('%d:%.3f'%(i,v) for i,v in enumerate(m) if v>2e-3),flush=True)
np.save('best_%d_%d_%d_%d.npy'%(n,a,b,K),best[1])
