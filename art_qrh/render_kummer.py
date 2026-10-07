"""KUMMER'S THREE ROADS: every primary prime pi of Z[w] with norm <= D at its own place in the plane; its colour is
the normalised cubic Gauss sum gamma_2(pi), a point on the unit circle. Lemma 4.2 of the paper: gamma_2(pi)^3 = -pi/|pi|,
so the only freedom is which of three cube roots -- Kummer's problem (1846)."""
import numpy as np, sys, math
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from caption import caption, CORAL, INK, SOFT, F
S=int(sys.argv[1]); out=sys.argv[2]; D=float(sys.argv[3]); mode=sys.argv[4] if len(sys.argv)>4 else 'class'
A=np.load('gauss_200000.npy'); A=A[A[:,2]<=D]
g=A[:,4]+1j*A[:,5]; z=A[:,0]+A[:,1]*complex(-0.5,3**0.5/2); split=A[:,3]==0; N=A[:,2]
base=np.angle(-z)/3; k=(np.round((np.angle(g)-base)/(2*np.pi/3))%3).astype(int)
SS=2; W=S*SS; H=int(W*1.17); cx,cy=W/2,W*0.47; R=math.sqrt(D); sc=W*0.44/R
PAPER=(252,251,249)
img=Image.new('RGB',(W,H),PAPER); d=ImageDraw.Draw(img)
CLASS=[(250,140,160),(120,205,232),(253,214,110)]   # strawberry / sky / butter for k = 0,1,2
PAL=np.array([[250,140,160],[255,175,140],[253,214,120],[180,224,140],[130,214,184],[130,196,240],[156,160,240],[196,150,236],[250,140,160]],float)
def wheel(h):
    h=(h%1)*(len(PAL)-1); i=int(h); f=h-i; return tuple(int(v) for v in PAL[i]*(1-f)+PAL[i+1]*f)
# faint three-sector guide: arg(-pi)/3 sweeps a third of a turn as pi goes round; draw a soft spoke pattern? keep the paper quiet.
rr=max(1.6,W*0.0014*(2e5/D)**0.25)
sh=Image.new('L',(W,H),0); sd=ImageDraw.Draw(sh)
for i in np.argsort(-N):
    x,y=cx+z[i].real*sc,cy-z[i].imag*sc
    sd.ellipse([x-rr+rr*0.25,y-rr+rr*0.35,x+rr+rr*0.25,y+rr+rr*0.35],fill=110)
sh=sh.filter(ImageFilter.GaussianBlur(rr*0.5))
a_=np.asarray(img).astype(float)*(1-0.20*np.asarray(sh)[...,None]/255*np.array([0.9,0.9,0.55]))
img=Image.fromarray(a_.astype(np.uint8)); d=ImageDraw.Draw(img)
for i in np.argsort(-N):
    x,y=cx+z[i].real*sc,cy-z[i].imag*sc
    col=CLASS[k[i]] if mode=='class' else wheel((np.angle(g[i])/(2*np.pi))%1)
    d.ellipse([x-rr,y-rr,x+rr,y+rr],fill=tuple(int(v*0.9) for v in col)); d.ellipse([x-rr*0.92,y-rr*0.95,x+rr*0.85,y+rr*0.8],fill=col)
    if rr>3: d.ellipse([x-rr*0.5,y-rr*0.55,x-rr*0.1,y-rr*0.15],fill=tuple(int(255-(255-v)*0.4) for v in col))
# legend by construction: the unit circle with the three cube roots for one prime
lx,ly,lr=W*0.88,W*0.88,W*0.065
d.ellipse([lx-lr,ly-lr,lx+lr,ly+lr],outline=(180,165,185),width=max(2,int(W/1400)))
i0=np.argmax(N*(split)*(np.abs(np.angle(z))<0.6))   # a sample split prime
for kk in range(3):
    ang=base[i0]+2*np.pi*kk/3; px,py=lx+lr*math.cos(ang),ly-lr*math.sin(ang); r2=W*0.009
    d.ellipse([px-r2,py-r2,px+r2,py+r2],fill=CLASS[kk],outline=(255,255,255),width=max(1,int(W/2000)))
ang=np.angle(-z[i0]); d.line([lx,ly,lx+lr*0.6*math.cos(ang),ly-lr*0.6*math.sin(ang)],fill=INK,width=max(2,int(W/1400)))
fs=ImageFont.truetype(F+'LiberationSerif-Italic.ttf',int(W*0.015))
for t,yy in (('γ₂(π)³ = −π/|π|',ly+lr*1.25),('three roots, one answer',ly+lr*1.25+fs.size*1.3)):
    tw=d.textlength(t,font=fs); d.text((lx-tw/2,yy),t,font=fs,fill=SOFT)
cnt=np.bincount(k[split],minlength=3)
# bias ledger: fraction of each road in dyadic norm shells
lo,hi=W*0.04,W*0.20; by0,by1=W*0.945,W*0.84
shells=[(2**j,2**(j+1)) for j in range(7,int(math.log2(D))+1)]
fr=[]
for a,b in shells:
    m=split&(N>=a)&(N<b)
    if m.sum()<30: continue
    fr.append((a,np.bincount(k[m],minlength=3)/m.sum()))
d.line([lo,by0,hi,by0],fill=(180,165,185),width=max(1,int(W/2000)))
yb=lambda f: by0-(f-0.15)/(0.55-0.15)*(by0-by1)
d.line([lo,yb(1/3),hi,yb(1/3)],fill=(200,190,205),width=max(1,int(W/2000)))
for kk in range(3):
    pts=[(lo+(i/(len(fr)-1))*(hi-lo),yb(f[kk])) for i,(a,f) in enumerate(fr)]
    d.line(pts,fill=CLASS[kk],width=max(3,int(W/700)))
    for (x,y) in pts: d.ellipse([x-W*0.004,y-W*0.004,x+W*0.004,y+W*0.004],fill=CLASS[kk],outline=(255,255,255),width=max(1,int(W/2500)))
for t,yy in (('share of each road, by norm shell 2⁷ … 2¹⁸',by0+fs.size*0.5),('the strawberry road is favoured, less and less',by0+fs.size*1.8)):
    d.text((lo,yy),t,font=fs,fill=SOFT)
d.text((hi+fs.size*0.4,yb(1/3)-fs.size*0.5),'⅓',font=fs,fill=SOFT)
caption(img,W/2,W*1.0,'Kummer’s Three Roads',
  f'every primary prime π of Z[ω] with norm ≤ {int(D):,} at its place in the plane ({len(A):,} primes), coloured by the angle of its cubic Gauss sum γ₂(π)',
  f'γ₂(π)³ = −π/|π| (Lemma 4.2), so each prime chooses one of three cube roots, a third of the wheel apart: {cnt[0]:,} / {cnt[1]:,} / {cnt[2]:,}  ·  mirror primes have conjugate colours',
  W*0.032,align='center',line3='Kummer (1846) guessed the roads were used 1:2:3; Heath-Brown and Patterson (1979) proved they even out, slowly  ·  these are the cubic theta coefficients that the openai/math proof reflects')
img.resize((S,int(H/SS)),Image.LANCZOS).save(out)
print(cnt)
