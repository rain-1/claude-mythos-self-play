import json, math
from fractions import Fraction as F
D={int(n):{int(x):c for x,c in v.items()} for n,v in json.load(open('dist.json')).items()}
def cum(n):
    d=D[n];T=2**(n-1)
    m=[sum(F(c)*x**k for x,c in d.items())/T for k in range(5)]
    k2=m[2]-m[1]**2; k3=m[3]-3*m[2]*m[1]+2*m[1]**3
    k4=m[4]-4*m[3]*m[1]-3*m[2]**2+12*m[2]*m[1]**2-6*m[1]**4
    return k2,k3,k4
C={n:cum(n) for n in D}
for j,deg in ((1,6),(2,8)):
    # find polynomial of given degree with rational coeffs through points n=3..3+deg, test all
    import numpy as np
    pts=list(range(3,4+deg))
    # solve Vandermonde exactly
    A=[[F(n)**k for k in range(deg+1)] for n in pts]; b=[C[n][j] for n in pts]
    m=len(A)
    for i in range(m):
        p=next(r for r in range(i,m) if A[r][i]!=0); A[i],A[p]=A[p],A[i]; b[i],b[p]=b[p],b[i]
        for r in range(m):
            if r!=i and A[r][i]!=0:
                f=A[r][i]/A[i][i]; A[r]=[a-f*c for a,c in zip(A[r],A[i])]; b[r]-=f*b[i]
    co=[b[i]/A[i][i] for i in range(m)]
    ok=all(sum(c*F(n)**k for k,c in enumerate(co))==C[n][j] for n in D)
    print("cumulant",j+2,"poly fits all n:",ok,[str(c) for c in co])
# Laplace transform check: Q/n^2 = 8((n^3+2n)/24 - X)/n^2
for n in (20,40,60):
    d=D[n];T=2**(n-1)
    for lam in (0.5,1,2,5):
        L=sum(c*math.exp(-lam*8*((n**3+2*n)/24-x)/n**2) for x,c in d.items())/T
        print(n,lam,round(L,6),"sech:",round(1/math.cosh(math.sqrt(2*lam)),6))
# largest missing value (respecting parity for even n)
for n in range(5,61):
    d=D[n];M=max(d); step=2 if n%2==0 else 1
    miss=[x for x in range(M%step,M+1,step) if x not in d]
    print(n,"M",M,"largest missing",max(miss) if miss else None,"M-that",M-max(miss) if miss else None, "#support",len(d))
