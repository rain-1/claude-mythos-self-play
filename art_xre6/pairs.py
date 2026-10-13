import sys, numpy as np; sys.path.insert(0,'.')
from scene import *; from neck import EX, minper
import scene
CAND={'strawberry':(0.98,0.62,0.70),'butter':(1.0,0.86,0.52),'mint':(0.62,0.90,0.76),'sky':(0.60,0.80,0.98)}
KIND=sys.argv[2] if len(sys.argv)>2 else 'glass'
ab=0.6
for k in scene.GLASS: scene.GLASS[k]=tuple(ab*v for v in scene.GLASS[k])
S=Scene(); cmap={'A':'strawberry','B':'butter','C':'mint','D':'sky'}
N=EX[4]; r=1.0; gap=1.08
ring(S, N, cmap if KIND=='glass' else {k:CAND[v] for k,v in cmap.items()}, 0, 0, r, gap=gap, rot=np.pi/2, kind=KIND)
def spaced(w, cx, cy, sg=1.3*r):
    p=minper(w); n=len(w); m=n//p
    L=n*2*r*gap+m*sg; Rr=L/(2*np.pi); pts=[]
    for i,ch in enumerate(w):
        s_=(i+0.5)*2*r*gap+(i//p+0.5)*sg; a=np.pi/2-2*np.pi*s_/L
        x,y=cx+Rr*np.cos(a),cy+Rr*np.sin(a); pts.append((x,y)); S.bead(x,y,r,KIND,cmap[ch] if KIND=='glass' else CAND[cmap[ch]])
    for j in range(m):
        a=np.pi/2-2*np.pi*j*(p*2*r*gap+sg)/L
        S.bead(cx+Rr*np.cos(a),cy+Rr*np.sin(a),0.62*r,'candy','coral',z=r)
    S.thread([(cx+Rr*np.cos(np.pi/2-2*np.pi*t/(8*n)),cy+Rr*np.sin(np.pi/2-2*np.pi*t/(8*n))) for t in range(8*n)], r, 0.07*r, col=(0.96,0.86,0.93))
D=float(sys.argv[1]) if len(sys.argv)>1 else 15.5
order=['AB','AC','BC','CD','BD','AD']
for t,pr in enumerate(order):
    a=np.pi/2+2*np.pi*t/6
    w=''.join(c for c in N if c in pr)
    spaced(w, D*np.cos(a), D*np.sin(a))
S.save('pairs.bin')
