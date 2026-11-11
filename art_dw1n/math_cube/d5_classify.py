# Classify the 96 rho-invariant decompositions of d=5 (rho = cyclic coordinate shift acting as a 5-cycle
# on the 5 Hamiltonian cycles) under N = normaliser of <rho> in Aut(Q5) (affine coordinate maps i->a*i+b,
# times complement of all bits; order 40), together with global reversal (order 80).
import json
from collections import Counter
d=5;n=32
C=[tuple(map(int,l.split()[1:])) for l in open('ansatz_d5_all.txt') if l.startswith('example')]
def succ(c):
    s=[0]*n
    for k in range(n): s[c[k]]=c[(k+1)%n]
    return tuple(s)
def rho(v,k=1): k%=d; return ((v<<k)|(v>>(d-k)))&31 if k else v
def act(g,s):
    t=[0]*n
    for v in range(n): t[g[v]]=g[s[v]]
    return tuple(t)
def rev(s):
    t=[0]*n
    for v in range(n): t[s[v]]=v
    return tuple(t)
R=tuple(rho(v) for v in range(n))
def dec(s):
    out=[s]
    for k in range(d-1): out.append(act(R,out[-1]))
    return frozenset(out)
D=set(dec(succ(c)) for c in C); print('cycles',len(C),'decompositions',len(D))
N=[]
for a in (1,2,3,4):
    for b in range(5):
        for x in (0,31):
            N.append(tuple(sum(((v>>i)&1)<<((a*i+b)%5) for i in range(d))^x for v in range(n)))
anti=tuple(v^31 for v in range(n))
def tolist(s):
    c=[0]
    while len(c)<n: c.append(s[c[-1]])
    return c
def trans(s):
    c=tolist(s); return ''.join(str((c[k]^c[(k+1)%n]).bit_length()-1) for k in range(n))
seen=set(); reps=[]
for X in sorted(D,key=sorted):
    if X in seen: continue
    orb=set(); stab=0
    for g in N:
        for r in (0,1):
            Y=frozenset((rev(act(g,s)) if r else act(g,s)) for s in X); assert Y in D
            orb.add(Y); stab+=(Y==X)
    seen|=orb
    s0=sorted(X)[0]
    reps.append(dict(orbit_size=len(orb),stabiliser_in_N_x_rev=stab,
        each_cycle_fixed_by_antipodal=act(anti,s0)==s0, antipodal_reverses_each_cycle=rev(act(anti,s0))==s0,
        contains_reverse_pair=any(rev(s) in X for s in X),
        coord_counts_of_C=[trans(s0).count(str(i)) for i in range(d)],
        transition_sequence_of_C=trans(s0), C=tolist(s0)))
print('orbits under N x reversal (order 80):',len(reps),sorted(Counter(r['orbit_size'] for r in reps).items()))
for r in reps: print(json.dumps(r))
json.dump(reps,open('d5_ansatz_orbits.json','w'),indent=1)
