"""THE MAP TO INFINITY: the right half of the critical strip with the distance to Re s = 1 on a log scale
(x = -log10(1 - sigma)), height t upward on a log-log scale. Paper sheets = regions with no zeros: de la Vallee
Poussin 1896 (Mossinghoff-Trudgian constant 5.573412), Vinogradov-Korobov (Ford's constant 57.54), and the two
claimed half-planes 11/12 and 7/8. Right panel: Dirichlet L(s,chi) by conductor q near t = 0 (Kadiri 2018)."""
import numpy as np, sys
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter, shift as nshift
from caption import caption, CORAL, INK, SOFT, F
S=int(sys.argv[1]); out=sys.argv[2]
SS=2; W=S*SS; H=int(W*1.26)
PAPER=np.array([0.994,0.990,0.984])
img=np.ones((H,W,3))*PAPER
mL=int(W*0.10); gap=int(W*0.07); mR=int(W*0.07); pw=int((W-mL-mR-gap)*0.60); pw2=W-mL-mR-gap-pw; top=int(W*0.05); ph=int(W*0.98)
X0,X1=0.2,7.6
def xof(sig): return -np.log10(1-sig)
LIL=np.array([0.87,0.81,0.98]); SKY=np.array([0.76,0.87,1.0]); MINT=np.array([0.74,0.92,0.84]); PEACH=np.array([1.0,0.84,0.70]); STRIP=np.array([0.985,0.978,0.988])
def panel(x0,width,sheets):
    ys=np.linspace(0,1,ph); xs=np.linspace(X0,X1,width)
    hgt=np.zeros((ph,width)); col=np.ones((ph,width,3))*PAPER
    for fL,c in sheets:
        L=fL(ys); m=xs[None,:]>=L[:,None]; hgt[m]+=1; col[m]=c
    s=width/1000
    up=nshift(hgt,(2.0*s,1.5*s),order=0,mode='nearest'); d=np.clip(up-hgt,0,None); d=2*(1-np.exp(-d/2))
    sh=gaussian_filter(d,1.6*s)
    col*=1-0.30*(1-np.exp(-sh))[...,None]*np.array([0.55,0.50,0.30])*1.9
    tl=nshift(hgt,(0.9*s,0.9*s),order=0,mode='nearest'); lit=1-np.exp(-np.clip(hgt-tl,0,None))
    col=col+(1-col)*0.5*lit[...,None]
    img[top:top+ph,x0:x0+width]=col[::-1]
Y0,Y1=0.0,6.0
def logt(y): return np.log(10)*10**(Y0+y*(Y1-Y0))
def x_dlvp(y): return np.log10(5.573412*logt(y))
def x_vk(y):
    lt=logt(y); return np.log10(57.54*lt**(2/3)*np.log(lt)**(1/3))
sheets=[(lambda y:np.full_like(y,xof(0.5)),STRIP),(lambda y:np.full_like(y,xof(7/8)),LIL),(lambda y:np.full_like(y,xof(11/12)),SKY),
        (lambda y:np.minimum(x_vk(y),x_dlvp(y)),MINT),(x_dlvp,PEACH)]
panel(mL,pw,sheets)
LQ0,LQ1=0.4771,600.0
def logq(y): return np.log(10)*(LQ0+y*(LQ1-LQ0))
def x_kad(y): return np.log10(6.4355*logq(y))
def x_sie(y): return np.log10(logq(y))
xR0=mL+pw+gap
panel(xR0,pw2,[(lambda y:np.full_like(y,xof(0.5)),STRIP),(lambda y:np.full_like(y,xof(7/8)),LIL),(lambda y:np.full_like(y,xof(11/12)),SKY),(x_kad,PEACH)])
im=Image.fromarray((np.clip(img,0,1)*255).astype(np.uint8)); d=ImageDraw.Draw(im,'RGBA')
def XL(x): return mL+(x-X0)/(X1-X0)*(pw-1)
def XR(x): return xR0+(x-X0)/(X1-X0)*(pw2-1)
def YY(y): return top+ph-1-y*(ph-1)
s=W/2800
ys=np.linspace(0,1,600)
d.line([(XL(x_dlvp(y)),YY(y)) for y in ys],fill=(92,77,102,230),width=max(2,int(1.8*s)))
d.line([(XL(x_vk(y)),YY(y)) for y in ys],fill=(60,120,100,200),width=max(2,int(1.8*s)))
d.line([(XR(x_kad(y)),YY(y)) for y in ys],fill=(92,77,102,230),width=max(2,int(1.8*s)))
d.line([(XR(x_sie(y)),YY(y)) for y in ys],fill=(92,77,102,160),width=max(2,int(1.6*s)))
zs=np.concatenate([np.load('proto/zeros_mp120.npy'),np.load('proto/zeros_3000.npy')[120:]])
yz=(np.log10(np.log10(zs))-Y0)/(Y1-Y0)
for k,(g,y) in enumerate(zip(zs,yz)):
    r=(5.5 if k<120 else 2.2)*s; x=XL(xof(0.5)); yy=YY(y)
    if k<120: d.ellipse([x-r*1.5,yy-r*1.5,x+r*1.5,yy+r*1.5],fill=(255,255,255,200))
    d.ellipse([x-r,yy-r,x+r,yy+r],fill=CORAL+(255,))
yb=0.25; xb=XR(0.5*(x_kad(np.array([yb]))[0]+x_sie(np.array([yb]))[0]))
r=6*s; d.ellipse([xb-r*1.5,YY(yb)-r*1.5,xb+r*1.5,YY(yb)+r*1.5],fill=(255,255,255,210)); d.ellipse([xb-r,YY(yb)-r,xb+r,YY(yb)+r],outline=CORAL+(255,),width=max(2,int(2*s)))
d.text((xb-200*s,YY(yb)+14*s),'the one real zero the classical theorem allows',font=ImageFont.truetype(F+'LiberationSerif-Italic.ttf',int(26*s)),fill=(92,77,102,255))
fs=ImageFont.truetype(F+'LiberationSerif-Italic.ttf',int(30*s)); fsm=ImageFont.truetype(F+'LiberationSerif-Italic.ttf',int(26*s))
for sig,lab,dy in ((0.5,'½',0),(7/8,'7/8',1),(11/12,'11/12',0),(0.99,'0.99',0),(0.999,'0.999',0),(1-1e-4,'0.9999',0),(1-1e-5,'0.99999',0),(1-1e-6,'0.999999',0),(1-1e-7,'0.9999999',0)):
    for X in (XL,XR):
        xx=X(xof(sig)); tw=d.textlength(lab,font=fsm); d.text((xx-tw/2,top+ph+10*s+dy*fsm.size*1.1),lab,font=fsm,fill=INK+(255,))
        d.line([xx,top+ph,xx,top+ph+6*s],fill=INK+(255,),width=max(1,int(1.5*s)))
for e,lab in ((1,'t = 10'),(10,'t = 10^10'),(100,'10^100'),(1000,'10^1000'),(10**4,'10^10000'),(10**5,'10^100000'),(10**6,'10^1000000')):
    y=(np.log10(e)-Y0)/(Y1-Y0); tw=d.textlength(lab,font=fs); d.text((mL-tw-14*s,YY(y)-fs.size/2),lab,font=fs,fill=SOFT+(255,))
    d.line([mL-8*s,YY(y),mL,YY(y)],fill=SOFT+(255,),width=max(1,int(1.5*s)))
for lq,lab in ((0.4771,'q = 3'),(10,'q = 10^10'),(100,'10^100'),(300,'10^300'),(600,'10^600')):
    y=(lq-LQ0)/(LQ1-LQ0); d.text((xR0+pw2+10*s,YY(y)-fs.size/2),lab,font=fs,fill=SOFT+(255,))
    d.line([xR0+pw2,YY(y),xR0+pw2+8*s,YY(y)],fill=SOFT+(255,),width=max(1,int(1.5*s)))
def lab(x,y,txt,col=INK,f=None): d.text((x,y),txt,font=f or fs,fill=col+(255,))
lab(XL(0.33),YY(0.965),'ζ(s): the critical strip, right half, with the distance to Re s = 1 on a log scale')
lab(XL(0.33),YY(0.965)+fs.size*1.3,'coral: the first 2,469 zeros, all on ½ · lilac: claimed zero-free beyond 7/8 · sky: beyond 11/12',SOFT)
lab(XL(0.33),YY(0.965)+fs.size*2.6,'plum thread: 1896, σ = 1 − 1/(5.573 log t) · green thread: Vinogradov–Korobov, 1 − 1/(57.5 (log t)^(2/3) (log log t)^(1/3))',SOFT)
lab(XL(0.33),YY(0.965)+fs.size*3.9,'peach and mint: all that was proved zero-free before; they drift toward 1 forever, the claimed sheets do not',SOFT)
lab(XR(0.33),YY(0.965),'L(s, χ), Dirichlet characters of conductor q, near t = 0')
lab(XR(0.33),YY(0.965)+fs.size*1.3,'plum thread: 1 − 1/(6.4355 log q), zero-free except for one possible',SOFT)
lab(XR(0.33),YY(0.965)+fs.size*2.6,'real zero (Kadiri 2018), the hollow bead; paler thread: the claimed cut',SOFT)
lab(XR(0.33),YY(0.965)+fs.size*3.9,'(1 − β) log q ≥ c, drawn with c = 1 (the paper gives no value)',SOFT)
caption(im,W/2,top+ph+W*0.05,'The Map to Infinity',
  'the right half of the critical strip, height upward on a log-log scale from the first zero to t = 10^1,000,000, the last eighth of the width on a log scale',
  'every paper sheet is a region where no zero can be; the classical regions thin to nothing as the height grows, the claimed half-planes keep their width at every height',
  W*0.031,align='center',line3='openai/math family 003 claims no zeros of ζ, of any Dirichlet L-function, or of any finite-order Hecke L-function over Q(√−3) with real part above 7/8')
im.convert('RGB').resize((S,int(H/SS)),Image.LANCZOS).save(out)
