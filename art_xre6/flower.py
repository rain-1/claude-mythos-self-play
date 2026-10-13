import sys, numpy as np; sys.path.insert(0,'.')
from scene import *; from neck import EX
import scene
for k in scene.GLASS: scene.GLASS[k]=tuple(0.6*v for v in scene.GLASS[k])
S=Scene(); cmap={'A':'strawberry','B':'butter','C':'mint','D':'sky','E':'lilac'}
N=EX[5]; n=len(N); r=1.0; gap=1.07
a=float(sys.argv[1]) if len(sys.argv)>1 else 0.3
th=np.linspace(0,2*np.pi,200001)
rr=1+a*np.cos(6*th); x=rr*np.cos(th+np.pi/2); y=rr*np.sin(th+np.pi/2)
ds=np.hypot(np.diff(x),np.diff(y)); s=np.concatenate([[0],np.cumsum(ds)]); L=s[-1]
scale=n*2*r*gap/L
pts=[]
for i,ch in enumerate(N):
    si=i*L/n; j=np.searchsorted(s,si)
    X,Y=x[j]*scale,y[j]*scale; pts.append((X,Y)); S.bead(X,Y,r,'glass',cmap[ch])
S.thread([(x[j]*scale,y[j]*scale) for j in range(0,len(x)-1,(len(x)-1)//(8*n))],r,0.07*r,col=(0.96,0.86,0.93))
# min distance check
P=np.array(pts); D=np.hypot(*(P[:,None]-P[None]).transpose(2,0,1)); np.fill_diagonal(D,99)
print('scale',scale,'min dist',D.min())
if len(sys.argv)>2: ring(S, EX[4], cmap, 0, 0, r, gap=1.08, rot=np.pi/2)
S.save('flower.bin')
