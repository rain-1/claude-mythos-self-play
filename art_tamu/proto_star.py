import numpy as np, math, sys
from PIL import Image, ImageDraw
from traj import *
S=1400; im=Image.new('RGB',(S,S),(253,251,249)); d=ImageDraw.Draw(im,'RGBA')
cols={1:(110,200,170),2:(170,140,225),3:(250,150,120)}
R0,R1=0.05,0.95
top=float(sys.argv[1]) if len(sys.argv)>1 else 31
def pos(n):
    L=math.log2(n); r=(R0+(R1-R0)*L/(top+1))*S/2; th=2*math.pi*L
    return S/2+r*math.sin(th), S/2-r*math.cos(th)
starts_=starts(top=top,per=4,spread=0.01)
for n0 in starts_:
    o,lab=orbit(n0)
    pts=[pos(n) for n in o]
    d.line(pts,fill=cols[lab]+(110,),width=2)
    for p in pts: d.ellipse([p[0]-3,p[1]-3,p[0]+3,p[1]+3],fill=cols[lab]+(200,))
im.save('/tmp/claude-0/-home-user-claude-mythos-self-play/cb461e3e-8d57-5230-8c79-a9f7980093db/scratchpad/star.png')
