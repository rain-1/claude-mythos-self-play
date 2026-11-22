"""count.py n : PREDICTED a(n-1) - R(n) if tossprint equivalence = closure of stutter moves.
Enumerates every string that admits a non-ordinary stutter decomposition, takes its closure class,
and counts the BTvW (ribbon) classes inside it."""
import sys, itertools
from verify import comp, cls, neighbours
def strings(L):
    return [''.join(p) for p in itertools.product('01', repeat=L)]
def predicted(n, verbose=False):
    seen=set(); diff=0; ncls=0; ncand=0
    for b in range(3, n):
        if n%b: continue
        m=n//b
        byones={}
        for be in strings(b-1): byones.setdefault(be.count('1'),[]).append(be)
        for a in range(3, m):
            if m%a: continue
            r=m//a
            if r<2: continue
            alphas=[al for al in strings(a-1) if len(cls(al))>1]
            for g in strings(r-1):
                for al in alphas:
                    x=comp(g,[al]*r)
                    for k,bl in byones.items():
                        if len(bl)<2: continue
                        for tup in itertools.product(bl, repeat=r):
                            if len(set(tup))==1: continue
                            blocks=[t for t in tup for _ in range(a)]
                            w=comp(x,blocks); ncand+=1
                            if w in seen: continue
                            C=cls(w); seen|=C
                            k2=len(set(cls(u,True) for u in C))
                            diff+=k2-1; ncls+=1
    return diff, ncls, ncand
if __name__=='__main__':
    for n in map(int, sys.argv[1:]):
        d,c,k=predicted(n)
        print(f'n={n} N={n-1}: predicted R-a = {d}  ({c} closure classes from {k} candidate strings)', flush=True)
