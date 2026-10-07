"""WHERE THE ZEROS MAY NOT GO: log|zeta| over the strip as paper terraces, hue = arg zeta; zeros as coral beads;
the classical 1896 region (Mossinghoff-Trudgian constant) as a plum thread; the claimed walls at 11/12 and 7/8 as glass."""
import numpy as np, sys
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter, shift as nshift
from caption import caption, CORAL, INK, SOFT, F
src=sys.argv[1]; out=sys.argv[2]
D=np.load(src); Z=D['Z'].astype(complex); sig=D['sig']; t=D['t']; H,W=Z.shape
L=np.log(np.abs(Z)+1e-30); A=np.angle(Z)
STEP=float(sys.argv[3]) if len(sys.argv)>3 else 0.25
lev=np.clip(np.floor(L/STEP),-14,10)           # terrace index
hgt=(lev-lev.min()).astype(np.float32)
WHEEL=np.array([[0.98,0.60,0.66],[1.0,0.74,0.58],[1.0,0.88,0.56],[0.78,0.92,0.62],[0.58,0.90,0.80],[0.60,0.82,1.0],[0.70,0.72,1.0],[0.84,0.70,0.98],[0.98,0.60,0.66]],np.float32)
def wheel(h):
    h=(h%1)*(len(WHEEL)-1); i=np.minimum(h.astype(int),len(WHEEL)-2); f=(h-i)[...,None]; return WHEEL[i]*(1-f)+WHEEL[i+1]*f
hue=(A/(2*np.pi))%1
col=wheel(hue)
# strength: deep terraces saturated, high ground pale
depth=np.clip((lev.max()-lev)/(lev.max()-lev.min()),0,1)
st=(0.25+0.75*depth**1.6)[...,None]
PAPER=np.array([0.994,0.990,0.984],np.float32)
img=1-(1-col)*st
# shading from the height field (light from upper-left)
s=W/1000
up=nshift(hgt,(2.0*s,1.5*s),order=0,mode='nearest'); d=np.clip(up-hgt,0,None); d=2.5*(1-np.exp(-d/2.5))
shadow=gaussian_filter(d,1.4*s)
img*=1-0.30*(1-np.exp(-shadow))[...,None]*np.array([0.55,0.50,0.30])*1.9
tl=nshift(hgt,(0.8*s,0.8*s),order=0,mode='nearest'); lit=1-np.exp(-np.clip(hgt-tl,0,None))
img=img+(1-img)*0.5*lit[...,None]
img=img[::-1]   # t upward
im=Image.fromarray((np.clip(img,0,1)*255).astype(np.uint8)).convert('RGBA'); d=ImageDraw.Draw(im,'RGBA')
def X(sv): return (sv-sig[0])/(sig[-1]-sig[0])*(W-1)
def Y(tv): return (H-1)-(tv-t[0])/(t[-1]-t[0])*(H-1)
# glass walls
for sv,lab in ((11/12,'11/12'),(7/8,'7/8')):
    x=X(sv); d.rectangle([x-2.2*s,0,x+2.2*s,H],fill=(255,255,255,110)); d.line([x,0,x,H],fill=(255,255,255,200),width=max(1,int(1.2*s)))
    d.line([x+2.2*s,0,x+2.2*s,H],fill=(120,100,130,70),width=max(1,int(0.8*s)))
# classical region boundary 1 - 1/(5.573412 log t), t >= 3
tt=np.linspace(3,t[-1],400); sb=1-1/(5.573412*np.log(tt))
d.line([(X(a),Y(b)) for a,b in zip(sb,tt)],fill=(92,77,102,210),width=max(2,int(1.6*s)))
# critical line + zeros
d.line([X(0.5),0,X(0.5),H],fill=(92,77,102,60),width=max(1,int(0.8*s)))
zs=np.load('proto/zeros_mp120.npy'); r=4.2*s
for g in zs:
    if g>t[-1]: break
    x,y=X(0.5),Y(g); d.ellipse([x-r*1.6,y-r*1.6,x+r*1.6,y+r*1.6],fill=(255,255,255,170)); d.ellipse([x-r,y-r,x+r,y+r],fill=CORAL+(255,))
fs=ImageFont.truetype(F+'LiberationSerif-Italic.ttf',int(26*s))
for sv,lab in ((0.5,'½'),(7/8,'7/8'),(11/12,'11/12'),(1.0,'1')):
    tw=d.textlength(lab,font=fs); d.text((X(sv)-tw/2,H-fs.size*1.5),lab,font=fs,fill=INK+(255,))
im=im.convert('RGB'); im.save(out); print(im.size)
