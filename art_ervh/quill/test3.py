import numpy as np, json, time
from PIL import Image
import quill as Q, tiles as T
d5=json.load(open('../math_poly/runs/t5.json'))['found']; d7=json.load(open('../math_poly/runs/e7.json'))['found']
d9=json.load(open('../math_poly/runs/t9.json'))['found']
rng=np.random.default_rng(2)
pick=[d5[i] for i in rng.choice(len(d5),3,replace=False)]+[d7[i] for i in rng.choice(len(d7),3,replace=False)]+[d9[i] for i in range(3)]
S=520; g=80; tilt=30; cs=np.cos(np.radians(tilt))
Sy=S/cs; gy=g/cs
N=(int(Sy*3+gy*4), S*3+g*4)
H,A=T.card(N)
for i,p in enumerate(pick):
    r,c=divmod(i,3); ox=g+c*(S+g); oy=gy+r*(Sy+gy)
    T.tile(H,A,np.array(p['verts']),ox,oy,S,T.WARM[i%5],T.COOL[i%6:]+T.COOL[:i%6],Sy=Sy)
img=Q.render(H,A,tilt_deg=tilt,spp=4,light=(-0.65,0.30,0.70),amb=(0.62,0.62,0.70),sun=(0.75,0.72,0.68))
Image.fromarray(Q.tonemap(img)).save('proto/t3.png')
for i,p in enumerate(pick): print(len(p['verts']),p['turns'],round(p['clearance'],3))
