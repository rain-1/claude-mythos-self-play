"""Still 5 — G2, the fixed point of triality.
Triality is an order-3 automorphism of so(8). The subalgebra it leaves fixed is
G2 -- the smallest of the exceptional Lie algebras (dimension 14). Its root
system is 12 roots: 6 short (inner hexagon) + 6 long (outer hexagram), the
densest, most beautiful rank-2 root system. What survives the threefold
symmetry of so(8) is exactly this exceptional jewel."""
import numpy as np, sys, math
sys.path.insert(0,'triality')
from tdraw import Canvas

WARM=np.array([255,200,90])/255    # short roots
COOL=np.array([90,200,255])/255    # long roots
ROSE=np.array([255,110,180])/255

def render(S=2048, ss=2):
    W=S*ss; cx=cy=W/2
    short=[(math.cos(math.radians(60*k)), math.sin(math.radians(60*k))) for k in range(6)]
    long =[(math.sqrt(3)*math.cos(math.radians(30+60*k)), math.sqrt(3)*math.sin(math.radians(30+60*k))) for k in range(6)]
    short=np.array(short); long=np.array(long)
    scale=W*0.255
    s_scr=np.stack([cx+short[:,0]*scale, cy-short[:,1]*scale],1)
    l_scr=np.stack([cx+long[:,0]*scale, cy-long[:,1]*scale],1)
    cv=Canvas(W,bg=(0.012,0.012,0.025))
    # root vectors from origin
    for p in s_scr: cv.line((cx,cy),p,WARM*0.7,WARM,width=1.4*ss,bright=0.22)
    for p in l_scr: cv.line((cx,cy),p,COOL*0.7,COOL,width=1.4*ss,bright=0.22)
    # inner hexagon (short roots)
    for k in range(6):
        cv.line(s_scr[k],s_scr[(k+1)%6],WARM,WARM,width=1.8*ss,bright=0.40)
    # outer hexagram (long roots = two triangles -> Star of David)
    for k in range(6):
        cv.line(l_scr[k],l_scr[(k+2)%6],COOL,COOL,width=1.8*ss,bright=0.40)
    # points
    for p in s_scr:
        cv.splat(p,WARM,radius=W*0.011,bright=1.6); cv.splat(p,(1,1,1),radius=W*0.004,bright=1.3)
    for p in l_scr:
        cv.splat(p,COOL,radius=W*0.011,bright=1.6); cv.splat(p,(1,1,1),radius=W*0.004,bright=1.3)
    cv.splat((cx,cy),ROSE,radius=W*0.02,bright=0.7)   # the Cartan / origin
    return cv.finish(S,bloom=(W*0.0007+0.6,W*0.006),gloss=(0.5,0.3),expo=1.22)

if __name__=="__main__":
    if len(sys.argv)>1 and sys.argv[1]=='preview':
        render(700,2).save('triality/proto/_g2.png')
    else:
        render(2048,2).save('triality/05_g2_fixed_by_triality.png')
    print('done')
