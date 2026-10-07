"""Paper-cut stack, height-field version: colour = the top sheet's colour (sheet k = {w >= k}), ONE shadow map and
ONE rim map from the height field h = min(w, cap), so a vortex of 60 nested edges never goes muddy."""
import numpy as np, argparse
from PIL import Image
from scipy.ndimage import gaussian_filter, shift as nshift
ap=argparse.ArgumentParser()
ap.add_argument('--field'); ap.add_argument('--out'); ap.add_argument('--crop',default='0,1,0,1')
ap.add_argument('--span',type=float,default=0.9); ap.add_argument('--kshift',type=float,default=0.13)
ap.add_argument('--st1',type=float,default=0.5); ap.add_argument('--st2',type=float,default=0.9)
ap.add_argument('--tblur',type=float,default=4); ap.add_argument('--hoff',type=float,default=0.0)
ap.add_argument('--sd',type=float,default=0.30); ap.add_argument('--sh',type=float,default=1.6)
ap.add_argument('--rim',type=float,default=0.5); ap.add_argument('--cap',type=float,default=2.5)
ap.add_argument('--npy',default='')
a=ap.parse_args()
F=np.load(a.field); w=F['w'].astype(np.int16)[::-1]; sm=F['s'].astype(np.float32)[::-1]
G=w.shape[0]; y0,y1,x0,x1=[int(float(c)*G) for c in a.crop.split(',')]
w=w[y0:y1,x0:x1]; sm=sm[y0:y1,x0:x1]
SS=2; H,W=w.shape[0]//SS,w.shape[1]//SS
def down(m): return m[:H*SS,:W*SS].reshape(H,SS,W,SS,*m.shape[2:]).mean((1,3))
PAPER=np.array([0.994,0.990,0.984],np.float32)
WHEEL=np.array([[1.0,0.86,0.88],[1.0,0.78,0.66],[1.0,0.90,0.60],[0.80,0.94,0.66],[0.62,0.92,0.84],[0.64,0.84,1.0],[0.74,0.76,1.0],[0.86,0.74,1.0],[1.0,0.72,0.88],[1.0,0.66,0.70]],np.float32)
def wheel(h):
    idx=(h%1)*len(WHEEL); i0=idx.astype(np.int32)%len(WHEEL); f=(idx-np.floor(idx))[...,None]
    return WHEEL[i0]*(1-f)+WHEEL[(i0+1)%len(WHEEL)]*f
S_=gaussian_filter(sm,a.tblur*W/1000*SS)
k=w.astype(np.float32)
st=np.where(k<=1,a.st1,a.st2)[...,None]
col=1-(1-wheel(a.span*S_+a.hoff+a.kshift*(k-1)))*st
col=np.where((k>=1)[...,None],col,PAPER)
img=down(col.astype(np.float32))
rng=np.random.default_rng(3)
img*=1-0.012*gaussian_filter(rng.standard_normal((H,W)),1.0)[...,None]
s=a.sh*W/1000.0
hgt=down(np.minimum(np.maximum(k,0),60).astype(np.float32))
# shadow: neighbour toward the light (top-left) higher than me
up=nshift(hgt,(2.2*s,1.6*s),order=1,mode='nearest')
d=np.clip(up-hgt,0,None); d=a.cap*(1-np.exp(-d/a.cap))
shadow=gaussian_filter(d,1.6*s)
img*=1-a.sd*(1-np.exp(-shadow))[...,None]*(1-np.array([0.55,0.50,0.30]))*1.9
# rims
tl=nshift(hgt,(0.9*s,0.9*s),order=1,mode='nearest'); br=nshift(hgt,(-0.9*s,-0.9*s),order=1,mode='nearest')
lit=1-np.exp(-np.clip(hgt-tl,0,None)); dark=1-np.exp(-np.clip(hgt-br,0,None))
img=img+(1-img)*a.rim*lit[...,None]
img*=1-0.10*dark[...,None]
if a.npy: np.save(a.npy,img.astype(np.float32))
Image.fromarray((np.clip(img,0,1)*255).astype(np.uint8)).save(a.out)
print(H,W)
