import numpy as np, time
from PIL import Image
from scipy import ndimage as ndi
import quill as Q
N=900; m=110; S=N-2*m
H=np.zeros((N,N),np.float32)
rng=np.random.default_rng(1)
A=np.ones((N,N,3),np.float32)*np.array([0.985,0.98,0.975])
A*= (1-0.02*ndi.gaussian_filter(rng.random((N,N)),1.0)[...,None])
tri=np.array([[0,0],[1,0],[0.5,np.sqrt(3)/2]]); tri[:,1]+=0.06
P=m+tri*S; P[:,1]=N-P[:,1]
sq=np.array([[m,m],[N-m,m],[N-m,N-m],[m,N-m]],float)
wall=5.0; hgt=24.0
d_sq=Q.seg_dist(Q.poly_segs(sq),(N,N)); d_tri=Q.seg_dist(Q.poly_segs(P),(N,N))
from matplotlib.path import Path
yy,xx=np.mgrid[0:N,0:N]; pts=np.c_[xx.ravel()+.5,yy.ravel()+.5]
inside_sq=Path(sq).contains_points(pts).reshape(N,N)
inside_tri=Path(P).contains_points(pts).reshape(N,N)
free=(d_sq>wall)&(d_tri>wall)
regions,nr=ndi.label(free&inside_sq)
cols=[(1.0,0.62,0.62),(0.62,0.82,1.0),(0.70,0.92,0.70),(0.80,0.70,1.0),(1.0,0.86,0.52),(1.0,0.70,0.86)]
for r in range(1,nr+1):
    msk=regions==r
    c=cols[0] if inside_tri[msk].mean()>.5 else cols[(r%5)+1]
    Q.coil(H,A,msk,pitch=24,width=2.4,height=hgt*0.8,col=c,smooth=9)
Q.put(H,A,Q.wall_profile(d_tri,3.0),hgt,(0.97,0.55,0.55))
Q.put(H,A,Q.wall_profile(d_sq,3.4),hgt*1.05,(0.96,0.93,0.86))
t=time.time(); img=Q.render(H,A,spp=4,light=(-0.65,0.30,0.70),amb=(0.62,0.62,0.70),sun=(0.75,0.72,0.68)); print(time.time()-t)
Image.fromarray(Q.tonemap(img)).save('proto/t1.png')
