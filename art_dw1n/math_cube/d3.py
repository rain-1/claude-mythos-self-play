# d=3: max arc-disjoint directed Hamiltonian cycles, leftover structure, undirected double covers.
import itertools, json
from collections import Counter
d=3; n=8
def ham_cycles(d):
    n=1<<d; out=[]; path=[0]; used=[False]*n; used[0]=True
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
cyc=ham_cycles(d)
def arcs(c): return frozenset((c[k],c[(k+1)%n]) for k in range(n))
def edges(c): return frozenset(frozenset(a) for a in arcs(c))
A=[arcs(c) for c in cyc]
print('directed Ham cycles:',len(cyc)); 
for c in cyc: print(' ',c,''.join(str((c[k]^c[(k+1)%n]).bit_length()-1) for k in range(n)))
und=sorted(set(edges(c) for c in cyc),key=sorted); print('undirected Ham cycles:',len(und))
allarcs=frozenset((v,v^(1<<i)) for v in range(n) for i in range(d))
# max family of pairwise arc-disjoint
best=0
for k in range(1,4):
    fam=[f for f in itertools.combinations(range(len(cyc)),k) if all(not(A[a]&A[b]) for a,b in itertools.combinations(f,2))]
    print('families of',k,'pairwise arc-disjoint directed Ham cycles:',len(fam))
    if fam: best=k; bestfam=fam
# undirected double covers: multisets of 3 undirected ham cycles covering each edge exactly twice
cnt=0
for f in itertools.combinations_with_replacement(range(len(und)),3):
    c=Counter(e for i in f for e in und[i])
    if len(c)==12 and all(v==2 for v in c.values()): cnt+=1
print('undirected Hamiltonian double covers of Q3 (3 cycles, each edge twice):',cnt)
# group with reversal
G=[]
for p in itertools.permutations(range(d)):
    for x in range(n):
        G.append(tuple((sum(((v>>i)&1)<<p[i] for i in range(d)))^x for v in range(n)))
def img(g,S,r): 
    return frozenset(((g[b],g[a]) if r else (g[a],g[b])) for a,b in S)
def leftover_struct(L):
    # L: set of 8 arcs, in=out degree 1 at every vertex => a permutation; cycle lengths
    s=dict(L); assert len(s)==8 and sorted(s.values())==list(range(8))
    seen=set(); lens=[]
    for v in range(n):
        if v not in seen:
            l=0;u=v
            while u not in seen: seen.add(u);u=s[u];l+=1
            lens.append(l)
    return tuple(sorted(lens))
seen=set(); reps=[]
for f in bestfam:
    key=frozenset(A[i] for i in f)
    if key in seen: continue
    orb=set()
    for g in G:
        for r in (0,1): orb.add(frozenset(img(g,A[i],r) for i in f))
    seen|=orb
    L=allarcs-A[f[0]]-A[f[1]]
    same_und = edges(cyc[f[0]])==edges(cyc[f[1]])
    shared=len(edges(cyc[f[0]])&edges(cyc[f[1]]))
    reps.append(dict(cycles=[list(cyc[i]) for i in f],orbit_size=len(orb),reverse_pair=same_und,shared_undirected_edges=shared,
        leftover_cycle_lengths=leftover_struct(L),leftover=sorted(L)))
print('orbits of arc-disjoint pairs under Aut(Q3) x reversal:',len(reps))
for r in reps: print(json.dumps(r))
