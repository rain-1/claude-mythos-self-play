"""WHERE THE SHORE TURNS INSIDE OUT — engraved chart.  Same height h = log|E(s)/E(1-s)|, but E(s)=M^(s-1) sum a(d) d^-s with
a(d) the Epstein coefficients of x^2+5y^2 on the divisors of 5040 (no Euler product).   usage: lagoon.py W out.png"""
import sys, json, numpy as np
from scipy.ndimage import gaussian_filter, maximum_filter
from PIL import Image, ImageDraw, ImageFont
from core import *
W=int(sys.argv[1]); OUT=sys.argv[2]; S=W/2048.0
MM=5040; ds,a,Mask=setup(MM,'ep'); M=float(sys.argv[3]) if len(sys.argv)>3 else np.sqrt(MM)
TA=float(sys.argv[4]) if len(sys.argv)>4 else 6.3; TL=float(sys.argv[5]) if len(sys.argv)>5 else 4.2
lnM=np.log(M); ld=np.log(ds)
def fields(s):
    """h, arg F, |F'/F| at complex array s"""
    s=np.asarray(s,np.complex128); A1=np.zeros(s.shape,np.complex128); dA1=np.zeros_like(A1); A2=np.zeros_like(A1); dA2=np.zeros_like(A1)
    for l,c in zip(ld,a):
        e=c*np.exp(-s*l); A1+=e; dA1-=l*e
        e=c*np.exp(-(1-s)*l); A2+=e; dA2-=l*e
    with np.errstate(divide='ignore',invalid='ignore'):
        h=(2*s.real-1)*lnM+np.log(np.abs(A1))-np.log(np.abs(A2))
        ph=np.angle(A1/A2*np.exp(2j*s.imag*lnM)); gr=np.abs(2*lnM+dA1/A1+dA2/A2)
    return np.nan_to_num(h,posinf=50,neginf=-50),ph,np.nan_to_num(gr,posinf=1e6)
def noise(shape,sig,seed):
    r=np.random.default_rng(seed).standard_normal(shape); r=gaussian_filter(r,sig,mode='wrap'); return r/r.std()
def engrave(s,ppu,u,scale=1.0):
    """ink coverage for the chart at complex pixel grid s; ppu pixels per unit; u = design px"""
    h,ph,gr=fields(s); g=np.maximum(gr/ppu,1e-6)          # |grad h| per pixel
    ink=np.zeros(h.shape)
    # --- sea: water-lining, lines parallel to the shore, closer and bolder near it
    dep=np.clip(-h,0,None); K=5.2*scale
    U=K*dep**0.62; dU=K*0.62*np.maximum(dep,1e-3)**(-0.38)*g
    d=np.abs(U-np.round(U))/dU; w=(0.55+1.5*np.exp(-dep/0.9))*u
    w=np.minimum(w,0.62/dU)                                 # never more than 62 % ink
    sea=np.clip(w/2-d+0.5,0,1)*(h<0)*(np.round(U)>=1)
    # --- land: hachures down the slope (lines of constant arg F), in staggered rows between contours
    hh=np.clip(h,0,None); dl=0.55/scale; band=np.floor(hh/dl)
    NH=int(46*scale); U=ph*NH/(2*np.pi)+0.5*(band%2); dU=NH/(2*np.pi)*g
    d=np.abs(U-np.round(U))/dU
    wl=(0.45+2.3*np.clip(gr/ (2.2*lnM+6),0,1.6))*u; wl=np.minimum(wl,0.70/dU)
    edge=np.abs(hh/dl-np.round(hh/dl))*dl/g                 # px distance to the nearest contour
    land=np.clip(wl/2-d+0.5,0,1)*np.clip(edge-1.0*u+0.5,0,1)*(h>0)*(dU<0.9)
    # --- the shore itself
    shore=np.clip(1.5*u-np.abs(h)/g+0.5,0,1)
    return np.maximum(np.maximum(sea,land),shore),h
# ---------------- layout ----------------
MXp=int(150*S); x0,x1=MXp,W-MXp; y0=int(120*S); y1=y0+(x1-x0)*0+int(1560*S); ww=x1-x0; wh=y1-y0
ppu=ww/TL; yc=y0+0.5*wh; u=S
X=np.arange(W)+0.5; Y=np.arange(W)+0.5
t=TA+(X-x0)/ppu; sg=0.5-(Y-yc)/ppu
ink,h=engrave(sg[:,None]+1j*t[None,:],ppu,u)
XX,YY=np.meshgrid(X,Y)
inwin=(XX>=x0)&(XX<x1)&(YY>=y0)&(YY<y1); ink*=inwin
# lights: zeros of D.  On the line: sign changes of the tide.  Off the line: Newton from a grid.
TB=TA+TL; lt,_=lights(MM,M,TA,TB,dsa=(ds,a))
sys.path.insert(0,'math_coast')
from check1 import zeros_in
fD=lambda s:np.exp((np.asarray(s,complex)-1)*lnM)*A(s,ds,a)+np.exp(-np.asarray(s,complex)*lnM)*A(1-np.asarray(s,complex),ds,a)
smax=0.5+0.5*wh/ppu
off=zeros_in(fD,(0.5003,smax,TA,TB),n=260); zA=zeros_in(lambda s:A(s,ds,a),(0.5003,smax,TA,TB),n=260)
print('M=%.2f on-line lights %d, off-line zeros (right half) %s ; zeros of A right of the line %s'%(M,len(lt),np.round(off,4),np.round(zA,4)))
def P(z): return x0+(z.imag-TA)*ppu, yc-(z.real-0.5)*ppu
red=np.zeros((W,W)); knock=np.zeros((W,W))
def disc(cx,cy,r): return np.clip(r-np.hypot(XX-cx,YY-cy)+0.5,0,1)
for tv in lt:
    cx,cy=P(0.5+1j*tv); red=np.maximum(red,disc(cx,cy,5.8*u)); knock=np.maximum(knock,disc(cx,cy,9*u))
for z in off:
    for zz in (z,1-z.conjugate()):
        cx,cy=P(zz); red=np.maximum(red,disc(cx,cy,5.6*u)); knock=np.maximum(knock,disc(cx,cy,9*u))
        red=np.maximum(red,disc(cx,cy,15*u)*(1-disc(cx,cy,12.6*u)))
# soundings in the sea, spot heights on land
im=Image.new('L',(W,W),0); dr=ImageDraw.Draw(im)
FI=lambda sz: ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf',int(sz*S))
FR=lambda sz: ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf',int(sz*S))
rng=np.random.default_rng(5); nx,ny=9,8; pts=[]
for i in range(nx):
    for j in range(ny):
        px=x0+(i+0.5+rng.uniform(-0.3,0.3))*ww/nx; py=y0+(j+0.5+rng.uniform(-0.3,0.3))*wh/ny
        hv=h[int(py),int(px)]
        if abs(hv)<0.25 or abs(hv)>30: continue
        dr.text((px,py),('%.1f'%abs(hv)).replace('.',' ' if False else '.'),font=FI(21) if hv<0 else FR(19),fill=255,anchor='mm'); pts.append((px,py))
txt=np.asarray(im,float)/255; clear=np.clip(maximum_filter(txt,int(9*S))*3,0,1)
# ---------------- inset: one lagoon, magnified ----------------
inset=None
if len(off):
    z0=min(off,key=lambda z:abs(z.imag-(TA+0.72*TL))); MAG=5.0; R=int(250*S); cxi=x0+int(0.215*ww); cyi=y0+int(0.20*wh)
    if P(z0)[0]<x0+0.5*ww: cxi=x0+int(0.785*ww)
    ys=np.arange(cyi-R,cyi+R)+0.5; xs=np.arange(cxi-R,cxi+R)+0.5
    ti=z0.imag+(xs-cxi)/(ppu*MAG); si=0.5-(ys-cyi)/(ppu*MAG)
    ink_i,h_i=engrave(si[:,None]+1j*ti[None,:],ppu*MAG,u,scale=2.4)
    xi,yi=np.meshgrid(xs,ys); rr=np.hypot(xi-cxi,yi-cyi)
    def Pi(z): return cxi+(z.imag-z0.imag)*ppu*MAG, cyi-(z.real-0.5)*ppu*MAG
    red_i=np.zeros_like(ink_i); kn_i=np.zeros_like(ink_i)
    cand=[(0.5+1j*tv) for tv in lt]+[z for z in off]+[1-z.conjugate() for z in off]
    for zz in cand:
        cx,cy=Pi(zz)
        if np.hypot(cx-cxi,cy-cyi)<R-14*u:
            dd=np.hypot(xi-cx,yi-cy); red_i=np.maximum(red_i,np.clip(8*u-dd+0.5,0,1)); kn_i=np.maximum(kn_i,np.clip(12*u-dd+0.5,0,1))
    inset=dict(sl=(slice(cyi-R,cyi+R),slice(cxi-R,cxi+R)),ink=ink_i,rr=rr,R=R,red=red_i,kn=kn_i,c=(cxi,cyi),z0=z0,MAG=MAG)
if inset:
    cxi,cyi=inset['c']; lab='the lagoon at %.3f + %.3f i, five times larger'%(inset['z0'].real,inset['z0'].imag)
    tw=ImageDraw.Draw(Image.new('L',(8,8))).textlength(lab,font=FI(21))
    plate=((np.abs(XX-cxi)<tw/2+12*S)&(YY>cyi+inset['R']+2*S)&(YY<cyi+inset['R']+40*S)).astype(float); clear=np.maximum(clear,plate)
# ---------------- compose ----------------
paper=np.array([0.957,0.937,0.878]); indigo=np.array([0.085,0.105,0.26]); redc=np.array([0.80,0.20,0.16])
img=np.ones((W,W,3))*paper; img*= (1+0.015*noise((W,W),0.9*S,1)[...,None]+0.012*noise((W,W),50*S,2)[...,None])
cov=ink*(1-clear)*(1-knock); cov=np.maximum(cov,txt*inwin)
# border: double rule and a graduated scale
def rect(xa,ya,xb,yb): return ((XX>=xa)&(XX<xb)&(YY>=ya)&(YY<yb)).astype(float)
b1=rect(x0-3*S,y0-3*S,x1+3*S,y1+3*S)-rect(x0,y0,x1,y1)
g0=int(16*S); b2=rect(x0-g0-5*S,y0-g0-5*S,x1+g0+5*S,y1+g0+5*S)-rect(x0-g0,y0-g0,x1+g0,y1+g0)
tick=np.floor((t[None,:]-np.floor(TA))*10)%2; grad=((YY>=y1+3*S)&(YY<y1+g0)&(XX>=x0)&(XX<x1))*tick + ((YY>=y0-g0)&(YY<y0-3*S)&(XX>=x0)&(XX<x1))*tick
tk2=np.floor((sg[:,None]+10)*10)%2; grad=grad+(((XX>=x0-g0)&(XX<x0-3*S))|((XX>=x1+3*S)&(XX<x1+g0)))*((YY>=y0)&(YY<y1))*tk2
cov=np.maximum(cov,np.clip(b1+b2+grad,0,1))
a_=(cov*0.94)[...,None]; img=img*(1-a_)+indigo*a_
r_=(red*inwin)[...,None]; img=img*(1-r_)+redc*r_
if inset:
    sl=inset['sl']; R=inset['R']; rr=inset['rr']; inside=np.clip(R-rr+0.5,0,1)[...,None]
    sub=np.ones(rr.shape+(3,))*paper*(1+0.015*noise(rr.shape,0.9*S,7)[...,None])
    c2=np.maximum(inset['ink']*(1-inset['kn']),np.clip(4.5*S-np.abs(rr-(R-6*S))+0.5,0,1)); c2=np.maximum(c2,np.clip(1.2*S-np.abs(rr-(R-14*S))+0.5,0,1))
    sub=sub*(1-(c2*0.94)[...,None])+indigo*(c2*0.94)[...,None]; sub=sub*(1-inset['red'][...,None])+redc*inset['red'][...,None]
    shadow=np.clip(1-(rr-R)/(10*S),0,1)*(rr>R)*0.0
    img[sl]=img[sl]*(1-inside)+sub*inside
out=Image.fromarray((np.clip(img,0,1)*255+.5).astype(np.uint8)); dr=ImageDraw.Draw(out)
pc=(60,62,92); rc=(205,52,42)
FIt=lambda sz: ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf',int(sz*S))
for k in range(int(np.ceil(TA)),int(TB)+1):
    xk=x0+(k-TA)*ppu; dr.text((xk,y1+g0+int(10*S)),str(k),font=FR(20),fill=pc,anchor='ma')
if inset:
    cxi,cyi=inset['c']; z0=inset['z0']; px,py=P(z0)
    dr.text((cxi,cyi+inset['R']+int(8*S)),'the lagoon at %.3f + %.3f i, five times larger'%(z0.real,z0.imag),font=FIt(21),fill=pc,anchor='ma')
ty=y1+int(92*S)
dr.text((MXp,ty),'Where the Shore Turns Inside Out',font=FR(46),fill=pc)
n_off=len(off)
L1='The same chart for coefficients that do not factor over the primes (those of x² + 5y², on the divisors of 5040). The straight line is still shore. But on %s short'%({1:'one',2:'two',3:'three',4:'four'}.get(n_off,str(n_off)))
L2='stretches the water lies on the landward side: a lagoon inland, its twin island offshore, and on the far bank of each a ringed light: a zero that has left the line.'
dr.text((MXp,ty+int(60*S)),L1,font=FIt(22.5),fill=pc); dr.text((MXp,ty+int(90*S)),L2,font=FIt(22.5),fill=pc)
note='soundings and heights are |log |F||; hachures run down the slope; red = zeros (%d on the line, %d pairs off it); M = %s'%(len(lt),n_off,'√5040' if abs(M-np.sqrt(MM))<1e-9 else ('4√5040' if abs(M-4*np.sqrt(MM))<1e-3 else '%g'%M))
tw=dr.textlength(note,font=FIt(20)); dr.text((W-MXp-tw,ty+int(20*S)),note,font=FIt(20),fill=pc)
out.save(OUT); print('saved',OUT)
