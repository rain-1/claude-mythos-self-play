import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter
from characters import partitions, hook_dim
from figkit import annotate
import time

def covers(lam):
    """partitions mu that cover lam (lam + one box, staying a partition)."""
    out=[]; l=list(lam)
    for i in range(len(l)+1):
        if i==len(l):
            if i==0 or l[-1]>=1: out.append(tuple(l+[1]))
        else:
            if i==0 or l[i-1]>l[i]:
                m=l[:]; m[i]+=1; out.append(tuple(m))
    # dedupe & valid
    res=[]
    for m in out:
        if all(m[k]>=m[k+1] for k in range(len(m)-1)) and all(x>0 for x in m): res.append(m)
    return list(dict.fromkeys(res))

def render(N=8, S=1700):
    t0=time.time()
    levels=[partitions(n) for n in range(N+1)]
    # verify: #paths from empty to lam == f^lam
    paths={():1}
    for n in range(1,N+1):
        for lam in levels[n]:
            s=0
            for i in range(len(lam)):
                m=list(lam); m[i]-=1
                m=tuple(x for x in m if x>0)
                if (i==len(lam)-1 or lam[i]>lam[i+1]): s+=paths[m]
            paths[lam]=s
    assert all(paths[lam]==hook_dim(lam) for n in range(1,N+1) for lam in levels[n])
    print("verified #paths==f^lambda t=%.1f"%(time.time()-t0))
    # layout
    pos={}
    W=S; H=int(S*1.05)
    mtop=int(H*0.05); mbot=int(H*0.06)
    for n in range(N+1):
        L=levels[n]; y=H-mbot-(n/N)*(H-mtop-mbot)
        for k,lam in enumerate(L):
            x=(k+0.5)/len(L)*W*0.92+W*0.04
            pos[lam]=(x,y)
    SS=2; img=Image.new("RGB",(W*SS,H*SS),(7,8,13)); dr=ImageDraw.Draw(img)
    maxf=max(paths.values())
    # edges
    for n in range(N):
        for lam in levels[n]:
            for mu in covers(lam):
                if mu in pos:
                    x0,y0=pos[lam]; x1,y1=pos[mu]
                    f=(paths[lam]*paths[mu])**0.5/maxf
                    c=int(60+150*f**0.4)
                    dr.line([(x0*SS,y0*SS),(x1*SS,y1*SS)],fill=(c,int(c*0.7+30),int(c*0.4+50)),width=max(1,int(SS*(0.6+1.6*f**0.4))))
    # nodes = tiny young diagrams, colour by f^lam
    def col_f(f):
        t=(np.log1p(f)/np.log1p(maxf))
        cs=np.array([[0.3,0.45,0.7],[0.2,0.75,0.7],[1.0,0.8,0.3]]);p=np.array([0,0.5,1])
        return tuple(int(255*np.interp(t,p,cs[:,k])) for k in range(3))
    for lam in pos:
        x,y=pos[lam]; x*=SS; y*=SS
        if not lam:
            dr.ellipse([x-4*SS,y-4*SS,x+4*SS,y+4*SS],fill=(230,230,240)); continue
        b=SS*3.0; col=col_f(paths[lam])
        tw=lam[0]*b; th=len(lam)*b; ox=x-tw/2; oy=y-th/2
        for r,part in enumerate(lam):
            for cc in range(part):
                X=ox+cc*b; Y=oy+r*b; dr.rectangle([X,Y,X+b-SS*0.5,Y+b-SS*0.5],fill=col)
    arr=np.asarray(img).astype(np.float32)/255
    g=arr.copy()
    for k in range(3): g[...,k]+=0.3*gaussian_filter(arr[...,k],SS*1.2)
    out=Image.fromarray((np.clip(g,0,1)*255).astype(np.uint8)).resize((W,H),Image.LANCZOS)
    body=("Young's lattice: every partition (drawn as its Young diagram), with an edge whenever one is obtained from "
          "another by adding a single box. Level n holds the partitions of n; the empty diagram is the single root at the "
          "bottom. A standard Young tableau of shape lambda is exactly a saturated CHAIN from the root up to lambda, so "
          "the number of upward paths to lambda equals f^lambda - the dimension of the irreducible from Figure 15 "
          "(verified: paths == hook-length formula). Nodes are tinted by f^lambda. This is the prototypical DIFFERENTIAL "
          "POSET (Stanley): the up and down operators satisfy DU - UD = I, which alone forces sum f^lambda^2 = n! - the "
          "same identity RSK proves bijectively.")
    fig=annotate(out,"FIGURE 16 - YOUNG'S LATTICE","The Tree of All Shapes",body,accent=(120,205,180))
    fig.save("16_young_lattice.png"); print("saved",fig.size,"nodes",len(pos),"t=%.1f"%(time.time()-t0))

if __name__=="__main__": render()
