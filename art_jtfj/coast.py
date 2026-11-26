"""THE STRAIGHT COAST — hero.  Cut-paper bathymetric chart of h = log|E(s)/E(1-s)|, E(s)=M^(s-1) sigma_{-s}(m), at M = sqrt(m).
usage: coast.py W out.png [t0]"""
import sys, json, numpy as np
from scipy import ndimage as ndi
from PIL import Image, ImageDraw, ImageFont
from papercut import Box, rgb, mix, SERIF, SERIF_I, SERIF_B
from core import *
W=int(sys.argv[1]); OUT=sys.argv[2]; T0=float(sys.argv[3]) if len(sys.argv)>3 else 0.6
m=int(sys.argv[4]) if len(sys.argv)>4 else 6983776800; L=float(sys.argv[5]) if len(sys.argv)>5 else 4.0; VE=float(sys.argv[6]) if len(sys.argv)>6 else 1.0; M=np.sqrt(m)
B=Box(W,seed=3,base='#070a1c'); u=B.u
mx=int(0.075*W); x0,x1,y0,y1=mx,W-mx,mx,int(W-0.205*W); ww=x1-x0; wh=y1-y0
ppu=ww/L; yc=y0+0.5*wh
X,Y=B.grid()
t=T0+(X[0]-x0+0.5)/ppu; TA,TB=T0,T0+L; sg=0.5-(Y[:,0]-yc+0.5)/(ppu*VE)
h,ph=logF_fast(sg[:,None]+1j*t[None,:],m,M)
h=np.nan_to_num(h,posinf=40,neginf=-40).astype(np.float32); ph=ph.astype(np.float32)
P=0.5*np.log(m); gy,gx=np.gradient(np.clip(h,-2.2*P,2.2*P)); g=np.maximum(np.hypot(gx,gy),1e-4)
def above(lev): return np.clip((h-lev)/g+0.5,0,1)
# ---------- the stack of sheets: lowest first ----------
fr=np.array([0.0,0.06,0.14,0.24,0.36,0.50,0.64,0.80,1.20,1.42,1.68])
sea_lv=list(-fr[:0:-1]*P)
sea_col=['#0a0e26','#0d1230','#111840','#151c46','#1b2658','#22326c','#2b4483','#3a5d9b','#5681b3','#86abc8','#bcd3d6']
land_lv=list(fr*P)
land_col=['#f6ecd2','#f5dfbd','#f1cba6','#eab39c','#de9d9a','#c98a9c','#ad7a9e','#8f6c9c','#6f5c93','#514c86','#f6ecd2']
B.img[:]=rgb(sea_col[0])*B.fibre(1.0,0)[...,None]; B.z[:]=-len(sea_lv)
for i,lv in enumerate(sea_lv):
    B.lay(above(lv),rgb(sea_col[i+1]),z=-len(sea_lv)+i+1,shadow=0.50,reach=7.0,soft=2.6,edge=0.8,k=i,ao=0.16,ao_soft=10)
    print('sea',i,flush=True)
for i,lv in enumerate(land_lv):
    B.lay(above(lv),rgb(land_col[i]),z=i+1,shadow=0.52 if i else 0.60,reach=7.0 if i else 9.0,soft=2.6,edge=0.9,k=i+2,ao=0.18,ao_soft=10)
    print('land',i,flush=True)
ZTOP=len(land_lv)+1
# ---------- red threads: arg F = pi, from each pit to its own mountain ----------
zz=np.exp(1j*ph); zy,zx=np.gradient(zz); gp=np.maximum(np.hypot(np.abs(zx),np.abs(zy)),1e-4)
d=np.abs(np.angle(-zz))/gp            # pixel distance to the curve arg F = pi
thr=np.clip(2.1*u-d+0.5,0,1)*(np.abs(h)<1.9*P)
red=rgb('#d8362b')
B.lay(thr,red,z=ZTOP+1,shadow=0.42,reach=1.3,soft=1.2,edge=0.5,tex=0.3,contact=0.0)
# pins at pits and peaks, lights on the shore
pt=pits(m,TA,TB); lt,(tt,yy_)=lights(m,M,TA,TB)
def px(tv): return x0+(tv-T0)*ppu
ypit=yc+0.5*ppu*VE; ypk=yc-0.5*ppu*VE
pin=np.zeros((W,W),np.float32); lamp=np.zeros((W,W),np.float32); halo=np.zeros((W,W),np.float32)
for tv,p in pt:
    for yv in (ypit,ypk):
        pin=np.maximum(pin,np.clip(3.4*u-np.hypot(X-px(tv),Y-yv)+0.5,0,1))
for tv in lt:
    r=np.hypot(X-px(tv),Y-yc); halo=np.maximum(halo,np.clip(19*u-r+0.5,0,1)); lamp=np.maximum(lamp,np.clip(11*u-r+0.5,0,1))
B.lay(pin,rgb('#f6ecd2'),z=ZTOP+2,shadow=0.5,reach=1.5,soft=1.2,edge=1.0,tex=0.3)
B.lay(halo,rgb('#f6ecd2'),z=ZTOP+2,shadow=0.55,reach=2.2,soft=1.6,edge=1.0,tex=0.5,k=1)
B.lay(lamp,red,z=ZTOP+3,shadow=0.45,reach=1.0,soft=1.0,edge=0.9,tex=0.3)
# ---------- life and weather: boats, a compass, two clouds ----------
def tri(pts): return B.poly(pts)
boats=[(0.30,0.90,1.9,0.25),(0.50,0.80,1.3,-0.2),(0.93,0.90,1.5,0.5)]
hull=np.zeros((W,W),np.float32); sail=np.zeros((W,W),np.float32)
for bx,by,sc,rot in boats:
    cx=x0+bx*ww; cy=y0+by*wh; s=26*u*sc; c,sn=np.cos(rot),np.sin(rot)
    def R(pts): return [(cx+s*(a*c-b*sn),cy+s*(a*sn+b*c)) for a,b in pts]
    hull=np.maximum(hull,tri(R([(-1.0,0.0),(0.0,-0.34),(1.25,0.0),(0.0,0.34)])))
    sail=np.maximum(sail,tri(R([(-0.55,0.0),(0.55,0.0),(0.1,-0.95)])))
B.lay(hull,rgb('#0d1230'),z=-len(sea_lv)+7,shadow=0.45,reach=3,soft=2,edge=0.8,tex=0.4)
B.lay(sail,rgb('#f6ecd2'),z=-len(sea_lv)+10,shadow=0.5,reach=2.2,soft=1.8,edge=1.0,tex=0.5)
# compass rose (cream and dusk) in the abyss
cx=x0+0.085*ww; cy=y0+0.875*wh; Rr=0.052*ww
ang=np.arctan2(Y-cy,X-cx); rr=np.hypot(X-cx,Y-cy)
def star(n,R,r0,rot=0.0):
    a=(ang-rot)%(2*np.pi/n); a=np.minimum(a,2*np.pi/n-a); half=np.pi/n
    # star radius profile: line between tip (angle 0,R) and notch (angle half,r0)
    x=rr*np.cos(a); yv=rr*np.sin(a); nx=r0*np.sin(half); ny=R-r0*np.cos(half); dd=((R-x)*nx-yv*ny)/np.hypot(nx,ny)
    return np.clip(dd+0.5,0,1)
B.lay(np.clip(Rr*0.80-rr+0.5,0,1)*np.clip(rr-Rr*0.74+0.5,0,1),rgb('#86abc8'),z=-3,shadow=0.4,reach=2,soft=1.5,tex=0.4)
B.lay(star(4,Rr*0.62,Rr*0.13,np.pi/4),rgb('#5681b3'),z=-2,shadow=0.45,reach=2,soft=1.5,tex=0.4)
B.lay(star(4,Rr,Rr*0.15,0.0),rgb('#f6ecd2'),z=-1,shadow=0.5,reach=2.5,soft=1.8,tex=0.5)
# clouds: the highest sheets
def noise1(sig,seed):
    r=np.random.default_rng(seed).standard_normal((W//8+2,W//8+2)).astype(np.float32); r=ndi.gaussian_filter(r,sig*u/8,mode='wrap'); r/=r.std()
    return ndi.zoom(r,8,order=1)[:W,:W]
def cloud(cx,cy,sx,sy,seed,puffs=7):
    rng=np.random.default_rng(seed); f=np.full((W,W),-1e9,np.float32)
    for k in range(puffs):
        ox=cx+rng.uniform(-1,1)*sx; oy=cy+rng.uniform(-0.45,0.45)*sy; r=sy*rng.uniform(0.55,1.0)*(1-0.45*abs(ox-cx)/sx)
        f=np.maximum(f,r-np.hypot(X-ox,(Y-oy)*1.25))
    f=np.minimum(f,(cy+0.42*sy)-Y+0*X) if False else f
    return np.clip(f+2.0*u*noise1(10,seed+5)+0.5,0,1)
for (cxf,cyf,sxf,syf,sd) in [(0.80,0.105,0.115,0.050,11),(0.70,0.87,0.085,0.036,23),(0.10,0.075,0.060,0.030,37)]:
    cm=cloud(x0+cxf*ww,y0+cyf*wh,sxf*ww,syf*wh,sd)
    B.lay(cm,rgb('#fbf6e8'),z=ZTOP+34,shadow=0.30,reach=4.2,soft=2.2,edge=0.8,tex=0.6,k=3,contact=0.0)
# ---------- mat, tide strip, captions ----------
B.mat(x0,y0,x1,y1,colour='#efe6d0',z=ZTOP+60)
# tide strip: an engraved label pasted on the mat, aligned with the chart
sy0=y1+int(0.020*W); sy1=sy0+int(0.056*W)
B.lay(B.rect(x0,sy0,x1,sy1),rgb('#f8f1dd'),z=ZTOP+61,shadow=0.35,reach=1.2,soft=1.0,edge=0.8,tex=0.7,k=2)
env=2*np.abs(Aprod(0.5+1j*t,m)); f=2*np.real(np.exp(1j*t*np.log(M))*Aprod(0.5+1j*t,m))
win=(t>=TA)&(t<=TB); sc_=np.percentile(np.abs(f[win]),88); f=np.tanh(0.9*f/sc_); amp=0.44*(sy1-sy0); ym=0.5*(sy0+sy1)
col=ym-amp*f                                  # curve y per pixel column
pitch=5.0*u; dcol=np.abs((X-x0)/pitch-np.round((X-x0)/pitch))*pitch
inside=((Y-ym)*(Y-col[None,:])<=0)
frac=np.clip(np.abs(Y-ym)/(np.abs(col[None,:]-ym)+1e-6),0,1)
hatch=np.clip((0.35+1.1*frac)*0.9*u-dcol+0.5,0,1)*inside
slope=np.gradient(col); outline=np.clip(1.5*u-np.abs(Y-col[None,:])/np.sqrt(1+slope[None,:]**2)+0.5,0,1)
mean=np.clip(0.6*u-np.abs(Y-ym)+0.5,0,1)
strip=((X>=x0+2*u)&(X<=x1-2*u)&(Y>sy0)&(Y<sy1))
B.ink(np.maximum(np.maximum(hatch*0.8,outline),mean*0.8)*strip,'#1b2658',0.92)
dots=np.zeros((W,W),np.float32)
for tv in lt: dots=np.maximum(dots,np.clip(5.5*u-np.hypot(X-px(tv),Y-ym)+0.5,0,1))
B.ink(dots,'#d8362b',1.0)
it=[]
cap_y=sy1+int(0.015*W)
it.append((x0,cap_y,"The Straight Coast",SERIF,int(0.026*W),'la'))
B.ink(B.text_mask(it),'#33324a',0.9)
extra="" if len(pt)==len(lt) else " (%d thread%s ashore outside the frame)"%(abs(len(pt)-len(lt)),' comes' if abs(len(pt)-len(lt))==1 else 's come')
lines=["Height above the sea is log |E(s)/E(1−s)|, where E(s) = M^(s−1) · Σ d^(−s) over the divisors d of m = %s, and M = √m."%format(m,","),
       "Every pit in the sea has its own mountain inland, and the red thread between them crosses the shore at a zero of E(s) + E(1−s).",
       "The shore is the line Re s = ½, exactly. In this window: %d pits, %d mountains, %d lights%s."%(len(pt),len(pt),len(lt),extra),
       "Below the chart, the same function along the shore, as a tide: it passes mean level under every light and nowhere else."]
it=[(x0,cap_y+int(0.034*W)+i*int(0.0158*W),s,SERIF_I,int(0.0125*W),'la') for i,s in enumerate(lines)]
it.append((x1,cap_y+int(0.012*W),"Im s from %.2f to %.2f"%(TA,TB),SERIF,int(0.0115*W),'ra'))
B.ink(B.text_mask(it),'#4b4a55',0.85)
json.dump(dict(pits=len(pt),lights=len(lt),t0=TA,t1=TB,lt=[float(v) for v in lt]),open('data_hero.json','w'))
B.save(OUT); print('saved',OUT,len(pt),len(lt))
