import numpy as np, sys, time
sys.path.insert(0,'/home/user/claude-mythos-self-play/art_i3k3')
from common import *
from scipy.ndimage import gaussian_filter
from PIL import Image, ImageDraw, ImageFont
t0=time.time()
OUT=2560; S=OUT
NL=6
roots_by_level={1:('N',np.roots(FC),None)}
for n in range(2,NL+1):
    A,B=basin_split(n); roots_by_level[n]=('AB',A,B)
vmin,vmax=-1.78,2.58
img=np.zeros((S,S,3),np.float32)
ytop,ybot=0.16*S,0.95*S
def yof(t): return ytop+(ybot-ytop)*t
def tlev(n): return (n-1)/(NL-1)
tf=tlev(2)*0.55                     # fork position
trunk_x=0.5*S
def gg(t):
    tt=np.clip((t-tf)/(1-tf),0,1)
    return trunk_x+(0.255*S-trunk_x)*tt, (0.012+0.105*tt)*S
def cg(t):
    tt=np.clip((t-tf)/(1-tf),0,1)
    return trunk_x+(0.725*S-trunk_x)*tt, (0.024+0.21*tt)*S

# ---------- river envelopes (continuous) ----------
xs=np.arange(S)[None,:]
yy=np.arange(S)[:,None]
tt=(yy-ytop)/(ybot-ytop)
inside=(tt>=0)&(tt<=1.001)
# trunk region tt<=tf
for yi in range(S):
    t=(yi-ytop)/(ybot-ytop)
    if t<-0.02 or t>1.02: continue
    ramp=0.06+0.34*np.clip(t,0,1)
    row=np.zeros((S,3),np.float32)
    if t<=tf:
        c=trunk_x; h=0.018*S
        b=np.exp(-((np.arange(S)-c)/h)**2)
        for i in range(3): row[:,i]+=b*NEUT[i]*0.16
    else:
        c1,h1=gg(t); c2,h2=cg(t)
        b1=np.exp(-((np.arange(S)-c1)/h1)**2); b2=np.exp(-((np.arange(S)-c2)/h2)**2)
        for i in range(3): row[:,i]+=b1*GOLD[i]*0.14*ramp+b2*CYAN[i]*0.14*ramp
    img[yi]+=row

# ---------- flowing streamlines ----------
rng=np.random.default_rng(3)
def stream(geom,col,nlines,amp):
    for k in range(nlines):
        off=(k/(nlines-1)-0.5)*1.7
        ph=rng.uniform(0,6.28); fr=rng.uniform(1.5,3.0)
        ts=np.linspace(tf,1,400)
        for t in ts:
            c,h=geom(t)
            wig=0.12*np.sin(fr*t*6.28+ph)
            x=c+(off+wig)*h; y=yof(t)
            xi,yi=int(x),int(y)
            if 0<=xi<S and 0<=yi<S:
                img[yi,xi]+=col*amp
stream(gg,GOLD,40,0.09); stream(cg,CYAN,54,0.09)

# ---------- sediment strata: actual roots ----------
def place(vals,c,h,y,col,a,rad=2):
    for v in vals:
        x=c+(np.clip((v-vmin)/(vmax-vmin),0,1)-0.5)*2*h
        xi,yi=int(x),int(y)
        if rad<=xi<S-rad and rad<=yi<S-rad:
            for dx in range(-rad,rad+1):
                for dy in range(-rad,rad+1):
                    img[yi+dy,xi+dx]+=col*a*np.exp(-(dx*dx+dy*dy)/(rad*0.7))
place([r.real for r in roots_by_level[1][1]],trunk_x,0.018*S,yof(tlev(1)),NEUT*1.15,1.2,3)
for n in range(2,NL+1):
    _,A,B=roots_by_level[n]; t=tlev(n)
    c1,h1=gg(t); c2,h2=cg(t)
    place([r.real for r in A],c1,h1,yof(t),GOLD*1.2+0.12,1.05,2)
    place([r.real for r in B],c2,h2,yof(t),CYAN*1.15+0.12,1.05,2)

# spring glow at the fork
def glow(x,y,col,amp,rad):
    for dx in range(-rad,rad+1):
        for dy in range(-rad,rad+1):
            xi,yi=int(x+dx),int(y+dy)
            if 0<=xi<S and 0<=yi<S:
                img[yi,xi]+=col*amp*np.exp(-(dx*dx+dy*dy)/(rad*rad*0.25))
glow(trunk_x,yof(tf),np.array([1,0.95,0.8]),0.9,26)

# bloom
lum=img.mean(2); mask=np.clip((lum-0.4)/0.6,0,1)[...,None]*img
def bloom(a,sig):
    ds=max(1,int(sig/6)); sm=a[::ds,::ds]
    b=gaussian_filter(sm,(sig/ds,sig/ds,0))
    return np.repeat(np.repeat(b,ds,0),ds,1)[:a.shape[0],:a.shape[1]]
img=img+0.6*bloom(mask,60)+0.35*bloom(mask,18)
img=filmic(img,k=1.7,g=0.9)

# ---------- text AFTER glow ----------
im=Image.fromarray((np.clip(img,0,1)*255).astype('uint8'))
d=ImageDraw.Draw(im)
FB=lambda s:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',s)
F=lambda s:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',s)
gcol=(255,180,70); ccol=(70,190,255); ncol=(220,210,180)
d.text((70,55),"THE CERTIFICATE",font=FB(58),fill=(235,225,200))
d.text((70,125),"f(x) = x³ − x² − 3x + 1  is irreducible — yet every iterate fⁿ splits.",font=F(30),fill=(180,175,160))
d.text((70,163),"fⁿ = (deg 3ⁿ⁻¹) · (deg 2·3ⁿ⁻¹).  One spring, forked once, two eternal rivers.",font=F(30),fill=(150,150,140))
degA=[3,9,27,81,243]; degB=[6,18,54,162,486]
for i,n in enumerate(range(2,NL+1)):
    t=tlev(n); y=yof(t)
    c1,h1=gg(t); c2,h2=cg(t)
    d.text((c1-h1-70,y-16),str(degA[i]),font=FB(30),fill=gcol,anchor="ra")
    d.text((c2+h2+18,y-16),str(degB[i]),font=FB(30),fill=ccol,anchor="la")
d.text((trunk_x+30,yof(tlev(1))-14),"3",font=FB(30),fill=ncol,anchor="la")
d.text((trunk_x+40,yof(tf)-70),"the kind breaks",font=F(26),fill=(230,220,190),anchor="ma")
im.save('/home/user/claude-mythos-self-play/art_i3k3/panelB_certificate.png')
print("saved B",time.time()-t0)
