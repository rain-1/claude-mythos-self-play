# The 3-cube: two schools can close, the third cannot. Both kinds of best failure, side by side.
import sys, numpy as np, math
from PIL import Image
import koi, scene
W=int(sys.argv[1]); ss=int(sys.argv[2]); out=sys.argv[3]
pos=np.zeros((8,2))
for v in range(8):
    r=1.50 if v&1 else 0.62
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
    sc=scene.build(pos,S,cols,seed=5+k,R=1.80,ppu=1/4.06,center=(0.5,0.5),flen=0.36,fw=0.036,fish_density=1.25,pad_r=0.14,
                   delta=0.062,rin=0.22,petals=30,ripples=4,trail_w=0.046)
    imgs.append(koi.finish(koi.render(sc,P,P,ss=ss,strip=256,quiet=True),seed=k))
H=int(W*0.635)
can=np.broadcast_to((koi.PAPER*255).astype(np.uint8),(H,W,3)).copy()
y0=int(W*0.004); g=(W-2*P)//3
can[y0:y0+P,g:g+P]=imgs[0]; can[y0:y0+P,W-g-P:W-g]=imgs[1]
im=Image.fromarray(can)
from PIL import ImageDraw
dr=ImageDraw.Draw(im)
def ctext(cx,y,text,fn,sz,col=(92,77,102)):
    f=scene.font(fn,int(sz*W)); w=dr.textlength(text,font=f); dr.text((cx-w/2,y*W),text,font=f,fill=col)
ctext(g+P/2,0.497,"the third school splits into two rings that never meet",'FreeSerifItalic',0.0125)
ctext(W-g-P/2,0.497,"or a school and its reverse leave four pairs pacing back and forth",'FreeSerifItalic',0.0125)
ctext(W/2,0.530,"With Eight Pads, the Third School Never Closes",'FreeSerifBold',0.0290)
ctext(W/2,0.570,"On the ordinary cube two schools can each visit all eight pads and come home. The lanes left over never join into one loop, and these are the only two ways to come this close.",'FreeSerifItalic',0.0135)
ctext(W/2,0.593,"why: every loop swims one direction four times and the other two twice, so three loops need three different favourites; then a row and a column of lanes must share one, and it is swum three times",'FreeSerifItalic',0.0105,(140,126,150))
im.save(out,optimize=True)
