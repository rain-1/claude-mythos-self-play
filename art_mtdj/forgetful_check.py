# MO 515731 check: inscribed polygons given by arc sequences; forgetful iff all one-vertex deletions are dihedrally equal.
# Exhaustive over integer arc sequences (n arcs, each 1..K) to confirm: forgetful <=> constant or alternating arcs.
import itertools
def canon(seq):
    s=list(seq); n=len(s); best=None
    for r in (s, s[::-1]):
        for i in range(n):
            t=tuple(r[i:]+r[:i])
            if best is None or t<best: best=t
    return best
def forgetful(x):
    n=len(x); c=None
    for i in range(n):
        y=list(x); y[i]=x[i]+x[(i+1)%n]; del y[(i+1)%n]
        k=canon(y)
        if c is None: c=k
        elif k!=c: return False
    return True
for n in range(4,9):
    K=5 if n<=6 else 4
    bad=0; hits=0
    for x in itertools.product(range(1,K+1),repeat=n):
        if forgetful(x):
            hits+=1
            const=len(set(x))==1
            alt= n%2==0 and len(set(x[0::2]))==1 and len(set(x[1::2]))==1
            if not(const or alt): bad+=1; print('exception',x)
    print('n',n,'forgetful arc sequences',hits,'exceptions',bad)
