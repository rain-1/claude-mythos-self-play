import numpy as np, colorsys
from PIL import Image
from icing import *
W=1000; P=Plate(W,W,bg=(226,234,250))
# octahedron-like: outer triangle, inner triangle
c=np.array([500,520]); R=380
outer=[c+R*np.array([np.cos(a),np.sin(a)]) for a in np.radians([-90,30,150])]
inner=[c+130*np.array([np.cos(a),np.sin(a)]) for a in np.radians([90,210,330])]
V=outer+inner
cookie=[c+(R+70)*np.array([np.cos(a),np.sin(a)])*(1+0.0*a) for a in np.linspace(0,2*np.pi,200)]
P.cookie([cookie]); P.flood([cookie],(253,248,244),inset=26,thick=9)
E=[(0,1),(1,2),(2,0),(3,4),(4,5),(5,3),(0,4),(0,5),(1,5),(1,3),(2,3),(2,4)]
F=[(0,4,5),(1,5,3),(2,3,4),(0,1,5),(1,2,3),(2,0,4),(3,4,5)]
for i,f in enumerate(F):
    cen=np.mean([V[j] for j in f],0); a=np.arctan2(*(cen-c)[::-1])
    r,g,b=colorsys.hls_to_rgb((a/2/np.pi)%1,0.82,0.75)
    P.flood([[V[j] for j in f]],(r*255,g*255,b*255),inset=7)
P.lines([(V[a],V[b]) for a,b in E],(253,250,246),radius=6)
dots=[];
for a,b in E:
    L=np.linalg.norm(V[a]-V[b]); n=int(L//40)
    for t in np.linspace(0,1,n+1)[1:-1]: dots.append(V[a]+(V[b]-V[a])*t)
P.dots(dots,[(255,250,252)]*len(dots),radius=5.5)
P.dots(V,[(250,160,180)]*6,radius=13)
Image.fromarray(P.render()).save('t1.png')
