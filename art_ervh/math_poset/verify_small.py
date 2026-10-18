"""Independent brute-force check of g(n) for n<=6: enumerate all naturally
labelled posets (strict order relations R subset of {(i,j): i<j}, transitive),
compute e by permutations, Aut by permutations, dedupe by canonical form.
Also brute-force e(P) by permutations for the n=8 optimum."""
import itertools
from fractions import Fraction
from math import factorial
def check(n):
    pairs=[(i,j) for i in range(n) for j in range(i+1,n)]
    perms=list(itertools.permutations(range(n)))
    seen=set(); best=Fraction(0); bestP=[]; cnt=0
    for mask in range(1<<len(pairs)):
        R={pairs[k] for k in range(len(pairs)) if mask>>k&1}
        if any((a,c) not in R for (a,b) in R for (b2,c) in R if b==b2): continue
        canon=min(tuple(sorted((p[a],p[b]) for a,b in R)) for p in perms)
        if canon in seen: continue
        seen.add(canon); cnt+=1
        e=sum(1 for p in perms if all(p[a]<p[b] for a,b in R))
        aut=sum(1 for p in perms if {(p[a],p[b]) for a,b in R}==R)
        f=Fraction(e,aut)
        if f>best: best=f; bestP=[R]
        elif f==best: bestP.append(R)
    print(n,cnt,'posets; g =',best,'attained by',len(bestP))
for n in range(1,7): check(n)
cov=[(1,5),(1,6),(2,5),(2,7),(3,5),(4,6)]
print('n=8 spider check e =',sum(1 for p in itertools.permutations(range(8)) if all(p[a]<p[b] for a,b in cov)))
