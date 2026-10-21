# Exact distribution of X = #triangles containing the centre, n random points on a circle.
# Counts are out of 2^(n-1).  Two methods: brute force over sign vectors (via k_i), and
# transfer matrix over the walk W_t = (s_{t+1}+..+s_n) - (s_1+..+s_t).
import itertools, json, sys
import numpy as np
from math import comb

def X_bruteforce(s):
    n=len(s); tot=0
    for i in range(n):
        k=sum(1 for j in range(i+1,n) if s[j]==s[i])+sum(1 for j in range(i) if s[j]!=s[i])
        tot+=comb(k,2)
    return comb(n,3)-tot

def X_walk(s):
    n=len(s); S=sum(s); P=0; Q=0
    for t in range(n):
        Q+=(S-2*P)**2; P+=s[t]
    assert (n**3+2*n-3*Q)%24==0
    return (n**3+2*n-3*Q)//24

def dist_brute(n):
    d={}
    for s in itertools.product((1,-1),repeat=n-1):
        s=(1,)+s; x=X_bruteforce(s); assert x==X_walk(s); d[x]=d.get(x,0)+1
    return d

def dist_tm(n):
    """sum over s in {+-1}^n of z^{Q/4-ish}: Q=sum_{t=0}^{n-1} W_t^2, W walk with steps -+2 from S to -S."""
    # use V = W (integers, parity n), index Q directly; Q <= n*n^2
    Qmax=n**3
    use_obj = n>60
    dt = object if use_obj else np.int64
    total=np.zeros(Qmax+1,dtype=dt)
    off=n
    for S in range(-n,n+1,2):
        # state: W value -> polynomial in Q (array)
        cur={S:np.zeros(Qmax+1,dtype=dt)}; cur[S][0]=1
        for t in range(n):
            nxt={}
            for W,poly in cur.items():
                w2=W*W
                sh=np.zeros_like(poly); sh[w2:]=poly[:Qmax+1-w2]
                for d in (-2,2):
                    W2=W+d
                    # remaining steps n-t-1 must allow reaching -S
                    if abs(W2-(-S))>2*(n-t-1): continue
                    if W2 in nxt: nxt[W2]=nxt[W2]+sh
                    else: nxt[W2]=sh.copy()
            cur=nxt
        if -S in cur: total=total+cur[-S]
    d={}
    for Q in np.nonzero(total)[0]:
        Q=int(Q); x=(n**3+2*n-3*Q)
        assert x%24==0
        d[x//24]=int(total[Q])//2   # s and -s give the same configuration
    return d

if __name__=="__main__":
    N=int(sys.argv[1])
    out={}
    for n in range(3,N+1):
        d=dist_tm(n); assert sum(d.values())==2**(n-1)
        if n<=16: assert d==dist_brute(n), n
        out[n]={x:d[x] for x in sorted(d)}
        print(n, file=sys.stderr, flush=True)
    json.dump({str(n):{str(x):c for x,c in v.items()} for n,v in out.items()},open('dist.json','w'))
