import numpy as np, sys
from graph import *; from geo import geodesic
from PIL import Image, ImageDraw
V,F=geodesic(1); n=len(V); F=[tuple(int(x) for x in f) for f in F]
deg=degrees(F)
o1=[f for f in F if any(deg[v]==5 for v in f)][0]
o2=[f for f in F if all(deg[v]==6 for v in f)][0]
def stereo(outer):
    c=V[list(outer)].mean(0); c/=np.linalg.norm(c)
    z=c; x=np.cross(z,[0.3,0.5,0.7]); x/=np.linalg.norm(x); y=np.cross(z,x)
    Q=V@np.stack([x,y,z],1); return Q[:,:2]/(1-Q[:,2:3]+1e-9)
W=420; img=Image.new('RGB',(W*6,W),'white'); d=ImageDraw.Draw(img)
def drawP(P,k,outer):
    ok,ratio=check_planar(P,F,outer); print(k,ok,ratio)
    P=P-P.min(0); P=P/P.max()*(W-40)+20
    for f in F:
        if set(f)==set(outer): continue
        d.polygon([tuple(P[v]*[1,-1]+[k*W,W]) for v in f],outline='black')
k=0
for o in (o1,o2):
  S=stereo(o)
  for p in (1,2,3):
    wf=lambda u,v,S=S,p=p: np.linalg.norm(S[u]-S[v])**(p*0.6)
    drawP(tutte(F,n,o,wf),k,o); k+=1
img.save('/tmp/claude-0/test3.png')
