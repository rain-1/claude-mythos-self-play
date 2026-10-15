"""Back-and-forth construction of a Z x Z-scrambling, run for finitely many steps.
Requirements are enumerated as an interleaved sequence:
  step 2n   : CELL task  -> n-th cell in spiral order gets a value (if not yet set)
  step 2n+1 : VALUE task -> n-th triple (family, k, v): ensure value v occurs on line (family,k)
Each step extends a finite partial assignment that is injective on every line.
Families: row (y=k), col (x=k), diag (x-y=k)  [+ anti (x+y=k) if ANTI]."""
import sys, itertools
ANTI = len(sys.argv)>2 and sys.argv[2]=='anti'
FAM = ['row','col','diag'] + (['anti'] if ANTI else [])
def lines_of(x,y):
    d={'row':y,'col':x,'diag':x-y,'anti':x+y}; return [(F,d[F]) for F in FAM]
def cells_on(F,k,i):  # i-th cell of line (F,k), parametrised by integer i
    return {'row':(i,k),'col':(k,i),'diag':(i+k,i),'anti':(i,k-i)}[F]
def zz(n): return (n+1)//2 if n%2 else -(n//2)   # 0,1,-1,2,-2,...
def spiral():
    yield (0,0); r=1
    while True:
        for t in range(2*r): yield (r,-r+1+t)
        for t in range(2*r): yield (r-1-t,r)
        for t in range(2*r): yield (-r,r-1-t)
        for t in range(2*r): yield (-r+1+t,-r)
        r+=1
def triples():   # enumerate (F,k,v) in Z-order: all with max(|k|,|v|)<=s, s=0,1,...
    seen=set()
    for s in itertools.count():
        for F in FAM:
            for a in range(-s,s+1):
                for b in range(-s,s+1):
                    if max(abs(a),abs(b))==s: yield (F,a,b)
f={}; used={}  # used[(F,k)] = set of values on that line
def ok(c,v): return all(v not in used.get(L,()) for L in lines_of(*c))
def put(c,v):
    assert c not in f and ok(c,v); f[c]=v
    for L in lines_of(*c): used.setdefault(L,set()).add(v)
N=int(sys.argv[1]); sp=spiral(); tr=triples(); far=0
for n in range(N):
    c=next(sp)
    if c not in f:     # free cell: smallest |v| not blocked (finitely many blocked)
        v=next(zz(j) for j in itertools.count() if ok(c,zz(j)))
        put(c,v)
    F,k,v=next(tr)
    if v not in used.get((F,k),()):   # place v on line: finitely many cells are bad
        i=next(zz(j) for j in itertools.count() if cells_on(F,k,zz(j)) not in f and ok(cells_on(F,k,zz(j)),v))
        c2=cells_on(F,k,i); put(c2,v); far=max(far,max(abs(c2[0]),abs(c2[1])))
# verify invariant
for L,S in used.items(): pass
cnt={}
for c,v in f.items():
    for L in lines_of(*c): cnt[(L,v)]=cnt.get((L,v),0)+1
assert max(cnt.values())==1
print(f'{N} rounds, {len(f)} cells assigned, injective on all lines: True; farthest value-placement cell: {far}')
