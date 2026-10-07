import numpy as np, scipy.sparse as sp
from scipy.sparse.csgraph import dijkstra
def tree(N,seed=0):
    rng=np.random.default_rng(seed); idx=np.arange(N*N).reshape(N,N)
    a=np.concatenate([idx[:,:-1].ravel(),idx[:-1,:].ravel()]); b=np.concatenate([idx[:,1:].ravel(),idx[1:,:].ravel()])
    w=rng.exponential(1.0,len(a))
    G=sp.coo_matrix((np.concatenate([w,w]),(np.concatenate([a,b]),np.concatenate([b,a]))),shape=(N*N,N*N)).tocsr()
    src=idx[N//2,N//2]
    D,P=dijkstra(G,indices=src,return_predecessors=True)
    order=np.argsort(-D); size=np.ones(N*N)
    for v in order:
        p=P[v]
        if p>=0: size[p]+=size[v]
    return D.reshape(N,N),P,size,src
