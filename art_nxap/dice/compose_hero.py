import numpy as np, json, sys
from PIL import Image
from scene import tonemap
from caption import caption
img=np.load(sys.argv[1]); cfg=json.load(open('hero_final.json'))
im=Image.fromarray(tonemap(img.astype(np.float64),**cfg.get('tone',{})))
W=im.width
caption(im,int(W*0.055),int(W*0.045),[
 ('Five of Them Are Fair Without Symmetry','title'),
 ('Glass dice from d4 to d13 and a d20, in a ring by number of faces.','italic'),
 ('The odd ones are prisms cut to the length at which a simulated throw lands on every face equally often.','small'),
 ('d5  L/R 1.065     d7  1.62     d9  1.88     d11  2.10     d13  2.33','small'),
],scale=1.0)
im.save(sys.argv[2])
