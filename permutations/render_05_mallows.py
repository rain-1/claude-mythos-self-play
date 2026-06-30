import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
from figkit import annotate
import time

def mallows(n,q,rng):
    """exact Mallows sample: Lehmer digit c_i ~ truncated geometric P(k)∝q^k, k in 0..n-i."""
    avail=list(range(n)); sigma=np.empty(n,int)
    for i in range(n):
        m=n-i
        if abs(q-1)<1e-9:
            k=rng.integers(0,m)
        else:
            w=q**np.arange(m); w/=w.sum()
            k=rng.choice(m,p=w)
        sigma[i]=avail.pop(k)
    return sigma

def matrix_density(sigma,n,G):
    img=np.zeros((G,G))
    xi=(np.arange(n)/n*(G-1)).astype(int)
    yi=((n-1-sigma)/n*(G-1)).astype(int)
    np.add.at(img,(yi,xi),1.0)
    return img

def render(n=2200, S=1500, seed=2):
    t0=time.time(); rng=np.random.default_rng(seed)
    qs=[0.985, 1.0, 1/0.985]   # diagonal band / uniform / anti-diagonal band
    labels=["q = 0.985  (few inversions)","q = 1  (uniform)","q = 1.015  (many inversions)"]
    G=S//3-20
    panels=[]
    for q in qs:
        sig=mallows(n,q,rng)
        d=matrix_density(sig,n,G)
        d=gaussian_filter(d,1.2)
        d/=np.percentile(d[d>0],99.7); d=np.clip(d,0,1)**0.8
        panels.append(d)
    W=S; H=G+30
    canvas=np.zeros((H,W,3))
    cols=[np.array([1.0,0.78,0.35]),np.array([0.45,0.8,0.95]),np.array([0.95,0.45,0.7])]
    x=15
    from PIL import ImageDraw, ImageFont
    for d,c,lab in zip(panels,cols,labels):
        for k in range(3): canvas[20:20+G,x:x+G,k]=d*c[k]+0.35*gaussian_filter(d*c[k],2)
        x+=G+15
    canvas=np.clip(canvas,0,1)
    out=Image.fromarray((canvas*255).astype(np.uint8))
    dr=ImageDraw.Draw(out)
    try: fnt=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",int(S*0.018))
    except: fnt=ImageFont.load_default()
    x=15
    for lab,c in zip(labels,cols):
        dr.text((x+8,2),lab,font=fnt,fill=tuple(int(v*255) for v in c)); x+=G+15
    body=("The Mallows measure weights each permutation by q^(inversions): P(sigma) ∝ q^inv(sigma). Sampled EXACTLY "
          "by drawing independent Lehmer digits c_i with P(c_i=k) ∝ q^k (so inv = sum c_i). Each panel is the "
          f"permutation matrix of one sample on n={n} points. q<1 rewards few inversions -> the mass concentrates on a "
          "diagonal band (a limit shape whose width scales like 1/(1-q)); q=1 is the uniform permutation (white noise, "
          "no structure); q>1 rewards inversions -> the anti-diagonal. The order/disorder of S_n in one dial.")
    fig=annotate(out,"FIGURE 5 - THE MALLOWS MEASURE","Order, Tuned by a Single Parameter",body,accent=(245,160,90))
    fig.save("05_mallows.png"); print("saved",fig.size,"t=%.1f"%(time.time()-t0))

if __name__=="__main__": render()
