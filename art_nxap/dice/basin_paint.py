import numpy as np, sys
from PIL import Image
from scipy.ndimage import gaussian_filter, zoom
B=np.load(sys.argv[1]); out=sys.argv[2]; up=int(sys.argv[3]) if len(sys.argv)>3 else 1
sig=float(sys.argv[4]) if len(sys.argv)>4 else 1.3
B=np.where(B<0,-1-B,B)
nf=int(B.max())+1
cols=np.array([(0.98,0.62,0.68),(1.0,0.78,0.62),(1.0,0.92,0.58),(0.76,0.93,0.60),(0.62,0.92,0.82),(0.62,0.80,1.0),(0.82,0.70,1.0)])[:nf]
A=-np.log(cols)*1.15
H,W=B.shape
P=np.zeros((nf,H*up,W*up),np.float32)
for f in range(nf):
    m=(B==f).astype(np.float32)
    if up>1: m=zoom(m,up,order=0)
    P[f]=gaussian_filter(m,sig*up)
pi=P.max(0)
pur=np.clip((pi-1/nf)/(1-1/nf),0,1)**1.6
Am=np.einsum('fhw,fc->hwc',P,A)/np.maximum(P.sum(0),1e-6)[...,None]
rng=np.random.default_rng(3)
grain=gaussian_filter(rng.standard_normal((H*up,W*up)),1.0)*0.04+gaussian_filter(rng.standard_normal((H*up,W*up)),6)*0.05
D=Am*pur[...,None]*(1+grain[...,None])
paper=np.array([0.992,0.985,0.975])
img=paper*np.exp(-D)
np.save(out+'.lin.npy',img.astype(np.float32))
Image.fromarray((np.clip(img,0,1)**(1/1.0)*255).astype(np.uint8)).save(out)
