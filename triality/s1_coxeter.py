"""Still 1 — the 24-cell in the Coxeter plane (the triality rose).
The 24-cell's 24 vertices (three 16-cells = 8_v/8_s/8_c) and 96 edges, projected
onto the D4 Coxeter plane. Edges weave the three colours into a symmetric rose;
the threefold colour structure is triality seen flattened."""
import numpy as np, sys
sys.path.insert(0,'triality')
import t4d
from tdraw import Canvas, CLASS_COL

def render(S=2048, ss=2):
    W=S*ss
    V,cls=t4d.cell24_weights(); E,_=t4d.edges_of(V)
    u,v=t4d.coxeter_plane_basis_f4()
    P=np.stack([V@u, V@v],1)
    rad=np.linalg.norm(P,axis=1); rmax=rad.max()
    cx=cy=W/2; scale=W*0.42/(rmax+1e-9)
    scr=np.stack([cx+P[:,0]*scale, cy-P[:,1]*scale],1)
    cv=Canvas(W,bg=(0.012,0.012,0.026))
    cols=[CLASS_COL[c] for c in cls]
    for (i,j) in E:
        cv.line(scr[i],scr[j],cols[i],cols[j],width=1.5*ss,bright=0.30)
    # vertices, slightly bigger if multiple roots coincide (depth-free here)
    for i in range(len(V)):
        cv.splat(scr[i],cols[i],radius=W*0.010,bright=1.5)
        cv.splat(scr[i],(1,1,1),radius=W*0.0038,bright=1.3)
    cv.splat((cx,cy),(0.7,0.78,1.0),radius=W*0.02,bright=0.45)
    return cv.finish(S,bloom=(W*0.0007+0.6,W*0.006),gloss=(0.55,0.32),expo=1.25)

if __name__=="__main__":
    import sys as s
    if len(s.argv)>1 and s.argv[1]=='preview':
        render(700,2).save('triality/proto/_coxeter.png')
    else:
        render(4096,2).save('triality/01_d4_coxeter_rose.png')
    print('done')
