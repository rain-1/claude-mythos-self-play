import numpy as np, sys
from PIL import Image
f,W,H,out=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),sys.argv[4]; ex=float(sys.argv[5]) if len(sys.argv)>5 else 1.0
x=np.fromfile(f,np.float32).reshape(H,W,3)*ex
wp=1.2; y=x*(1+x/wp**2)/(1+x)          # extended Reinhard
y=np.clip(y,0,1)**(1/2.2)
Image.fromarray((y*255).astype(np.uint8)).save(out)
