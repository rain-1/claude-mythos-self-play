"""Dawn lake of the Hofstadter-Conway hills.  One island per octave k of n: its ridge is A(n) = c(n) - n/2 over
[2^k, 2^{k+1}], mirrored in the water.  The variant B(n) = c*(n) - n/2 is a second ridge: above the water in even
octaves (a hill inside the hill), below it in odd octaves (a hill that exists only in the reflection)."""
import numpy as np, argparse
from PIL import Image
from scipy.ndimage import gaussian_filter, map_coordinates
ap=argparse.ArgumentParser(); ap.add_argument('--W',type=int,default=1600); ap.add_argument('--H',type=int,default=1000)
ap.add_argument('--k0',type=int,default=8); ap.add_argument('--k1',type=int,default=20)
ap.add_argument('--out',default='lake.png'); ap.add_argument('--sf',type=float,default=0.16); ap.add_argument('--sn',type=float,default=0.56); ap.add_argument('--ratio',type=float,default=0.16); ap.add_argument('--spread',type=float,default=0.30); ap.add_argument('--npy',default='')
ap.add_argument('--hmax',type=float,default=0.26); ap.add_argument('--hmin',type=float,default=0.05)
ap.add_argument('--yf',type=float,default=0.40); ap.add_argument('--yn',type=float,default=0.80)
a=ap.parse_args()
Z=np.load('lake/seq.npz'); A=Z['A']; B=Z['B']
W,H=a.W,a.H; SS=2; w,h=W*SS,H*SS
yy=np.arange(h,dtype=np.float32)[:,None]/h; xx=np.arange(w,dtype=np.float32)[None,:]/w
def lerp(c0,c1,t): return np.asarray(c0,np.float32)*(1-t)+np.asarray(c1,np.float32)*t
def grad(stops,t):
    t=np.clip(t,0,1); n=len(stops)-1; u=t*n; i=np.minimum(u.astype(int),n-1); f=(u-i)[...,None]
    S=np.asarray(stops,np.float32); return S[i]*(1-f)+S[i+1]*f
HOR=a.yf-0.005
# sky: periwinkle top -> lilac -> rose -> peach -> butter at horizon
sky=grad([[0.74,0.80,0.98],[0.84,0.80,0.97],[0.97,0.82,0.90],[1.0,0.87,0.80],[1.0,0.95,0.82]],(yy/HOR)**1.1)
sky=np.broadcast_to(sky,(h,w,3)).copy()
# sun: soft disc just above the horizon
sx,sy=0.63,HOR-0.07; dsun=np.hypot((xx-sx)*w/h,yy-sy)
glow=np.exp(-(dsun/0.10)**2)*0.35+np.exp(-(dsun/0.035)**2)*0.5
img=sky+(np.array([1,0.98,0.90])-sky)*np.clip(glow,0,1)[...,None]
img=np.where(yy[...,None]<HOR,img,0)
# water: reflected sky (flip about the horizon), cooler, plus horizontal ripple streaks
yr=np.clip(2*HOR-yy,0,HOR)
wsky=grad([[0.74,0.80,0.98],[0.84,0.80,0.97],[0.97,0.82,0.90],[1.0,0.87,0.80],[1.0,0.95,0.82]],(yr/HOR)**1.1)
wsky=np.broadcast_to(wsky,(h,w,3)).copy()
dsr=np.hypot((xx-sx)*w/h*0.6,(yy-(2*HOR-sy))*0.35)
wsky=wsky+(np.array([1,0.98,0.90])-wsky)*np.clip(np.exp(-(dsr/0.05)**2)*0.6,0,1)[...,None]
wsky=wsky*0.94+np.array([0.62,0.72,0.92])*0.06
rng=np.random.default_rng(2)
rip=gaussian_filter(rng.standard_normal((h,w)).astype(np.float32),(0.6*SS,40*SS)); rip/=rip.std()
img=np.where(yy[...,None]<HOR,img,wsky*(1+0.025*rip[...,None]))
grain=gaussian_filter(rng.standard_normal((h,w)).astype(np.float32),(1.2*SS,0.5*SS)); grain/=grain.std()
land=np.zeros((h,w),bool)
# islands, far (small k) to near (large k)
ks=list(range(a.k0,a.k1+1)); K=len(ks)
NEAR=[[0.80,0.74,0.96],[0.74,0.78,0.98],[0.86,0.72,0.94],[0.80,0.72,0.97]]
MINT=np.array([0.60,0.90,0.80],np.float32)
for j,k in enumerate(ks):
    t=j/(K-1); te=t**1.6
    base=a.yf+(a.yn-a.yf)*te                      # baseline (water line of this island)
    span=a.sf+(a.sn-a.sf)*te
    hs=span*(W/H)*a.ratio                         # dome height from its width
    CX=[0.30,0.66,0.84,0.47,0.14,0.70,0.36,0.90,0.20,0.62,0.28,0.76]; cxn=CX[j%len(CX)]
    x0=cxn-span/2
    lo,hi=2**k,2**(k+1); n=np.arange(lo,hi+1)
    Ak=A[lo:hi+1]; Bk=B[lo:hi+1]; mx=Ak.max()
    u=(xx[0]-x0)/span; inside=(u>=0)&(u<=1)
    idx=np.clip(u,0,1)*(hi-lo)
    # box-filter the ridge to the pixel grid (max over the sub-range would alias; use interpolation of a smoothed copy)
    pxn=(hi-lo)/(span*w); sm=max(pxn*0.5,0.0)
    As=gaussian_filter(Ak.astype(np.float32),sm) if sm>0.3 else Ak
    Bs=gaussian_filter(Bk.astype(np.float32),sm) if sm>0.3 else Bk
    ra=np.interp(idx,np.arange(hi-lo+1),As)/mx*hs; rb=np.interp(idx,np.arange(hi-lo+1),Bs)/mx*hs
    ra=np.where(inside,ra,-1); rb=np.where(inside,rb,0)
    col=grad(NEAR,np.array([(j*0.37)%1]))[0] if False else grad(NEAR,np.array([t]))[0]
    haze=0.80*(1-te)**1.3                         # aerial perspective: far islands fade into the horizon colour
    hz=np.array([0.96,0.88,0.92]); body=col*(1-haze)+hz*haze
    deep=MINT*(1-haze)+hz*haze                    # the c* ridge: mint
    # vertical shading on the island (lighter at the ridge, a little darker at the water)
    above=(yy<base)&(yy>=base-ra[None,:])
    tt=np.clip((base-yy)/np.maximum(ra[None,:],1e-6),0,1)
    uu=np.clip(u,0,1)[None,:]
    sun=0.86+0.12*uu+0.12*tt**0.7+0.018*grain
    rim=np.exp(-((base-ra[None,:]-yy)*h/(1.5*SS))**2)*(ra[None,:]>0)
    ic=body[None,None,:]*sun[...,None]; ic=ic+(1-ic)*0.45*rim[...,None]
    img=np.where(above[...,None],ic,img); land|=above
    if k%2==0:
        inb=(yy<base)&(yy>=base-rb[None,:])&(rb[None,:]>0)
        img=np.where(inb[...,None],(deep[None,None,:]*sun[...,None])+(1-deep*sun[...,None])*0.45*np.exp(-((base-rb[None,:]-yy)*h/(1.5*SS))**2)[...,None],img)
    # reflection: mirror below the baseline, compressed, blended with water colour
    dep=np.clip((yy-base),0,None)
    disp=(rip*0.0035*np.clip(dep/0.05,0,1)).astype(np.float32)
    xg=xx[0]
    rad_=np.interp((xx+disp).ravel(),xg,ra).reshape(h,w); rbd=np.interp((xx+disp).ravel(),xg,rb).reshape(h,w)
    fade=(0.85-0.5*np.clip(dep/np.maximum(ra.max(),1e-6),0,1))[...,None]
    below=(yy>=base)&(yy<base+rad_*0.92)
    wcol=img
    rc=body*0.80+np.array([0.70,0.78,0.95])*0.20
    img=np.where(below[...,None],img*(1-fade)+rc*fade*(1+0.03*rip[...,None]),img)
    if k%2==1:
        inb=(yy>=base)&(yy<base-rbd*0.92)&(rbd<0)
        img=np.where(inb[...,None],img*(1-fade)+(deep*0.86+np.array([0.70,0.78,0.95])*0.14)*fade*(1+0.03*rip[...,None]),img)
    mist=np.exp(-((yy-base+0.004)/0.010)**2)*np.clip(1-np.abs(np.clip(u,-1,2)[None,:]-0.5)*1.6,0,1)
    img=img+(np.array([1.0,0.97,0.97])-img)*0.40*mist[...,None]
    # bright water line
    wl=np.exp(-((yy-base)*h/(1.2*SS))**2)*(ra[None,:]>=0)
    img=img+(1-img)*0.5*wl[...,None]
# sun glitter on the water path under the sun
gl=(rng.random((h,w))<0.0016).astype(np.float32)
path=np.exp(-((xx-sx)/(0.03+0.20*np.clip(yy-HOR,0,1)))**2)*(yy>HOR)
gl=gaussian_filter(gl*path,(0.5*SS,2.5*SS))*30
img=img+(1-img)*(np.clip(gl,0,1)*(~land))[...,None]*0.9
def down(m): return m.reshape(H,SS,W,SS,*m.shape[2:]).mean((1,3))
out=down(img.astype(np.float32))
if a.npy: np.save(a.npy,out)
Image.fromarray((np.clip(out,0,1)*255).astype(np.uint8)).save(a.out)
