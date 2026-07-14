"""Render 'Cauchy's Cage' — a convex, rigid crystal (still, solid, luminous)."""
import numpy as np, sys, os
from scipy.spatial import ConvexHull
from scipy.ndimage import gaussian_filter
from PIL import Image
from art_50e7 import r3d
from art_50e7.cauchy import spread_points, flex_analysis

S=int(sys.argv[1]) if len(sys.argv)>1 else 900
SS=2; W=S*SS
N=int(os.environ.get('NV',9))
P=spread_points(N)*8.0                      # scale to ~Steffen size
h=ConvexHull(P)
faces=[tuple(int(x) for x in f) for f in h.simplices]
eset=set()
for f in faces:
    for a,b in [(f[0],f[1]),(f[1],f[2]),(f[2],f[0])]:
        eset.add((min(a,b),max(a,b)))
edges=sorted(eset)
fa=flex_analysis(P/8.0,edges)
print("N=%d E=%d F=%d kernel=%d min_stiff=%.3f"%(N,len(edges),len(faces),fa['kernel'],fa['min_stiff']))

# orient faces outward
cen=P.mean(0)
ofaces=[]
for f in faces:
    a,b,c=[P[i] for i in f]
    nrm=np.cross(b-a,c-a)
    if np.dot(nrm, (a+b+c)/3-cen)<0: f=(f[0],f[2],f[1])
    ofaces.append(f)

AY=float(os.environ.get('AY',0.7)); AX=float(os.environ.get('AX',-0.42))
Rm=r3d.rot('y',AY)@r3d.rot('x',AX)
cam=r3d.Camera(W,Rm,cam_z=34.0,focal=2.0,center=tuple(cen))
cam.fit([P],margin=0.72)
xy,z=cam.project(P)

# lighting (strong key from the side for facet contrast + cool fill)
L=np.array([-0.72,0.42,0.55]); L=L/np.linalg.norm(L)
Lf=np.array([0.6,-0.2,0.5]); Lf=Lf/np.linalg.norm(Lf)   # cool fill
view=np.array([0,0,1.0])
H=(L+ (cam.R.T@view)); H=H/np.linalg.norm(H)
gold=np.array([1.0,0.68,0.28]); spec_c=np.array([1.0,0.94,0.74]); fill_c=np.array([0.30,0.38,0.55])

acc=np.zeros((W,W,3),np.float32)          # face layer (alpha-composited, painter far->near)
# depth per face (mean camera z, larger=farther)
fz=[np.mean([z[i] for i in f]) for f in ofaces]
order=np.argsort(fz)[::-1]                 # far first

def raster_tri(buf, tri_xy, col, alpha):
    x0=int(max(0,np.floor(tri_xy[:,0].min()))); x1=int(min(W,np.ceil(tri_xy[:,0].max())+1))
    y0=int(max(0,np.floor(tri_xy[:,1].min()))); y1=int(min(W,np.ceil(tri_xy[:,1].max())+1))
    if x1<=x0 or y1<=y0: return
    yy,xx=np.mgrid[y0:y1,x0:x1]
    ax,ay=tri_xy[0]; bx,by=tri_xy[1]; cx,cy=tri_xy[2]
    d=(by-cy)*(ax-cx)+(cx-bx)*(ay-cy)
    if abs(d)<1e-9: return
    l1=((by-cy)*(xx-cx)+(cx-bx)*(yy-cy))/d
    l2=((cy-ay)*(xx-cx)+(ax-cx)*(yy-cy))/d
    l3=1-l1-l2
    m=(l1>=-0.002)&(l2>=-0.002)&(l3>=-0.002)
    sub=buf[y0:y1,x0:x1,:]
    sub[m]=col[None,:]*alpha+sub[m]*(1-alpha)

for oi in order:
    f=ofaces[oi]; a,b,c=[P[i] for i in f]
    nrm=np.cross(b-a,c-a); nrm=nrm/ (np.linalg.norm(nrm)+1e-9)
    face=nrm@cam.R.T
    if face[2]<=0.02: continue                 # backface cull -> solid read
    diff=max(0.0,np.dot(nrm,L))
    fillv=max(0.0,np.dot(nrm,Lf))
    spec=max(0.0,np.dot(nrm,H))**22
    fres=(1-min(1,face[2]))**2.4               # brighten silhouette-grazing facets
    col=gold*(0.03+0.95*diff) + fill_c*(0.30*fillv) + spec_c*(0.9*spec) + gold*0.4*fres
    tri=np.array([xy[i] for i in f])
    raster_tri(acc, tri, col, alpha=0.96)

# glowing edges (additive) + vertex stars
eb=np.zeros((W,W,3),np.float32)
ecol=np.repeat(np.array([[1.0,0.86,0.55]]),len(edges),0)
r3d.draw_edges(eb, cam, P, edges, ecol, 0.32, samp=1.8, depthfade=0.5)
r3d.draw_verts(eb, cam, P, list(range(N)), np.array([[1.0,0.95,0.85]]*N),[2.2*SS]*N,1.0)

bs=SS*S/900.0
img=acc + eb
img=img + 0.5*gaussian_filter(eb,(3*bs,3*bs,0)) + 0.25*gaussian_filter(eb,(12*bs,12*bs,0))
img=1.0-np.exp(-1.35*img)
img=np.clip(img,0,1)**0.9
out=(np.clip(img,0,1)*255).astype(np.uint8)
im=Image.fromarray(out).resize((S,S),Image.LANCZOS)
name='proto_cauchy.png' if S<2000 else 'comp_cauchy.png'
im.save('/home/user/claude-mythos-self-play/art_50e7/'+name)
print("saved",name)
