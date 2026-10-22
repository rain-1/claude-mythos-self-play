import numpy as np, sys, time
from PIL import Image
from wc import *
from flower import paint_flower
W=H=int(sys.argv[1]) if len(sys.argv)>1 else 1024
out=sys.argv[2] if len(sys.argv)>2 else '../proto/sampler.png'
S=Sheet(H,W,seed=21); s=S.s
F='/usr/share/fonts/truetype/freefont/'
ink=pigment(hexrgb('#7a5f86'))
PAL={(10,1):('butter','peach'),(6,1):('sky','mint'),(5,1):('rose','lilac'),(4,1):('lilac','sky'),
     (10,3):('butter','peach'),(3,1):('mint','butter'),(5,2):('rose','lilac'),(2,1):('lilac','rose')}
def name(nk): return '{%d}'%nk[0] if nk[1]==1 else '{%d/%d}'%nk
rows=[
 (0.13,0.40,[(((10,1),(6,1)),(5,1),0.2,'Euclid'),(((6,1),(10,3)),(5,2),0.0,'its Galois twin'),(((10,1),(10,3)),(3,1),0.0,'')]),
 (0.42,0.68,[(((6,1),(6,1)),(4,1),0.0,''),(((6,1),(4,1)),(3,1),0.0,'')]),
 (0.75,0.90,[(((4,1),(4,1)),(2,1),0.0,''),(((6,1),(3,1)),(2,1),0.0,''),(((10,1),(5,2)),(2,1),0.0,''),(((5,1),(10,3)),(2,1),0.0,'')]),
]
for y0,y1,items in rows:
    n=len(items); m=0.06; cw=(1-2*m)/n
    for i,(legs,hyp,rot,tag) in enumerate(items):
        x0=m+i*cw; pad=0.012
        paint_flower(S,legs=legs,hyp=hyp,rot=rot,pal=[PAL[legs[0]],PAL[legs[1]],PAL[hyp]],fit=(x0+pad,y0+pad,x0+cw-pad,y1-pad),labels=False)
        cap='%s² + %s² = %s²'%(name(legs[0]),name(legs[1]),name(hyp))
        S.text(((x0+cw/2)*W,(y1+0.012)*H),cap,0.016*W if n<4 else 0.013*W,anchor='mt',weight=0.9)
        if tag: S.text(((x0+cw/2)*W,(y1+0.034)*H),tag,0.013*W,anchor='mt',weight=0.6)
S.text((0.06*W,0.035*H),'Every Right Angle Among the Chords',0.033*W,font=F+'FreeSerifBold.ttf',color=ink,dens=1.0)
S.text((0.06*W,0.078*H),'right triangles whose sides are edges of regular polygons {n/k} in equal circles',0.0155*W,weight=0.9)
S.text((0.06*W,0.715*H),'… and the Thales family, where the hypotenuse is a diameter (a digon {2}): infinitely many',0.0145*W,weight=0.8)
Image.fromarray(to8(S.finish())).save(out)
