"""Exact recursion for the MISSING set M_k = Z[i] \ D_k:  M_{k+1} = b M_k  u  (1 - b M_k)
(z -> bz and z -> 1-bz are bijections of Z[i] onto the even / odd cosets of b Z[i], and
D_{k+1} is the union of the images of D_k, so the complement obeys the same rule).
Hence s_{k+1} = min(2 s_k, min_{z in M_k} |1-bz|^2) and only missing points with
|z| <= sqrt(s_k)+3 can ever matter.  Track that annulus exactly with Python integers."""
import sys, json
from math import isqrt
K=int(sys.argv[1]) if len(sys.argv)>1 else 64
def closed(k):
    if k<2: return 1
    j=(k-2)//4; r=(k-2)%4; u=(2**(2*j+1)+1)//3
    return [(u*u+1)//2,u*u,2*u*u,4*u*u][r]
# start from brute force at k=10
import numpy as np
x=np.zeros(1,np.int64); y=np.zeros(1,np.int64)
k0=10
for k in range(1,k0+1):
    bx=x-y; by=x+y; x=np.concatenate([bx,1-bx]); y=np.concatenate([by,-by])
D=set(zip(x.tolist(),y.tolist())); R=40
A={(a,b) for a in range(-R,R+1) for b in range(-R,R+1) if (a,b) not in D}
def keep(A):
    s=min(a*a+b*b for a,b in A)
    # |z| <= sqrt(s)+3  <=>  |z|^2 <= s + 6 sqrt(s) + 9  (use ceil of sqrt: superset is fine)
    lim=s+6*(isqrt(s)+1)+9
    return s,{z for z in A if z[0]*z[0]+z[1]*z[1]<=lim}
s,A=keep(A); rows=[]
for k in range(k0,K+1):
    mn=sorted(A,key=lambda z:z[0]*z[0]+z[1]*z[1])[:3]
    gaps=[z[0]*z[0]+z[1]*z[1]-s for z in mn]
    print(k,s,s==closed(k),len(A),mn[0],gaps,flush=True)
    rows.append(dict(k=k,s=str(s),ok=s==closed(k),annulus=len(A),nearest=[str(mn[0][0]),str(mn[0][1])]))
    B=set()
    for a,b in A:
        B.add((a-b,a+b)); B.add((1-(a-b),-(a+b)))
    s,A=keep(B)
json.dump(rows,open(__file__.replace('annulus.py','annulus_check.json'),'w'))
