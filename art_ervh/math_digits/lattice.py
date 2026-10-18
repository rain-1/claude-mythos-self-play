# Residual lattice after the capture fixed point: vectors over uncaptured primes.
# 1) iterated singleton pruning (a prime occurring in one vector only),
# 2) HNF of the core (if any), 3) exact membership test e_q in L for pruned vectors' private primes.
import sys, collections
from sympy import Matrix
from sympy.matrices.normalforms import hermite_normal_form
V=[]
for line in open(sys.argv[1]):
    a=line.split(); V.append({int(x.split(':')[0]):int(x.split(':')[1]) for x in a[1:]})
print('residual vectors',len(V))
occ=collections.defaultdict(set)
for i,v in enumerate(V):
    for p in v: occ[p].add(i)
alive=set(range(len(V))); order=[]   # (vector index, private prime)
stack=[p for p in occ if len(occ[p])==1]
while stack:
    p=stack.pop()
    if len(occ[p])!=1: continue
    i=next(iter(occ[p])); 
    if i not in alive: continue
    alive.discard(i); order.append((i,p))
    for q in V[i]:
        occ[q].discard(i)
        if len(occ[q])==1: stack.append(q)
core=sorted(alive); cprimes=sorted({p for i in core for p in V[i]})
print('pruned',len(order),'core vectors',len(core),'core primes',len(cprimes))
newcap=[]
if core:
    if len(cprimes)>400: print('core too large for dense HNF'); sys.exit()
    idx={p:j for j,p in enumerate(cprimes)}
    M=Matrix([[V[i].get(p,0) for p in cprimes] for i in core]).T  # columns = generators
    H=hermite_normal_form(M)
    print('core lattice rank',H.shape)
    # e_p in L iff solvable; check via HNF columns
    import sympy
    for p in cprimes:
        e=Matrix([1 if q==p else 0 for q in cprimes])
        try:
            sol=H.gauss_jordan_solve(e)[0]
            if all(x.is_integer for x in sol): newcap.append(p)
        except ValueError: pass
print('primes newly in G via lattice:',sorted(newcap)[:50], len(newcap))
for i in core: print('core',V[i])
# exact test for pruned private primes
import heapq
pos={p:k for k,(i,p) in enumerate(order)}
corevecs=[V[i] for i in core]
def in_core(w):
    if not w: return True
    if not core: return False
    M=Matrix([[v.get(p,0) for v in corevecs] for p in cprimes]); b=Matrix([w.get(p,0) for p in cprimes])
    if any(p not in idx for p in w): return False
    from sympy.solvers.diophantine.diophantine import diophantine
    # small: brute HNF via smith
    from sympy.matrices.normalforms import smith_normal_form
    return None
hits=[];unknown=0
for k,(i,q) in enumerate(order):
    if V[i][q]!=1: continue
    w=dict(V[i]); del w[q]; ok=True
    h=[(pos[p],p) for p in w if p in pos and pos[p]>k]
    if any(p in pos and pos[p]<k for p in w): ok=False
    heapq.heapify(h)
    while h and ok:
        j,p=heapq.heappop(h)
        if p not in w: continue
        vi=V[order[j][0]]; c,r=divmod(w[p],vi[p])
        if r: ok=False;break
        for t,e in vi.items():
            w[t]=w.get(t,0)-c*e
            if w[t]==0: del w[t]
            elif t in pos and pos[t]>j: heapq.heappush(h,(pos[t],t))
            elif t in pos and pos[t]<=j: ok=False
    if ok:
        r=in_core(w)
        if r is None: unknown+=1; print("undecided q",q,"residual",w)
        elif r: hits.append(q)
print('pruned primes newly in G:',sorted(hits)[:30],len(hits),'undecided(core needed):',unknown)
