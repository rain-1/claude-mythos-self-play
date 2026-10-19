import sys, numpy as np, json, collections
from gn import run, parts
from classify import mapdeg, signature
kx,ky,j,tl=int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3]),float(sys.argv[4])
s,k=run(kx,ky,j,10**6,kx*100+ky*10+j,tl)
c=collections.Counter()
keep=[]
for A,B,C,D in s:
    dx,dy=mapdeg(A,B),mapdeg(C,D)
    c[(dx,dy)]+=1
    keep.append((dx,dy,A,B,C,D))
print("kx,ky,j=",kx,ky,j,"starts",k,"converged",len(s),"reduced map bidegrees:",dict(c),flush=True)
np.save('gn_%d%d%d.npy'%(kx,ky,j),np.array([np.r_[dx,dy,A,B,C,D] for dx,dy,A,B,C,D in keep],dtype=complex) if keep else np.zeros(0))
