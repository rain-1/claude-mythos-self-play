"""Fast version of MO 516862 via the reformulation
   state (T, c), N = (n+1)c - 1;  next firing = least T' >= T with gcd(T', N) > 1  (T' <= n-2+c);
   then g = gcd(T', N), c += g-1, T = T'+g.  The least T' is min over primes q | N of ceil(T/q) q,
   and trial division may stop as soon as q exceeds the best candidate so far."""
import numpy as np, numba as nb, sys
from rec import gcd
def primes_upto(M):
    s=np.ones(M+1,np.bool_); s[:2]=False
    for i in range(2,int(M**.5)+1):
        if s[i]: s[i*i::i]=False
    return np.nonzero(s)[0].astype(np.int64)
@nb.njit(cache=True)
def one(n,pr):
    m=n+1; T=1; c=1; last=-1; nf=0; gm=1
    while True:
        N=m*c-1
        hi=n-2+c                 # largest T at which a gcd is evaluated
        best=hi+1
        for i in range(len(pr)):
            q=pr[i]
            if q>=best or q>hi: break
            if N%q==0:
                t=((T+q-1)//q)*q
                if t<best: best=t
        if best>hi: break
        g=gcd(best,N)
        last=best-c; nf+=1
        if g>gm: gm=g
        c+=g-1; T=best+g
    a=m*c-1
    # primality by trial division
    isp=1
    for i in range(len(pr)):
        q=pr[i]
        if q*q>a: break
        if a%q==0: isp=0; break
    if pr[-1]*pr[-1]<a and isp==1: isp=2   # table too short: undecided
    return a,c,last,nf,gm,isp
@nb.njit(parallel=True)
def scan(lo,hi,pr):
    M=hi-lo
    A=np.zeros(M,np.int64);C=np.zeros(M,np.int64);L=np.zeros(M,np.int64);F=np.zeros(M,np.int64);G=np.zeros(M,np.int64);P=np.zeros(M,np.uint8)
    for j in nb.prange(M):
        A[j],C[j],L[j],F[j],G[j],P[j]=one(lo+j,pr)
    return A,C,L,F,G,P
if __name__=="__main__":
    lo,hi=int(sys.argv[1]),int(sys.argv[2])
    pr=primes_upto(40*hi)
    A,C,L,F,G,P=scan(lo,hi,pr)
    np.savez('fast_%d_%d.npz'%(lo,hi),A=A,C=C,L=L,F=F,G=G,P=P,lo=lo)
    n=np.arange(lo,hi)
    print('undecided',(P==2).sum(),'composite n:',list(n[P==0]))
