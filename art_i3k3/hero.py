import numpy as np, sys, time
sys.path.insert(0,'/home/user/claude-mythos-self-play/art_i3k3')
from common import *
from scipy.ndimage import gaussian_filter
from PIL import Image
t0=time.time()

OUT=4096; SS=1  # render internal at INT, downscale
INT=6144       # internal render size
S=INT
cx=0.42; half=2.88
xs=np.linspace(cx-half,cx+half,S); ys=np.linspace(-half,half,S)
X,Y=np.meshgrid(xs,ys); Z=(X+1j*Y).ravel()

# level-3 factor wells for the two potential families
A3,B3 = basin_split(3)      # 9 gold, 18 cyan
print("potentials...", time.time()-t0)
phiA=potential(Z,A3).reshape(S,S)
phiB=potential(Z,B3).reshape(S,S)
print("done pot", time.time()-t0)

def contour(phi,d,w):
    fr=np.abs(((phi/d)%1.0)-0.5)*2.0
    return np.exp(-(fr/w)**2)

# two interleaving equipotential families
dA=0.205; dB=0.205
lineA=contour(phiA,dA,0.115)*np.exp(-np.clip(phiA-0.14,0,None)*1.5)
lineB=contour(phiB,dB,0.115)*np.exp(-np.clip(phiB-0.14,0,None)*1.5)

img=np.zeros((S,S,3),np.float32)
for i in range(3):
    img[:,:,i]+=(lineA*GOLD[i]*0.95 + lineB*CYAN[i]*0.95).astype(np.float32)

# faint basin wash in the void (which factor's potential is lower = whose territory)
basin=phiA-phiB
washA=np.clip(-basin,0,None)*np.exp(-np.clip(phiA,0,None)*1.1)
washB=np.clip( basin,0,None)*np.exp(-np.clip(phiB,0,None)*1.1)
for i in range(3):
    img[:,:,i]+=(0.05*washA*GOLD[i]+0.05*washB*CYAN[i]).astype(np.float32)

def to_px(pts):
    px=(pts.real-(cx-half))/(2*half)*S
    py=(pts.imag+half)/(2*half)*S
    return px,py

# deep Cantor well-dust (level 5) as faint stars -> rewards native res
A5,B5=basin_split(5)
def dust(pts,col,amp,rad):
    px,py=to_px(pts)
    for x,y in zip(px,py):
        xi,yi=int(round(x)),int(round(y))
        if rad<=xi<S-rad and rad<=yi<S-rad:
            for dx in range(-rad,rad+1):
                for dy in range(-rad,rad+1):
                    img[yi+dy,xi+dx]+=col*amp*np.exp(-(dx*dx+dy*dy)/(rad*0.9))
print("dust...",time.time()-t0)
dust(A5,GOLD,0.16,2); dust(B5,CYAN,0.16,2)
# blazing seed-wells (level 3, the 27 preimages)
dust(A3,GOLD*1.2+0.25,1.25,5); dust(B3,CYAN*1.15+0.25,1.25,5)
# origin seed 0 — the point that seeds the whole preimage tree f^{-n}(0)
dust(np.array([0+0j]), np.array([1.0,1.0,0.95]), 1.7, 6)

# bloom on the bright loci (wells + saddle crossings)
lum=img.mean(2)
mask=np.clip((lum-0.5)/0.5,0,1)[...,None]*img
def fast_bloom(a,sig):
    ds=max(1,int(sig/6))
    small=a[::ds,::ds]
    b=gaussian_filter(small,(sig/ds,sig/ds,0))
    b=np.repeat(np.repeat(b,ds,0),ds,1)[:a.shape[0],:a.shape[1]]
    return gaussian_filter(b,(2,2,0))
print("bloom...",time.time()-t0)
img=img+0.7*fast_bloom(mask,90)+0.4*fast_bloom(mask,26)

img=filmic(img,k=1.55,g=0.87)
out=downscale(img,INT//OUT if INT%OUT==0 else 1)
if out.size!=(OUT,OUT):
    out=out.resize((OUT,OUT),Image.LANCZOS)
out.save('/home/user/claude-mythos-self-play/art_i3k3/hero_schism.png')
print("saved hero", out.size, time.time()-t0)
