"""Animation 2 — TRIALITY itself.
T is the order-3 isometry of the 24-cell that cyclically permutes its three
16-cells.  We apply T^t = exp(t logT) continuously for t in [0,3]: the polytope
rotates rigidly and, every one-third of the loop, lands back on the SAME 24-cell
-- but the colours have advanced 8_v -> 8_s -> 8_c.  The shape is invariant;
only the names cycle.  That is the outer automorphism, made visible."""
import numpy as np, sys, time
sys.path.insert(0,'triality')
import t4d, tdraw
from scipy.linalg import logm, expm
from PIL import Image

def main(S=560, ss=2, N=120, out='triality/anim_triality_cycle.gif'):
    T,V,cls,G=t4d.find_triality(); E,_=t4d.edges_of(V)
    L=np.real(logm(T))                      # real skew-symmetric generator
    R3=tdraw.rot3(0,1,0.18)@tdraw.rot3(1,2,-0.42)
    frames=[]; t0=time.time()
    for f in range(N):
        t=3.0*f/N                           # 0..3 ; T^3 = I  -> perfect loop
        R4=expm(t*L)
        im=tdraw.render_4d(V,E,cls,S=S,ss=ss,R4=R4,R3=R3,scale_frac=1.5,
            edge_bright=0.5,vtx_bright=0.80,vtx_r_frac=0.0058,gloss=(0.35,0.22),
            expo=1.15,edge_w=1.3,bloom_frac=(0.0006,0.005),zrange=(-0.6,0.6))
        frames.append(im.convert('P',palette=Image.ADAPTIVE,colors=128))
        if f%20==0: print('frame',f,round(time.time()-t0,1))
    frames[0].save(out,save_all=True,append_images=frames[1:],duration=60,loop=0,optimize=True,disposal=2)
    print('saved',out,round(time.time()-t0,1))

if __name__=="__main__":
    if len(sys.argv)>1 and sys.argv[1]=='preview':
        main(S=300,ss=1,N=45,out='triality/proto/_tri_prev.gif')
    else:
        main()
