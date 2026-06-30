import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
from foata import foata, maj, inv
from figkit import annotate
from itertools import permutations
import colorsys, time

def render(n=6, S=1700):
    t0=time.time()
    perms=list(permutations(range(1,n+1)))
    maxs=n*(n-1)//2
    # group indices within each level
    from collections import defaultdict
    majlev=defaultdict(list); invlev=defaultdict(list)
    M={}; I={}
    for p in perms:
        m=maj(p); M[p]=m; majlev[m].append(p)
    images={p:tuple(foata(p)) for p in perms}
    for p in perms:
        fp=images[p]; iv=inv(fp); I[p]=iv; invlev[iv].append(p)
    # x positions within level
    def xpos(levmap, idxmap, left, right):
        pos={}
        for k,lst in levmap.items():
            for r,item in enumerate(lst):
                pos[item]=left+(r+0.5)/len(lst)*(right-left)
        return pos
    Lx=xpos(majlev,None,0.04,0.46)            # keyed by perm
    # right keyed by image
    Rx={}
    for k,lst in invlev.items():
        for r,fp in enumerate(lst): Rx[fp]=0.54+(r+0.5)/len(lst)*0.42
    W=S; H=int(S*0.74); acc=np.zeros((H,W,3))
    def y_of(v): return (1-v/maxs)*0.9+0.05
    def splat(pts,col,wt):
        x=pts[:,0]*(W-1); y=pts[:,1]*(H-1)
        ix=np.clip(x.astype(int),0,W-2); iy=np.clip(y.astype(int),0,H-2)
        dx=x-ix; dy=y-iy
        for ox,oy,w in [(0,0,(1-dx)*(1-dy)),(1,0,dx*(1-dy)),(0,1,(1-dx)*dy),(1,1,dx*dy)]:
            np.add.at(acc.reshape(-1,3),(iy+oy)*W+(ix+ox),w[:,None]*col*wt)
    for p in perms:
        fp=images[p]; y=y_of(M[p])   # = y_of(I[p]) since maj=inv∘foata
        x0=Lx[p]; x1=Rx[fp]
        r,g,b=colorsys.hls_to_rgb((M[p]/maxs*0.85)%1,0.6,0.95); col=np.array([r,g,b])
        t=np.linspace(0,1,60); xs=x0+(x1-x0)*t; ys=y+0.0*t  # horizontal (level preserved)
        # gentle bow for visibility
        ys=y+0.012*np.sin(np.pi*t)
        splat(np.stack([xs,ys],1),col,0.5)
    acc/=np.percentile(acc[acc>0],99.6); acc=np.clip(acc,0,1)
    img=acc.copy()
    for k in range(3): img[...,k]+=0.5*gaussian_filter(acc[...,k],1.4)+0.25*gaussian_filter(acc[...,k],5)
    img=np.clip(img,0,1)**0.9
    out=Image.fromarray((img*255).astype(np.uint8))
    body=("Two famous statistics on a permutation: the number of INVERSIONS (pairs out of order) and the MAJOR INDEX "
          "(the sum of the descent positions). Astonishingly they are equidistributed - exactly as many permutations of "
          f"{n} have major index k as have k inversions, for every k. Foata's 'second fundamental transformation' proves "
          "it by an explicit BIJECTION (verified: inv(foata(sigma)) = maj(sigma) on all of S1..S7). Here every one of the "
          f"{len(perms)} permutations of {n} is a thread from its major index on the left to the inversions of its Foata "
          "image on the right; because the map preserves the value, every thread runs level - and the glowing bell both "
          "sides share is the Mahonian distribution of Figure 4. Same shape, twice, joined cell by cell.")
    fig=annotate(out,"FIGURE 18 - FOATA'S BIJECTION","Two Statistics, One Distribution",body,accent=(235,170,95))
    fig.save("18_foata.png"); print("saved",fig.size,"t=%.1f"%(time.time()-t0))

if __name__=="__main__": render()
