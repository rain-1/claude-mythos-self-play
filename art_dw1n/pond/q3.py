# The 3-cube: two schools can close, the third cannot. Both kinds of best failure, side by side.
import sys, numpy as np, math
from PIL import Image
import koi, scene
W=int(sys.argv[1]); ss=int(sys.argv[2]); out=sys.argv[3]
pos=np.zeros((8,2))
for v in range(8):
    r=1.42 if v&1 else 0.60
    a=math.pi/4+ (math.pi/2)*[0,1,3,2][(v>>1)&3]
    pos[v]=(r*math.cos(a), r*math.sin(a))
c1=(0,1,3,2,6,7,5,4); c2=(0,2,3,7,6,4,5,1)
ringA=(0,4,6,2); ringB=(1,5,7,3)
left=[c1,c2,ringA,ringB]
rev=tuple(reversed(c1))
right=[c1,rev,(0,2),(1,5),(3,7),(4,6)]
# check: arcs partition
def arcs(c): return {(c[k],c[(k+1)%len(c)]) for k in range(len(c))}
ALL={(v,v^(1<<i)) for v in range(8) for i in range(3)}
for S in (left,right):
    U=set()
    for c in S: assert not (U&arcs(c)); U|=arcs(c)
    assert U==ALL, sorted(ALL-U)
P=int(W*0.5)
imgs=[]
for k,(S,cols) in enumerate(((left,[0,1,2,2]),(right,[0,1,2,2,2,2]))):
    sc=scene.build(pos,S,cols,seed=5+k,R=1.86,ppu=1/4.1,center=(0.5,0.5),flen=0.30,fw=0.030,fish_density=1.05,pad_r=0.125,
                   delta=0.055,rin=0.27,petals=30,ripples=4,trail_w=0.040)
    imgs.append(koi.finish(koi.render(sc,P,P,ss=ss,strip=256,quiet=True),seed=k))
H=int(W*0.62)
can=np.broadcast_to((koi.PAPER*255).astype(np.uint8),(H,W,3)).copy()
rng=np.random.default_rng(0)
can=np.clip(can+rng.normal(0,1.0,(H,W,1)),0,255).astype(np.uint8)
y0=int(W*0.012)
can[y0:y0+P,0:P]=imgs[0]; can[y0:y0+P,W-P:W]=imgs[1]
Image.fromarray(can).save(out)
