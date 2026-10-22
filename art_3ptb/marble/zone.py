import numpy as np, sys
sys.path.insert(0,'../wc')
from PIL import Image, ImageDraw, ImageFont
from marble import Bath
from wc import hexrgb
from design import shade
INK=['#fbf7f0','#f4aabd','#fbcfa0','#f8e39a','#b7e5c8','#acd2f2','#cdbdf0','#f29a8c','#ffffff']
N=int(sys.argv[1]); ss=2; v=int(sys.argv[2]) if len(sys.argv)>2 else 0
pal=np.array([hexrgb(c) for c in INK])
g=(np.arange(N*ss)+0.5)/(N*ss); xs,ys=np.meshgrid(g,g)
B=Bath()
r=0.072; M=12
seq=[1,2,3,4,5,6]
for i in range(M): B.drop(0.5,0.47,r,seq[i%6] if i%2==0 else 8) if False else B.drop(0.5,0.47,r,seq[i%6])
if v==1:
    B.comb((0.5,0.47),(0,1),0.06,0.006,0.16)
if v==2:
    B.line((0.5,0.47),(0,1),0.10,0.03)
ink,tt=B.render(xs,ys,0)
rgb=shade(ink,tt,pal,N,ss)
im=Image.fromarray((rgb*255+0.5).astype(np.uint8))
d=ImageDraw.Draw(im)
F='/usr/share/fonts/truetype/freefont/'
pen=(92,77,102)
fb=ImageFont.truetype(F+'FreeSerifBold.ttf',int(0.036*N)); fi=ImageFont.truetype(F+'FreeSerifItalic.ttf',int(0.018*N))
d.text((0.5*N,0.865*N),'Every Drop Adds a Right Angle',font=fb,fill=pen,anchor='mm')
d.text((0.5*N,0.905*N),'a drop of radius r pushes every point from distance ρ to √(ρ² + r²): twelve equal drops leave rings at r√1, r√2, … r√12,',font=fi,fill=pen,anchor='mm')
d.text((0.5*N,0.932*N),'equal in area, a Fresnel zone plate in ink — and the {6}, {4}, {3} chords are its first three rings',font=fi,fill=pen,anchor='mm')
im.save(sys.argv[3])
