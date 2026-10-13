import sys, numpy as np; sys.path.insert(0,'.')
from scene import *; from neck import EX, minper
import scene
ab = float(sys.argv[1]) if len(sys.argv)>1 else 0.6
for k in scene.GLASS: scene.GLASS[k]=tuple(ab*v for v in scene.GLASS[k])
S=Scene(); cmap={'A':'strawberry','B':'butter','C':'mint','D':'sky'}
N=EX[4]; r=1.0; gap=1.08
R0=ring(S, N, cmap, 0, 0, r, gap=gap, rot=np.pi/2)
D=float(sys.argv[2]) if len(sys.argv)>2 else 15.5
corners=[(-1,1),(1,1),(-1,-1),(1,-1)]
for (sx,sy),c in zip(corners,'ABCD'):
    w=N.replace(c,''); p=minper(w); n=len(w)
    # rotate the word so a period starts at the top; spacers between periods
    cx,cy=sx*D,sy*D
    m=n//p; sg=1.3*r   # extra arc length per spacer
    L=n*2*r*gap+m*sg; Rr=L/(2*np.pi)
    pts=[]
    for i,ch in enumerate(w):
        s_=(i+0.5)*2*r*gap+(i//p+0.5)*sg
        a=np.pi/2-2*np.pi*s_/L
        x,y=cx+Rr*np.cos(a),cy+Rr*np.sin(a); pts.append((x,y)); S.bead(x,y,r,'glass',cmap[ch])
    for j in range(n//p):
        s_=j*(p*2*r*gap+sg)
        a=np.pi/2-2*np.pi*s_/L
        S.bead(cx+Rr*np.cos(a),cy+Rr*np.sin(a),0.62*r,'candy','coral',z=r)
    S.thread([(cx+Rr*np.cos(np.pi/2-2*np.pi*t/(8*n)),cy+Rr*np.sin(np.pi/2-2*np.pi*t/(8*n))) for t in range(8*n)], r, 0.07*r, col=(0.96,0.86,0.93))
    S.bead(cx,cy,r,'glass',cmap[c])   # the bead that was taken away sits in the middle
S.save('hero.bin')
print(R0)
