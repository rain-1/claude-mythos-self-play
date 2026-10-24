import numpy as np
from collections import defaultdict
def names(R):
    # essentially distinct representations N = a^2+b^2 with a>=b>=0
    rep=defaultdict(list)
    for a in range(0,2*R):
        for b in range(0,a+1):
            rep[a*a+b*b].append((a,b))
    return rep
def chart(R):
    rep=names(R)
    xs=np.arange(-R,R+1)
    X,Y=np.meshgrid(xs,xs)
    N=X*X+Y*Y
    k=np.vectorize(lambda n: len(rep[n]))(N)
    return X,Y,N,k
if __name__=='__main__':
    from PIL import Image
    for R in (30,40):
        X,Y,N,k=chart(R)
        pal=np.array([[250,246,240],[250,246,240],[244,150,165],[250,215,120],[140,215,180],[150,180,245],[200,160,235],[245,140,120]],np.uint8)
        img=pal[np.clip(k,0,7)]
        Image.fromarray(img).resize((img.shape[1]*8,img.shape[0]*8),Image.NEAREST).save(f'/tmp/claude-0/chart{R}.png')
        print(R,np.bincount(k.ravel()))
