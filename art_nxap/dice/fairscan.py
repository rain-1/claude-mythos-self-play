import numpy as np, sys, json
from geom import *; from sim import *
n=int(sys.argv[1]); M=int(sys.argv[2]); e=float(sys.argv[3]); mu=float(sys.argv[4]); ws=float(sys.argv[5])
rng=np.random.default_rng(n)
res=[]
for L in np.linspace(float(sys.argv[6]),float(sys.argv[7]),int(sys.argv[8])):
    V,F=prism(n,L); Vb,Nb,Ii=prepare(V,F)
    o=monte_carlo(Vb,Nb,Ii,rng.random((M,9)),e,mu,2e-4,15.0,3.0,1.0,ws)
    ok=np.where(o<0,-1-o,o); pend=np.isin(ok,[0,1]).mean(); nfail=(o<0).sum()
    res.append((L,pend,2/(n+2),len(ok)))
    print(n,round(L,4),round(pend,4),"target",round(2/(n+2),4),len(ok),"fail",nfail,flush=True)
