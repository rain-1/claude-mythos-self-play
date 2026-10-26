import numpy as np, json
from PIL import Image
from scene import tonemap
from caption import caption
img=np.load('strobe_3600.npy').astype(np.float64)
im=Image.fromarray(tonemap(img,white=1.3))
W=im.width
caption(im,int(W*0.035),int(W*0.025),[
 ('Ten Moments of One Throw','title'),
 ('One simulated throw of a fair d7, photographed ten times on its way to face 5: thrown, tumbling, hopping, coming to rest.','italic'),
 ('Every moment follows from the one before it. Hue walks with time, strawberry to bubblegum.','small')],scale=0.8)
im.save('../ten_moments_of_one_throw.png')
im.resize((1200,int(1200*im.height/W)),Image.LANCZOS).save('s_small.png')
im.crop((1200,500,2400,1300)).save('s_crop.png')
