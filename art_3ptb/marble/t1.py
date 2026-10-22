import numpy as np, time, sys
sys.path.insert(0,'../wc')
from PIL import Image
from marble import Bath
from wc import hexrgb
INK=['#fbf6ee','#f6b3c4','#fbd4a6','#f9e7a0','#bfe8cf','#b5d8f4','#d3c4f2','#f59a8a']
pal=np.array([hexrgb(c) for c in INK])
N=1024; ss=2
g=(np.arange(N*ss)+0.5)/(N*ss)
xs,ys=np.meshgrid(g,g)
B=Bath()
rng=np.random.default_rng(1)
# bullseye
for i in range(26): B.drop(0.5,0.5,0.045,1+i%6)
# polygons rings
for n,R,ink in ((10,0.30,3),(6,0.22,5),(5,0.15,1)):
    for j in range(n):
        a=-np.pi/2+2*np.pi*j/n
        for q in range(3): B.drop(0.5+R*np.cos(a),0.5+R*np.sin(a),0.022,[ink,7,0][q] if q<2 else 6)
B.vortex((0.5,0.5),0.35,0.25,0.12)
B.comb((0.5,0.5),(1,0),0.03,0.01,0.08)
t=time.time()
ink,tt=B.render(xs,ys,0)
print(time.time()-t)
rgb=pal[ink].reshape(N,ss,N,ss,3).mean((1,3))
Image.fromarray((rgb*255).astype(np.uint8)).save('../proto/m1.png')
