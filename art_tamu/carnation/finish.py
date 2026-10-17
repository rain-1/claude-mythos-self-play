"""Hero finish: stamen pearls (the three cycles, each at its pitch-class angle), note-name ring, caption."""
import numpy as np, math, argparse
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter
ap=argparse.ArgumentParser(); ap.add_argument('--npy'); ap.add_argument('--out'); ap.add_argument('--cy',type=float,default=0.10)
ap.add_argument('--rnames',type=float,default=0.875); ap.add_argument('--pr',type=float,default=0.016)
a=ap.parse_args()
img=np.load(a.npy); H,W=img.shape[:2]; sc=W/2; cx=W/2; cyp=H/2-a.cy*sc
FD='/usr/share/fonts/truetype/'
def pearl(img,x,y,rad,colr):
    x0,x1=int(x-rad*2.2),int(x+rad*2.6); y0,y1=int(y-rad*2.2),int(y+rad*2.8)
    yy,xx=np.mgrid[y0:y1,x0:x1].astype(np.float32)
    # soft lavender shadow, offset down-right
    sd=np.exp(-((xx-x-0.35*rad)**2+(yy-y-0.45*rad)**2)/(2*(0.75*rad)**2))
    patch=img[y0:y1,x0:x1]; patch*=1-0.30*sd[...,None]*(1-np.array([0.62,0.55,0.40]))*1.6
    u=(xx-x)/rad; v=(yy-y)/rad; rr=u*u+v*v; m=np.clip((1-rr)*rad*0.9,0,1)
    nz=np.sqrt(np.clip(1-rr,0,1)); L=np.array([-0.45,-0.6,0.66]); L/=np.linalg.norm(L)
    lam=np.clip(u*L[0]+v*L[1]+nz*L[2],0,1)
    c=np.array(colr,np.float32)
    body=c*(0.70+0.34*lam[...,None]) + 0.10*(1-nz)[...,None]*np.array([0.9,0.85,1.0])   # nacre rim sheen
    hx,hy=-0.36,-0.42; spec=np.exp(-((u-hx)**2+(v-hy)**2)/(2*0.13**2))
    body=body+(1-body)*0.85*spec[...,None]
    patch[:]=patch*(1-m[...,None])+np.clip(body,0,1)*m[...,None]
def P(n,rr):   # position of number n on the pitch-class circle at radius rr (fraction of half-width)
    t=math.log2(n)%1; return cx+rr*sc*math.sin(2*math.pi*t), cyp-rr*sc*math.cos(2*math.pi*t)
pr=a.pr*sc
MINT=(0.62,0.90,0.80); LIL=(0.80,0.72,0.97); PEA=(1.0,0.74,0.62)
# thread rings first (thin silk circles through the cycles)
im=Image.fromarray((np.clip(img,0,1)*255).astype(np.uint8)); d=ImageDraw.Draw(im,'RGBA')
for rr,cc in [(0.055,(176,150,220)),(0.10,(240,160,140))]:
    R=rr*sc; d.ellipse([cx-R,cyp-R,cx+R,cyp+R],outline=cc+(150,),width=max(2,int(W/1400)))
img=np.asarray(im).astype(np.float32)/255
pearl(img,cx,cyp,pr*1.25,MINT)
for n in (5,7): pearl(img,*P(n,0.055),pr*1.0,LIL)
for n in (17,25,37,55,41,61,91): pearl(img,*P(n,0.10),pr*0.9,PEA)
im=Image.fromarray((np.clip(img,0,1)*255).astype(np.uint8)); d=ImageDraw.Draw(im)
INK=(92,77,102)
fn=ImageFont.truetype(FD+'dejavu/DejaVuSerif.ttf',int(W*0.0135))
names=['C','C♯','D','E♭','E','F','F♯','G','A♭','A','B♭','B']
for j,nm in enumerate(names):
    t=j/12; x=cx+a.rnames*sc*math.sin(2*math.pi*t); y=cyp-a.rnames*sc*math.cos(2*math.pi*t)
    d.text((x,y),nm,font=fn,fill=INK,anchor='mm')
ft=ImageFont.truetype(FD+'dejavu/DejaVuSerif-Bold.ttf',int(W*0.026))
fi=ImageFont.truetype(FD+'liberation/LiberationSerif-Italic.ttf',int(W*0.0165))
fs=ImageFont.truetype(FD+'liberation/LiberationSerif-Italic.ttf',int(W*0.0128))
y0=int(H*0.895)
d.text((W/2,y0),'Twelve Petals, Then Fifty-Three',font=ft,fill=INK,anchor='mm')
d.text((W/2,y0+W*0.031),'every odd n below 2³², by the cycle that n → (3n−1)/2ᵛ falls into · one paper sheet per octave of n, angle = log₂ n mod 1, the pitch of n',font=fi,fill=INK,anchor='mm')
d.text((W/2,y0+W*0.053),'each edge traces how often n falls to the 17-cycle: 12 ripples within (3¹² ≈ 2¹⁹), 53 at the rim (3⁵³ ≈ 2⁸⁴) · the coral edge is 2²⁴, where 53 overtakes 12',font=fs,fill=INK,anchor='mm')
d.text((W/2,y0+W*0.071),'centre: the three cycles  1  ·  5, 7  ·  17, 25, 37, 55, 41, 61, 91 — each pearl at its own pitch',font=fs,fill=INK,anchor='mm')
im.save(a.out)
