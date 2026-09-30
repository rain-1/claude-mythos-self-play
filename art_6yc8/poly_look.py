import numpy as np
from PIL import Image, ImageDraw
def poly(c):
    k=len(c); z=np.concatenate([[0],np.cumsum(np.array(c)*np.exp(2j*np.pi*np.arange(k)/k))]); return z
tiles=[]
for n in [60,720,5040]:
    L=[l.split() for l in open(f'data/best{n}.txt')]
    im=Image.new('RGB',(800,800),'white'); dr=ImageDraw.Draw(im,'RGBA')
    Z=[poly(list(map(float,l[1:]))) for l in L[:40]]
    allz=np.concatenate(Z); allz-=0
    cen=[z[:-1].mean() for z in Z]
    lo=min((z-cz).real.min() for z,cz in zip(Z,cen)); hi=max((z-cz).real.max() for z,cz in zip(Z,cen))
    lo2=min((z-cz).imag.min() for z,cz in zip(Z,cen)); hi2=max((z-cz).imag.max() for z,cz in zip(Z,cen))
    s=700/max(hi-lo,hi2-lo2)
    for i,(z,cz) in enumerate(zip(Z,cen)):
        zz=(z-cz)*s
        pts=[(400+q.real,400-q.imag) for q in zz]
        col=tuple(int(255*v) for v in [(0.5+0.5*np.cos(i)),0.6+0.3*np.sin(i*1.7),0.9])
        dr.polygon(pts,fill=col+(25,),outline=col+(160,))
    tiles.append(im)
W=Image.new('RGB',(2400,800),'white')
for i,t in enumerate(tiles): W.paste(t,(800*i,0))
W.save('proto/polys.png')
