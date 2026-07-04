"""Sample a handful of FRESH random walks from just outside the frozen IDLA
disk, each absorbed on first contact with the real occupied set. Honest
illustration of 'free paths meeting a frozen shape' -- not fabricated texture."""
import numpy as np, sys

occ=np.load("art_eygo/idla_occ.npy")
M=occ.shape[0]
ys,xs=np.where(occ); cy,cx=ys.mean(),xs.mean()
R=np.sqrt(occ.sum()/np.pi)
K=int(sys.argv[1]) if len(sys.argv)>1 else 260
MAXLEN=int(sys.argv[2]) if len(sys.argv)>2 else 6000
rng=np.random.default_rng(11)

trails=[]
theta=rng.uniform(0,2*np.pi,K)
r0=R*1.07
x=(cx+r0*np.cos(theta)).astype(np.int32)
y=(cy+r0*np.sin(theta)).astype(np.int32)
DX=np.array([1,-1,0,0],np.int32); DY=np.array([0,0,1,-1],np.int32)
paths=[[] for _ in range(K)]
alive=np.ones(K,bool)
for t in range(MAXLEN):
    idx=np.where(alive)[0]
    if idx.size==0: break
    d=rng.integers(0,4,size=idx.size)
    nx=np.clip(x[idx]+DX[d],0,M-1); ny=np.clip(y[idx]+DY[d],0,M-1)
    x[idx]=nx; y[idx]=ny
    for j,i in enumerate(idx):
        paths[i].append((nx[j],ny[j]))
    hit=occ[nx,ny]
    if hit.any():
        alive[idx[hit]]=False
print(f"K={K} settled={ (~alive).sum() } steps<= {MAXLEN}")
np.save("art_eygo/idla_trail_meta.npy", np.array([cy,cx,R]))
import pickle
with open("art_eygo/idla_trails.pkl","wb") as f:
    pickle.dump(paths, f)
print("saved idla_trails.pkl")
