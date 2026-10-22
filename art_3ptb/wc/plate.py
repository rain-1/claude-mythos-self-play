import numpy as np, sys, time
from PIL import Image
from wc import *
from flower import paint_flower
from ico import paint_ico
W=H=int(sys.argv[1]) if len(sys.argv)>1 else 1024
out=sys.argv[2] if len(sys.argv)>2 else '../proto/plate.png'
seed=int(sys.argv[3]) if len(sys.argv)>3 else 11
t=time.time()
S=Sheet(H,W,seed=seed); s=S.s
u=0.104
X1=paint_flower(S,scale=u,center=(0.325,0.42),rot=0.10)
X2=paint_flower(S,legs=((6,1),(10,3)),hyp=(5,2),scale=u,center=(0.745,0.37),rot=-0.05,
                pal=[('sky','mint'),('butter','peach'),('rose','lilac')])
S.halo(0.70*W,0.81*H,0.13*W,pigment(hexrgb('#b9a3ea')),dens=0.04)
paint_ico(S,0.70*W,0.815*H,0.098*W,dens=0.13)
Kc=pigment(hexrgb('#f2735f'))
for (x,y,sp) in ():
    S.splatter(x*W,y*H,sp*W,Kc if x<0.5 else pigment(hexrgb('#ad92e6')),n=26,rmax=7,dens=0.35)
F='/usr/share/fonts/truetype/freefont/'
ink=pigment(hexrgb('#7a5f86'))
S.text((0.06*W,0.050*H),'Three Polygons, One Right Angle',0.036*W,font=F+'FreeSerifBold.ttf',color=ink,dens=1.0)
S.text((0.06*W,0.095*H),'a pentagon, a hexagon and a decagon in three equal circles — their edges close into a right triangle',0.0158*W,weight=0.9)
x0=0.06*W; y=0.735*H; L=0.0158*W
for line,sz,wt in (('Euclid XIII.10 (left):',1.0,1.0),
                   ('sin²(π/5) = sin²(π/6) + sin²(π/10)',1.0,0.9),('',0.5,0),
                   ('its Galois twin (right):',1.0,1.0),
                   ('sin²(2π/5) = sin²(π/6) + sin²(3π/10)',1.0,0.9),
                   ('hexagon, pentagram, decagram',0.85,0.7),('',0.5,0),
                   ('and the solid it builds: in the icosahedron',0.85,0.75),
                   ('the cap height is the decagon’s side, the ring',0.85,0.75),
                   ('radius the hexagon’s, the edge the pentagon’s',0.85,0.75)):
    if line: S.text((x0,y),line,L*sz,weight=wt)
    y+=L*sz*1.55
Image.fromarray(to8(S.finish())).save(out)
print(time.time()-t)
