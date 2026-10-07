"""SIX COLOURS OF EVERY NUMBER: hexagon mosaic of the Eisenstein integers n, cell colour = the sixth root of unity
mu(n) (u/n)_6 (the summand of the row u of the family A_u), paper where it is 0."""
import numpy as np, sys, pickle, math
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from eis import norm, primary, mulw, tocx
from caption import caption, CORAL, INK, SOFT, F
S=int(sys.argv[1]); out=sys.argv[2]; ua,ub=int(sys.argv[3]),int(sys.argv[4]); R=float(sys.argv[5])
T=pickle.load(open('tables_30000.pkl','rb'))
prim=T['prim']; mu=T['mu']; fac=T['fac']; pidx=T['pidx']; rows=T['rows']; sym=T['sym']
j=rows.index((ua,ub))
val={}   # primary (a,b) -> k in 0..5 or -1
for i,(a,b,N) in enumerate(prim):
    if mu[i]==0: val[(a,b)]=-1; continue
    k=0; ok=True
    for p,e in fac[i].items():
        s=sym[pidx[p],j]
        if s<0: ok=False; break
        k+=s
    val[(a,b)]=-1 if not ok else (k+(3 if mu[i]<0 else 0))%6
SS=2; W=S*SS; H=int(W*1.13); cx=W/2; cy=W*0.49; sc=(W*0.46)/R
HUES=np.array([[250,150,160],[255,180,130],[253,214,110],[160,222,150],[120,205,232],[160,160,240]],float)/255   # zeta6^0..5
PAPER=np.array([0.994,0.990,0.984])
img=Image.new('RGB',(W,H),tuple(int(v*255) for v in PAPER)); d=ImageDraw.Draw(img)
def hexagon(x,y,r,ang=0):
    return [(x+r*math.cos(ang+math.pi/6+k*math.pi/3),y+r*math.sin(ang+math.pi/6+k*math.pi/3)) for k in range(6)]
cells=[]
Ri=int(R)+1
for a in range(-Ri,Ri+1):
    for b in range(-Ri,Ri+1):
        N=norm(a,b)
        if N==0 or N>R*R: continue
        z=tocx(a,b); pr=primary(a,b)
        k=-1 if pr is None else val.get(pr,-1)
        cells.append((z,k,N))
hr=sc*0.5/math.cos(math.pi/6)*0.94   # hexagon circumradius (cells touch at 0.94)
sh=Image.new('L',(W,H),0); sd=ImageDraw.Draw(sh)
for z,k,N in cells:
    if k<0: continue
    x,y=cx+z.real*sc,cy-z.imag*sc
    sd.polygon(hexagon(x+hr*0.22,y+hr*0.30,hr),fill=120)
sh=sh.filter(ImageFilter.GaussianBlur(hr*0.35))
a_=np.asarray(img).astype(float)*(1-0.22*np.asarray(sh)[...,None]/255*np.array([0.9,0.9,0.55]))
img=Image.fromarray(a_.astype(np.uint8)); d=ImageDraw.Draw(img)
for z,k,N in cells:
    x,y=cx+z.real*sc,cy-z.imag*sc
    if k<0:
        d.ellipse([x-hr*0.10,y-hr*0.10,x+hr*0.10,y+hr*0.10],fill=(236,230,234)); continue
    c=HUES[k]
    col=tuple(int(v*255) for v in c)
    d.polygon(hexagon(x,y,hr),fill=tuple(int(v*0.90*255) for v in c))
    d.polygon(hexagon(x-hr*0.05,y-hr*0.07,hr*0.86),fill=col)
    d.polygon(hexagon(x-hr*0.22,y-hr*0.26,hr*0.30),fill=tuple(int(255-(255-v*255)*0.45) for v in c))
# the row u itself, as a coral bead
zu=tocx(ua,ub); x,y=cx+zu.real*sc,cy-zu.imag*sc; r=hr*0.55
d.ellipse([x-r*1.5,y-r*1.5,x+r*1.5,y+r*1.5],fill=(255,255,255)); d.ellipse([x-r,y-r,x+r,y+r],fill=CORAL)
# colour key: the six roots of unity as a ring of six hexes, labelled
fs=ImageFont.truetype(F+'LiberationSerif-Italic.ttf',int(W*0.016))
kx,ky,kr=W*0.90,W*0.90,W*0.045
names=['1','ζ₆','ζ₆²','−1','ζ₆⁴','ζ₆⁵']
for kk in range(6):
    ang=kk*math.pi/3; px,py=kx+kr*math.cos(ang),ky-kr*math.sin(ang); c=HUES[kk]
    d.polygon(hexagon(px,py,W*0.016),fill=tuple(int(v*255) for v in c))
    tw=d.textlength(names[kk],font=fs); d.text((kx+kr*1.55*math.cos(ang)-tw/2,ky-kr*1.55*math.sin(ang)-fs.size/2),names[kk],font=fs,fill=SOFT)
t='μ(n)·(u/n)₆'; tw=d.textlength(t,font=fs); d.text((kx-tw/2,ky+kr*1.95),t,font=fs,fill=SOFT)
nz=sum(1 for _,k,_ in cells if k>=0)
caption(img,W/2,W*0.985,'Six Colours of Every Number',
  f'every Eisenstein integer n with |n| ≤ {int(R)} as a hexagon coloured by μ(n)·(u/n)₆, the summand of the row u = {ua} of the family A_u; paper where μ(n) = 0',
  f'the six petals of a flower are the six unit multiples of one n, which the sum counts once  ·  {nz:,} coloured cells  ·  coral: u itself  ·  key: the six sixth roots of unity',
  W*0.033,align='center',line3='openai/math family 003 embeds the Möbius sum in this family of sextic twists; Poisson summation over u turns them into cubic Gauss sums, the coefficients of Kubota’s theta function')
img=img.resize((S,int(H/SS)),Image.LANCZOS); img.save(out)
cnt=np.bincount([k for _,k,_ in cells if k>=0],minlength=6); print('cells',len(cells),'nonzero',cnt.sum(),cnt)
