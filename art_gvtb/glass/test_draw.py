import numpy as np, sys
from graph import *
from PIL import Image, ImageDraw
n=int(sys.argv[1]); seed=int(sys.argv[2])
F=random_triangulation(n,seed,flips=800)
print(sorted(degrees(F).values()))
outs=[F[0],F[5],F[11]]
W=400; img=Image.new('RGB',(W*4,W),'white'); d=ImageDraw.Draw(img)
def drawP(P,k,outer):
    ok,ratio=check_planar(P,F,outer); print(k,ok,ratio)
    P=P-P.min(0); P=P/P.max()*(W-40)+20
    for f in F:
        if set(f)==set(outer): continue
        pts=[tuple(P[v]*[1,-1]+[k*W,W]) for v in f]
        d.polygon(pts,outline='black')
drawP(tutte(F,n,outs[0]),0,outs[0])
drawP(tutte(F,n,outs[1]),1,outs[1])
P,r=koebe(F,n,outs[0],iters=3000); drawP(P,2,outs[0])
drawP(shift_drawing(F,n,outs[0]),3,outs[0])
img.save('/tmp/claude-0/test_draw.png')
