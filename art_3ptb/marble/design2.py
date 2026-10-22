import numpy as np, time, sys
sys.path.insert(0,'../wc')
from PIL import Image
from marble import Bath
from wc import hexrgb, fnoise
from design import shade
INK=['#fbf7f0','#f4aabd','#fbcfa0','#f8e39a','#b7e5c8','#acd2f2','#cdbdf0','#f29a8c','#ffffff']
def build(v,seed=3):
    rng=np.random.default_rng(seed)
    B=Bath()
    # hex lattice of bullseyes; colour sequence walks the wheel by column
    sp=0.085
    cols=[1,2,3,4,5,6]
    pts=[]
    for i in range(-2,16):
        for j in range(-2,16):
            x=(i+0.5*(j%2))*sp; y=j*sp*0.866
            pts.append((x,y,i,j))
    rng.shuffle(pts)
    for x,y,i,j in pts:
        c=cols[(i+j)%6]; c2=cols[(i+j+2)%6]
        seq=[c,8,c2,8,c] if v!=2 else [c,8,c]
        for q,cc in enumerate(seq): B.drop(x,y,0.022,cc)
    if v in (0,1,2):
        B.wave((0.5,0.5),(1,0),0.035,0.25)      # gentle waves
        B.comb((0.5,0.5),(0,1),0.045,0.010,0.06) # gel
        B.comb((0.53,0.5),(0,-1),0.045,0.010,0.06) # git
    if v in (1,2):
        B.comb((0.5,0.5),(1,0),0.018,0.004,0.02) # fine comb -> nonpareil
    if v==2:
        B.wave((0.5,0.5),(0,1),0.02,0.07)
    if v==3:
        B.vortex((0.5,0.5),0.9,0.3,0.12)
        B.vortex((0.5,0.5),-0.6,0.12,0.06)
    return B
if __name__=='__main__':
    N=int(sys.argv[1]); ss=2
    pal=np.array([hexrgb(c) for c in INK])
    g=(np.arange(N*ss)+0.5)/(N*ss); xs,ys=np.meshgrid(g,g)
    for v in map(int,sys.argv[2:]):
        ink,tt=build(v).render(xs,ys,0)
        Image.fromarray((shade(ink,tt,pal,N,ss)*255).astype(np.uint8)).save(f'../proto/me{v}.png')
