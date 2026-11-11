# Independent cross-checks for d=4: (a) number of undirected Hamiltonian decompositions of Q4,
# (b) number of decompositions invariant under s:(x1,x2,x3,x4)->(x2,x3,x4,1-x1) itself.
import sys; sys.argv=['q',4]
d=4;n=16
def ham_cycles():
    out=[]; path=[0]; used=[False]*n; used[0]=True
    def rec():
        v=path[-1]
        if len(path)==n:
            if bin(v).count('1')==1: out.append(tuple(path))
            return
        for i in range(d):
            w=v^(1<<i)
            if not used[w]:
                used[w]=True; path.append(w); rec(); path.pop(); used[w]=False
    rec(); return out
cyc=ham_cycles()
E=lambda c: frozenset(frozenset((c[k],c[(k+1)%n])) for k in range(n))
und=set(E(c) for c in cyc); alle=frozenset(frozenset((v,v^(1<<i))) for v in range(n) for i in range(d))
print('undirected Ham cycles',len(und),'; undirected Hamiltonian decompositions of Q4:',sum(1 for u in und if (alle-u) in und)//2)
A=lambda c: frozenset((c[k],c[(k+1)%n]) for k in range(n))
arcsets=[A(c) for c in cyc]; idx={a:i for i,a in enumerate(arcsets)}
s=[(v>>1)|((1-(v&1))<<3) for v in range(n)]
img=[idx[frozenset((s[a],s[b]) for a,b in X)] for X in arcsets]
# enumerate s-invariant decompositions: unions of s-orbits of cycles that are pairwise arc-disjoint and total 4 cycles
orbs=set()
for i in range(len(cyc)):
    o=[i]
    while img[o[-1]]!=i: o.append(img[o[-1]])
    orbs.add(frozenset(o))
orbs=[o for o in orbs if len(o)<=4 and all(not(arcsets[a]&arcsets[b]) for a in o for b in o if a<b)]
from collections import Counter
print('s-orbits of cycles that are internally arc-disjoint, by size:',Counter(len(o) for o in orbs))
import itertools
cnt=Counter()
for k in (1,2,3,4):
    for f in itertools.combinations(orbs,k):
        if sum(len(o) for o in f)!=4: continue
        U=[c for o in f for c in o]
        if len(frozenset().union(*[arcsets[c] for c in U]))==64: cnt[tuple(sorted(len(o) for o in f))]+=1
print('s-invariant decompositions by s-orbit structure on the 4 cycles:',dict(cnt))
