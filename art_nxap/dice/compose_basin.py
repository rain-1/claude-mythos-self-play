import numpy as np
from PIL import Image, ImageDraw
from caption import caption
lin=np.load('bdisc_paint.png.lin.npy')
paper=np.array([0.992,0.985,0.975])
W=4096; D=3560
im=Image.fromarray((np.clip(lin,0,1)*255).astype(np.uint8)).resize((D,D),Image.LANCZOS)
can=Image.new('RGB',(W,W),tuple(int(c*255) for c in paper))
x0=(W-D)//2; y0=110
can.paste(im,(x0,y0))
d=ImageDraw.Draw(can)
cx,cy=x0+D//2,y0+D//2; r=26
d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=(244,128,112),width=7)
caption(can,W//2,y0+D+40,[('Every Spin Decides; Far Enough Out, None Is Favoured','title'),
 ('Where a simulated d7 lands for every initial spin: the centre is a drop with no spin (coral ring), the rim spins at 26 rad/s.','italic'),
 ('One colour per face, the same start every time. Where neighbouring spins disagree the colours mix, and an even mix is white paper.','small')],scale=0.92,align='center')
can.save('../every_spin_decides.png')
can.resize((900,900),Image.LANCZOS).save('cb_small.png')
