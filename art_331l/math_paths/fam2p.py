import networkx as nx
from search_fam_util import fGs
def F(a,b,uw,vw):
    G=nx.Graph()
    for i in range(a): G.add_edge('u',('m',i)); G.add_edge('v',('m',i))
    for i in range(b): G.add_edge('u',('n',i)); G.add_edge('w',('n',i))
    if uw: G.add_edge('u','w')
    if vw: G.add_edge('v','w')
    return G
for uw in (0,1):
  for vw in (0,1):
    print('uw',uw,'vw',vw)
    for b in range(0,6):
        print(' b',b,fGs([F(a,b,uw,vw) for a in range(2,11)]))
