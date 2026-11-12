"""MO 516850: graphs with exactly half of their spanning subgraphs connected.
conn-DP, parity test, and a two-terminal gluing search."""
import numpy as np, networkx as nx, itertools, json, sys
from collections import defaultdict
def conn_table(n,adj):
    """adj: list of bitmasks. returns list c[S] = # connected spanning subgraphs of G[S]"""
    N=1<<n; e=[0]*N
    for S in range(1,N):
        low=(S&-S).bit_length()-1; R=S&(S-1)
        e[S]=e[R]+bin(adj[low]&R).count('1')
    c=[0]*N
    for S in range(1,N):
        low=S&-S; R=S^low; tot=1<<e[S]
        T=(R-1)&R if R else 0
        # proper subsets T' = low | sub, sub proper subset of R
        sub=R
        while True:
            sub=(sub-1)&R if sub else -1
            if sub<0: break
            Tm=low|sub
            tot-=c[Tm]*(1<<e[S^Tm])
            if sub==0: break
        c[S]=tot
    return c,e
def adjmasks(G,n):
    adj=[0]*n
    for u,v in G.edges(): adj[u]|=1<<v; adj[v]|=1<<u
    return adj
if __name__=='__main__':
    atlas=[G for G in nx.graph_atlas_g() if G.number_of_nodes()>=1]
    # 1) parity: C odd iff bipartite?  2) exact-half graphs up to 7 vertices
    par_bad=0; halves=[]; pieces={}
    for G in atlas:
        n=G.number_of_nodes(); m=G.number_of_edges(); adj=adjmasks(G,n)
        c,e=conn_table(n,adj); C=c[-1]; full=(1<<n)-1
        if nx.is_connected(G):
            if (C%2==1)!=nx.is_bipartite(G): par_bad+=1
            if 2*C==2**m: halves.append((n,m,sorted(G.edges())))
        if n<2: continue
        for s,t in itertools.combinations(range(n),2):
            b=0
            rest=full^(1<<s)^(1<<t)
            sub=rest
            while True:
                T=sub|(1<<s); b+=c[T]*c[full^T]
                if sub==0: break
                sub=(sub-1)&rest
            a=C
            if a==0 and b==0: continue
            he=G.has_edge(s,t)
            key=(a,b,m,n,he)
            if key not in pieces: pieces[key]=(sorted(G.edges()),s,t)
    print('parity counterexamples (connected, n<=7):',par_bad)
    print('exact-half graphs n<=7:',halves)
    keys=list(pieces); print('distinct pieces',len(keys))
    A=np.array([k[0] for k in keys],dtype=object); B=np.array([k[1] for k in keys],dtype=object)
    a=np.array([k[0] for k in keys],np.float64); b=np.array([k[1] for k in keys],np.float64)
    m=np.array([k[2] for k in keys]); nn=np.array([k[3] for k in keys]); he=np.array([k[4] for k in keys])
    sg=(a+b)/2.0**m; be=b/2.0**m
    found=defaultdict(list)
    for i in range(len(keys)):
        val=sg[i]*sg[i:]-be[i]*be[i:]
        for j in np.nonzero(np.abs(val-0.5)<1e-12)[0]+i:
            if he[i] and he[j]: continue
            ai,bi,mi,ni,_=keys[i]; aj,bj,mj,nj,_=keys[j]
            if (ai+bi)*(aj+bj)-bi*bj==2**(mi+mj-1):
                found[ni+nj-2].append((i,j))
    res={}
    for n in sorted(found):
        print('n =',n,': ',len(found[n]),'glued (piece-class pairs)')
        i,j=found[n][0]
        res[n]=dict(count=len(found[n]),example=[pieces[keys[i]],pieces[keys[j]]],keys=[keys[i],keys[j]])
    json.dump(dict(parity_bad=par_bad,halves=halves,glue={str(k):v for k,v in res.items()}),open(__file__.replace('half.py','half_results.json'),'w'),default=str)
