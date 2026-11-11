# The d=11 loop as coiled beadwork: 2,048 rows of 11 beads; consecutive rows differ in exactly one bead.
import sys, json, math, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W=int(sys.argv[1]); out=sys.argv[2]; SS=2
d=11; n=2048
C=[int(x) for x in open('../math_cube/d11_C.txt').read().replace('\n',' ').split(',')]
assert sorted(C)==list(range(n)) and all(bin(C[k]^C[(k+1)%n]).count('1')==1 for k in range(n))
def hexc(h): return np.array([int(h[i:i+2],16)/255 for i in (1,3,5)])
HUES=[hexc(h) for h in ['#ff6f7d','#ff8a5c','#ffab45','#ffd23f','#b9dd52','#5fd08e','#3cc4c0','#58b4f0','#7592f0','#a583ec','#e07fd6']]
PAPER=np.array([0.992,0.985,0.975])
Wd=W*SS; cx=Wd*0.5; cy=Wd*0.456; Rout=Wd*0.432
lanes=d; gap=1.5
def layout(p):
    """centres of all beads for pitch p; returns arrays (n,d,2) and final outer radius"""
    r=7.0*p+5*p; th=0.0; P=np.zeros((n,d,2)); A=np.zeros(n)
    b=(lanes+gap)*p/(2*math.pi)
    for t in range(n):
        for j in range(d):
            rr=r+(j-5)*p
            P[t,j]=(cx+rr*math.cos(th-math.pi/2), cy+rr*math.sin(th-math.pi/2))
        A[t]=th
        dth=p*1.0/(r-5*p); th+=dth; r+=b*dth
    return P,r+5*p
lo,hi=2.0,200.0
for _ in range(50):
    mid=(lo+hi)/2
    if layout(mid)[1]>Rout: hi=mid
    else: lo=mid
p=lo; P,_=layout(p); print('pitch px (final)',p/SS)
rad=p*0.47
def sprite(col, glass):
    s=int(math.ceil(rad))+2; y,x=np.mgrid[-s:s+1,-s:s+1].astype(float)
    rr=np.hypot(x,y)/rad; a=np.clip((1-rr)*rad+0.5,0,1)
    z=np.sqrt(np.clip(1-rr**2,0,1)); nx,ny=x/rad,y/rad
    lam=np.clip(-0.50*nx-0.62*ny+0.60*z,0,1)
    if glass:
        base=np.array([0.985,0.980,0.992]); sh=0.90+0.13*lam
        rgb=base[None,None,:]*sh[...,None]
        rgb=rgb*(1-0.07*(rr**3))[...,None]
        # faint inner glow at the lower right, like milk glass
        gl=np.exp(-(((nx-0.35)**2+(ny-0.42)**2)/0.10)); rgb+=0.03*gl[...,None]
        spec=np.exp(-(((nx+0.34)**2+(ny+0.40)**2)/0.035)); rgb=rgb*(1-0.0)+0.10*spec[...,None]
        al=a*0.90
    else:
        sh=0.70+0.42*lam
        rgb=col[None,None,:]*sh[...,None]
        rgb=rgb*(1-0.22*(rr**4))[...,None]
        gl=np.exp(-(((nx-0.36)**2+(ny-0.44)**2)/0.12)); rgb+=0.16*gl[...,None]*(0.4+0.6*col)[None,None,:]
        spec=np.exp(-(((nx+0.34)**2+(ny+0.40)**2)/0.030)); rgb=rgb+0.62*spec[...,None]
        al=a
    return np.clip(rgb,0,1),al,s
img=np.broadcast_to(PAPER,(Wd,Wd,3)).copy()
# shadows
sh=np.zeros((Wd,Wd),np.float32)
s=int(math.ceil(rad))+2; y,x=np.mgrid[-s:s+1,-s:s+1].astype(float)
disc=np.clip((rad-np.hypot(x,y))+0.5,0,1).astype(np.float32)
ox,oy=int(round(rad*0.30)),int(round(rad*0.42))
for t in range(n):
    for j in range(d):
        X=int(round(P[t,j,0]))+ox; Y=int(round(P[t,j,1]))+oy
        v=sh[Y-s:Y+s+1,X-s:X+s+1]; np.maximum(v,disc,out=v)
shb=np.asarray(Image.fromarray((sh*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(rad*0.38)),dtype=np.float32)/255
img*= (1-shb[...,None]*np.array([0.30,0.27,0.17]))
del sh,shb
SP=[sprite(HUES[j],False) for j in range(d)]; GL=sprite(None,True)
flip=[(C[t]^C[t-1]).bit_length()-1 for t in range(n)]     # bead that changed on arriving at row t
for t in range(n):
    v=C[t]
    for j in range(d):
        rgb,al,s=SP[j] if (v>>j)&1 else GL
        X=int(round(P[t,j,0])); Y=int(round(P[t,j,1]))
        reg=img[Y-s:Y+s+1,X-s:X+s+1]
        reg[:]=reg*(1-al[...,None])+rgb*al[...,None]
im=Image.fromarray((np.clip(img,0,1)*255+0.5).astype(np.uint8)).resize((W,W),Image.LANCZOS)
# marks: start row (all clear) and the all-coloured row
dr=ImageDraw.Draw(im)
F=lambda nme,sz: ImageFont.truetype('/usr/share/fonts/truetype/freefont/'+nme+'.ttf',int(sz*W))
def mark(t,label,side):
    a=P[t,0]/SS; b=P[t,d-1]/SS; u=(b-a)/np.linalg.norm(b-a)
    q0=b+u*rad/SS*1.6; q1=b+u*rad/SS*5.5
    if side<0: q0=a-u*rad/SS*1.6; q1=a-u*rad/SS*5.5
    dr.line([tuple(q0),tuple(q1)],fill=(236,104,88),width=max(2,W//900))
    f=F('FreeSerifItalic',0.0105); w=dr.textlength(label,font=f)
    dr.text((q1[0]-w/2,q1[1]-(0.014*W if q1[1]<q0[1] else -0.003*W)),label,font=f,fill=(236,104,88))
t1=C.index(n-1)
for t in (0,n-1):
    q=(P[t,0]+P[t,d-1])/2/SS; u=(P[t,d-1]-P[t,0]); u=u/np.linalg.norm(u); tg=np.array([-u[1],u[0]])*(1 if t else -1)
    q=q+tg*rad/SS*3.2; r0=rad/SS*0.9
    dr.ellipse([q[0]-r0,q[1]-r0,q[0]+r0,q[1]+r0],fill=(236,104,88))
def ctext(y,text,fn,sz,col=(92,77,102)):
    f=F(fn,sz); w=dr.textlength(text,font=f); dr.text(((W-w)/2,y*W),text,font=f,fill=col)
ctext(0.905,"Eleven Beads Wide, One Bead Changes at a Time",'FreeSerifBold',0.0300)
ctext(0.9455,"A loop through all 2,048 corners of the eleven-dimensional cube, coiled from the centre. Each row of eleven beads is a corner: coloured for 1, milk glass for 0.",'FreeSerifItalic',0.0135)
ctext(0.9685,"slide every row one bead sideways, round the end, and you get another such loop; the eleven of them swim all 22,528 lanes once  \u00b7  the coral dots are the two ends, which join  \u00b7  found on a home computer",'FreeSerifItalic',0.0105,(140,126,150))
im.save(out)
print('all-ones row at',t1)
