"""Uniform dimer coverings of the Temperleyan domain {0..2m}^2 minus the corner (0,0), via Temperley:
UST of the (m+1)^2 'even' grid rooted at the corner (Wilson) + its dual tree rooted at the outer face.
Each primal vertex is matched to the midpoint toward its parent, each face likewise."""
import numpy as np, numba
from collections import deque
@numba.njit
def wilson(n,seed):
    np.random.seed(seed)
    N=n*n; parent=-np.ones(N,np.int64); intree=np.zeros(N,np.bool_); intree[0]=True; nxt=-np.ones(N,np.int64)
    for s in range(N):
        u=s
        while not intree[u]:
            x=u%n; y=u//n
            while True:
                d=np.random.randint(4)
                if d==0 and x+1<n: v=u+1; break
                if d==1 and x>0: v=u-1; break
                if d==2 and y+1<n: v=u+n; break
                if d==3 and y>0: v=u-n; break
            nxt[u]=v; u=v
        u=s
        while not intree[u]:
            parent[u]=nxt[u]; intree[u]=True; u=nxt[u]
    return parent
def matching(m,seed):
    n=m+1; par=wilson(n,seed); S=2*m+1
    mate=-np.ones((S,S,2),int)
    tree=set()
    for u in range(1,n*n):
        p=par[u]; x,y=u%n,u//n; px,py=p%n,p//n
        X,Y=2*x,2*y; MX,MY=x+px,y+py   # midpoint in fine coords
        mate[Y,X]=(MY,MX); mate[MY,MX]=(Y,X); tree.add((min(u,p),max(u,p)))
    # dual: faces (i,j) i,j<m at fine (2i+1,2j+1); outer face = -1. dual edge crosses primal edge not in tree
    def fid(i,j): return -1 if (i<0 or j<0 or i>=m or j>=m) else j*m+i
    adj={}
    def add(a,b,mid): adj.setdefault(a,[]).append((b,mid)); adj.setdefault(b,[]).append((a,mid))
    for y in range(n):
        for x in range(n):
            u=y*n+x
            if x+1<n and (min(u,u+1),max(u,u+1)) not in tree:   # horizontal primal edge, crossed by vertical dual edge
                add(fid(x,y-1),fid(x,y),(2*y,2*x+1))
            if y+1<n and (min(u,u+n),max(u,u+n)) not in tree:
                add(fid(x-1,y),fid(x,y),(2*y+1,2*x))
    seen={-1}; q=deque([-1])
    while q:
        a=q.popleft()
        for b,mid in adj.get(a,[]):
            if b in seen: continue
            seen.add(b); q.append(b)
            j,i=divmod(b,m); FY,FX=2*j+1,2*i+1
            mate[FY,FX]=mid; mate[mid[0],mid[1]]=(FY,FX)
    return mate
def loops(m,s1,s2):
    A=matching(m,s1); B=matching(m,s2); S=2*m+1
    seen=np.zeros((S,S),bool); seen[0,0]=True; out=[]
    for y in range(S):
        for x in range(S):
            if seen[y,x]: continue
            if tuple(A[y,x])==tuple(B[y,x]): seen[y,x]=True; seen[tuple(A[y,x])]=True; continue
            cyc=[]; p=(y,x); use=0
            while True:
                seen[p]=True; cyc.append(p)
                q=tuple((A if use==0 else B)[p]); use^=1
                if q==(y,x): break
                p=q
            out.append(np.array(cyc))
    return out
if __name__=="__main__":
    import time; t=time.time(); L=loops(60,1,2); print(time.time()-t, len(L), sorted(len(l) for l in L)[-5:])
    A=matching(60,1); S=121; ok=all(tuple(A[tuple(A[y,x])])==(y,x) for y in range(S) for x in range(S) if (y,x)!=(0,0)); print('perfect matching',ok, (A[1:,:]>=0).all())
