"""SIX FILMS, ONE SHORE — sun print.  One film per prime power of m = 720720 = 2^4 3^2 5 7 11 13; the density of film p at s is
|F_p(s)|, F_p(s) = p^(-a(s-1/2)) q(p^s)/q(p^(1-s)), q(x)=1+x+...+x^a.  Stacked films multiply, and F = prod F_p (M = sqrt m).
Each strip is printed alone, the last through the whole stack.   usage: stack.py W out.png"""
import sys, numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image, ImageDraw, ImageFont
from sympy import factorint
W=int(sys.argv[1]); OUT=sys.argv[2]; S=W/2048.0
m=720720; fac=sorted(factorint(m).items())
def noise(shape,sig,seed):
    r=np.random.default_rng(seed).standard_normal(shape); r=gaussian_filter(r,sig,mode='wrap'); return r/r.std()
MX=int(190*S); PW=W-2*MX+int(20*S); ppu=190*S; T0=0.7; SH=int(214*S); GAP=int(20*S); MY=int(104*S)
t=T0+(np.arange(PW)+0.5)/ppu; SL=int(1.42*SH)
def grid(hh):
    global s,sg
    sg=0.5-(np.arange(hh)-hh/2+0.5)/ppu; s=sg[:,None]+1j*t[None,:]
grid(SH)
def hp(p,a):
    x=np.exp(s*np.log(p)); y=p/x
    q=lambda z: sum(z**j for j in range(a+1))
    with np.errstate(divide='ignore'): return -a*(s.real-0.5)*np.log(p)+np.log(np.abs(q(x)))-np.log(np.abs(q(y)))
hs=[hp(p,a) for p,a in fac]
print('min over land of each film (must be >0):',[float(np.min(h[sg>0.5+1e-9])) for h in hs])
grid(SL); hs.append(sum(hp(p,a) for p,a in fac)); print('stack min over land',float(np.min(hs[-1][sg>0.5+1e-9])))
paper=np.array([0.957,0.937,0.878]); img=np.ones((W,W,3))*paper
img*= (1+0.016*noise((W,W),0.9*S,1)[...,None]+0.012*noise((W,W),50*S,2)[...,None])
blue_lo=np.array([0.36,0.56,0.74]); blue_hi=np.array([0.035,0.115,0.29])
ox=MX-int(10*S); n=len(hs); H=(n-1)*SH+SL+(n-1)*GAP; pad=int(40*S)
Q_h=H+2*pad; Q_w=PW+2*pad
y2,x2=np.mgrid[0:Q_h,0:Q_w]
rag=noise((Q_h,),6*S,10)*9*S+noise((Q_h,),1.5*S,20)*5*S; rag2=noise((Q_h,),6*S,30)*9*S+noise((Q_h,),1.5*S,40)*5*S
coat=np.clip((x2-pad*0.4-rag[:,None])/(3*S),0,1)*np.clip((Q_w-pad*0.4-rag2[:,None]-x2)/(3*S),0,1)
tb=noise((Q_w,),30*S,50)*3*S; tb2=noise((Q_w,),30*S,51)*3*S
coat*=np.clip((y2-pad*0.5-tb[None,:])/(2.5*S),0,1)*np.clip((Q_h-pad*0.5-tb2[None,:]-y2)/(2.5*S),0,1)
streak=1+0.9*gaussian_filter(np.random.default_rng(60).standard_normal((Q_h,Q_w)),(1.5*S,70*S))
# what the paper sees: full sun where no film lies (deep blue border), the film's density elsewhere
logdose=np.full((Q_h,Q_w),3.0)                         # bare coat: fully exposed
boxes=[]
for i,h in enumerate(hs):
    y0=pad+i*(SH+GAP); gamma=1.25
    ld=-gamma*np.clip(h,-30,30)
    # film edge: a thin clear rebate around each strip, then tape shadows (unexposed) between strips
    hh=h.shape[0]; logdose[y0:y0+hh,pad:pad+PW]=ld
    yt=y0+hh/2; thr=np.clip(0.9*S-np.abs(y2[y0:y0+hh,:]+0.5-yt)+0.5,0,1); logdose[y0:y0+hh,:]-=7*thr      # a thread stretched between the marks
    boxes.append(y0)
for i in range(n-1):
    y0=pad+i*(SH+GAP)+SH; logdose[y0+int(3*S):y0+GAP-int(3*S),:]=-9.0     # paper tape between the films: no light
b=0.5+np.arctan(1.25*logdose+np.log(np.clip(streak,0.8,1.2))*0.7)/np.pi
b=np.clip(b,0,1)**1.15
b=gaussian_filter(b,0.8*S)
col=blue_lo[None,None,:]*(1-b[...,None])+blue_hi[None,None,:]*b[...,None]
tt=np.clip(b*2.1,0,1)[...,None]; col=paper*(1-tt)+col*tt
col*= (1+0.03*noise((Q_h,Q_w),0.8*S,70)[...,None])
oy=MY-pad; a=coat[...,None]; sl=(slice(oy,oy+Q_h),slice(ox-pad,ox-pad+Q_w)); img[sl]=img[sl]*(1-a)+col*a
im=Image.fromarray((np.clip(img,0,1)*255+.5).astype(np.uint8)); dr=ImageDraw.Draw(im)
F=lambda nm,sz: ImageFont.truetype(f'/usr/share/fonts/truetype/liberation/LiberationSerif-{nm}.ttf',int(sz*S))
pc=(78,78,90); rc=(205,52,42)
sup={2:'2⁴',3:'3²'}
for i in range(n):
    yc=MY+i*(SH+GAP)+(SL if i==n-1 else SH)/2
    lab='all six' if i==n-1 else sup.get(fac[i][0],str(fac[i][0]))
    f=F('Italic',30) if i==n-1 else F('Regular',40)
    tw=dr.textlength(lab,font=f); dr.text((ox-pad-int(34*S)-tw,yc-int(24*S)),lab,font=f,fill=pc)
    # red register marks at the height of the shore, both margins
    for xa,xb in ((ox-pad-int(24*S),ox-pad-int(2*S)),(ox+PW+pad+int(2*S),ox+PW+pad+int(24*S))):
        dr.line((xa,yc,xb,yc),fill=rc,width=max(1,int(2.2*S)))
ty=MY+H+int(64*S)
dr.text((MX,ty),'Six Films, One Shore',font=F('Regular',46),fill=pc)
L1='One film for each prime power of 720720, printed alone. A thread is stretched between the red marks. Every film prints paler than mid-blue above its thread and deeper'
L2='below it, however it wanders elsewhere. Films laid together multiply; so the six in one stack do the same, only more so. That is the whole proof that the shore is straight.'
dr.text((MX,ty+int(60*S)),L1,font=F('Italic',22.5),fill=pc); dr.text((MX,ty+int(90*S)),L2,font=F('Italic',22.5),fill=pc)
note='film p has density |F(p)|, and F = F(2) F(3) F(5) F(7) F(11) F(13) at M = √m.  Im s from %.2f to %.2f'%(t[0],t[-1])
tw=dr.textlength(note,font=F('Italic',21)); dr.text((W-MX-tw,ty+int(18*S)),note,font=F('Italic',21),fill=pc)
im.save(OUT); print('saved',OUT)
