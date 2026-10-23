import numpy as np, json, colorsys, sys
from PIL import Image
from icing import *
N=int(sys.argv[1]); out=sys.argv[2]
d=[d for d in json.load(open('../math_harborth/drawings.json')) if 'C3' in d['name']][0]
X=np.array([(-159,-53),(159,-53),(0,106),(-71,-13),(-55,-29),(55,-29),(71,-13),(16,42),(-16,42),(39,-13),(0,26),(-39,-13)],float)
V=np.c_[X[:,0]/2, X[:,1]*np.sqrt(3)/2]           # unit = 1
s=N*0.00395; c=np.array([N*0.5,N*0.535])
img=lambda v: np.c_[c[0]+s*v[:,0], c[1]-s*v[:,1]] if v.ndim==2 else np.array([c[0]+s*v[0], c[1]-s*v[1]])
P=Plate(N,N,bg=(226,242,236),seed=3)
# triangular cookie with rounded corners, margin beyond the outer triangle
outer=V[:3]; cen=outer.mean(0)
pts=[]
for k in range(3):
    a=outer[k]; dirn=(a-cen)/np.linalg.norm(a-cen)
    corner=cen+(a-cen)*1.0+dirn*14
    ang0=np.arctan2(dirn[1],dirn[0])
    for t in np.linspace(-np.pi/3,np.pi/3,30): pts.append(corner+20*np.array([np.cos(ang0+t),np.sin(ang0+t)]))
pts=img(np.array(pts))
m=P.cookie([pts],thick=30*N/3072,edge=40*N/3072)
P.flood([pts],(254,250,247),inset=24*N/3072,thick=10*N/3072)
# piped bead border just inside the cookie's white flood, alternating sorbet colours
from scipy import ndimage as _nd
dist=_nd.distance_transform_edt(m)
ring=np.abs(dist-62*N/3072)<0.8
ys,xs=np.nonzero(ring); cc=np.array([N*0.5,N*0.5])
ang=np.arctan2(ys-cc[1],xs-cc[0]); o_=np.argsort(ang); pts_r=np.c_[xs[o_],ys[o_]].astype(float)
step=2.4*0.9*s; sel=[pts_r[0]]
for q in pts_r[1:]:
    if np.linalg.norm(q-sel[-1])>=step and np.linalg.norm(q-sel[0])>=step*0.9: sel.append(q)
border=np.array(sel); bcol=[(255,196,206),(255,236,170),(196,236,200),(206,198,250)]
border_cols=[bcol[i%4] for i in range(len(border))]

F=d['faces']
cents=np.array([V[f].mean(0) for f in F]); o=V[:3].mean(0)
R120=np.array([[-0.5,-np.sqrt(3)/2],[np.sqrt(3)/2,-0.5]])
orbit=-np.ones(len(F),int); no=0
for i in range(len(F)):
    if orbit[i]>=0: continue
    p=cents[i]
    for k in range(3):
        j=np.argmin(np.linalg.norm(cents-(o+np.linalg.matrix_power(R120,k)@(p-o)),axis=1)); orbit[j]=no
    no+=1
# sorbet box per orbit; the self-symmetric centre face gets coral
box=[(255,196,206),(255,214,186),(255,236,170),(196,236,200),(180,226,240),(206,198,250),(246,196,236),(250,160,150)]
order=np.argsort([np.linalg.norm(cents[orbit==q].mean(0)-o)+0*q for q in range(no)])
print('orbits',no,np.bincount(orbit))
for i,f in enumerate(F):
    q=orbit[i]; rank=int(np.where(order==q)[0][0])
    col=box[7] if (orbit==q).sum()==1 else box[rank % 7]
    P.flood([img(V[f])],col,inset=7*N/3072,thick=10*N/3072)
# beads: one per unit length, between the vertex pearls
beads=[];bc=[]
for i,j,L in d['edges']:
    a,b=V[i],V[j]
    for t in (np.arange(L)+0.5)/L:
        beads.append(a+(b-a)*t); bc.append((255,251,248))
rb=0.42*s
P.dots(img(np.array(beads)),bc,radius=rb)
P.dots(img(V),[(250,150,160)]*12,radius=1.7*s)
P.dots(border,border_cols,radius=1.0*s)
rng=np.random.default_rng(5)
loose=[];lc=[]
while len(loose)<70:
    p=rng.uniform(0,N,2)
    if m[int(p[1]),int(p[0])] or p[1]>N*0.86: continue
    from scipy import ndimage as _nd
    loose.append(p); lc.append([(255,251,248),(250,150,160),(255,214,186),(214,200,250)][rng.integers(4)])
P.dots(np.array(loose),lc,radius=1.1*s)
im=P.render(light=(-0.55,-0.6,0.58),soft=10)
Image.fromarray(im).save(out)
print(len(beads),'beads; px per unit',s)
