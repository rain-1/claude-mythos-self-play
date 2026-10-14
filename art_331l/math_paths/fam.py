import networkx as nx, subprocess, sys
def fG(G):
    G=nx.convert_node_labels_to_integers(G)
    s=nx.to_graph6_bytes(G,header=False)
    o=subprocess.run(['./fpaths','each'],input=s,capture_output=True).stdout.split()
    return int(o[0]),int(o[2]),int(o[3])
def K2a(a,uv=False,mm=0):
    G=nx.Graph()
    for i in range(a): G.add_edge('u',i); G.add_edge('v',i)
    if uv: G.add_edge('u','v')
    for j in range(mm): G.add_edge(2*j,2*j+1)
    return G
fams={
 'K2a':lambda a:K2a(a),
 'K2a+uv':lambda a:K2a(a,True),
 'K2a+m1m2':lambda a:K2a(a,False,1),
 'K2a+uv+m1m2':lambda a:K2a(a,True,1),
 'K2a+pend-u-v-w':lambda a:nx.compose(K2a(a),nx.Graph([('u','w'),('w','v')])) ,
}
for name,F in fams.items():
    print(name,[fG(F(a))[0] for a in range(2,14)])
