"""MO 516862: T(n,k)=T(n,k-1)+gcd(T(n,k-1),(n+1)(k-1)+1), T(n,0)=1, a(n)=(n+1)T(n,n-1)-n^2.
Write T(n,k)=k+c_k. Then gcd(T_k, (n+1)k+1) = gcd(k+c_k, (n+1)c_k-1) and a(n)=(n+1)c_{n-1}-1."""
import numpy as np, numba as nb, sys, json
@nb.njit(cache=True)
def gcd(a,b):
    while b: a,b=b,a%b
    return a
@nb.njit(cache=True)
def run(n):
    """returns a(n), final c, index of last firing (k at which gcd>1 last, -1 if none), number of firings"""
    m=n+1; T=1; last=-1; nf=0
    for k in range(1,n):
        g=gcd(T,m*(k-1)+1)
        if g>1: last=k-1; nf+=1
        T+=g
    c=T-(n-1)
    return m*T-n*n, c, last, nf
@nb.njit(cache=True)
def isprime(x):
    if x<2: return False
    if x%2==0: return x==2
    d=3
    while d*d<=x:
        if x%d==0: return False
        d+=2
    return True
@nb.njit(cache=True)
def scan(N):
    out=[]
    for n in range(2,N+1):
        a,c,last,nf=run(n)
        assert a==(n+1)*c-1
        if not isprime(a): out.append((n,a,c,last,nf))
    return out
if __name__=="__main__":
    N=int(sys.argv[1])
    r=scan(N)
    for t in r: print(t)
    print(len(r))
