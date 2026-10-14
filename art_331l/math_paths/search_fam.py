import networkx as nx, itertools, subprocess
def fGs(Gs):
    s=b''.join(nx.to_graph6_bytes(nx.convert_node_labels_to_integers(G),header=False) for G in Gs)
    o=subprocess.run(['./fpaths','each'],input=s,capture_output=True).stdout.decode().split('\n')
    return [int(l.split()[0]) for l in o if l]
res=[]
for t in range(0,4):
    V=['u','v']+['g%d'%i for i in range(t)]
    pairs=list(itertools.combinations(V,2))
    seen=set()
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
        if all(x==2 for x in d[2:]) and f[-1]%2==1:
            key=tuple(f)
            if key in seen: continue
            seen.add(key)
            res.append((t,H.number_of_edges(),sorted(H.edges()),f))
for r in sorted(res,key=lambda r:(r[0],r[1]))[:30]: print(r)
