import itertools, subprocess, numpy as np
A=[list(map(int,l.split(':')[1].split())) for l in subprocess.check_output(['./tetra','list'],text=True).splitlines()]
EV=[(0,1),(0,2),(0,3),(1,2),(1,3),(2,3)]
eidx={}
for e,(i,j) in enumerate(EV): eidx[(i,j)]=eidx[(j,i)]=e
def canon(p):
    best=None
    for s in itertools.permutations(range(4)):
        t=[0]*6
        for e,(i,j) in enumerate(EV): t[eidx[(s[i],s[j])]]=p[e]
        if best is None or t<best: best=t
    return A.index(best)
def desc(k):
    a=A[k]  # ranks 0=smallest; opposite pairs (e0,e5),(e1,e4),(e2,e3)
    pairs=sorted([tuple(sorted((a[0],a[5]),reverse=True)),tuple(sorted((a[1],a[4]),reverse=True)),tuple(sorted((a[2],a[3]),reverse=True))],reverse=True)
    # classify where the top-3 sit: star (common vertex) / face / path
    return f"ranks{a} opp-pairs{pairs}"
masks=[];cnt=[]
for l in open('runs/masks.txt'):
    m,c=map(int,l.split()); masks.append(m); cnt.append(c)
masks=np.array(masks,dtype=np.int64); cnt=np.array(cnt); tot=cnt.sum()
print("successes",tot,"distinct masks",len(masks))
V=canon([5,4,3,2,1,0]); F=canon([5,4,2,3,1,0])
print("user rule big-opposite-small, big3 at vertex: k=",V,desc(V)," fails",cnt[(masks>>V)&1==0].sum())
print("user rule big-opposite-small, big3 a face:    k=",F,desc(F)," fails",cnt[(masks>>F)&1==0].sum())
VF=((masks>>V)&1)|((masks>>F)&1); print("either of the two:", cnt[VF==0].sum())
# leonbloy p1=[0,1,4,5,3,2] in (a,b,c,A,B,C) ascending; his opposite pairs: a-A,b-B,c-C; vertex edges a,b,c
lb=[[0,1,4,5,3,2],[0,1,4,3,5,2],[0,2,4,1,5,3],[0,1,4,5,2,3],[0,1,4,2,5,3],[0,1,3,5,4,2],[0,1,3,4,5,2]]
def from_abc(q): a,b,c,A_,B,C=q; return [a,b,c,C,B,A_]  # 01=a,02=b,03=c, 23 opp a, 13 opp b, 12 opp c
lbk=[canon(from_abc(q)) for q in lb]; print("leonbloy 7 ->",lbk)
cov=np.zeros(len(masks),bool)
for k in lbk: cov|=((masks>>k)&1)==1
print("leonbloy 7 uncovered:",cnt[~cov].sum())
# per-assignment marginal
marg=sorted(((cnt[((masks>>k)&1)==1].sum()/tot,k) for k in range(30)),reverse=True)
print("top marginals:",[(k,round(f,5),desc(k)) for f,k in marg[:8]])
# greedy order
rem=np.ones(len(masks),bool); order=[]
while rem.any():
    best=max(range(30),key=lambda k:cnt[rem&(((masks>>k)&1)==1)].sum())
    g=cnt[rem&(((masks>>best)&1)==1)].sum(); order.append((best,g/tot)); rem&=((masks>>best)&1)==0
print("greedy:",[(k,round(f,6),desc(k)) for k,f in order])
# minimum hitting set size
bits=np.array([[(m>>k)&1 for k in range(30)] for m in masks],bool)
for r in range(1,8):
    sols=[c for c in itertools.combinations(range(30),r) if bits[:,list(c)].any(1).all()]
    if sols: print("min cover size",r,"num solutions",len(sols),sols[:5]); break
# masks containing only one assignment: forced
single=[(int(np.log2(m)),c) for m,c in zip(masks,cnt) if m&(m-1)==0]
from collections import Counter
sc=Counter(); [sc.__setitem__(k,sc[k]+c) for k,c in single]; print("single-valid masks by k:",dict(sc))
