import numpy as np, sys
from PIL import Image
def tone(fn,W,H,expo=1.0,white=1.25,out=None):
    a=np.fromfile(fn,dtype=np.float32).reshape(H,W,3)*expo
    L=0.2126*a[...,0]+0.7152*a[...,1]+0.0722*a[...,2]
    Lt=L*(1+L/white**2)/(1+L); a=a*(Lt/np.maximum(L,1e-6))[...,None]
    a=np.clip(a,0,1)**(1/2.2)
    im=Image.fromarray((a*255+0.5).astype(np.uint8)); 
    if out: im.save(out)
    return im
if __name__=='__main__':
    fn,W,H=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]); e=float(sys.argv[4]) if len(sys.argv)>4 else 1
    tone(fn,W,H,e,out=fn.replace('.f32','.png'))
