"""Still 2 — the D4 Dynkin diagram and the source of triality.
so(8) is the ONLY simple Lie algebra whose Dynkin diagram has a 3-fold symmetry:
a central node joined to three outer nodes. Permuting those three legs is an
outer automorphism of order 3 -- TRIALITY -- and the three legs correspond to
the three 8-dimensional representations 8_v, 8_s, 8_c."""
import numpy as np, math, sys
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter

CV=(70,190,255); CS=(255,200,80); CC=(255,95,180)

def font(sz):
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf","DejaVuSans-Bold.ttf"]:
        try: return ImageFont.truetype(p,sz)
        except Exception: pass
    return ImageFont.load_default()

def arrowhead(d,p,ang,size,col):
    sp=math.radians(26)
    q1=(p[0]+size*math.cos(ang+math.pi-sp),p[1]+size*math.sin(ang+math.pi-sp))
    q2=(p[0]+size*math.cos(ang+math.pi+sp),p[1]+size*math.sin(ang+math.pi+sp))
    d.polygon([p,q1,q2],fill=col)

def render(S=2048, ss=2):
    W=S*ss; cx=cy=W/2
    img=Image.new('RGB',(W,W),(5,6,14)); d=ImageDraw.Draw(img,'RGBA')
    R=W*0.30
    cols=[CV,CS,CC]; names=['8v','8s','8c']
    ang=[90,210,330]
    outer=[(cx+R*math.cos(math.radians(a)),cy+R*math.sin(math.radians(a))) for a in ang]
    nr=W*0.045; lw=int(W*0.010)
    # edges centre<->outer (the Dynkin bonds)
    for k,o in enumerate(outer):
        d.line([(cx,cy),o],fill=(200,210,255,180),width=lw)
    # triality 3-cycle arc (chiral) around centre
    rr=W*0.135
    for k in range(3):
        a0=math.radians(ang[k])+math.radians(30); a1=math.radians(ang[(k+1)%3])-math.radians(30)
        sweep=(a1-a0)%(2*math.pi); N=40
        c0=cols[k]; c1=cols[(k+1)%3]
        for i in range(N-1):
            t0=i/(N-1); t1=(i+1)/(N-1)
            p0=(cx+rr*math.cos(a0+sweep*t0),cy+rr*math.sin(a0+sweep*t0))
            p1=(cx+rr*math.cos(a0+sweep*t1),cy+rr*math.sin(a0+sweep*t1))
            col=tuple(int(c0[j]+(c1[j]-c0[j])*t0) for j in range(3))+(230,)
            d.line([p0,p1],fill=col,width=int(W*0.006))
        tip=(cx+rr*math.cos(a0+sweep*0.99),cy+rr*math.sin(a0+sweep*0.99))
        arrowhead(d,tip,a0+sweep*0.99+math.pi/2,W*0.026,c1+(255,))
    # central node (the node fixed by triality -> part of G2)
    d.ellipse([cx-nr,cy-nr,cx+nr,cy+nr],fill=(235,240,255),outline=(255,255,255),width=lw//2)
    # outer nodes coloured by rep
    for k,o in enumerate(outer):
        c=cols[k]
        d.ellipse([o[0]-nr,o[1]-nr,o[0]+nr,o[1]+nr],
                  fill=tuple(min(255,int(v*1.0)) for v in c),outline=(255,255,255),width=lw//2)
    arr=np.asarray(img).astype(np.float32)/255
    t=np.stack([gaussian_filter(arr[...,c],W*0.0012) for c in range(3)],-1)
    wd=np.stack([gaussian_filter(arr[...,c],W*0.009) for c in range(3)],-1)
    out=1.0-np.exp(-1.25*(arr+0.6*t+0.3*wd))
    im=Image.fromarray((np.clip(out,0,1)*255).astype('uint8'))
    od=ImageDraw.Draw(im); f=font(int(W*0.05/ss))  # final-res font
    # labels (draw at supersample then downscale keeps crisp enough; do before resize)
    fbig=font(int(W*0.050))
    od2=ImageDraw.Draw(im)
    for k,o in enumerate(outer):
        lp=(cx+(R+nr*2.0)*math.cos(math.radians(ang[k])),cy+(R+nr*2.0)*math.sin(math.radians(ang[k])))
        bb=od2.textbbox((0,0),names[k],font=fbig); wgt=bb[2]-bb[0]; hgt=bb[3]-bb[1]
        od2.text((lp[0]-wgt/2-bb[0],lp[1]-hgt/2-bb[1]),names[k],font=fbig,fill=cols[k])
    lab='D4 : so(8)'
    bb=od2.textbbox((0,0),lab,font=fbig);
    od2.text((cx-(bb[2]-bb[0])/2-bb[0], W*0.04),lab,font=fbig,fill=(190,200,235))
    return im.resize((S,S),Image.LANCZOS)

if __name__=="__main__":
    if len(sys.argv)>1 and sys.argv[1]=='preview':
        render(700,2).save('triality/proto/_dynkin.png')
    else:
        render(2048,2).save('triality/02_d4_dynkin_triality.png')
    print('done')
