import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
import pcolor as C

Pe=np.load('hero_field_8192.npy')
pal=C.cyclic_palette('thinfilm')
rgb=C.compose_v3(Pe, pal, k=2.5, gamma=1.05, sat_lo=0.06, sat_hi=0.55,
                 blaze=0.86, blaze_soft=0.92).astype(np.float32)
del Pe
lum=rgb.max(-1)
mask=np.clip((lum-0.72)/0.28,0,1)[...,None]*rgb    # only true foci bloom
b1=np.stack([gaussian_filter(mask[...,c],6) for c in range(3)],-1)
b2=np.stack([gaussian_filter(mask[...,c],20) for c in range(3)],-1)
out=rgb + 0.30*b1 + 0.20*b2
out=1-np.exp(-1.25*out)
out=np.clip(out,0,1)
out=(out[0::2,0::2]+out[1::2,0::2]+out[0::2,1::2]+out[1::2,1::2])*0.25
im=(np.clip(out,0,1)*255).astype(np.uint8)
Image.fromarray(im).save('01_hero.png')
Image.fromarray(im).resize((900,900),Image.LANCZOS).save('01_hero_final_prev.png')
print("done", im.shape)
