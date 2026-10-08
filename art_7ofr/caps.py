# Richest cap of radius n^{3/5} among lattice points on |v|=n (MO 515790). Centres: every point, every
# midpoint of close pairs, plus 200k random directions -> a lower bound for the sup.
import numpy as np, sys, json
from scipy.spatial import cKDTree
def E(n):
    out=[]
    for x in range(-n,n+1):
        y=np.arange(-n,n+1); r=n*n-x*x-y*y; m=r>=0
        z=np.sqrt(np.where(m,r,0)).round().astype(np.int64); ok=m&(z*z==r)
        for s in (1,-1): out.append(np.stack([np.full(ok.sum(),x),y[ok],s*z[ok]],1))
    return np.unique(np.concatenate(out),axis=0)
if __name__=="__main__":
    res=[]
    for n in [int(a) for a in sys.argv[1:]]:
        P=E(n); U=P/np.linalg.norm(P,axis=1,keepdims=True); T=cKDTree(U)
        eps=n**(-0.4); ch=2*np.sin(eps/2)
        rng=np.random.default_rng(0); R=rng.normal(size=(200000,3)); R/=np.linalg.norm(R,axis=1,keepdims=True)
        C=np.concatenate([U,R]); cnt=np.array([len(l) for l in T.query_ball_point(C,ch)])
        i=cnt.argmax(); exp=len(U)*(eps**2)/4
        res.append((n,len(U),exp,int(cnt.max()),C[i].tolist()))
        print(n,len(U),'expected %.2f'%exp,'max',cnt.max(),'ratio %.2f'%(cnt.max()/exp),'n^{2/5}=%.1f'%n**0.4,flush=True)
    json.dump(res,open('caps_%s.json'%sys.argv[1],'w'))
