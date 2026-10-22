import numpy as np, time, sys
sys.path.insert(0,'../wc')
from PIL import Image
from marble import Bath
from wc import hexrgb, fnoise
INK=['#fbf6ee','#f4aabd','#fbcfa0','#f8e39a','#b7e5c8','#acd2f2','#cdbdf0','#f29a8c','#ffffff']
def build(variant=0,seed=2):
    rng=np.random.default_rng(seed)
    B=Bath()
    # battal stone ground: random drops
    for i in range(500):
        r=0.06*(1-i/500)**0.6+0.012
        B.drop(rng.uniform(-0.05,1.05),rng.uniform(-0.05,1.05),r,rng.choice([1,2,3,4,5,6]))
    # three bullseye flowers (Euclid: pentagon, hexagon, decagon) with polygon rings
    cen=[(0.30,0.36,5,[1,6,8,1,6,8,1,6]),(0.70,0.40,6,[5,4,8,5,4,8,5,4]),(0.48,0.72,10,[3,2,8,3,2,8,3,2])]
    for cx,cy,n,cols in cen:
        for i,c in enumerate(cols): B.drop(cx,cy,0.05,c)
        for j in range(n):
            a=-np.pi/2+2*np.pi*j/n
            for q,c in enumerate((7,8,cols[0])): B.drop(cx+0.20*np.cos(a),cy+0.20*np.sin(a),0.022 if q<2 else 0.018,c)
    if variant>=1:
        B.comb((0.5,0.0),(0,1),0.035,0.012,0.055)
    if variant>=2:
        for cx,cy,n,cols in cen: B.vortex((cx,cy),0.5,0.16,0.07)
    return B
def shade(ink,tt,pal,N,ss,seed=0):
    rgb=pal[ink]
    edge=np.clip((tt-0.90)/0.1,0,1)*(ink>0)
    rgb=rgb*(1-0.10*edge[...,None])
    rgb=rgb.reshape(N,ss,N,ss,3).mean((1,3))
    rng=np.random.default_rng(seed)
    h=fnoise(N,N,3.0*N/4096+0.6,rng)*0.6+fnoise(N,N,10*N/4096+1,rng)*0.4
    gy,gx=np.gradient(h)
    sh=1+0.025*(gx-gy)/(gx-gy).std()
    return np.clip(rgb*sh[...,None],0,1)
if __name__=='__main__':
    N=int(sys.argv[1]); ss=2; v=int(sys.argv[2])
    pal=np.array([hexrgb(c) for c in INK])
    g=(np.arange(N*ss)+0.5)/(N*ss); xs,ys=np.meshgrid(g,g)
    t=time.time(); ink,tt=build(v).render(xs,ys,0); print(time.time()-t)
    Image.fromarray((shade(ink,tt,pal,N,ss)*255).astype(np.uint8)).save(f'../proto/md{v}.png')
