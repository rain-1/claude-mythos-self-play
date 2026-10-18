import numpy as np, time
from PIL import Image
import quill as Q, tiles as T
S=560; g=70; N=(S*3+g*4, S*3+g*4)
H,A=T.card(N)
polys=[np.array([[0,0.06],[1,0.06],[0.5,0.06+np.sqrt(3)/2]]), T.zigzag(5), T.zigzag(7),
       T.zigzag(9), None, T.zigzag(11), T.zigzag(13)[:, ::-1], T.zigzag(15), T.zigzag(17)]
for i,p in enumerate(polys):
    r,c=divmod(i,3); ox=g+c*(S+g); oy=g+r*(S+g)
    if p is None:
        T.tile(H,A,np.zeros((4,2)),ox,oy,S,(1,0.8,0.6),T.COOL,frame_col=(1.0,0.55,0.52),exception=True)
    else:
        T.tile(H,A,p,ox,oy,S,T.WARM[i%5],T.COOL[i%6:]+T.COOL[:i%6])
t=time.time(); img=Q.render(H,A,spp=4,light=(-0.65,0.30,0.70),amb=(0.62,0.62,0.70),sun=(0.75,0.72,0.68)); print(time.time()-t)
Image.fromarray(Q.tonemap(img)).save('proto/t2.png')
