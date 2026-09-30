import numpy as np, sys
from PIL import Image
from sympy import divisors, divisor_sigma
G=1024
tiles=[]
for n in [60,72,90,96]:
    H=np.fromfile(f'data/c{n}.bin',np.float32).reshape(G,G)
    s=float(divisor_sigma(n))
    # pinned view, crop to occupied box
    ys,xs=np.nonzero(H); 
    c=H[ys.min():ys.max()+1, xs.min():xs.max()+1]
    t=(c/np.percentile(c[c>0],99.5)).clip(0,1)**0.7
    im=Image.fromarray((255*(1-t)).astype(np.uint8)[::-1]).resize((512,512),Image.LANCZOS)
    tiles.append(im)
    # where is origin relative
    print(n, 'bbox x', (xs.min()-G/2)/G*2*s, (xs.max()-G/2)/G*2*s, 'y',(ys.min()-G/2)/G*2*s,(ys.max()-G/2)/G*2*s)
W=Image.new('L',(1024,1024),255)
for i,im in enumerate(tiles): W.paste(im,((i%2)*512,(i//2)*512))
W.save('proto/pinned_grid.png')
