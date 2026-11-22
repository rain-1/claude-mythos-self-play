"""hidden.py n [cap] : look for tossprint coincidences NOT explained by reversal + stutter moves among
the STRUCTURED words of n corners: all products alpha o beta (n = a*b) and all stutter candidates.
(Not exhaustive over all 2^(n-1) strings, but these are the words whose stair polynomial is reducible
for a known reason.)"""
import sys, itertools, subprocess, collections
from verify import comp, cls, neighbours
from count2 import closure, strings
n=int(sys.argv[1]); cap=int(sys.argv[2]) if len(sys.argv)>2 else 22
W=set()
for a in range(2,n):
    if n%a: continue
    b=n//a
    if a-1+b-1>cap: continue
    for x in strings(a-1):
        for y in strings(b-1): W.add(comp(x,[y]*a))
for b in range(3,n):
    if n%b: continue
    m=n//b
    by={}
    for be in strings(b-1): by.setdefault(be.count('1'),[]).append(be)
    for a in range(2,m):
        if m%a or m//a<2: continue
        r=m//a
        tot=sum(len(v)**r for v in by.values())*2**(a-1)*2**(r-1)
        if tot>2**cap: continue
        for g in strings(r-1):
            for al in strings(a-1):
                x=comp(g,[al]*r)
                for bl in by.values():
                    for tup in itertools.product(bl,repeat=r):
                        W.add(comp(x,[t for t in tup for _ in range(a)]))
W=sorted(W)
out=subprocess.run(['./tosshash'],input='\n'.join(W)+'\n',capture_output=True,text=True).stdout.split()
G=collections.defaultdict(list)
for w,h in zip(W,out): G[h].append(w)
bad=0; big=0
for h,ws in G.items():
    if len(ws)<2: continue
    C=closure(ws[0]); big+=1
    if not set(ws)<=C:
        bad+=1
        if bad<=6: print('UNEXPLAINED:', ws[0], [w for w in ws if w not in C][:3], flush=True)
print(f'n={n}: {len(W)} structured words, {big} tossprint groups of size>1, {bad} not explained', flush=True)
