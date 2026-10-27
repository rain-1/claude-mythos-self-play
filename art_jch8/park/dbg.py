import numpy as np, arrangement as AR, sys
from PIL import Image, ImageDraw
S=700;R=330;c=S/2
ims=[]
for b in map(float,sys.argv[1:]):
    paths,lines,C,cmid,order=AR.build(bend=b)
    im=Image.new('RGB',(S,S),'white');d=ImageDraw.Draw(im)
    for k in order:
        P=paths[k]; d.line([(c+R*x,c-R*y) for x,y in P],fill='red' if k=='p' else 'black',width=2)
    for k,v in C.items():
        q=AR.stereo(v[None])[0]; d.ellipse([c+R*q[0]-6,c-R*q[1]-6,c+R*q[0]+6,c-R*q[1]+6],outline='blue' if k!=cmid else 'green',width=3)
    q=AR.P_MID; d.ellipse([c+R*q[0]-4,c-R*q[1]-4,c+R*q[0]+4,c-R*q[1]+4],fill='orange')
    ims.append(im)
W=Image.new('RGB',(S*len(ims),S));[W.paste(im,(S*i,0)) for i,im in enumerate(ims)];W.save('dbg.png')
