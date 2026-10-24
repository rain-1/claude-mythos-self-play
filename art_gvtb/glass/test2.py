import numpy as np, sys
from graph import *; from geo import geodesic
from PIL import Image, ImageDraw
V,F=geodesic(int(sys.argv[1])); n=len(V)
F=[tuple(int(x) for x in f) for f in F]
cent=[V[list(f)].mean(0) for f in F]
# outer faces: one 'corner' (touching a degree-5 vertex) and one central
deg=degrees(F)
o1=[f for f in F if any(deg[v]==5 for v in f)][0]
o2=[f for f in F if all(deg[v]==6 for v in f)] ; o2=o2[0] if o2 else F[7]
W=420; img=Image.new('RGB',(W*5,W),'white'); d=ImageDraw.Draw(img)
def drawP(P,k,outer):
    ok,ratio=check_planar(P,F,outer); print(k,ok,ratio)
    P=P-P.min(0); P=P/P.max()*(W-40)+20
    for f in F:
        if set(f)==set(outer): continue
        pts=[tuple(P[v]*[1,-1]+[k*W,W]) for v in f]
        d.polygon(pts,outline='black')
def stereo(outer):
    c=V[list(outer)].mean(0); c/=np.linalg.norm(c)
    # rotate c to north pole, project from north
    z=c; x=np.cross(z,[0.3,0.5,0.7]); x/=np.linalg.norm(x); y=np.cross(z,x)
    Q=V@np.stack([x,y,z],1)
    return Q[:,:2]/(1-Q[:,2:3]+1e-9)
drawP(tutte(F,n,o1),0,o1)
drawP(tutte(F,n,o2),1,o2)
P,r=koebe(F,n,o1,iters=1500); drawP(P,2,o1)
drawP(shift_drawing(F,n,o1),3,o1)
drawP(stereo(o1),4,o1)
img.save('/tmp/claude-0/test2.png')
