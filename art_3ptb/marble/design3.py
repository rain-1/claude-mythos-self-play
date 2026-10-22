import numpy as np, time, sys
sys.path.insert(0,'../wc')
from PIL import Image
from marble import Bath
from wc import hexrgb
from design import shade
INK=['#fbf7f0','#f4aabd','#fbcfa0','#f8e39a','#b7e5c8','#acd2f2','#cdbdf0','#f29a8c','#ffffff']
def build(v,seed=3,sp=0.07,r=0.02):
    rng=np.random.default_rng(seed)
    B=Bath()
    pts=[]
    for i in range(-3,20):
        for j in range(-3,22):
            x=(i+0.5*(j%2))*sp; y=j*sp*0.866
            pts.append((x,y,i,j))
    rng.shuffle(pts)
    cols=[1,2,3,4,5,6]
    for x,y,i,j in pts:
        a=np.arctan2(y-0.5,x-0.5); k=int(((a/(2*np.pi))%1)*6+0.5*((i+j)%2))%6
        c=cols[k]; c2=cols[(k+1)%6]
        for cc in [c,8,c2,8,c]: B.drop(x,y,r,cc)
    if v==0:
        for rr,z in ((0.07,-0.9),(0.17,1.0),(0.29,-1.0),(0.42,1.0)): B.vortex((0.5,0.5),z,rr,0.05)
    if v==1:
        for rr,z in ((0.10,1.3),(0.25,-1.1),(0.42,0.9)): B.vortex((0.5,0.5),z,rr,0.07)
    if v==2:
        B.vortex((0.5,0.5),0.9,0.3,0.12); B.vortex((0.5,0.5),-0.6,0.12,0.06)
        for k in range(5):
            a=-np.pi/2+2*np.pi*k/5
            B.vortex((0.5+0.33*np.cos(a),0.5+0.33*np.sin(a)),0.5,0.06,0.04)
    if v==3:
        for k in range(6):
            a=2*np.pi*k/6
            B.vortex((0.5+0.25*np.cos(a),0.5+0.25*np.sin(a)),(-1)**k*0.7,0.1,0.06)
        B.vortex((0.5,0.5),0.8,0.08,0.05)
    return B
if __name__=='__main__':
    N=int(sys.argv[1]); ss=2
    pal=np.array([hexrgb(c) for c in INK])
    g=(np.arange(N*ss)+0.5)/(N*ss); xs,ys=np.meshgrid(g,g)
    for v in map(int,sys.argv[2:]):
        ink,tt=build(v).render(xs,ys,0)
        Image.fromarray((shade(ink,tt,pal,N,ss)*255).astype(np.uint8)).save(f'../proto/mf{v}.png')
