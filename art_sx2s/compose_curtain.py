import numpy as np, sys
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter, zoom
from caption import caption, CORAL, INK, SOFT, F
var=sys.argv[1]; scale=float(sys.argv[2]) if len(sys.argv)>2 else 1.0; out=sys.argv[3] if len(sys.argv)>3 else f'proto/cc_{var}.png'
D=np.load('cur_final.npz'); cur=D['cur']; law=D['law']
W,H=int(4096*scale),int(2560*scale)
PAPER=np.array([0.994,0.990,0.984])
def P(*c): return np.array(c)
if var=='a':
    W1,W2=P(1.0,0.86,0.62),P(0.98,0.55,0.64); C1,C2=P(0.66,0.90,0.92),P(0.66,0.64,1.0); dens=0.85
else:
    W1,W2=P(1.0,0.76,0.62),P(0.98,0.52,0.66); C1,C2=P(0.60,0.82,1.0),P(0.76,0.64,1.0); dens=0.8
mx,my=int(130*scale),int(130*scale); capH=int(470*scale); gapc=int(70*scale)
cw=int((W-2*mx-gapc)*0.85); pw=W-2*mx-gapc-cw; ch=H-my-capH
def fit(a,h,w): 
    return np.asarray(Image.fromarray(a.astype(np.float32)).resize((w,h),Image.BOX))
c=fit(cur,ch,cw); l=fit(law,ch,pw)
v=np.tanh(c/3.2); m=np.abs(v)[...,None]
tint=np.where(v[...,None]>0,W1*(1-m)+W2*m,C1*(1-m)+C2*m)
img=PAPER*np.exp(np.log(np.clip(tint,0.05,1))*dens*m**0.9)
dl=np.clip(gaussian_filter(l,1.2*scale),0,1)**0.45
LIL=P(0.80,0.70,0.98); pan=PAPER*np.exp(np.log(LIL)*2.2*dl[...,None])
can=np.ones((H,W,3))*PAPER
rng=np.random.default_rng(1); can*=1-0.010*gaussian_filter(rng.standard_normal((H,W)),1)[...,None]
can[my:my+ch,mx:mx+cw]=img; can[my:my+ch,mx+cw+gapc:mx+cw+gapc+pw]=pan
im=Image.fromarray((np.clip(can,0,1)*255).astype(np.uint8)); d=ImageDraw.Draw(im)
fi=ImageFont.truetype(F+'LiberationSerif-Italic.ttf',int(44*scale))
for xv,lab in ((0,'0'),(0.5,'½'),(1,'1'),(1.5,'3/2'),(2,'2')):
    X=mx+xv/2*cw; d.line([X,my+ch+8*scale,X,my+ch+30*scale],fill=CORAL if xv==1 else SOFT,width=max(1,int(4*scale)))
    tw=d.textlength('x = '+lab if xv==1 else lab,font=fi); d.text((X-tw/2,my+ch+36*scale),'x = '+lab if xv==1 else lab,font=fi,fill=CORAL if xv==1 else SOFT)
X=mx+cw/2; r=9*scale; d.ellipse([X-r,my+ch-r*3,X+r,my+ch-r],fill=CORAL)
fs=ImageFont.truetype(F+'LiberationSerif-Italic.ttf',int(38*scale))
px=mx+cw+gapc+pw/2
for txt,yy in (('h = 1',my-56*scale),('law of Q, row by row: −9 to 9',my+ch+36*scale)):
    tw=d.textlength(txt,font=fs); d.text((px-tw/2,yy),txt,font=fs,fill=SOFT)
d.text((mx,my-56*scale),'h = 1  (large steps)',font=fs,fill=SOFT)
t2='h = 4·10⁻⁴'; d.text((mx-d.textlength(t2,font=fs)-14*scale,my+ch-44*scale),'',font=fs,fill=SOFT)
caption(im,W/2,my+ch+120*scale,'The Curtain Keeps One Law',
  'Riemann’s function R(x) = Σ sin(πn²x)/n²: its steps Q = (R(x+h) − R(x)) / h¾, x across, h shrinking downward from 1 to 0.0003',
  'warm = rising, cool = falling  ·  right: the law of Q for every row settles to one shape, variance 4.65, tails ~ 10/t⁴',
  100*scale,align='center',line3='coral: x = 1, where R has a slope (Gerver 1970) and the curtain goes still')
im.save(out)
