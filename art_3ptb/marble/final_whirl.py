import numpy as np, time, sys
sys.path.insert(0,'../wc')
from PIL import Image
from design3 import build, INK
from design import shade
from wc import hexrgb
N=int(sys.argv[1]); v=int(sys.argv[2]); out=sys.argv[3]; ss=2
pal=np.array([hexrgb(c) for c in INK])
g=(np.arange(N*ss)+0.5)/(N*ss); xs,ys=np.meshgrid(g,g)
t=time.time()
B=build(v)
print(len(B.ops),'ops')
ink,tt=B.render(xs,ys,0)
del xs,ys
print(time.time()-t)
Image.fromarray((shade(ink,tt,pal,N,ss)*255+0.5).astype(np.uint8)).save(out)
