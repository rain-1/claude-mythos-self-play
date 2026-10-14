"""Computer-assisted proof that every k >= 20 is f(G) for some graph G.

Family G_H(a): gadget graph H on vertex set containing hubs u,v, plus a "middle"
vertices m_1..m_a each adjacent to exactly u and v.

LEMMA (affinity). For a fixed pair type (both ends in H / one end a middle /
both ends middles) the number of simple paths is c0 + c1*(a-e), e = #middle
endpoints, for every a >= e. Proof: an interior middle vertex is entered from u
and left to v (or vice versa) since its only neighbours are u,v; u and v occur
at most once on a simple path, so a path has at most one interior middle.
Paths with no interior middle do not depend on a; for each of the a-e possible
interior middles the number of paths through it is the same (by the symmetry
permuting middles) and does not depend on a.

Hence f(G_H(a)) = max of finitely many affine functions of a, each determined
exactly by its values at two values of a. We compute every pair-type line from
a=4 and a=5 (and double-check at a=6,7,8), then verify that the claimed line
5a+r dominates all lines for every a >= A0 (dominance at A0 + slope <= 5).
"""
import itertools, json
def count_paths(adj, s, t):
    # number of simple s-t paths (DFS)
    n=0; stack=[(s,1<<s)]
    res=0
    def dfs(x,vis):
        nonlocal res
        for y in adj[x]:
            if vis>>y&1: continue
            if y==t: res+=1; continue
            dfs(y,vis|1<<y)
    dfs(s,1<<s); return res
def build(Hedges,a):
    names=sorted({x for e in Hedges for x in e}|{'u','v'})
    idx={x:i for i,x in enumerate(names)}
    N=len(names)+a
    adj=[set() for _ in range(N)]
    for x,y in Hedges: adj[idx[x]].add(idx[y]); adj[idx[y]].add(idx[x])
    for i in range(a):
        m=len(names)+i
        for h in ('u','v'): adj[m].add(idx[h]); adj[idx[h]].add(m)
    return names,idx,[sorted(s) for s in adj]
def type_counts(Hedges,a):
    names,idx,adj=build(Hedges,a); L=len(names)
    d={}
    for x,y in itertools.combinations(names,2): d[(x,y)]=count_paths(adj,idx[x],idx[y])
    for x in names: d[(x,'M')]=count_paths(adj,idx[x],L)
    d[('M','M')]=count_paths(adj,L,L+1)
    return d
def verify(Hedges,slope,r,A0=4):
    D={a:type_counts(Hedges,a) for a in (4,5,6,7,8)}
    lines={}
    for k in D[4]:
        c1=D[5][k]-D[4][k]; c0=D[4][k]-4*c1
        for a in (6,7,8): assert D[a][k]==c0+c1*a, ('not affine?',k)
        lines[k]=(c1,c0)
    for k,(c1,c0) in lines.items():
        assert c1<=slope and c1*A0+c0<=slope*A0+r, (k,c1,c0)
    best=[k for k,(c1,c0) in lines.items() if (c1,c0)==(slope,r)]
    assert best, 'claimed line not attained'
    return best,lines
GADGETS={
 0:[('u','x'),('u','y'),('u','z'),('x','y'),('x','z'),('y','z')],          # K4 hanging at u (block product 5*a)
 1:[('u','y'),('u','z'),('x','y'),('x','z'),('y','z'),('v','x')],
 2:[('u','z'),('u','w'),('v','y'),('x','y'),('x','z'),('x','w'),('y','z')],
 3:[('u','x'),('u','y'),('u','z'),('u','w'),('v','x'),('x','y'),('x','z'),('x','w')],
 4:[('u','x'),('u','z'),('u','w'),('v','x'),('v','y'),('x','y'),('x','z'),('x','w')],
}
if __name__=='__main__':
    out={}
    for r,H in GADGETS.items():
        best,lines=verify(H,5,r)
        # also sanity check against C brute force for a=4..12
        from search_fam_util import fGs
        import networkx as nx
        Gs=[]
        for a in range(4,13):
            G=nx.Graph(H)
            for i in range(a): G.add_edge('u',('m',i)); G.add_edge('v',('m',i))
            Gs.append(G)
        fs=fGs(Gs); assert fs==[5*a+r for a in range(4,13)], fs
        print(f'r={r}: f(G(a)) = 5a+{r} for all a>=4 PROVED; maximising pair type(s): {best}; brute force a=4..12 {fs}')
        out[r]={'gadget_edges':H,'formula':f'5a+{r}','valid_for':'a>=4','max_pairs':[list(b) for b in best],
                'lines':{f'{k[0]}-{k[1]}':{'slope':v[0],'intercept':v[1]} for k,v in lines.items()}}
    json.dump(out,open('families_slope5.json','w'),indent=1)
