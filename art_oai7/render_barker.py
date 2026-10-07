"""openai/math family 179: binary sequences with all aperiodic autocorrelation sidelobes in {-1,0,1} exist only at
n = 2,3,4,5,7,11,13 (odd n classical, Turyn–Storer; even n via the claimed circulant Hadamard theorem)."""
import numpy as np, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from caption import caption, CORAL, INK, SOFT, F
S=int(sys.argv[1]); out=sys.argv[2]
B={2:'++',3:'++-',4:'++-+',5:'+++-+',7:'+++--+-',11:'+++---+--+-',13:'+++++--++-+-+'}
SS=2; W=S*SS; H=int(W*1.05)
PAPER=(252,251,249)
WARM=[(250,150,160),(255,180,140),(253,210,120)]; COOL=[(140,200,240),(150,165,240),(190,160,240)]
img=Image.new('RGB',(W,H),PAPER); sh=Image.new('L',(W,H),0); sd=ImageDraw.Draw(sh)
beads=[]  # (x,y,r,color,kind)
rowh=H*0.080; y0=H*0.09; pitch=W*0.029
def mix(P,h):
    h=h*(len(P)-1); i=min(int(h),len(P)-2); f=h-i
    return tuple(int(P[i][k]*(1-f)+P[i+1][k]*f) for k in range(3))
def lighten(c,f): return tuple(int(255-(255-v)*f) for v in c)
def darken(c,f): return tuple(int(v*f) for v in c)
fl=ImageFont.truetype(F+'LiberationSerif-Italic.ttf',int(W*0.017))
labels=[]
for k,(n,s) in enumerate(B.items()):
    v=np.array([1 if ch=='+' else -1 for ch in s]); y=y0+k*rowh
    # sequence beads (left block, right-aligned at centre-left)
    xr=W*0.31+(n-1)*pitch/2
    for i,x in enumerate(v):
        h=i/max(n-1,1); cx=xr-(n-1-i)*pitch; col=mix(WARM,h) if x>0 else mix(COOL,h)
        beads.append((cx,y,pitch*0.40,col,'b'))
    # autocorrelation C_k, k=-(n-1)..(n-1), centred at right block
    xc=W*0.745; ap=W*0.0185
    for kk in range(-(n-1),n):
        c=int(np.dot(v[:n-abs(kk)],v[abs(kk):]))
        cx=xc+kk*ap
        if kk==0: beads.append((cx,y,pitch*0.20+pitch*0.30*np.sqrt(n/13),CORAL,'b'))
        elif c==0: beads.append((cx,y,pitch*0.12,(225,215,225),'ring'))
        else: beads.append((cx,y-(pitch*0.18 if c>0 else -pitch*0.18),pitch*0.13,(250,170,160) if c>0 else (150,175,240),'b'))
    labels.append((W*0.035,y,f'n = {n}'))
# 4x4 circulant Hadamard, bottom
row=np.array([-1,1,1,1]); M=np.array([np.roll(row,i) for i in range(4)])
hx,hy=W*0.5,y0+7*rowh+H*0.07; hp=pitch*1.15
for i in range(4):
    for j in range(4):
        cx=hx+(j-1.5)*hp; cy=hy+(i-1.5)*hp; col=[(250,150,160),(255,180,140),(253,210,120),(250,150,160)][(j-i)%4] if M[i,j]>0 else (150,165,240)
        beads.append((cx,cy,hp*0.40,col,'b'))
for (x,y,r,c,kind) in beads:
    if kind=='b': sd.ellipse([x-r+r*0.18,y-r+r*0.28,x+r+r*0.18,y+r+r*0.28],fill=120)
sh=sh.filter(ImageFilter.GaussianBlur(W*0.004))
a=np.asarray(img).astype(float)*(1-0.25*np.asarray(sh)[...,None]/255*np.array([0.9,0.9,0.5]))
img=Image.fromarray(a.astype(np.uint8)); d=ImageDraw.Draw(img)
for (x,y,r,c,kind) in beads:
    if kind=='ring':
        d.ellipse([x-r,y-r,x+r,y+r],outline=c,width=max(2,int(r*0.3))); continue
    d.ellipse([x-r,y-r,x+r,y+r],fill=darken(c,0.92))
    d.ellipse([x-r*0.9,y-r*0.92,x+r*0.86,y+r*0.84],fill=c)
    d.ellipse([x-r*0.55,y-r*0.6,x-r*0.12,y-r*0.2],fill=lighten(c,0.35))
for x,y,t in labels:
    d.text((x,y-fl.size*0.6),t,font=fl,fill=SOFT)
fs=ImageFont.truetype(F+'LiberationSerif-Italic.ttf',int(W*0.014))
for t,x in (('the sequence',W*0.31),('its echoes: one loud peak, every other overlap −1, 0 or +1',W*0.75)):
    tw=d.textlength(t,font=fs); d.text((x-tw/2,y0-rowh*0.75),t,font=fs,fill=SOFT)
t='the 4 × 4 circulant Hadamard matrix: the only one bigger than 1 × 1'
tw=d.textlength(t,font=fs); d.text((hx-tw/2,hy+2.3*hp),t,font=fs,fill=SOFT)
caption(img,W/2,hy+2.3*hp+H*0.045,'Seven Lengths and No More',
  'binary sequences whose echoes never exceed one exist only at lengths 2, 3, 4, 5, 7, 11 and 13',
  'warm = +1, cool = −1  ·  coral: the peak, equal to the length; the whispers beside it are the whole point',
  W*0.042,align='center',line3='odd lengths: Turyn–Storer 1961  ·  even lengths need circulant Hadamard matrices, which openai/math family 179 claims exist only in orders 1 and 4')
img.resize((S,int(H/SS)),Image.LANCZOS).save(out)
