import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, gaussian_filter1d
from eg import uniform_syt_staircase, word_from_Q, trajectories
from sortnet import is_reduced_reversal
from figkit import annotate
import colorsys, time, sys

def render(n=120, S=1600, seed=2):
    t0=time.time(); rng=np.random.default_rng(seed)
    Q=uniform_syt_staircase(n,rng); w=word_from_Q(Q)
    assert is_reduced_reversal(w,n)
    print("sampled exact uniform word len",len(w),"t=%.1f"%(time.time()-t0))
    pos=trajectories(w,n); L=pos.shape[1]-1
    poss=gaussian_filter1d(pos,sigma=max(1,L*0.013),axis=1)
    W=S; acc=np.zeros((W,W,3))
    ts=np.linspace(0,1,L+1)
    def draw(wire,col,wt_scale,nseg):
        x=ts*(W-1); y=(1-poss[wire]/(n-1))*(W-1)
        xi=np.linspace(0,W-1,nseg); yi=np.interp(xi,x,y)
        ix=np.clip(xi.astype(int),0,W-2); iy=np.clip(yi.astype(int),0,W-2)
        dx=xi-ix; dy=yi-iy
        for ox,oy,wt in [(0,0,(1-dx)*(1-dy)),(1,0,dx*(1-dy)),(0,1,(1-dx)*dy),(1,1,dx*dy)]:
            np.add.at(acc.reshape(-1,3),(iy+oy)*W+(ix+ox),wt[:,None]*col*wt_scale)
    # dim woven mesh (all wires)
    for wire in range(n):
        r,g,b=colorsys.hls_to_rgb((wire/n*0.92)%1,0.55,0.85)
        draw(wire,np.array([r,g,b]),0.5,L*2)
    acc/=np.percentile(acc[acc>0],99.6); acc=np.clip(acc,0,1)
    mesh=(acc*0.55)
    # highlighted individual trajectories (each a sine curve)
    hi=np.zeros((W,W,3))
    saved=acc; acc=hi
    hilites=np.linspace(int(n*0.1),int(n*0.9),6).astype(int)
    hcols=[(1,0.85,0.4),(0.5,0.95,1.0),(1,0.5,0.8),(0.7,1,0.6),(0.7,0.7,1),(1,0.7,0.4)]
    for wire,c in zip(hilites,hcols):
        draw(wire,np.array(c),1.0,L*3)
    hi/=np.percentile(hi[hi>0],99.5); hi=np.clip(hi,0,1)
    img=mesh+hi*1.1
    for k in range(3): img[...,k]+=0.5*gaussian_filter(hi[...,k],1.6)+0.25*gaussian_filter(mesh[...,k],1.2)
    img=np.clip(img,0,1)**0.9
    out=Image.fromarray((img*255).astype(np.uint8))
    body=("A UNIFORM random sorting network on n=%d wires: a uniformly chosen shortest sequence of adjacent swaps that "
          "reverses the order (a reduced word for the longest permutation w0). Sampled EXACTLY - not by slow Markov "
          "chain - via a uniform standard Young tableau of staircase shape (the GNW hook walk) mapped through the "
          "verified Edelman-Greene bijection (round-trip checked on all reduced words of S4 and S5). Each wire's path "
          "is a trajectory; Angel-Holroyd-Romik-Virag proved that as n grows these converge to SINE CURVES (six "
          "highlighted), and the swarm fills an ellipse - the shadow of great circles on a sphere."%n)
    fig=annotate(out,"FIGURE 6 - RANDOM SORTING NETWORKS","The Sine Curves of a Perfect Shuffle",body,accent=(120,210,230))
    fig.save("06_sorting_network.png"); print("saved",fig.size,"t=%.1f"%(time.time()-t0))

if __name__=="__main__": render(seed=int(sys.argv[1]) if len(sys.argv)>1 else 2)
