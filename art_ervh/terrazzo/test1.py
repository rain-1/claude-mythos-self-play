import numpy as np, time
from PIL import Image
from scipy.spatial import cKDTree
import terrazzo as T
rng=np.random.default_rng(3)
gen={}
for line in open('../math_digits/t9.tsv'):
    f=line.split('\t'); gen[int(f[0])]=int(f[2])
W=1400; R=620; cx=cy=W/2; N=8000
c=R/np.sqrt(N)
ps=[p for p in sorted(gen) if p<=N]
n=np.array(ps,float)
r=c*np.sqrt(n); th=2*np.pi*np.sqrt(n)
P=np.c_[cx+r*np.cos(th), cy-r*np.sin(th)]
nn=cKDTree(P).query(P,2)[0][:,1]
G=np.array([gen[p] for p in ps])
pal={0:[(1.0,0.86,0.55),(1.0,0.78,0.60)],1:[(0.66,0.88,0.80),(0.66,0.82,0.96)],2:[(0.80,0.74,0.96),(0.92,0.74,0.90)],3:[(0.98,0.52,0.50)]}
polys=[];cols=[]
for i in range(len(ps)):
    rad=min(0.47*nn[i], 0.62*c)*(0.85+0.2*rng.random())
    if G[i]==3: rad=min(0.5*nn[i]*1.15,c*0.8)
    polys.append(T.chip_shape(rng,rad)+P[i])
    opts=pal[G[i]]; col=np.array(opts[rng.integers(len(opts))])*(0.96+0.06*rng.random(3))
    cols.append(col)
# aggregate grains in matrix
img=T.matrix((W,W),rng)
yy,xx=np.mgrid[0:W,0:W]; disc=((xx-cx)**2+(yy-cy)**2)<R**2*1.06
gp=rng.random((9000,2))*W
gp=gp[((gp[:,0]-cx)**2+(gp[:,1]-cy)**2)<(R*1.02)**2]
d,_=cKDTree(P).query(gp)
gp=gp[d>c*0.55]
gpolys=[T.chip_shape(rng,1.0+1.6*rng.random()**2)+q for q in gp]
gcols=[np.array([0.80,0.79,0.80])*(0.9+0.15*rng.random()) if rng.random()<.6 else np.array([0.97,0.97,0.96]) for _ in gp]
allp=T.pack_polys(polys+gpolys); allc=np.array(cols+gcols)
K=len(allp)
t=time.time()
T.draw_chips(img,allp,np.zeros(K+1),allc,np.r_[0.05+0.04*rng.random(len(polys)),0.02*np.ones(len(gpolys))],
             rng.random((K,3))*6.28,0.18,np.r_[0.05*np.ones(len(polys)),np.zeros(len(gpolys))],np.array([-0.6,-0.8]))
print(time.time()-t)
img+= T.window_reflection((W,W))[...,None]
page=np.ones_like(img)*np.array([0.985,0.982,0.978])
a=np.clip(R+0.5-np.sqrt((xx-cx)**2+(yy-cy)**2),0,1)[...,None]
out=page*(1-a)+img*a
Image.fromarray((np.clip(out,0,1)*255).astype(np.uint8)).save('proto/t1.png')
