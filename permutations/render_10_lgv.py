import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, gaussian_filter1d
from figkit import annotate
from lgv import lgv_determinant_check
import colorsys, time, sys

def sample_walkers(n, T, sweeps, seed=0):
    rng=np.random.default_rng(seed)
    x=np.zeros((n,T+1),dtype=np.int64)
    base=2*np.arange(n)[:,None]
    x=base + (np.arange(T+1)%2)[None,:]      # minimal valid non-colliding init
    t0=time.time()
    for s in range(sweeps):
        ks=rng.integers(0,n,size=n*T); tsel=rng.integers(1,T,size=n*T)
        for k,t in zip(ks,tsel):
            if x[k,t-1]==x[k,t+1]:
                v=x[k,t-1]
                lo=x[k-1,t] if k>0 else -10**9
                hi=x[k+1,t] if k<n-1 else 10**9
                opts=[o for o in (v-1,v+1) if lo<o<hi]
                if opts: x[k,t]=opts[rng.integers(0,len(opts))]
        if s%(max(1,sweeps//4))==0: print("  sweep",s,"t=%.1f"%(time.time()-t0)); sys.stdout.flush()
    # verify
    steps_ok=np.all(np.abs(np.diff(x,axis=1))==1)
    noncol=np.all(np.diff(x,axis=0)>0)
    ends_ok=np.all(x[:,0]==base[:,0]) and np.all(x[:,T]==base[:,0])
    print("valid: steps±1",steps_ok,"non-colliding",noncol,"endpoints",ends_ok)
    return x

def render(n=28, T=560, sweeps=400, S=1700, seed=4):
    det,cnt=lgv_determinant_check()
    x=sample_walkers(n,T,sweeps,seed)
    H=int(S*0.62); W=S
    acc=np.zeros((H,W,3))
    ymin=x.min(); ymax=x.max(); pad=2
    def toY(v): return (1-(v-ymin+pad)/(ymax-ymin+2*pad))*(H-1)
    ts=np.linspace(0,W-1,T+1)
    for k in range(n):
        y=np.array([toY(v) for v in x[k]])
        ysm=gaussian_filter1d(y.astype(float),sigma=2.5)
        r,g,b=colorsys.hls_to_rgb((0.55+0.4*k/n)%1,0.6,0.92); col=np.array([r,g,b])
        xi=np.linspace(0,W-1,T*2); yi=np.interp(xi,ts,ysm)
        ix=np.clip(xi.astype(int),0,W-2); iy=np.clip(yi.astype(int),0,H-2)
        dx=xi-ix; dy=yi-iy
        for ox,oy,wt in [(0,0,(1-dx)*(1-dy)),(1,0,dx*(1-dy)),(0,1,(1-dx)*dy),(1,1,dx*dy)]:
            np.add.at(acc.reshape(-1,3),(iy+oy)*W+(ix+ox),wt[:,None]*col*0.5)
    acc/=np.percentile(acc[acc>0],99.6); acc=np.clip(acc,0,1)
    img=acc.copy()
    for c in range(3): img[...,c]+=0.55*gaussian_filter(acc[...,c],1.4)+0.3*gaussian_filter(acc[...,c],5)
    img=np.clip(img,0,1)**0.92
    out=Image.fromarray((img*255).astype(np.uint8))
    body=("%d 'vicious walkers' - random up/down paths pinned at fixed positions at both ends and free between, but "
          "forbidden ever to touch (non-intersecting lattice paths), sampled uniformly by corner-flip Glauber. The "
          "Lindstrom-Gessel-Viennot lemma says the number of such non-intersecting families equals a single DETERMINANT "
          "of one-path counts (verified here: det = %d = brute-force count) - and the signed cancellation in that "
          "determinant is exactly a sum over PERMUTATIONS, every intersecting family killed by its sign-flipped partner. "
          "Held apart, the walkers fill a band whose top and bottom edges fluctuate by the Tracy-Widom law - random-matrix "
          "universality, and the very same non-intersecting-paths picture that underlies the plane-partition / lozenge "
          "tilings of the main set."%(n,det))
    fig=annotate(out,"FIGURE 10 - LINDSTROM-GESSEL-VIENNOT","Paths That May Never Touch",body,accent=(110,200,225))
    fig.save("10_lgv.png"); print("saved",fig.size)

if __name__=="__main__": render(sweeps=int(sys.argv[1]) if len(sys.argv)>1 else 400)
