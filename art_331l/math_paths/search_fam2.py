import networkx as nx, itertools, subprocess
from search_fam_util import fGs
res={}
for t in range(0,4):
    V=['u','v']+['g%d'%i for i in range(t)]
    pairs=list(itertools.combinations(V,2))
    for mask in range(1<<len(pairs)):
        H=nx.Graph(); H.add_nodes_from(V)
        H.add_edges_from(p for i,p in enumerate(pairs) if mask>>i&1)
        Gs=[]
        for a in range(3,10):
            G=H.copy()
            for i in range(a): G.add_edge('u',('m',i)); G.add_edge('v',('m',i))
            Gs.append(G)
        if not nx.is_connected(Gs[0]): continue
        f=fGs(Gs)
        d=[f[i+1]-f[i] for i in range(len(f)-1)]
        if len(set(d[2:]))==1:
            s=d[-1]; key=(s,f[-1]%s if s else f[-1])
            if key not in res or H.number_of_edges()+t*10<res[key][0]: res[key]=(H.number_of_edges()+t*10,t,sorted(H.edges()),f)
for k in sorted(res): print(k,res[k])
