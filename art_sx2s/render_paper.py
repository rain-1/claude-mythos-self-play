"""Paper-cut stack of the Riemann curve's winding number: sheet k = {w >= k} in sorbet paper,
drop shadows (cool), rim light on the lit edge, supersampled masks (field grid = SS x output)."""
import numpy as np, sys, argparse
from PIL import Image, ImageFilter
from scipy.ndimage import gaussian_filter, shift as nshift
ap=argparse.ArgumentParser()
ap.add_argument('--field'); ap.add_argument('--out'); ap.add_argument('--K',type=int,default=12)
ap.add_argument('--crop',type=str,default=''); ap.add_argument('--npy',default='')
ap.add_argument('--sh',type=float,default=1.0)   # shadow scale (px at 1000)
ap.add_argument('--rim',type=float,default=0.55); ap.add_argument('--tmode',type=int,default=0); ap.add_argument('--span',type=float,default=0.9); ap.add_argument('--kshift',type=float,default=0.13); ap.add_argument('--st1',type=float,default=0.5); ap.add_argument('--st2',type=float,default=0.9); ap.add_argument('--tblur',type=float,default=3)
ap.add_argument('--irid',type=float,default=0.0); ap.add_argument('--hoff',type=float,default=0.0); ap.add_argument('--sd',type=float,default=0.2)
a=ap.parse_args()
F=np.load(a.field); w=F['w'].astype(np.int16)[::-1]   # v up -> rows down
sm_=F['s'].astype(np.float32)[::-1] if 's' in F else None
G=w.shape[0]
if a.crop:
    y0,y1,x0,x1=[int(float(c)*G) for c in a.crop.split(',')]; w=w[y0:y1,x0:x1]
    if sm_ is not None: sm_=sm_[y0:y1,x0:x1]
SS=2; H,W=w.shape[0]//SS,w.shape[1]//SS
def down(m): return m[:H*SS,:W*SS].reshape(H,SS,W,SS).mean((1,3))
PAPER=np.array([0.994,0.990,0.984])
WHEEL=np.array([[1.0,0.86,0.88],[1.0,0.78,0.66],[1.0,0.90,0.60],[0.80,0.94,0.66],[0.62,0.92,0.84],[0.64,0.84,1.0],[0.74,0.76,1.0],[0.86,0.74,1.0],[1.0,0.72,0.88],[1.0,0.66,0.70]])
img=np.ones((H,W,3))*PAPER
# faint paper grain
rng=np.random.default_rng(3); img*=1-0.012*gaussian_filter(rng.standard_normal((H,W)),1.0)[...,None]
s=a.sh*W/1000.0
yy,xx=np.mgrid[0:H,0:W]/max(H,W)
if a.tmode:
    S_=gaussian_filter(down(sm_),a.tblur*W/1000)
def wheel(h):
    idx=(h%1)*len(WHEEL); i0=idx.astype(int)%len(WHEEL); f=(idx-np.floor(idx))[...,None]
    return WHEEL[i0]*(1-f)+WHEEL[(i0+1)%len(WHEEL)]*f
for k in range(1,a.K+1):
    m=down((w>=k).astype(np.float32))
    if m.max()==0: break
    c=WHEEL[(k-1)%len(WHEEL)]
    # drop shadow: offset down-right, blurred, periwinkle-grey
    sm=gaussian_filter(nshift(m,(2.2*s,1.6*s),order=1),1.6*s)
    img*=1-a.sd/(1+0.35*(k-1))*sm[...,None]*(1-np.array([0.55,0.50,0.30]))*1.9
    # sheet with gentle light gradient (lit from top-left)
    shade=1.0+0.035*(0.5-(xx+yy)/2)
    sheet=c*shade[...,None]
    if a.tmode:
        st=a.st1 if k==1 else a.st2
        sheet=(1-(1-wheel(a.span*S_+a.hoff+a.kshift*(k-1)))*st)*shade[...,None]
    if k==1 and a.irid>0:
        # iridescent wash: pastel hue by angle about the sheet's centroid
        cy,cx=np.average(yy,weights=m),np.average(xx,weights=m)
        ang=np.arctan2(yy-cy,xx-cx); r=np.hypot(yy-cy,xx-cx)
        hue=(ang/(2*np.pi)+0.6*r+a.hoff)%1
        idx=hue*len(WHEEL); i0=idx.astype(int)%len(WHEEL); f=(idx-np.floor(idx))[...,None]
        wc=WHEEL[i0]*(1-f)+WHEEL[(i0+1)%len(WHEEL)]*f
        wc=1-(1-wc)*a.irid
        sheet=wc*shade[...,None]
    img=img*(1-m[...,None])+sheet*m[...,None]
    # rim light on top-left edge, darker rim bottom-right
    e=m-nshift(m,(0.9*s,0.9*s),order=1); lit=np.clip(-e,0,1); dark=np.clip(e,0,1)
    img=img+(1-img)*a.rim/(1+0.25*(k-1))*lit[...,None]
    img=img*(1-0.10*dark[...,None])
if a.npy: np.save(a.npy,img.astype(np.float32))
Image.fromarray((np.clip(img,0,1)*255).astype(np.uint8)).save(a.out)
print(H,W)
