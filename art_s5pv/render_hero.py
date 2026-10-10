# render_hero.py — the halo display over a pastel snowfield, with a mother-of-pearl bead holding the whole sky
import numpy as np,sys,struct
from PIL import Image
from scipy.ndimage import gaussian_filter, map_coordinates
from scene import *
pre=sys.argv[1];W=int(sys.argv[2]);H=W;EW=int(sys.argv[3]);out=sys.argv[4]
CAZ,CEL,SC=0.0,30.0,0.85
S=W/1024.0
HC=0.05                     # camera height (m): a bead's-eye view
RB=0.0150;BD=0.175;BAZ=-15.0  # bead radius, distance, azimuth (deg)
BC=np.array([BD*np.cos(BAZ*D2R),BD*np.sin(BAZ*D2R),RB],np.float32);CAM=np.array([0,0,HC],np.float32)

# ---------- halo maps
cam=np.fromfile(pre+'_cam.f32',np.float32).reshape(H,W,3)
eq=np.fromfile(pre+'_eq.f32',np.float32).reshape(EW//2,EW,3)
d=cam_dirs(W,H,CAZ,CEL,SC)
gsun=np.degrees(np.arccos(np.clip(d@SUN,-1,1)))
cam[gsun<1.2]=0                       # direct-transmission spike: the sun is drawn separately
cam=gaussian_filter(cam,(1.3*S,1.3*S,0))
rgbh=cam@XYZ2RGB.T
Yh=cam[...,1];ref=np.percentile(Yh[(gsun>21.6)&(gsun<22.6)&(d[...,2]>0)&(np.abs(d[...,1])<0.25)],50)
GAIN=float(sys.argv[5]) if len(sys.argv)>5 else 0.30
rgbh=np.clip(rgbh/ref*GAIN,-0.2,None)
lum=(rgbh*[0.2126,0.7152,0.0722]).sum(-1,keepdims=True)
rgbh=np.clip(lum+(rgbh-lum)*1.9,0,None)
# equirect halo for reflections (same normalisation by ray density: scale by pixel solid angle)
eqY=gaussian_filter(eq,(1.5,1.5,0))
el_e=(0.5-(np.arange(EW//2)+0.5)/(EW//2))*np.pi
sa=np.cos(el_e)[:,None,None]*(2*np.pi/EW)*(np.pi/(EW//2))
# camera pixel solid angle at the 22-degree halo ~ (2/(W*SC))^2 /(1+cos)^2*4 -> compute ratio generically
pix_sa_cam=(2/(W*SC))**2*((1+np.cos(22*D2R))/2)**-2
eqh=(eqY/sa*pix_sa_cam)@XYZ2RGB.T/ref*GAIN
lum=(eqh*[0.2126,0.7152,0.0722]).sum(-1,keepdims=True);eqh=np.clip(lum+(eqh-lum)*1.9,0,None).astype(np.float32)

def env(r):
    """radiance seen along unit directions r (sky + halos + sun, or a soft snow ground)"""
    az=np.arctan2(r[...,1],r[...,0]);el=np.arcsin(np.clip(r[...,2],-1,1))
    ix=(az/(2*np.pi)+0.5)*EW-0.5;iy=(0.5-el/np.pi)*(EW//2)-0.5
    h=np.stack([map_coordinates(eqh[...,c],[iy,ix],order=1,mode='wrap') for c in range(3)],-1)
    s=sky_rgb(r)+h
    g=np.degrees(np.arccos(np.clip(r@SUN,-1,1)))
    s=s+(40*np.exp(-(g/0.3)**2))[...,None]*np.array([1,0.97,0.9])
    gr=np.array([0.93,0.90,1.0])*0.92
    t=smoothstep(-0.02,0.02,r[...,2])[...,None]
    return s*t+gr*(1-t)

# ---------- sky
sky=sky_rgb(d)+rgbh
# sun disk + bloom
sky+= (3.5*np.exp(-(gsun/0.27)**8)+0.9*np.exp(-gsun/0.9)+0.25*np.exp(-gsun/3.0))[...,None]*np.array([1,0.96,0.86],np.float32)

# ---------- ground plane and hills
el=np.degrees(np.arcsin(np.clip(d[...,2],-1,1)));az=np.degrees(np.arctan2(d[...,1],d[...,0]))
def ridge(az,base,amp,seed,oct=5):
    rng=np.random.default_rng(seed);v=np.zeros_like(az)+base
    for o in range(oct):
        k=2**o*1.0;ph=rng.random(3)*6.28;a=amp/ (1.7**o)
        v=v+a*(np.sin(az*D2R*k*3+ph[0])*0.6+np.sin(az*D2R*k*5.3+ph[1])*0.4)
    return v
far=ridge(az,2.2,1.4,7);near=ridge(az,0.55,0.55,11)
img=sky.copy()
ground=el<0
# world hit points
t=np.where(d[...,2]<-1e-6,HC/np.maximum(-d[...,2],1e-6),1e9)
P=CAM+d*t[...,None]
dist=np.minimum(t,5e3)
# snow relief by a sum of sinusoids, wavelengths from 4 mm to 6 m, antialiased by footprint
pa=(2/(W*SC))                                    # pixel angle (rad) near centre
foot=dist*pa/np.maximum(np.abs(d[...,2]),0.02)   # ground footprint per pixel (m)
rng=np.random.default_rng(3);hx=np.zeros_like(dist);hy=np.zeros_like(dist)
for i in range(90):
    lam=0.006*(800**(rng.random()));th=rng.random()*2*np.pi
    k=2*np.pi/lam;kx,ky=k*np.cos(th),k*np.sin(th);ph=rng.random()*6.28
    a=0.016*lam*(lam/0.3)**0.35*np.exp(-(foot*k/2.0)**2)
    c=np.cos(kx*P[...,0]+ky*P[...,1]+ph)*a
    hx+=kx*c;hy+=ky*c
n=np.stack([-hx,-hy,np.ones_like(hx)],-1);n/=np.linalg.norm(n,axis=-1,keepdims=True)
ndl=np.clip(n@SUN,0,1)
# bead shadow on the ground
v=BC-P;tc=np.clip((v@SUN),0,None);closest=np.linalg.norm(v-tc[...,None]*SUN,axis=-1)
shadow=smoothstep(RB*0.80,RB*1.05,closest)
shadow=np.where(tc>0,shadow,1.0)
rel=np.clip((ndl-np.sin(SUN_EL*D2R))/0.30,-1,1)
graze=np.clip(-d[...,2]/0.12,0,1)                 # flatten the relief near the horizon
rel=rel*graze
hi=np.array([1.00,0.95,0.93]);lo=np.array([0.78,0.76,1.0])
w=(0.62+0.38*rel)*shadow
snow=lo*(1-w[...,None])+hi*w[...,None]
fwd=np.exp(-(np.abs(az)/14)**2)*np.exp(-np.clip(-el,0,None)/10)
snow=snow*(0.93+0.15*fwd[...,None])+np.array([1.0,0.92,0.82])*(0.10*fwd*shadow)[...,None]
snow=snow*np.where(shadow<0.99,0.85+0.15*shadow,1.0)[...,None]
# sun glitter: grains whose facet sends the sun to us (random, heavy-tailed), coloured by ice dispersion
hz=0
fog=1-np.exp(-dist/9.0);hazec=np.array([0.95,0.86,0.93])
snow=snow*(1-fog[...,None]*0.85)+hazec*fog[...,None]*0.85
img[ground]=snow[ground]
# hills (occlude the sky above the horizon)
mfar=(el>0)&(el<far);mnear=(el>-0.15)&(el<near)
hfar=np.array([0.74,0.74,0.98]);hnear=np.array([0.97,0.92,1.0])
shf=(0.85+0.15*np.cos((az-20)*D2R*6))[...,None]
img[mfar]=(img[mfar]*0.25+hfar*0.75*shf[mfar])
img[mnear]=(hnear*shf[mnear])
# small frosted firs on the near ridge (scale), clustered away from the sun's column
rt_=np.random.default_rng(21)
trees=[]
for cx,n_,spread in ((38,9,9),(-44,11,10),(66,5,6),(-70,6,6)):
    for k in range(n_):
        trees.append((cx+rt_.normal()*spread*0.6, 1.6+rt_.random()*2.2))
trees.sort(key=lambda t:-t[1])
for taz,th in trees:
    base=np.interp(taz,az[int(H*0.7)],near[int(H*0.7)]) if False else 0.0
    w_=th*0.30
    u=(az-taz)/w_; v=(el-0.15)/th           # v in [0,1] from base to tip
    tiers=3
    vv=np.clip(v,0,1);tier=np.floor(vv*tiers);fv=vv*tiers-tier
    half=(1-vv)*(0.75+0.35*(1-fv))
    m=(v>-0.05)&(v<1)&(np.abs(u)<half)&(np.abs(az-taz)<4)
    if not m.any():continue
    col=np.array([0.62,0.78,0.86])*0.9+0.1
    side=np.clip(0.5-u[m]*0.6,0,1)[:,None]
    snowcap=(fv[m]>0.55)[:,None]
    c=col*(0.85+0.15*side)
    c=np.where(snowcap,np.array([0.96,0.94,1.0])*(0.9+0.1*side),c)
    fogt=0.35
    img[m]=c*(1-fogt)+np.array([0.95,0.88,0.93])*fogt
# ---------- the bead
oc=CAM-BC;b=d@oc;c=oc@oc-RB*RB;disc=b*b-c
hit=(disc>0)&(-b-np.sqrt(np.maximum(disc,0))>0)
if hit.any():
    th=(-b-np.sqrt(np.maximum(disc,0)))[hit];dh=d[hit];Ph=CAM+dh*th[:,None];N=(Ph-BC)/RB
    r=dh-2*(dh*N).sum(-1,keepdims=True)*N
    R=env(r)
    cosi=np.clip(-(dh*N).sum(-1),0,1)
    # nacre: film thickness varies with latitude on the bead + growth rings
    lat=np.arctan2(N[:,2],np.hypot(N[:,0],N[:,1]));lon=np.arctan2(N[:,1],N[:,0])
    thick=330+45*np.sin(lat*3+np.sin(lon*2)*0.5)+12*np.sin(lon*5+lat*3)
    film=thinfilm_rgb(thick.astype(np.float32))
    film=film/np.maximum(film.max(-1,keepdims=True),1e-3)
    tint=0.72+0.28*film
    fr=0.28+0.72*(1-cosi)**3
    body=np.array([0.98,0.94,0.96])*(0.62+0.5*np.clip(N@SUN,0,1)+0.25*np.clip(N[:,2],0,1))[:,None]
    tint=0.78+0.22*film
    sheen=0.80+0.20*film
    img[hit]=body*tint*(1-fr[:,None])*0.55+R*sheen*(0.50+0.50*fr[:,None])
# ---------- diamond-dust sparks (each one is one ray of the halo)
sp=np.fromfile(pre+'_sparks.bin',np.float32).reshape(-1,4)
from scene import thinfilm_rgb as _t
def spec_rgb(lam):
    def g1(x,m,s1,s2):
        t=(x-m)/np.where(x<m,s1,s2);return np.exp(-0.5*t*t)
    X=1.056*g1(lam,599.8,37.9,31.0)+0.362*g1(lam,442.0,16.0,26.7)-0.065*g1(lam,501.1,20.4,26.2)
    Y=0.821*g1(lam,568.8,46.9,40.5)+0.286*g1(lam,530.9,16.3,31.1)
    Z=1.217*g1(lam,437.0,11.8,36.0)+0.681*g1(lam,459.0,26.0,13.8)
    c=np.stack([X,Y,Z],-1)@XYZ2RGB.T;c=np.clip(c,0,None);return c/np.maximum(c.max(-1,keepdims=True),1e-6)
spk=np.zeros_like(img)
rs=np.random.default_rng(5)
for x,y,lam,pi in sp[rs.random(len(sp))<min(1,3500/len(sp))]:
    ix,iy=int(x),int(y)
    if not(0<=ix<W and 0<=iy<H) or not(el[iy,ix]>max(far[iy,ix],0)+0.3):continue
    br=rs.pareto(2.2)*0.35+0.25;col=0.35+0.65*spec_rgb(np.array(lam))
    L=int(5*S*(0.6+br));
    for dx in range(-L,L+1):
        for (xx,yy,w) in ((ix+dx,iy,np.exp(-abs(dx)/(1.6*S))),(ix,iy+dx,np.exp(-abs(dx)/(1.6*S)))):
            if 0<=xx<W and 0<=yy<H: spk[yy,xx]+=col*br*w
img=img+spk
# glitter on the snow: random sparkles, denser near the sun's glitter path
ng=int(9000*S*1.3)
gx=rs.random(ng)*W;gy=rs.random(ng)*H
ok=ground[gy.astype(int),gx.astype(int)]&~hit[gy.astype(int),gx.astype(int)]
gx,gy=gx[ok],gy[ok]
azg=az[gy.astype(int),gx.astype(int)]
keep=rs.random(len(gx))<np.exp(-(azg/22)**2)*0.9+0.1
for x,y in zip(gx[keep],gy[keep]):
    ix,iy=int(x),int(y);br=(rs.pareto(2.5)*0.25+0.15)*shadow[iy,ix];col=0.4+0.6*spec_rgb(np.array(400+300*rs.random()))
    L=int(3*S*(0.6+br))
    for dx in range(-L,L+1):
        for (xx,yy,w) in ((ix+dx,iy,np.exp(-abs(dx)/(1.1*S))),(ix,iy+dx,np.exp(-abs(dx)/(1.1*S)))):
            if 0<=xx<W and 0<=yy<H: img[yy,xx]+=col*br*w
# ---------- tone
lum0=(img*[0.2126,0.7152,0.0722]).sum(-1,keepdims=True);img=np.clip(lum0+(img-lum0)*1.14,0,None)
Lw=1.25;x=img*1.0
lum=(x*[0.2126,0.7152,0.0722]).sum(-1,keepdims=True)
lo=lum*(1+lum/Lw**2)/(1+lum);x=x*lo/np.maximum(lum,1e-6)
x=np.clip(x,0,1)
srgb=np.where(x<=0.0031308,12.92*x,1.055*np.power(x,1/2.4)-0.055)
Image.fromarray((srgb*255+0.5).astype(np.uint8)).save(out)
np.save(out.replace('.png','_lin.npy'),img.astype(np.float16))
print('done')
# ---------- caption on the snow (bottom right)
from PIL import ImageDraw,ImageFont
im=Image.open(out);dr=ImageDraw.Draw(im);plum=(92,77,102)
fT=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf',int(30*S))
fI=ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf',int(17.5*S))
fM=ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf',int(15*S))
lines=[(fT,'Six Billion Accidents, One Sky',plum,0),
 (fI,'Each ray met one hexagonal ice crystal, turned any which way;',(104,90,116),int(46*S)),
 (fI,'together they drew the halo, the sundogs, the arcs and the circle.',(104,90,116),int(70*S)),
 (fM,'6×10⁹ Monte Carlo rays · Fresnel at every face · ice dispersion · sun 22° up · stereographic sky.',(128,114,140),int(100*S)),
 (fM,'The mother-of-pearl bead in the snow holds the whole sky, the half behind you too.',(128,114,140),int(120*S))]
x0=int(30*S);y0=int(H-170*S)
for f,tx,c,dy in lines:
    dr.text((x0,y0+dy),tx,font=f,fill=c)
im.save(out)
