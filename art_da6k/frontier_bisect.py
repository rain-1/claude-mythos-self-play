import numpy as np, json, sys
from math import log, pi
from zeta_g import gseq, torus_setup, torus_min
N=int(sys.argv[1]); g=gseq(N); primes,V=torus_setup(N,g); lg=np.array([log(x) for x in g[:N]])
lo,hi=1.00,1.02; theta=None
res={}
# warm start from the sigma=1.00 world
m,theta=torus_min(1.00,V,lg,restarts=40,seed=3)
print('N',N,'primes',len(primes),'sigma=1.00 min',m)
for it in range(9):
    mid=0.5*(lo+hi)
    m,th=torus_min(mid,V,lg,restarts=25,seed=it,theta0=theta)
    res[round(mid,5)]=float(m)
    print(f'sigma={mid:.5f} min|Z|={m:.3e}'); sys.stdout.flush()
    if m<1e-4: lo=mid; theta=th
    else: hi=mid
print('sigma* in',lo,hi)
desc={str(p):round(float(np.mod(theta[i],2*pi)),3) for i,p in enumerate(primes[:12])}
print('frontier world phases',desc)
json.dump(dict(N=N,lo=lo,hi=hi,theta=[float(x) for x in theta],primes=primes,scan=res),open(f'bisect_N{N}.json','w'))
