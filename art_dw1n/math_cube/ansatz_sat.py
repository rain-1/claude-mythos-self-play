# Symmetric ansatz: find ONE directed Hamiltonian cycle C of Q_d whose d images under the cyclic
# coordinate shift rho (bit i -> bit i+1 mod d) are pairwise arc-disjoint (hence partition all arcs).
# Arc (v,i) = v -> v^(1<<i).  rho maps arc (v,i) to (rho v, i+1); rho acts freely on arcs, so
# the condition is: C contains exactly one arc of every rho-orbit, i.e. the "label"
# rho^{-i}(v) of the arcs (v,i) of C are all distinct (a bijection onto the vertices).
# SAT with lazily added subtour-elimination cuts.  usage: ansatz_sat.py d [seed] [count_all]
import sys, json, random, time
from pysat.solvers import Cadical153, Glucose4
from pysat.card import CardEnc, EncType
d=int(sys.argv[1]); seed=int(sys.argv[2]) if len(sys.argv)>2 else 0
n=1<<d; mask=n-1
def rho(v,k=1):
    k%=d; return ((v<<k)|(v>>(d-k)))&mask if k else v
var=lambda v,i: v*d+i+1
cl=[]
def exactly1(lits):
    cl.append(list(lits))
    for a in range(len(lits)):
        for b in range(a+1,len(lits)): cl.append([-lits[a],-lits[b]])
for v in range(n):
    exactly1([var(v,i) for i in range(d)])                 # out-degree 1
    exactly1([var(v^(1<<i),i) for i in range(d)])          # in-degree 1
    exactly1([var(rho(v,i),i) for i in range(d)])          # one arc per rho-orbit (label v)
    for i in range(d): cl.append([-var(v,i),-var(v^(1<<i),i)])  # no 2-cycles
random.seed(seed); random.shuffle(cl)
import os
S=(Cadical153 if os.environ.get("SOLVER")=="cadical" else Glucose4)(bootstrap_with=cl)
OUT=os.environ.get("OUT","ansatz_d%d.json"%d)
t0=time.time(); it=0
while True:
    it+=1
    if not S.solve(): print('UNSAT: ansatz impossible for d=%d (after %d rounds, %.1fs)'%(d,it,time.time()-t0)); sys.exit()
    m=S.get_model(); succ=[None]*n
    for v in range(n):
        for i in range(d):
            if m[var(v,i)-1]>0: succ[v]=v^(1<<i)
    seen=[False]*n; comps=[]
    for v in range(n):
        if not seen[v]:
            c=[]; u=v
            while not seen[u]: seen[u]=True; c.append(u); u=succ[u]
            comps.append(c)
    if len(comps)==1: break
    comps.sort(key=len)
    for c in comps[:-1]:
        cs=set(c)
        S.add_clause([var(v,i) for v in c for i in range(d) if (v^(1<<i)) not in cs])
    if it%50==0: print('round',it,'components',len(comps),'%.1fs'%(time.time()-t0),flush=True)
C=comps[0]
cycles=[[rho(v,k) for v in C] for k in range(d)]
print('FOUND d=%d rounds=%d %.1fs'%(d,it,time.time()-t0))
print('C =',C)
json.dump(cycles,open(OUT,"w"))
