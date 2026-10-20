"""Count square-free 2-colourings of the n x n grid with colour(rot90 p) = 1 - colour(p) (n even),
modulo nothing (all of them), by SAT enumeration with blocking clauses on the n^2/4 free cells."""
import sys, time, json
from pysat.solvers import Cadical153
def squares(n):
    for s in range(1,n):
        for r in range(n-s):
            for c in range(n-s):
                yield [(r,c),(r,c+s),(r+s,c),(r+s,c+s)]
def run(n, limit=10**7):
    # orbit representative: cells (r,c) in the top-left quadrant
    def lit(r,c):
        # map (r,c) to quadrant rep with sign: rot90(r,c)=(c,n-1-r) flips colour
        k=0
        while not (r<n//2 and c<n//2):
            r,c=c,n-1-r; k+=1
        v=r*(n//2)+c+1
        return v if k%2==0 else -v
    cls=set()
    for sq in squares(n):
        L=[lit(*p) for p in sq]
        if len(set(L))<4 and any(-x in L for x in L):
            continue   # contains both x and ¬x -> never monochrome
        cls.add(tuple(sorted(set(L)))); cls.add(tuple(sorted(set(-x for x in L))))
    s=Cadical153(bootstrap_with=[list(c) for c in cls])
    m=(n//2)**2; cnt=0; t=time.time(); sols=[]
    while s.solve():
        mod=s.get_model()[:m]; cnt+=1
        if len(sols)<50: sols.append(mod)
        s.add_clause([-x for x in mod])
        if cnt>=limit: break
    return cnt,time.time()-t,sols
if __name__=='__main__':
    for n in map(int,sys.argv[1:]):
        c,dt,sols=run(n); print(n,c,f'{dt:.1f}s',flush=True)
        json.dump(sols,open(f'anti90_{n}.json','w'))
