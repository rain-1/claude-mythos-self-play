"""First-passage percolation: geodesic tree + emergent limit shape (prototype)."""
import numpy as np, time, sys
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra
from PIL import Image

def build_and_solve(W, seed=1):
    rng=np.random.default_rng(seed)
    idx=np.arange(W*W).reshape(W,W)
    # iid Exponential(1) edge weights
    sh=idx[:, :-1].ravel(); dh=idx[:, 1:].ravel(); wh=rng.exponential(1.0, sh.size)
    sv=idx[:-1,:].ravel(); dv=idx[1:,:].ravel(); wv=rng.exponential(1.0, sv.size)
    src=np.concatenate([sh,sv,dh,dv]); dst=np.concatenate([dh,dv,sh,sv])
    w=np.concatenate([wh,wv,wh,wv])
    M=csr_matrix((w,(src,dst)), shape=(W*W,W*W))
    c=(W//2)*W + W//2
    t=time.time()
    dist,pred=dijkstra(M, directed=True, indices=c, return_predecessors=True)
    print(f"dijkstra {time.time()-t:.1f}s", flush=True)
    return dist.reshape(W,W), pred, c

def subtree_flow(pred, dist, W):
    order=np.argsort(dist.ravel())[::-1]      # far -> near
    flow=np.ones(W*W, dtype=np.float64)
    p=pred
    for i in order:
        pi=p[i]
        if pi>=0: flow[pi]+=flow[i]
    return flow.reshape(W,W)

if __name__=="__main__":
    W=int(sys.argv[1]) if len(sys.argv)>1 else 700
    dist,pred,c=build_and_solve(W)
    t=time.time(); flow=subtree_flow(pred,dist,W); print(f"flow {time.time()-t:.1f}s",flush=True)
    # quick look: log flow hist-eq
    f=np.log1p(flow)
    r=f.ravel(); order=np.argsort(np.argsort(r)); eq=(order/order.max()).reshape(W,W)
    img=(255*eq**1.0).astype(np.uint8)
    # overlay rings (contours of dist)
    ncol=12; lv=dist/np.nanmax(dist[np.isfinite(dist)])
    ring=((lv*ncol)%1.0)
    ringmask=(np.abs(ring-0.0)<0.02)
    out=np.stack([img, img, np.clip(img.astype(int)+ (ringmask*120),0,255).astype(np.uint8)],-1)
    Image.fromarray(out).save("art_eygo/fpp_proto.png")
    print("saved. dist max", np.nanmax(dist[np.isfinite(dist)]), "flow max", flow.max())
