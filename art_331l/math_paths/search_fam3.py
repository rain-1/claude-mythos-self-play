import networkx as nx, itertools, sys
from search_fam_util import fGs
T=int(sys.argv[1]); A=list(range(4,13))
res={}
V=list(range(2+T))  # 0=u,1=v
pairs=list(itertools.combinations(V,2))
batch=[];meta=[]
def flush():
    global batch,meta
    if not batch: return
    f=fGs(batch)
    L=len(A)
    for j,(H) in enumerate(meta):
        ff=f[j*L:(j+1)*L]; d=[ff[i+1]-ff[i] for i in range(L-1)]
        if len(set(d[-4:]))==1 and d[-1]>0:
            s=d[-1]; key=(s,ff[-1]%s)
            sc=len(H)
            if key not in res or sc<res[key][0]: res[key]=(sc,H,ff)
    batch=[];meta=[]
for mask in range(1<<len(pairs)):
    E=[p for i,p in enumerate(pairs) if mask>>i&1]
    H=nx.Graph(); H.add_nodes_from(V); H.add_edges_from(E)
    # require each gadget vertex connected to {u,v} ; allow disconnected handled by middles
    G0=H.copy(); G0.add_edges_from([(0,'m'),(1,'m')])
    if not nx.is_connected(G0): continue
    for a in A:
        G=H.copy()
        for i in range(a): G.add_edge(0,('m',i)); G.add_edge(1,('m',i))
        batch.append(G)
    meta.append(E)
    if len(meta)>=2000: flush()
flush()
for k in sorted(res): print(k,res[k])
