"""Paper carnation of the 3n-1 basins: one paper sheet per octave of n (inner = small n).
Sheet k's edge r_k(theta) follows the band-limited density profile of one basin in that octave,
theta = 2*pi*frac(log2 n) (pitch class).  Sheet colour = local mix of the three basin pigments."""
import numpy as np, argparse
from PIL import Image
from scipy.ndimage import gaussian_filter, shift as nshift
ap=argparse.ArgumentParser()
ap.add_argument('--S',type=int,default=1400); ap.add_argument('--out',default='carn.png')
ap.add_argument('--k0',type=int,default=10); ap.add_argument('--k1',type=int,default=31)
ap.add_argument('--Q',type=float,default=120); ap.add_argument('--amp',type=float,default=0.05)
ap.add_argument('--edge',type=int,default=3); ap.add_argument('--rin',type=float,default=0.16)
ap.add_argument('--rout',type=float,default=0.93); ap.add_argument('--temp',type=float,default=1.4)
ap.add_argument('--sd',type=float,default=0.32); ap.add_argument('--rim',type=float,default=0.45)
ap.add_argument('--light',type=float,default=0.30); ap.add_argument('--npy',default='')
a=ap.parse_args()
D=np.loadtxt('math_collatz/dens.txt'); B=240
P=D[:,1:4].reshape(-1,B,3)[a.k0-8:a.k1-8+1]          # octaves k0..k1
K=P.shape[0]; NT=4096
F=np.fft.rfft(P-P.mean(1,keepdims=True),axis=1)
q=np.arange(F.shape[1]); F*=np.exp(-(q/a.Q)**2)[None,:,None]
Fp=np.zeros((K,NT//2+1,3),complex); Fp[:,:F.shape[1]]=F
prof=np.fft.irfft(Fp,n=NT,axis=1)*(NT/B)               # K x NT x 3 deviations
Z=prof/prof.std(1,keepdims=True)                        # per-octave normalised
SS=2; S=a.S*SS
yy,xx=np.mgrid[0:S,0:S].astype(np.float32); dx=(xx-S/2+0.5)/(S/2); dy=(yy-S/2+0.5)/(S/2)
r=np.hypot(dx,dy); th=(np.arctan2(dx,-dy)/(2*np.pi))%1; it=(th*NT).astype(np.int32)%NT
R=a.rin+(a.rout-a.rin)*(np.arange(K)+1)/K               # nominal outer radius of sheet k
cnt=np.zeros((S,S),np.float32); top=np.full((S,S),-1,np.int16)
for k in range(K-1,-1,-1):                              # bottom (outer) first
    e=Z[k,:,a.edge-1] if a.edge>0 else Z[k].max(1)
    rk=R[k]*(1+a.amp*np.tanh(e/2.0)*2)
    inside=r<rk[it]
    cnt+=inside; top[inside]=k
PIG=np.array([[0.56,0.86,0.76],[0.76,0.68,0.95],[1.00,0.70,0.60]],np.float32)  # mint(1) lilac(5) peach(17)
w=np.exp(a.temp*np.clip(Z,-3,3)); w/=w.sum(-1,keepdims=True)
colk=w@PIG                                              # K x NT x 3
kk=np.clip(top,0,K-1)
col=colk[kk,it]
lift=(a.light*(1-kk/(K-1)))[...,None]                  # inner sheets lighter
col=col+(1-col)*lift
PAPER=np.array([0.993,0.989,0.983],np.float32)
col=np.where((top>=0)[...,None],col,PAPER)
H=W=a.S
def down(m): return m.reshape(H,SS,W,SS,*m.shape[2:]).mean((1,3))
img=down(col); hgt=down(cnt)
s=a.S/1000.0
up=nshift(hgt,(2.2*s,1.6*s),order=1,mode='nearest'); d=np.clip(up-hgt,0,None); d=2.5*(1-np.exp(-d/2.5))
sh=gaussian_filter(d,1.8*s); img*=1-a.sd*(1-np.exp(-sh))[...,None]*(1-np.array([0.55,0.50,0.30]))*1.9
tl=nshift(hgt,(0.9*s,0.9*s),order=1,mode='nearest'); br=nshift(hgt,(-0.9*s,-0.9*s),order=1,mode='nearest')
img=img+(1-img)*a.rim*(1-np.exp(-np.clip(hgt-tl,0,None)))[...,None]; img*=1-0.10*(1-np.exp(-np.clip(hgt-br,0,None)))[...,None]
if a.npy: np.save(a.npy,img.astype(np.float32))
Image.fromarray((np.clip(img,0,1)*255).astype(np.uint8)).save(a.out)
