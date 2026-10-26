import numpy as np
from PIL import Image
from caption import caption
lin=np.load('bwin_paint.png.lin.npy')
im=Image.fromarray((np.clip(lin,0,1)*255).astype(np.uint8))
W=im.width; band=430
can=Image.new('RGB',(W,W+band),(253,251,249)); can.paste(im,(0,0))
caption(can,int(W*0.04),W+60,[('Where Deciding Frays','title'),
 ('The same d7, the same start: a window of spins ω_x from −16 to −6 rad/s, ω_y from −5 to 5, at 4.2 million throws.','italic'),
 ('Each thread of colour is a family of throws that agree; between them, a hair’s difference in the wrist changes the face.','small')],scale=0.9)
can.save('../where_deciding_frays.png')
can.resize((800,int(800*can.height/W)),Image.LANCZOS).save('z_small.png')
im.crop((1400,1400,2600,2600)).save('z_crop.png')
