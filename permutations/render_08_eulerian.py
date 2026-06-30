import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter
from figkit import annotate
import time

def eulerian_triangle(N):
    rows=[[1]]
    for n in range(2,N+1):
        prev=rows[-1]; cur=[0]*n
        for k in range(n):
            a=(k+1)*prev[k] if k<len(prev) else 0
            b=(n-k)*prev[k-1] if 0<=k-1<len(prev) else 0
            cur[k]=a+b
        rows.append(cur)
    return rows

def verify(rows):
    import math
    ok=all(sum(r)==math.factorial(i+1) for i,r in enumerate(rows))   # row n sums to n!
    sym=all(r==r[::-1] for r in rows)                                 # A(n,k)=A(n,n-1-k)
    return ok,sym

def render(N=46, S=1600, seed=0):
    t0=time.time()
    rows=eulerian_triangle(N); ok,sym=verify(rows)
    assert ok and sym,(ok,sym)
    W=S; H=int(S*0.72)
    img=np.zeros((H,W,3))
    margin=int(S*0.04); cw=(W-2*margin)/N
    ch=(H-2*margin)/N
    # colormap deep-violet -> teal -> gold
    def cmap(t):
        cs=np.array([[0.10,0.05,0.22],[0.20,0.45,0.75],[0.20,0.82,0.78],[1.0,0.85,0.35]]);pos=np.array([0,0.45,0.75,1.0])
        return np.array([np.interp(t,pos,cs[:,k]) for k in range(3)])
    for n in range(1,N+1):
        r=np.array(rows[n-1],dtype=float)
        rn=r/r.max()
        y=margin+(n-1)*ch
        x0=W/2-(n*cw)/2
        for k in range(n):
            t=rn[k]**0.4
            col=cmap(t)*(0.15+0.95*t)
            X=int(x0+k*cw); Y=int(y)
            img[Y:int(Y+ch)+1, X:int(X+cw)+1]=col
    img=gaussian_filter(img,(0.6,0.6,0))
    g=img.copy()
    for k in range(3): g[...,k]+=0.4*gaussian_filter(img[...,k],2.0)
    img=np.clip(g,0,1)
    out=Image.fromarray((img*255).astype(np.uint8))
    body=("The Eulerian number A(n,k) counts the permutations of n with exactly k DESCENTS (places where "
          "sigma(i)>sigma(i+1)). Row n of this triangle is A(n,0..n-1), per-row normalized to brightness: it sums to "
          "n! and is symmetric (A(n,k)=A(n,n-1-k)) - ascents and descents balance. Built by the recurrence "
          "A(n,k)=(k+1)A(n-1,k)+(n-k)A(n-1,k-1) (verified: each row sums to n!). Almost every permutation has close to "
          "(n-1)/2 descents - the bright central ridge - and the row distribution tends to a Gaussian. Eulerian numbers "
          "also give Worpitzky's identity and the h-vector of the permutohedron in Figure 2.")
    fig=annotate(out,"FIGURE 8 - DESCENTS","The Eulerian Triangle",body,accent=(230,180,90))
    fig.save("08_eulerian.png"); print("saved",fig.size,"verify rowsums=n!,symmetric:",ok,sym,"t=%.1f"%(time.time()-t0))

if __name__=="__main__": render()
