"""Replace the nearest-curve time map s by its HARMONIC extension: Dirichlet data s on the curve (pixels where
the winding number changes), Laplace elsewhere — i.e. the mean moment t at which a random walk from each point
first meets the curve. Coarse-to-fine Jacobi on a pyramid, solved at --R then upsampled to the field grid."""
import numpy as np, sys, argparse
from scipy.ndimage import zoom
ap=argparse.ArgumentParser(); ap.add_argument('field'); ap.add_argument('out'); ap.add_argument('--R',type=int,default=2048)
a=ap.parse_args()
F=np.load(a.field); w=F['w']; s=F['s'].astype(np.float32); G=w.shape[0]
f=G//a.R
# boundary at solve resolution: blocks that contain a winding change
edge=np.zeros_like(w,bool)
edge[:-1]|=w[:-1]!=w[1:]; edge[:,:-1]|=w[:,:-1]!=w[:,1:]
E=edge[:a.R*f,:a.R*f].reshape(a.R,f,a.R,f)
bm=E.any((1,3))
sv=(s[:a.R*f,:a.R*f]*edge[:a.R*f,:a.R*f]).reshape(a.R,f,a.R,f).sum((1,3))/np.maximum(E.sum((1,3)),1)
def solve(bm,bv,init,its):
    u=init.copy(); u[bm]=bv[bm]
    for _ in range(its):
        p=np.pad(u,1,mode='edge')
        u=0.25*(p[:-2,1:-1]+p[2:,1:-1]+p[1:-1,:-2]+p[1:-1,2:]); u[bm]=bv[bm]
    return u
levels=[]; b,v=bm,sv.astype(np.float32)
while b.shape[0]>128:
    levels.append((b,v)); n=b.shape[0]//2
    B=b.reshape(n,2,n,2); V=(v*b).reshape(n,2,n,2).sum((1,3)); C=B.sum((1,3))
    b=B.any((1,3)); v=np.where(C>0,V/np.maximum(C,1),0).astype(np.float32)
levels.append((b,v))
u=np.full(b.shape,float(v[b].mean()),np.float32)
for i,(b,v) in enumerate(reversed(levels)):
    if u.shape!=b.shape: u=zoom(u,b.shape[0]/u.shape[0],order=1)
    its=4000 if i==0 else 600
    u=solve(b,v,u,its); print(b.shape,its,flush=True)
U=zoom(u,G/a.R,order=1).astype(np.float16)
np.savez_compressed(a.out,w=w,ext=F['ext'],s=U)
