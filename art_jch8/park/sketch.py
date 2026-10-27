import numpy as np,geom,sys
from PIL import Image,ImageDraw
def halfcircle(n,K=800):
    # great circle normal n: basis u (on equator, z=0), w
    u=geom.unit(np.cross(n,[0,0,1.])); w=np.cross(n,u)
    if w[2]<0: w=-w
    t=np.linspace(0,np.pi,K); return np.outer(np.cos(t),u)+np.outer(np.sin(t),w)
ims=[]
for f in sys.argv[1:]:
    x=np.load(f); lines,A,B,C=geom.config(x[:9].reshape(3,3),np.sort(x[9:12]),np.sort(x[12:15]))
    S=500; im=Image.new('RGB',(S,S),'white'); d=ImageDraw.Draw(im); R=230
    d.ellipse([S/2-R,S/2-R,S/2+R,S/2+R],outline='gray')
    for k,n in lines.items():
        P=halfcircle(n); pts=[(S/2+R*p[0]/(1+p[2]),S/2-R*p[1]/(1+p[2])) for p in P]
        d.line(pts,fill='red' if k=='p' else 'black',width=2)
    for k,c in C.items():
        c=c/(1+c[2]); d.ellipse([S/2+R*c[0]-5,S/2-R*c[1]-5,S/2+R*c[0]+5,S/2-R*c[1]+5],outline='blue',width=2)
    ims.append(im)
W=Image.new('RGB',(500*len(ims),500),'white')
for i,im in enumerate(ims): W.paste(im,(500*i,0))
W.save('sketch.png')
