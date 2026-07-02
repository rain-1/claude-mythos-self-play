import numpy as np, time
from PIL import Image
from lic import make_field, lic
from lic_color import color_lic
world=1.38
ch=[(-0.6,0.0,1),(0.6,0.0,-1),(0.0,0.7,-1),(0.0,-0.7,1),(-0.5,-0.55,-1),(0.5,0.55,1)]
field,C=make_field(ch)
t0=time.time()
S=2048
L,X,Y=lic(field,S,steps=95,ds=1.0,world=world,seed=4)
print("lic",round(time.time()-t0,1))
rgb=color_lic(L,field,X.astype(np.float64),Y.astype(np.float64),C,world,
              div_gain=0.75,licgain=1.7,base=0.10,glow_amp=1.25).astype(np.float32)
im=(np.clip(rgb,0,1)*255).astype(np.uint8)
Image.fromarray(im).save('03_lic.png')
Image.fromarray(im).resize((820,820),Image.LANCZOS).save('03_preview.png')
print("saved",round(time.time()-t0,1))
