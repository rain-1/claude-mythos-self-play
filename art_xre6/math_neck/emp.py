import sys, math
from drive import search
from construct import check, construct
sys.path.insert(0,'..'); from neck import EX
from drive import canon
for k,N in EX.items():
    c=construct(k); print(k, 'asker==construction up to symmetry:', canon(N)==canon(c) if len(N)<200 else None)
def pf(m):
    return {p for p in range(2,m+1) if m%p==0 and all(p%q for q in range(2,p))}
for k,hi in ((3,30),(4,36)):
    for n in range(k,hi+1):
        sols,_=search(k,n,2000)
        viol=0; trip=0
        for s in sols:
            M=check(s)['mult']
            from collections import Counter
            cnt=Counter(p for m in M.values() for p in pf(m))
            if any(v>=3 for v in cnt.values()): trip+=1
        if sols: print(k,n,len(sols),'classes; with a prime dividing >=3 multiplicities:',trip, 'example',sorted(sols)[0], check(sorted(sols)[0])['mult'])
