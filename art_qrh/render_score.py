"""WHERE THE ZEROS MAY NOT GO: the strip 0.4 <= Re s <= 1.1 cut into isotropic lines like a score. Terraces of
log|zeta|, hue = arg zeta, zeros as coral beads on Re s = 1/2, the classical 1896 region as a plum thread, the
claimed walls at 11/12 and 7/8 as glass."""
import numpy as np, sys
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter, shift as nshift
from caption import caption, CORAL, INK, SOFT, F
src=sys.argv[1]; out=sys.argv[2]; nrows=int(sys.argv[3]); STEP=float(sys.argv[4]) if len(sys.argv)>4 else 0.25
D=np.load(src); Z=D['Z'].astype(complex); sig=D['sig']; t=D['t']; Hs,Wt=Z.shape
L=np.log(np.abs(Z)+1e-30); A=np.angle(Z)
lev=np.clip(np.floor(L/STEP),-14,10); hgt=(lev-lev.min()).astype(np.float32)
WHEEL=np.array([[0.98,0.60,0.66],[1.0,0.74,0.58],[1.0,0.88,0.56],[0.78,0.92,0.62],[0.58,0.90,0.80],[0.60,0.82,1.0],[0.70,0.72,1.0],[0.84,0.70,0.98],[0.98,0.60,0.66]],np.float32)
def wheel(h):
    h=(h%1)*(len(WHEEL)-1); i=np.minimum(h.astype(int),len(WHEEL)-2); f=(h-i)[...,None]; return WHEEL[i]*(1-f)+WHEEL[i+1]*f
col=wheel((A/(2*np.pi))%1)
depth=np.clip((lev.max()-lev)/(lev.max()-lev.min()),0,1); st=(0.22+0.78*depth**1.5)[...,None]
img=1-(1-col)*st
s=Hs/280
up=nshift(hgt,(2.0*s,1.5*s),order=0,mode='nearest'); d=np.clip(up-hgt,0,None); d=2.5*(1-np.exp(-d/2.5))
shadow=gaussian_filter(d,1.4*s)
img*=1-0.30*(1-np.exp(-shadow))[...,None]*np.array([0.55,0.50,0.30])*1.9
tl=nshift(hgt,(0.8*s,0.8*s),order=0,mode='nearest'); lit=1-np.exp(-np.clip(hgt-tl,0,None))
img=img+(1-img)*0.5*lit[...,None]
img=img[::-1]   # sigma upward within a row
rw=Wt//nrows; rh=Hs
PAPER=np.array([0.994,0.990,0.984])
mg=int(rw*0.035); gapr=int(rh*0.22); capH=int(rh*2.3)
W=rw+2*mg; H=mg+nrows*(rh+gapr)+capH
can=np.ones((H,W,3))*PAPER
for r in range(nrows):
    y0=mg+r*(rh+gapr); can[y0:y0+rh,mg:mg+rw]=img[:,r*rw:(r+1)*rw]
im=Image.fromarray((np.clip(can,0,1)*255).astype(np.uint8)).convert('RGBA'); d=ImageDraw.Draw(im,'RGBA')
px=rw/(t[rw]-t[0])     # pixels per unit (isotropic)
def XY(sv,tv):
    r=int(tv/(t[rw]-t[0])); r=min(r,nrows-1); x=mg+(tv-r*(t[rw]-t[0]))*px; y=mg+r*(rh+gapr)+rh-1-(sv-sig[0])/(sig[-1]-sig[0])*(rh-1)
    return x,y,r
zs=np.load('proto/zeros_mp120.npy'); fs=ImageFont.truetype(F+'LiberationSerif-Italic.ttf',int(rh*0.115))
for r in range(nrows):
    y0=mg+r*(rh+gapr)
    for sv,lab in ((11/12,'11/12'),(7/8,'7/8')):
        y=y0+rh-1-(sv-sig[0])/(sig[-1]-sig[0])*(rh-1)
        d.rectangle([mg,y-1.6*s,mg+rw,y+1.6*s],fill=(255,255,255,120)); d.line([mg,y,mg+rw,y],fill=(255,255,255,220),width=max(1,int(1.0*s)))
        d.line([mg,y+1.6*s,mg+rw,y+1.6*s],fill=(120,100,130,80),width=max(1,int(0.7*s)))
    y=y0+rh-1-(0.5-sig[0])/(sig[-1]-sig[0])*(rh-1); d.line([mg,y,mg+rw,y],fill=(92,77,102,70),width=max(1,int(0.7*s)))
    # classical boundary
    ta=np.linspace(max(3,r*(t[rw]-t[0])+1e-9),(r+1)*(t[rw]-t[0]),300); sb=1-1/(5.573412*np.log(ta))
    pts=[(mg+(tv-r*(t[rw]-t[0]))*px, y0+rh-1-(sv-sig[0])/(sig[-1]-sig[0])*(rh-1)) for tv,sv in zip(ta,sb)]
    d.line(pts,fill=(92,77,102,200),width=max(2,int(1.4*s)))
    # row label
    lab=f't = {r*(t[rw]-t[0]):.0f} … {(r+1)*(t[rw]-t[0]):.0f}'
    d.text((mg+rw*0.004,y0-fs.size*1.15),lab,font=fs,fill=SOFT+(255,))
rb=rh*0.028
for g in zs:
    if g>t[-1]: break
    x,y,r=XY(0.5,g); d.ellipse([x-rb*1.6,y-rb*1.6,x+rb*1.6,y+rb*1.6],fill=(255,255,255,170)); d.ellipse([x-rb,y-rb,x+rb,y+rb],fill=CORAL+(255,))
# sigma labels on the first row
y0=mg
for sv,lab in ((0.5,'½'),(7/8,'7/8'),(11/12,'11/12'),(1.0,'1')):
    y=y0+rh-1-(sv-sig[0])/(sig[-1]-sig[0])*(rh-1); tw=d.textlength(lab,font=fs); d.text((mg-tw-rh*0.03,y-fs.size/2),lab,font=fs,fill=INK+(255,))
im=im.convert('RGB')
caption(im,W/2,mg+nrows*(rh+gapr)+rh*0.05,'Where the Zeros May Not Go',
  f'the strip 0.4 ≤ Re s ≤ 1.1 of ζ(s), cut into {nrows} lines like a score and read left to right, {t[rw]-t[0]:.2f} units of height per line, true proportions',
  'terraces: log|ζ| in steps of ¼  ·  hue: arg ζ, which winds once round every zero  ·  coral beads: the zeros, all on Re s = ½  ·  plum thread: the 1896 zero-free region, 1 − 1/(5.573 log t)',
  W*0.024,align='center',line3='the two glass lines are the claimed walls, 11/12 (Part I) and 7/8 (Part II): openai/math family 003 claims no zero ever crosses them, at any height')
im.save(out); print(im.size)
