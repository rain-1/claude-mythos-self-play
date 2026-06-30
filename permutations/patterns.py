import random

def catalan_upto(n):
    C=[1]*(n+1)
    for m in range(1,n+1):
        s=0
        for k in range(m): s+=C[k]*C[m-1-k]
        C[m]=s
    return C

def uniform_av231(n, C, rng):
    """uniform 231-avoiding permutation of 1..n, iterative recursive Catalan decomposition.
       sigma = L (max) R, where L on the k smallest values, R on the rest; P(k)=C_k C_{n-1-k}/C_n."""
    perm=[0]*n
    stack=[(1,n,0)]   # (lo,hi value range, start position)
    while stack:
        lo,hi,start=stack.pop()
        m=hi-lo+1
        if m<=0: continue
        if m==1: perm[start]=lo; continue
        tot=C[m]; r=rng.randrange(tot); acc=0; k=0
        for kk in range(m):
            acc+=C[kk]*C[m-1-kk]
            if r<acc: k=kk; break
        perm[start+k]=hi                       # max at split
        stack.append((lo,lo+k-1,start))        # left: k smallest values
        stack.append((lo+k,hi-1,start+k+1))    # right
    return perm

def avoids_231(p):
    n=len(p)
    # 231 pattern: i<j<k with p[k]<p[i]<p[j]
    # efficient: scan, maintain... do O(n^2) for small n test
    for i in range(n):
        for j in range(i+1,n):
            if p[j]>p[i]:
                for k in range(j+1,n):
                    if p[k]<p[i]: return False
    return True

if __name__=="__main__":
    from itertools import permutations
    C=catalan_upto(8)
    # verify count of Av(231) == Catalan
    for n in range(1,8):
        cnt=sum(1 for p in permutations(range(1,n+1)) if avoids_231(list(p)))
        print(f"n={n}: #Av(231)={cnt}  Catalan={C[n]}  match={cnt==C[n]}")
    # verify sampler produces only avoiders + rough uniformity n=4
    rng=random.Random(0); C=catalan_upto(50)
    from collections import Counter
    ct=Counter()
    for _ in range(14000):
        p=tuple(uniform_av231(4,C,rng)); assert avoids_231(list(p)); ct[p]+=1
    print(f"n=4 sampler: distinct={len(ct)}/{C[4]} counts min/mean/max={min(ct.values())}/{14000//C[4]}/{max(ct.values())}")
