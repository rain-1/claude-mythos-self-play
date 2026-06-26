"""Animation 1 — the 24-cell turning in 4D (isoclinic double rotation).
A smooth Clifford rotation: both invariant planes turn at the same rate, the
hypnotic 'rigid' spin unique to 4D. Three 16-cells in azure/gold/rose."""
import numpy as np, sys, time
sys.path.insert(0,'triality')
import t4d, tdraw
from PIL import Image

def frame(V,E,cls,th,S,ss):
    # isoclinic: rotate planes (0,1) and (2,3) together; tilt (1,2) slowly for a 4D feel
    R4=tdraw.rot4(0,1,th)@tdraw.rot4(2,3,th)@tdraw.rot4(1,3,0.30)
    R3=tdraw.rot3(0,1,0.18)@tdraw.rot3(1,2,-0.42)
    return tdraw.render_4d(V,E,cls,S=S,ss=ss,R4=R4,R3=R3,scale_frac=1.5,
        edge_bright=0.5,vtx_bright=0.78,vtx_r_frac=0.0055,gloss=(0.35,0.22),
        expo=1.15,edge_w=1.3,bloom_frac=(0.0006,0.005),zrange=(-0.55,0.55))

def main(S=560, ss=2, N=90, out='triality/anim_24cell_spin.gif'):
    V,cls=t4d.cell24_weights(); E,_=t4d.edges_of(V)
    frames=[]; t0=time.time()
    for f in range(N):
        th=2*np.pi*f/N
        im=frame(V,E,cls,th,S,ss).convert('P',palette=Image.ADAPTIVE,colors=128)
        frames.append(im)
        if f%15==0: print('frame',f,round(time.time()-t0,1))
    frames[0].save(out,save_all=True,append_images=frames[1:],duration=70,loop=0,optimize=True,disposal=2)
    print('saved',out,round(time.time()-t0,1))

if __name__=="__main__":
    if len(sys.argv)>1 and sys.argv[1]=='preview':
        main(S=300,ss=1,N=36,out='triality/proto/_spin_prev.gif')
    else:
        main()
