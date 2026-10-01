# exhaustive 3x3 minors of [C(i,j)^r] with indices <= N; find r-range where some minor < 0
import numpy as np, itertools
from scipy.special import gammaln
N=int(__import__('sys').argv[1])
lb=np.full((N+1,N+1),-np.inf)
for i in range(N+1):
    for j in range(i+1): lb[i,j]=gammaln(i+1)-gammaln(j+1)-gammaln(i-j+1)
T=list(itertools.combinations(range(N+1),3))
R=np.array([t for t in T]); 
for r in [0.02,0.05,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.85,0.9,0.95,0.98,0.99,1.0,1.01,1.5,2]:
    M=np.exp(r*lb)  # 0 where -inf
    M[np.isinf(lb)]=0
    worst=(1,None)
    for rows in T:
        sub=M[list(rows)]            # 3 x (N+1)
        S=sub[:,R]                   # 3 x nT x 3
        S=np.transpose(S,(1,0,2))
        d=np.linalg.det(S)
        scale=np.prod(np.max(np.abs(S),axis=2),axis=1)+1e-300
        v=d/scale
        k=np.argmin(v)
        if v[k]<worst[0]: worst=(v[k],(rows,T[k]))
    print(f"r={r:5.2f} min normalized 3x3 minor {worst[0]: .3e} at {worst[1]}",flush=True)
