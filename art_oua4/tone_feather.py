import numpy as np, sys
from PIL import Image
from scipy.ndimage import gaussian_filter
tag=sys.argv[1] if len(sys.argv)>1 else ""
out=sys.argv[2] if len(sys.argv)>2 else f"feather{tag}.png"
acc=np.load(f"/home/user/claude-mythos-self-play/art_oua4/feather_acc{tag}.npy")
S=acc.shape[0]
sf=S/1400.0
# log-compress
a=np.log1p(acc); a/=a.max()
# bloom from the bright convergence region (use raw acc for the hot tip)
hot=acc/acc.max()
bloom1=gaussian_filter(hot,sigma=2.5*sf)
bloom2=gaussian_filter(hot,sigma=7*sf)
glow=0.6*bloom1+0.9*bloom2
glow/=glow.max()+1e-9
# tone curve on structure
t=1-np.exp(-2.6*a*2.0); t=np.clip(t,0,1)**0.82
# palette: deep void -> teal -> green-gold -> warm gold -> white
stops=[(0.00,(3,6,12)),(0.18,(8,34,46)),(0.42,(20,110,120)),(0.66,(70,180,150)),
       (0.84,(225,195,120)),(1.001,(255,248,225))]
img=np.zeros((S,S,3))
for (lo,c0),(hi,c1) in zip(stops[:-1],stops[1:]):
    m=(t>=lo)&(t<hi); f=((t[m]-lo)/(hi-lo))[:,None]
    img[m]=np.array(c0)*(1-f)+np.array(c1)*f
# add bloom as warm-gold halo
halo=np.array([255,225,150])
img+= (glow[...,None]**1.3)*halo*0.55
img=np.clip(img,0,255)
Image.fromarray(img.astype(np.uint8)).save(f"/home/user/claude-mythos-self-play/art_oua4/{out}")
print("saved",out, img.shape)
