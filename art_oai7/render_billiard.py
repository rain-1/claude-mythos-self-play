import numpy as np, sys
from PIL import Image, ImageDraw
from billiard import triangle, orbit
from caption import caption, CORAL, INK
S=int(sys.argv[1]) if len(sys.argv)>1 else 1400; out=sys.argv[2] if len(sys.argv)>2 else 'proto/bil.png'
NB=int(sys.argv[3]) if len(sys.argv)>3 else 6000
WHEEL=np.array([[250,140,160],[255,175,140],[253,214,120],[190,226,140],[140,218,180],[140,200,240],[160,165,240],[200,160,240],[240,150,210]],float)
def wheel(h):
    h=(h%1)*len(WHEEL); i=int(h)%len(WHEEL); f=h-int(h); return tuple(int(v) for v in WHEEL[i]*(1-f)+WHEEL[(i+1)%len(WHEEL)]*f)
SS=2; W=S*SS
img=Image.new('RGB',(W,W),(252,251,249))
panels=[(np.pi*(np.sqrt(2)-1)/1.0*0.5, np.pi/3, 'irr', (0.08,0.06,0.84)),   # big: alpha = (sqrt2-1)pi/2 irrational
        (np.pi/6, np.pi/3, 'rat', (0.06,0.78,0.26)),(np.pi/4, np.pi/4,'rat',(0.37,0.78,0.26)),(np.pi/5,2*np.pi/5,'rat',(0.68,0.78,0.26))]
for k,(al,be,kind,(x0,y0,sz)) in enumerate(panels):
    V=triangle(al,be); V=V-V.mean(0)
    ext=max(np.ptp(V[:,0]),np.ptp(V[:,1])); sc=sz*W/ext*0.95
    cx,cy=(x0+sz/2)*W,(y0+sz/2)*W
    P=lambda q:(cx+q[0]*sc, cy-q[1]*sc)
    nb=NB if k==0 else NB//6
    p0=V.mean(0)+np.array([0.013,0.007]); ang=0.7234567
    O=orbit(V,p0,ang,nb)
    lay=Image.new('RGBA',(W,W),(0,0,0,0)); d=ImageDraw.Draw(lay)
    lw=max(1,int(W/1400*(1.1 if k==0 else 1.4)))
    for i in range(len(O)-1):
        c=wheel(i/len(O)*1.0+0.02)
        d.line([P(O[i]),P(O[i+1])],fill=c+(52 if k==0 else 90,),width=lw)
    img.paste(Image.alpha_composite(img.convert('RGBA'),lay).convert('RGB'))
    dd=ImageDraw.Draw(img)
    dd.polygon([P(v) for v in V],outline=(150,130,160),width=max(2,int(3*W/2800)))
    r=7*W/2800*(1.6 if k==0 else 1); q=P(p0); dd.ellipse([q[0]-r,q[1]-r,q[0]+r,q[1]+r],fill=CORAL)
img=img.resize((S,S),Image.LANCZOS); img.save(out)
