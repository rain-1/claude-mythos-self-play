import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
from cycles import cycles_of
from figkit import annotate
import colorsys, sys, time

def render(n=1400, S=1600, ss=2, seed=11):
    t0=time.time(); rng=np.random.default_rng(seed)
    p=rng.permutation(n); cy=cycles_of(p); cy.sort(key=len,reverse=True)
    order=[]
    for c in cy: order+=sorted(c)
    pos=np.zeros(n,int)
    for k,e in enumerate(order): pos[e]=k
    th=2*np.pi*np.arange(n)/n
    ang=np.zeros(n)
    for e in range(n): ang[e]=th[pos[e]]
    P=np.stack([np.cos(ang),np.sin(ang)],1)*0.95
    W=S*ss; acc=np.zeros((W,W,3))
    col_e=np.zeros((n,3))
    palette=[(1.0,0.82,0.32),(0.30,0.45,0.95),(0.35,0.85,0.32),(0.92,0.30,0.62),(0.20,0.82,0.82),(0.75,0.55,0.95),(0.95,0.55,0.25)]
    for ci,c in enumerate(cy):
        col=np.array(palette[ci]) if ci<len(palette) else np.array(colorsys.hls_to_rgb((0.13*ci)%1,0.6,0.9))
        for e in c: col_e[e]=col
    def splat(pts,col):
        x=(pts[:,0]*0.5+0.5)*(W-1); y=(0.5-pts[:,1]*0.5)*(W-1)
        ix=np.clip(np.floor(x).astype(int),0,W-2); iy=np.clip(np.floor(y).astype(int),0,W-2)
        dx=x-ix; dy=y-iy
        for ox,oy,wt in [(0,0,(1-dx)*(1-dy)),(1,0,dx*(1-dy)),(0,1,(1-dx)*dy),(1,1,dx*dy)]:
            np.add.at(acc.reshape(-1,3),(iy+oy)*W+(ix+ox),wt[:,None]*col*0.30)
    for i in range(n):
        j=p[i]; Pi=P[i]; Pj=P[j]; d=np.linalg.norm(Pi-Pj)
        if d<0.02:
            splat(Pi[None]+rng.normal(0,0.002,(6,2)),col_e[i]); continue
        M=(Pi+Pj)/2; C=M*(1-0.9*min(d/2,1.0))
        tt=np.linspace(0,1,max(16,int(220*d)))[:,None]
        B=(1-tt)**2*Pi+2*(1-tt)*tt*C+tt**2*Pj
        splat(B,col_e[i])
    acc/=np.percentile(acc[acc>0],99.6); acc=np.clip(acc,0,1)**0.82
    img=acc.copy()
    for k in range(3): img[...,k]+=0.55*gaussian_filter(acc[...,k],ss*1.0)+0.3*gaussian_filter(acc[...,k],ss*4)
    img=np.clip(img,0,1)
    out=Image.fromarray((img*255).astype(np.uint8)).resize((S,S),Image.LANCZOS)
    sizes=[len(c) for c in cy]; frac=sizes[0]/n
    body=(f"A uniform random permutation of {n} points, decomposed into disjoint cycles; each cycle is a contiguous "
          f"arc of chords i->sigma(i). Cycle lengths follow the Poisson-Dirichlet (GEM) law: here {len(cy)} cycles of "
          f"sizes {sizes[:5]}..., the longest holding {frac:.0%} of all points. On average a random permutation has "
          f"H_n = 1+1/2+...+1/n ~ ln n cycles, and the largest spans the Golomb-Dickman fraction ~62.4%.")
    fig=annotate(out,"FIGURE 1 - CYCLE STRUCTURE","The Cycles of a Random Permutation",body,accent=(235,185,70))
    fig.save("01_cycles.png"); print("saved 01_cycles.png",fig.size,"sizes",sizes,"t=%.1f"%(time.time()-t0))

if __name__=="__main__": render()
