# Classify the d=4 decompositions under Aut(Q4) (384) and Aut(Q4) x <reversal> (768).
import sys, itertools, json, pickle
from collections import Counter, defaultdict
d=4; n=16
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
def succ_of(c):
    s=[0]*n
    for k in range(n): s[c[k]]=c[(k+1)%n]
    return tuple(s)
S=[succ_of(c) for c in cyc]; idx={s:i for i,s in enumerate(S)}
def amask(s): 
    m=0
    for v in range(n): m|=1<<(v*d+((v^s[v]).bit_length()-1))
    return m
A=[amask(s) for s in S]
full=(1<<(d*n))-1
sols=[]
def cover(mask,chosen):
    if mask==full: sols.append(tuple(sorted(chosen))); return
    free=(~mask)&full; a=free&-free
    for i,m in enumerate(A):
        if m&a and not m&mask:
            chosen.append(i); cover(mask|m,chosen); chosen.pop()
cover(0,[])
sols=sorted(set(sols)); print('cycles',len(cyc),'decompositions',len(sols))
# group
G=[]
for p in itertools.permutations(range(d)):
    for x in range(n):
        g=tuple((sum(((v>>i)&1)<<p[i] for i in range(d)))^x for v in range(n))
        G.append((p,x,g))
def act(g,s):
    t=[0]*n
    for v in range(n): t[g[v]]=g[s[v]]
    return tuple(t)
T=[[idx[act(g,s)] for s in S] for (_,_,g) in G]
def rev(s):
    t=[0]*n
    for v in range(n): t[s[v]]=v
    return tuple(t)
R=[idx[rev(s)] for s in S]
solset=set(sols)
def app(gi,sol,r=False):
    t=[T[gi][c] for c in sol]
    if r: t=[R[c] for c in t]
    return t
def orbits(with_rev):
    seen={}; orbs=[]
    for s in sols:
        if s in seen: continue
        O=set()
        for gi in range(len(G)):
            for r in ([False,True] if with_rev else [False]):
                t=tuple(sorted(app(gi,s,r))); assert t in solset; O.add(t)
        for t in O: seen[t]=len(orbs)
        orbs.append(sorted(O))
    return orbs,seen
orb1,_=orbits(False); orb2,seen2=orbits(True)
print('orbits under Aut(Q4):',len(orb1),sorted(Counter(len(o) for o in orb1).items()))
print('orbits under Aut x rev:',len(orb2),sorted(Counter(len(o) for o in orb2).items()))
def trans(c):
    return ''.join(str((c[k]^c[(k+1)%n]).bit_length()-1) for k in range(n))
def canon_trans(c):
    # canonical transition sequence up to rotation, reversal, relabelling of coordinates
    t=[(c[k]^c[(k+1)%n]).bit_length()-1 for k in range(n)]
    best=None
    for tt in (t,t[::-1]):
        for r in range(n):
            u=tt[r:]+tt[:r]; m={}; w=[]
            for x in u:
                if x not in m: m[x]=len(m)
                w.append(m[x])
            w=''.join(map(str,w))
            if best is None or w<best: best=w
    return best
def perm_cycle_type(pm):
    k=len(pm); seen=[0]*k; ty=[]
    for i in range(k):
        if not seen[i]:
            l=0;j=i
            while not seen[j]: seen[j]=1;j=pm[j];l+=1
            ty.append(l)
    return tuple(sorted(ty))
antip=[i for i,(p,x,g) in enumerate(G) if p==tuple(range(d)) and x==15][0]
def gorder(g):
    k=1; h=g
    while h!=tuple(range(n)): h=tuple(g[v] for v in h); k+=1
    return k
out=[]
# conjugacy classes of Aut(Q4) elems: use (order, cycle type on vertices) as fingerprint
def vtype(g): return perm_cycle_type(list(g))
s_map=tuple(( (v<<1)&15 | (1-((v>>3)&1)) ) for v in range(n))  # x_i -> position i+1, new x0 = 1-x3
# s:(x1,x2,x3,x4)->(x2,x3,x4,1-x1): new coord i = old coord i+1, new coord 3 = 1-old coord 0
s_map2=tuple(( (v>>1) | ((1-(v&1))<<3) ) for v in range(n))
print('order of s:',gorder(s_map2), 'vertex cycle type',vtype(s_map2))
sclass=vtype(s_map2)
for oi,O in enumerate(orb2):
    s=O[0]
    stab=[]; 
    for gi in range(len(G)):
        for r in (False,True):
            t=app(gi,s,r)
            if tuple(sorted(t))==s:
                pm=[s.index(x) for x in t]
                stab.append((gi,r,tuple(pm)))
    stab_norev=[x for x in stab if not x[1]]
    paired=sorted(R[c] for c in s)==list(s)
    npairs=sum(1 for c in s if R[c] in s)//2
    cyc4=[(G[gi][0],G[gi][1],r,gorder(G[gi][2])) for gi,r,pm in stab if perm_cycle_type(pm)==(4,)]
    s_inv=[(G[gi][0],G[gi][1],r) for gi,r,pm in stab if gorder(G[gi][2])==8]
    ap_fixed=[T[antip][c]==c for c in s]
    ap_rev=[T[antip][c]==R[c] for c in s]
    pmtypes=Counter((perm_cycle_type(pm),r) for gi,r,pm in stab)
    rec=dict(orbit=oi,size_under_Aut_x_rev=len(O),
      sizes_of_Aut_orbits_inside=sorted(len(o) for o in orb1 if seen2[o[0]]==oi),
      stab_size_Aut=len(stab_norev),stab_size_Aut_x_rev=len(stab),
      n_reverse_pairs=npairs,fully_paired=paired,
      has_cyclic4_symmetry_no_reversal=any(not r for _,_,r,_ in cyc4),
      has_cyclic4_symmetry_with_reversal=any(r for _,_,r,_ in cyc4),
      cyclic4_elements=[dict(perm=list(p),xor=x,reversal=r,order=o) for p,x,r,o in cyc4],
      order8_elements_in_stab=[dict(perm=list(p),xor=x,reversal=r) for p,x,r in s_inv],
      stab_action_types={str(k):v for k,v in pmtypes.items()},
      antipodal_fixes_cycle=ap_fixed, antipodal_reverses_cycle=ap_rev,
      transition_sequences=[trans(cyc[c]) for c in s],
      transition_types=[canon_trans(cyc[c]) for c in s],
      coord_counts=[[trans(cyc[c]).count(str(i)) for i in range(d)] for c in s],
      cycles=[list(cyc[c]) for c in s])
    out.append(rec)
    print(json.dumps({k:v for k,v in rec.items() if k not in('cycles',)}))
# all solutions invariant under some order-8 element (with or without reversal)
o8=[gi for gi,(p,x,g) in enumerate(G) if gorder(g)==8]
print('order-8 elements in Aut(Q4):',len(o8),'vertex types',Counter(vtype(G[gi][2]) for gi in o8))
cnt=Counter()
for s in sols:
    for gi in o8:
        for r in (False,True):
            if tuple(sorted(app(gi,s,r)))==s: cnt[(r)]+=1
print('(solution,order-8 g) invariant incidences by reversal flag:',dict(cnt))
print('paired-type count:',sum(1 for s in sols if sorted(R[c] for c in s)==list(s)))
print('by number of reverse pairs:',Counter(sum(1 for c in s if R[c] in s)//2 for s in sols))
print('distinct transition types among 2688 cycles:',Counter(canon_trans(c) for c in cyc))
json.dump(out,open('d4_orbits.json','w'),indent=1)
