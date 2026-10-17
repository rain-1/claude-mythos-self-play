"""Pleated paper medallion of the 3n-1 basins.  One fan-folded paper sheet per octave k of n (top = small n).
Edge r_k(theta) = R_k + A * tanh(z_k(theta)) where z_k is the band-limited, per-octave normalised density profile
of one basin; theta = 2 pi frac(log2 n) (pitch class).  Colour = local mix of the three basin pigments;
pleat shading from d(z)/d(theta) (a fold at every max and min of the profile)."""
import numpy as np, argparse
from PIL import Image
from scipy.ndimage import gaussian_filter, shift as nshift
ap=argparse.ArgumentParser()
ap.add_argument('--S',type=int,default=1400); ap.add_argument('--out',default='med.png')
ap.add_argument('--k0',type=int,default=10); ap.add_argument('--k1',type=int,default=31)
ap.add_argument('--Qa',type=float,default=30); ap.add_argument('--Qb',type=float,default=120)
ap.add_argument('--A',type=float,default=0.05); ap.add_argument('--edge',type=int,default=3)
ap.add_argument('--rin',type=float,default=0.30); ap.add_argument('--rout',type=float,default=0.90)
ap.add_argument('--gam',type=float,default=1.0)
ap.add_argument('--temp',type=float,default=1.3); ap.add_argument('--pleat',type=float,default=0.10)
ap.add_argument('--sd',type=float,default=0.34); ap.add_argument('--rim',type=float,default=0.45)
ap.add_argument('--light',type=float,default=0.25); ap.add_argument('--cy',type=float,default=0.0)
ap.add_argument('--H',type=int,default=0); ap.add_argument('--step',type=int,default=1); ap.add_argument('--mix',type=float,default=1.0); ap.add_argument('--octs',default=''); ap.add_argument('--src',default=''); ap.add_argument('--coral',type=int,default=-1); ap.add_argument('--alt',type=float,default=0.0); ap.add_argument('--npy',default='')
a=ap.parse_args()
if a.src.endswith('.u32'):
    C=np.fromfile(a.src,np.uint32).reshape(-1,2048,10).astype(np.float64)
    tot=C[:,:,1:].sum(2,keepdims=True); Pall=C[:,:,1:9]/np.maximum(tot,1)   # octave index = k
    order=np.argsort(-C[20,:,1:9].sum(0)); Pall=Pall[:,:,order]           # basins by size
    B=2048; OFF=0
else:
    D=np.loadtxt('math_collatz/dens.txt'); B=240; Pall=D[:,1:4].reshape(-1,B,3); OFF=8
OCTS=[int(v) for v in a.octs.split(',')] if a.octs else list(range(a.k0,a.k1+1))[::-1][::a.step][::-1]
P=Pall[[o-OFF for o in OCTS]]
K=P.shape[0]; NT=8192
F=np.fft.rfft(P-P.mean(1,keepdims=True),axis=1); q=np.arange(F.shape[1])
Qk=a.Qa+(a.Qb-a.Qa)*(np.array(OCTS)-OCTS[0])/(OCTS[-1]-OCTS[0])
F*=np.exp(-(q[None,:]/Qk[:,None])**2)[...,None]
Fp=np.zeros((K,NT//2+1,F.shape[2]),complex); Fp[:,:F.shape[1]]=F
prof=np.fft.irfft(Fp,n=NT,axis=1)
Z=prof/prof.std(1,keepdims=True)
SS=2; W=a.S; H=a.H or a.S; Sw,Sh=W*SS,H*SS
yy,xx=np.mgrid[0:Sh,0:Sw].astype(np.float32); sc=Sw/2
dx=(xx-Sw/2+0.5)/sc; dy=(yy-Sh/2+0.5)/sc+a.cy
r=np.hypot(dx,dy); th=(np.arctan2(dx,-dy)/(2*np.pi))%1; it=(th*NT).astype(np.int32)%NT
t=(np.arange(K)+1)/K
R=a.rin+(a.rout-a.rin)*t**a.gam
cnt=np.zeros((Sh,Sw),np.float32); top=np.full((Sh,Sw),-1,np.int16)
E=np.empty((K,NT),np.float32)
for k in range(K-1,-1,-1):
    e=Z[k,:,a.edge-1] if a.edge>0 else Z[k].max(1)
    E[k]=np.tanh(e/1.5)
    rk=R[k]+a.A*E[k]
    inside=r<rk[it]; cnt+=inside; top[inside]=k
    if OCTS[k]==a.coral: cdist=(rk[it]-r)
PIG=np.array([[0.56,0.86,0.76],[0.76,0.68,0.95],[1.00,0.70,0.60]],np.float32)
w=np.exp(a.temp*np.clip(Z[...,:3],-3,3)); w/=w.sum(-1,keepdims=True); colk=w@PIG
dE=np.gradient(E,axis=1)*NT/(2*np.pi)                      # d/dtheta
pl=np.tanh(dE/ (np.abs(dE).mean(1,keepdims=True)*1.5+1e-9))   # pleat facing
kk=np.clip(top,0,K-1)
OCT=np.array([[1.0,0.93,0.70],[1.0,0.80,0.66],[1.0,0.74,0.80],[0.90,0.74,0.96],[0.74,0.78,1.0],[0.64,0.88,0.96],[0.62,0.90,0.80]],np.float32)
u=(np.arange(K)/(K-1))*(len(OCT)-1); i0=np.minimum(u.astype(int),len(OCT)-2); f=(u-i0)[:,None]
ocol=OCT[i0]*(1-f)+OCT[i0+1]*f
col=a.mix*colk[kk,it]+(1-a.mix)*ocol[kk]; col*= (1-a.alt*(kk%2))[...,None]
lift=(a.light*(1-kk/(K-1)))[...,None]; col=col+(1-col)*lift
shade=1+a.pleat*pl[kk,it]*np.clip((r/np.maximum(R[kk],1e-3))**2,0,1)   # pleats fade toward the sheet centre
col=col*shade[...,None]
PAPER=np.array([0.993,0.989,0.983],np.float32)
col=np.where((top>=0)[...,None],col,PAPER)
def down(m): return m.reshape(H,SS,W,SS,*m.shape[2:]).mean((1,3))
if a.coral>=0:
    px=Sw/2/1000*2.2*1.0                          # rim width ~ 2.2 px per 1000 px of canvas (in SS units below)
    ci=np.where(OCTS==None,0,0)
    kc=OCTS.index(a.coral)
    vis=(top<=kc)                                   # rim visible only where no smaller sheet covers it
    band=np.clip(1-np.abs(cdist*sc-1.6*SS*W/1000)/(1.6*SS*W/1000),0,1)*vis*(cdist>0)
    col=col*(1-0.85*band[...,None])+np.array([1.0,0.50,0.44],np.float32)*0.85*band[...,None]
img=down(col); hgt=down(cnt)
s=W/1000.0
up=nshift(hgt,(2.2*s,1.6*s),order=1,mode='nearest'); d=np.clip(up-hgt,0,None); d=2.5*(1-np.exp(-d/2.5))
sh=gaussian_filter(d,1.8*s); img*=1-a.sd*(1-np.exp(-sh))[...,None]*(1-np.array([0.55,0.50,0.30]))*1.9
# soft drop shadow of the whole medallion on the paper
base=gaussian_filter((hgt>0).astype(np.float32),14*s); base=nshift(base,(9*s,6*s),order=1,mode='nearest')
img*=1-0.16*(base*(hgt==0))[...,None]*(1-np.array([0.55,0.50,0.30]))*1.6
tl=nshift(hgt,(0.9*s,0.9*s),order=1,mode='nearest'); br=nshift(hgt,(-0.9*s,-0.9*s),order=1,mode='nearest')
img=img+(1-img)*a.rim*(1-np.exp(-np.clip(hgt-tl,0,None)))[...,None]; img*=1-0.10*(1-np.exp(-np.clip(hgt-br,0,None)))[...,None]
rng=np.random.default_rng(5); img*=1-0.010*gaussian_filter(rng.standard_normal((H,W)).astype(np.float32),0.8*s)[...,None]
if a.npy: np.save(a.npy,img.astype(np.float32))
Image.fromarray((np.clip(img,0,1)*255).astype(np.uint8)).save(a.out)
