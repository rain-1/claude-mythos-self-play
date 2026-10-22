import sys, itertools
from math import gcd
def int_kernel(M, n):
    # M: list of rows (ints), n columns. Return integer basis of {v in Z^n: M v = 0} via column HNF.
    m=len(M)
    A=[row[:] for row in M]
    U=[[1 if i==j else 0 for j in range(n)] for i in range(n)]  # columns ops tracked: U columns
    def colop_swap(i,j):
        for r in A: r[i],r[j]=r[j],r[i]
        for r in U: r[i],r[j]=r[j],r[i]
    def colop_add(i,j,c): # col i += c*col j
        for r in A: r[i]+=c*r[j]
        for r in U: r[i]+=c*r[j]
    piv=0
    for r in range(m):
        if piv>=n: break
        while True:
            nz=[c for c in range(piv,n) if A[r][c]!=0]
            if not nz: break
            c0=min(nz,key=lambda c:abs(A[r][c]))
            colop_swap(piv,c0)
            done=True
            for c in range(piv+1,n):
                if A[r][c]:
                    q=A[r][c]//A[r][piv]
                    colop_add(c,piv,-q)
                    if A[r][c]: done=False
            if done: break
        if any(A[r][c] for c in range(piv,n)) and A[r][piv]!=0: piv+=1
    return [[U[i][c] for i in range(n)] for c in range(piv,n)]

def lll_small(basis):
    return basis
zeros=[list(map(int,l.split())) for l in open(sys.argv[1])]
R=int(sys.argv[2]) if len(sys.argv)>2 else 3
best={}
for z in zeros:
    A=z[0::2]; C=z[1::2]
    M=[[a*a for a in A],[a*c for a,c in zip(A,C)],[c*c for c in C]]
    ker=int_kernel(M,6)
    k=len(ker)
    pq=None
    for co in itertools.product(range(-R,R+1),repeat=k):
        if not any(co): continue
        B=[sum(co[j]*ker[j][i] for j in range(k)) for i in range(6)]
        QA=sum(A[i]*B[i]**2 for i in range(6)); QC=sum(C[i]*B[i]**2 for i in range(6))
        if QA==0 and QC==0: continue
        if pq is None:
            g=gcd(QA,QC); p,q=QA//g,QC//g
            pq=(p,q)
            Ap=[q*A[i]-p*C[i] for i in range(6)]
            if 0 in Ap: break
            g2=0
            for a in Ap: g2=gcd(g2,a)
            Ap=[a//g2 for a in Ap]
            Cp=C if q!=0 else A
        H=max(max(abs(v) for v in Ap),max(abs(v) for v in Cp),max(abs(v) for v in B))
        beta=sum(Cp[i]*B[i]**2 for i in range(6)); alpha=sum(b**3 for b in B)
        assert sum(Ap[i]*B[i]**2 for i in range(6))==0
        if beta==0: continue
        mod=3*abs(beta); res=alpha%mod
        key=(mod,res)
        if key not in best or best[key][0]>H:
            best[key]=(H,[(Ap[i],B[i],Cp[i]) for i in range(6)],alpha,beta)
mods={}
for (mod,res),v in best.items(): mods.setdefault(mod,[]).append(res)
for mod in sorted(mods)[:15]:
    print(mod, sorted(mods[mod]))
import json
json.dump({f"{k[0]}:{k[1]}":v for k,v in best.items()}, open(sys.argv[3] if len(sys.argv)>3 else 'families.json','w'))
