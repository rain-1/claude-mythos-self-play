"""zeta(s) on a grid by Euler-Maclaurin (vectorised), good to ~1e-10 for |t| <= 150 with N=120, K=12."""
import numpy as np
from math import factorial
B2=[1/6,-1/30,1/42,-1/30,5/66,-691/2730,7/6,-3617/510,43867/798,-174611/330,854513/138,-236364091/2730,8553103/6]
def zeta(s,N=120,K=12):
    s=np.asarray(s,complex); n=np.arange(1,N)
    z=np.zeros_like(s)
    for chunk in range(0,s.size,200000):
        sl=slice(chunk,chunk+200000); ss=s.reshape(-1)[sl][:,None]
        z.reshape(-1)[sl]=np.sum(n[None,:]**(-ss),axis=1)
    z=z+N**(1-s)/(s-1)+N**(-s)/2
    term=s*N**(-s-1)   # k=1: B2/2! * s * N^{-s-1}
    rising=s.copy()
    for k in range(1,K+1):
        z=z+B2[k-1]/factorial(2*k)*rising*N**(-s-2*k+1)
        rising=rising*(s+2*k-1)*(s+2*k)
    return z
if __name__=="__main__":
    import mpmath
    for sv in (0.5+14.134725j, 0.7+50.3j, 1.0+100j, 0.45+140j, 0.9+2j, 2+0.5j):
        a=zeta(np.array([sv]))[0]; b=complex(mpmath.zeta(sv)); print(sv, abs(a-b))
