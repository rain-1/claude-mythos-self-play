import numpy as np
from functools import lru_cache
from math import factorial

def partitions(n, mx=None):
    if mx is None: mx=n
    if n==0: return [()]
    out=[]
    for k in range(min(n,mx),0,-1):
        for rest in partitions(n-k,k): out.append((k,)+rest)
    return out

def beta_of(lam, m):
    lam=list(lam)+[0]*(m-len(lam))
    return tuple(lam[i]+(m-1-i) for i in range(m))

@lru_cache(maxsize=None)
def mn(beta, alpha):
    """Murnaghan-Nakayama via abacus. beta: sorted-desc tuple of bead positions; alpha: cycle type tuple."""
    if not alpha: return 1
    k=alpha[0]; rest=alpha[1:]; bs=set(beta); total=0
    for i,bp in enumerate(beta):
        if bp>=k and (bp-k) not in bs:
            height=sum(1 for b in beta if bp-k < b < bp)
            nb=sorted((b if idx!=i else bp-k for idx,b in enumerate(beta)),reverse=True)
            total+=(-1)**height * mn(tuple(nb), rest)
    return total

def char(lam, mu, n):
    return mn(beta_of(lam,n), tuple(mu))

def hook_dim(lam):
    n=sum(lam); lam=list(lam); conj=[sum(1 for x in lam if x>j) for j in range(lam[0])]
    prod=1
    for i,r in enumerate(lam):
        for j in range(r): prod*=(r-j)+(conj[j]-i)-1
    return factorial(n)//prod

def zmu(mu):
    from collections import Counter
    c=Counter(mu); z=1
    for part,m in c.items(): z*= (part**m)*factorial(m)
    return z

if __name__=="__main__":
    # S_3 check
    P3=partitions(3)
    print("partitions(3)",P3)
    for lam in P3: print(lam, [char(lam,mu,3) for mu in P3])
    # verify dims = hook length, and row orthogonality, for n up to 8
    for n in [5,8]:
        P=partitions(n)
        ok_dim=all(char(lam,tuple([1]*n),n)==hook_dim(lam) for lam in P)
        # row orthogonality: sum_mu |C_mu| chi^lam(mu) chi^nu(mu) = n! delta
        bad=0
        for a in range(len(P)):
            for b in range(a,len(P)):
                ssum=sum((factorial(n)//zmu(mu))*char(P[a],mu,n)*char(P[b],mu,n) for mu in P)
                exp=factorial(n) if a==b else 0
                if ssum!=exp: bad+=1
        print(f"n={n}: #irreps={len(P)} dims==hook:{ok_dim} orthogonality violations:{bad}")
