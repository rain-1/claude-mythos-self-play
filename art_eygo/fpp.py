"""FPP compute + cache: dist field, subtree flow, geodesic wandering."""
import numpy as np, time, sys
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra

def solve(W, seed):
    rng=np.random.default_rng(seed)
    idx=np.arange(W*W).reshape(W,W)
    sh=idx[:, :-1].ravel(); dh=idx[:, 1:].ravel(); wh=rng.exponential(1.0, sh.size)
    sv=idx[:-1,:].ravel(); dv=idx[1:,:].ravel(); wv=rng.exponential(1.0, sv.size)
    src=np.concatenate([sh,sv,dh,dv]); dst=np.concatenate([dh,dv,sh,sv])
    w=np.concatenate([wh,wv,wh,wv]).astype(np.float32)
    M=csr_matrix((w,(src,dst)), shape=(W*W,W*W))
    c=(W//2)*W + W//2
    t=time.time(); dist,pred=dijkstra(M, directed=True, indices=c, return_predecessors=True)
    print(f"dijkstra {time.time()-t:.1f}s", flush=True)
    return dist.reshape(W,W).astype(np.float32), pred.astype(np.int32), c

def subtree_flow(pred, dist, W):
    order=np.argsort(dist.ravel())[::-1]
    flow=np.ones(W*W, dtype=np.float64)
    for i in order:
        pi=pred[i]
        if pi>=0: flow[pi]+=flow[i]
    return flow.reshape(W,W)

if __name__=="__main__":
    W=int(sys.argv[1]); seed=int(sys.argv[2]) if len(sys.argv)>2 else 3
    tag=sys.argv[3] if len(sys.argv)>3 else f"fpp{W}"
    dist,pred,c=solve(W,seed)
    t=time.time(); flow=subtree_flow(pred,dist,W); print(f"flow {time.time()-t:.1f}s",flush=True)
    np.save(f"art_eygo/{tag}_dist.npy", dist)
    np.save(f"art_eygo/{tag}_flow.npy", flow.astype(np.float32))
    print(f"saved {tag}; W={W} distmax={np.nanmax(dist[np.isfinite(dist)]):.1f} flowmax={flow.max():.0f}")
