import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter
import json, sys

S3=np.sqrt(3)
def basis(s): return np.array([[s,0],[s/2,s*S3/2]])
def axial_round(qf,rf):
    xf=qf; zf=rf; yf=-xf-zf
    rx=np.round(xf); ry=np.round(yf); rz=np.round(zf)
    dx=np.abs(rx-xf); dy=np.abs(ry-yf); dz=np.abs(rz-zf)
    c1=(dx>dy)&(dx>dz); c2=(dy>dz)&~c1
    rx=np.where(c1,-ry-rz,rx); ry=np.where(c2,-rx-rz,ry); rz=np.where(~c1&~c2,-rx-ry,rz)
    return rx.astype(np.int64),rz.astype(np.int64)

def render(OUT=2048, s=0.75, units_across=8.2, fname="03_restrict_the_possible.png"):
    U=OUT/units_across
    Binv=np.linalg.inv(basis(s))
    X,Y=np.meshgrid(np.arange(OUT),np.arange(OUT))
    wx=(X-OUT/2)/U; wy=(OUT/2-Y)/U
    QR=np.stack([wx,wy],-1)@Binv
    q,r=axial_round(QR[...,0],QR[...,1])
    cidx=(q-2*r)%7
    pal=np.array([
        [235,176, 64],[ 52,168,176],[214, 74, 92],[ 96,112,210],
        [122,188,108],[176,100,196],[238,132, 58]],dtype=np.float32)/255
    luma=(pal@np.array([0.299,0.587,0.114]))[:,None]
    pal=pal*0.86+luma*0.14   # slight desaturation -> deep-jewel mood
    img=pal[cidx]*0.74
    # leaded-glass grout
    qr=q*100003+r
    edge=np.zeros((OUT,OUT),bool)
    edge[:-1,:]|=qr[:-1,:]!=qr[1:,:]; edge[1:,:]|=qr[:-1,:]!=qr[1:,:]
    edge[:,:-1]|=qr[:,:-1]!=qr[:,1:]; edge[:,1:]|=qr[:,:-1]!=qr[:,1:]
    edge=gaussian_filter(edge.astype(np.float32),0.6)
    img*= (1-0.7*edge)[...,None]
    # stained-glass backlight bloom
    glowfield=np.zeros_like(img)
    for k in range(3): glowfield[...,k]=gaussian_filter(img[...,k],sigma=OUT/220)
    img=np.clip(img*0.82+glowfield*0.4,0,1)
    # spindle (computed + verified in spindle.py)
    from spindle import moser_spindle, chromatic_number
    V,edges,_=moser_spindle(); _,col=chromatic_number(7,edges)
    cen=V.mean(0); Vw=(V-cen)+np.array([-0.6,0.1])
    def w2p(p): return (p[0]*U+OUT/2, OUT/2-p[1]*U)
    SS=2
    big=Image.new("RGB",(OUT*SS,OUT*SS),(0,0,0)); dd=ImageDraw.Draw(big)
    def w2pb(p): return (p[0]*U*SS+OUT*SS/2, OUT*SS/2-p[1]*U*SS)
    for ni in [0,3]:
        cx,cy=w2pb(Vw[ni]); rr=U*SS
        dd.ellipse([cx-rr,cy-rr,cx+rr,cy+rr],outline=(120,135,175),width=int(2*SS))
    for (i,j) in edges:
        dd.line([w2pb(Vw[i]),w2pb(Vw[j])],fill=(255,255,255),width=int(5.5*SS))
    glow=np.asarray(big.resize((OUT,OUT),Image.LANCZOS)).astype(np.float32)/255
    g=np.zeros_like(glow)
    for k in range(3):
        g[...,k]=glow[...,k]+1.0*gaussian_filter(glow[...,k],sigma=2.4)+0.55*gaussian_filter(glow[...,k],sigma=7)
    # warm halo behind proof
    halo=gaussian_filter(glow.mean(2),sigma=OUT/40)
    img=np.clip(img+halo[...,None]*np.array([0.18,0.16,0.12])+g*0.85,0,1)
    ncols=np.array([[248,92,82],[96,206,124],[92,162,252],[250,218,92]],dtype=np.float32)/255
    base=Image.fromarray((img*255).astype(np.uint8)); dn=ImageDraw.Draw(base)
    for vi,p in enumerate(Vw):
        cx,cy=w2p(p); rr=U*0.125
        c=tuple(int(x) for x in (ncols[col[vi]]*255))
        dn.ellipse([cx-rr-4,cy-rr-4,cx+rr+4,cy+rr+4],fill=(252,252,255))
        dn.ellipse([cx-rr,cy-rr,cx+rr,cy+rr],fill=c)
    img=np.asarray(base).astype(np.float32)/255
    yy,xx=np.mgrid[0:OUT,0:OUT]; rad=np.sqrt(((xx-OUT/2)/(OUT/2))**2+((yy-OUT/2)/(OUT/2))**2)
    img*=np.clip(1-0.55*np.clip(rad-0.42,0,1)**1.4,0,1)[...,None]
    Image.fromarray((np.clip(img,0,1)*255).astype(np.uint8)).save(fname)
    print("saved",fname,OUT)

if __name__=="__main__":
    render(OUT=int(sys.argv[1]) if len(sys.argv)>1 else 2048)
