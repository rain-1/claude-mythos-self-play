"""Sunflower of pinwheel primes (MO 515784): every quarter-turn-symmetric 7x7 binary matrix whose number is prime
(161 of them) + the unique 5x5 one, as sugared-clay button tiles on a Vogel spiral around an empty coral socket
(the pinwheel square that never turns up). Cells coloured by quadrant so the quarter turn reads as colour."""
import numpy as np, json, sys, argparse
from PIL import Image, ImageDraw, ImageFilter, ImageFont
ap=argparse.ArgumentParser(); ap.add_argument('--S',type=int,default=1200); ap.add_argument('--out',default='proto/pin1.png')
ap.add_argument('--H',type=int,default=0)
a=ap.parse_args()
SS=2; W=a.S*SS; H=(a.H or a.S)*SS
P=json.load(open('pin/primes.json'))
tiles=[(5,P['5'][0])]+[(7,N) for N in P['7']]
PAPER=(252,251,249)
QH=[(250,150,165),(253,214,120),(140,218,180),(150,165,240)]   # strawberry, butter, mint, periwinkle
CORAL=(247,125,110)
def bits(n,N): return [[(N>>(n*n-1-(i*n+j)))&1 for j in range(n)] for i in range(n)]
def quad(n,i,j):
    c=(n-1)/2; x=j-c; y=i-c
    if x==0 and y==0: return -1
    # quadrant chosen so the 4 cells of an orbit get 4 different quadrants (rotation (i,j)->(j,n-1-i))
    if x>0 and y<=0: return 0
    if x>=0 and y>0: return 1
    if x<0 and y>=0: return 2
    return 3
base=Image.new('RGB',(W,H),PAPER)
shadow=Image.new('L',(W,H),0); sd=ImageDraw.Draw(shadow)
top=Image.new('RGBA',(W,H),(0,0,0,0)); td=ImageDraw.Draw(top)
cx,cy=W/2,H*0.47
c=W*0.0255; R=c*0.80
GA=np.pi*(3-np.sqrt(5))
def rot(px,py,ang,ox,oy):
    ca,sa=np.cos(ang),np.sin(ang); return (ox+px*ca-py*sa, oy+px*sa+py*ca)
def rsquare(ox,oy,h,ang,rr=0.28,k=5):
    pts=[]
    for qx,qy,a0 in ((1,1,0),(-1,1,90),(-1,-1,180),(1,-1,270)):
        ccx,ccy=qx*h*(1-rr),qy*h*(1-rr)
        for t in np.linspace(np.radians(a0),np.radians(a0+90),k):
            pts.append(rot(ccx+h*rr*np.cos(t),ccy+h*rr*np.sin(t),ang,ox,oy))
    return pts
def lighten(c,f): return tuple(int(255-(255-v)*f) for v in c)
def darken(c,f): return tuple(int(v*f) for v in c)
items=[]
# socket at centre
items.append(('socket',cx,cy,R*1.55,0))
for i,(n,N) in enumerate(tiles):
    k=i+2.2
    r=c*np.sqrt(k)*1.0+R*1.15; th=k*GA
    ox,oy=cx+r*np.cos(th),cy+r*np.sin(th)
    items.append(('tile',ox,oy,R*(1.18 if n==5 else 1.0),th,n,N))
for it in items:
    if it[0]=='socket':
        _,ox,oy,rr,_=it
        sd.ellipse([ox-rr+0.1*rr,oy-rr+0.16*rr,ox+rr+0.1*rr,oy+rr+0.16*rr],fill=0)
        continue
    _,ox,oy,rr,th,n,N=it
    sd.ellipse([ox-rr+0.10*rr,oy-rr+0.16*rr,ox+rr+0.10*rr,oy+rr+0.16*rr],fill=150)
shadow=shadow.filter(ImageFilter.GaussianBlur(R*0.18))
sh=np.asarray(shadow,np.float32)/255
img=np.asarray(base,np.float32)*(1-0.22*sh[...,None]*np.array([1,1,0.6])[None,None,:]*1.0)
base=Image.fromarray(img.clip(0,255).astype(np.uint8)); d=ImageDraw.Draw(base)
# cell shadows layer
cshadow=Image.new('L',(W,H),0); cs=ImageDraw.Draw(cshadow)
for it in items:
    if it[0]=='socket':
        _,ox,oy,rr,_=it
        d.ellipse([ox-rr,oy-rr,ox+rr,oy+rr],fill=(246,240,238))
        d.ellipse([ox-rr*0.86,oy-rr*0.86,ox+rr*0.86,oy+rr*0.86],fill=(238,232,232))
        d.ellipse([ox-rr*0.80,oy-rr*0.80,ox+rr*0.80,oy+rr*0.80],fill=(250,248,246))
        w0=max(2,int(rr*0.06)); d.ellipse([ox-rr,oy-rr,ox+rr,oy+rr],outline=CORAL,width=w0)
        d.ellipse([ox-rr*0.80,oy-rr*0.80,ox+rr*0.80,oy+rr*0.80],outline=lighten(CORAL,0.55),width=max(1,w0//2))
        continue
    _,ox,oy,rr,th,n,N=it
    disc=(255,254,252)
    d.ellipse([ox-rr,oy-rr,ox+rr,oy+rr],fill=disc,outline=(236,230,232),width=max(1,int(rr*0.03)))
    ang=th+np.pi/4*0  # tiles turned with the spiral
    B=bits(n,N); cell=rr*1.30/n; h=cell*0.40
    for i in range(n):
        for j in range(n):
            px=(j-(n-1)/2)*cell; py=(i-(n-1)/2)*cell
            X,Y=rot(px,py,ang,ox,oy)
            if B[i][j]:
                cs.polygon(rsquare(X+h*0.25,Y+h*0.4,h*1.02,ang),fill=170)
            else:
                d.ellipse([X-h*0.16,Y-h*0.16,X+h*0.16,Y+h*0.16],fill=(240,236,238))
cshadow=cshadow.filter(ImageFilter.GaussianBlur(R*0.035))
csh=np.asarray(cshadow,np.float32)/255
img=np.asarray(base,np.float32)*(1-0.30*csh[...,None]*np.array([1,1,0.7])[None,None,:])
base=Image.fromarray(img.clip(0,255).astype(np.uint8)); d=ImageDraw.Draw(base)
for it in items:
    if it[0]!='tile': continue
    _,ox,oy,rr,th,n,N=it
    ang=th
    B=bits(n,N); cell=rr*1.30/n; h=cell*0.40
    for i in range(n):
        for j in range(n):
            if not B[i][j]: continue
            q=quad(n,i,j); col=CORAL if q<0 else QH[q]
            if n==5 and q>=0: col=QH[q]
            px=(j-(n-1)/2)*cell; py=(i-(n-1)/2)*cell
            X,Y=rot(px,py,ang,ox,oy)
            d.polygon(rsquare(X,Y,h,ang),fill=darken(col,0.93))
            d.polygon(rsquare(X-h*0.06,Y-h*0.08,h*0.86,ang),fill=col)
            d.polygon(rsquare(X-h*0.22,Y-h*0.26,h*0.36,ang,rr=0.5),fill=lighten(col,0.45))
    if n==5:
        w0=max(2,int(rr*0.05)); d.ellipse([ox-rr*1.07,oy-rr*1.07,ox+rr*1.07,oy+rr*1.07],outline=CORAL,width=w0)
out=base.resize((W//SS,H//SS),Image.LANCZOS)
out.save(a.out)
