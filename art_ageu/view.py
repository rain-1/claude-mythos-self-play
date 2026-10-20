import numpy as np,sys
from PIL import Image
import porcelain as P, bg
SPD='/tmp/claude-0/-home-user-claude-mythos-self-play/1158cf4a-3a4a-5fc9-95bf-b9f6e7ef9209/scratchpad/'
img=np.load(SPD+sys.argv[1]+'.npy'); sun=np.load(SPD+sys.argv[1]+'_sun.npy')
H,W=img.shape[:2]
ex=float(sys.argv[2]) if len(sys.argv)>2 else 1.0
a=img[...,3:4]
sky=bg.sky(W,H,sun[:2],sun_r=0.045)**2.2
lin=img[...,:3]*ex+sky*(1-a)
x=np.maximum(lin,0); lum=x.mean(2,keepdims=True)
k=np.where(lum>0.8,(0.8+(1-np.exp(-(lum-0.8)*2.5))*0.2)/np.maximum(lum,1e-6),1.0)
x=np.clip(x*k,0,1)**(1/2.2)
x=x*255+np.random.default_rng(0).random(x.shape)-0.5
Image.fromarray(np.clip(np.round(x),0,255).astype(np.uint8)).save(SPD+sys.argv[1]+'.png')
