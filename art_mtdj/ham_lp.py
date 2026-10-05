# MO 515726 via LP: G = T1 ∪ P (T1 = cycle 0..n-1, P = Ham path x..y edge-disjoint from T1), v adjacent to x,y only.
# Need weights w>0 with T1 the unique min Ham cycle of G and P the unique min x-y Ham path of G.
import itertools, sys, numpy as np
from scipy.optimize import linprog
def ham_cycles(n, adj):
    out=[]; path=[0]; used=[False]*n; used[0]=True
    def rec():
        u=path[-1]
        if len(path)==n:
            if 0 in adj[u] and path[1]<path[-1]: out.append(list(path))
            return
        for v in adj[u]:
            if not used[v]:
                used[v]=True; path.append(v); rec(); path.pop(); used[v]=False
    rec(); return out
def ham_paths(n, adj, x, y):
    out=[]; path=[x]; used=[False]*n; used[x]=True
    def rec():
        u=path[-1]
        if len(path)==n:
            if u==y: out.append(list(path))
            return
        for v in adj[u]:
            if not used[v] and (v!=y or len(path)==n-1):
                used[v]=True; path.append(v); rec(); path.pop(); used[v]=False
    rec(); return out
def E(seq, closed):
    m=len(seq); r=[frozenset((seq[i],seq[i+1])) for i in range(m-1)]
    if closed: r.append(frozenset((seq[-1],seq[0])))
    return r
if __name__ == '__main__':
  exec(compile('''n=int(sys.argv[1]); found=0; tried=0
T1=E(list(range(n)),True); T1s=set(T1)
comp=[frozenset(e) for e in itertools.combinations(range(n),2) if frozenset(e) not in T1s]
cadj={i:[j for j in range(n) if j!=i and frozenset((i,j)) not in T1s] for i in range(n)}
seen=set()
for x in range(n):
  for P in ham_paths(n,cadj,x,None) if False else []: pass
# enumerate Ham paths of the complement (all endpoints), canonical by reversal
def all_paths():
    for s in range(n):
        path=[s]; used=[False]*n; used[s]=True
        stack=[]
        def rec():
            if len(path)==n:
                if path[0]<path[-1]: yield list(path)
                return
            for v in cadj[path[-1]]:
                if not used[v]:
                    used[v]=True; path.append(v); yield from rec(); path.pop(); used[v]=False
        yield from rec()
for P in all_paths():
    tried+=1
    Pe=E(P,False); allE=T1+Pe; idx={e:i for i,e in enumerate(allE)}
    adj={i:[] for i in range(n)}
    for e in allE:
        a,b=tuple(e); adj[a].append(b); adj[b].append(a)
    x,y=P[0],P[-1]
    cyc=[c for c in ham_cycles(n,adj) if set(E(c,True))!=T1s]
    pth=[p for p in ham_paths(n,adj,x,y) if set(E(p,False))!=set(Pe) and set(E(p[::-1],False))!=set(Pe)]
    m=len(allE); A=[];b=[]
    def vec(es):
        v=np.zeros(m+1)
        for e in es: v[idx[e]]+=1
        return v
    # maximize t s.t. w(other) - w(T1) >= t ; w >= 1 ; w <= 100
    for c in cyc: r=vec(T1)-vec(E(c,True)); r[m]=1; A.append(r); b.append(0)
    for p in pth: r=vec(Pe)-vec(E(p,False)); r[m]=1; A.append(r); b.append(0)
    cobj=np.zeros(m+1); cobj[m]=-1
    bounds=[(1,100)]*m+[(None,1)]
    res=linprog(cobj,A_ub=np.array(A) if A else None,b_ub=b if A else None,bounds=bounds,method='highs')
    if res.status==0 and -res.fun>1e-7:
        found+=1
        if found<=3:
            w={tuple(sorted(e)):round(res.x[i],3) for i,e in enumerate(allE)}
            print('FOUND n',n,'P',P,'margin',-res.fun,'#cyc',len(cyc),'#paths',len(pth)); print(w)
print('n',n,'tried',tried,'found',found)
''','ham_lp','exec'))
