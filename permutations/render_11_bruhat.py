import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter
from figkit import annotate
from itertools import permutations
import time

def inv(p):
    n=len(p); return sum(1 for i in range(n) for j in range(i+1,n) if p[i]>p[j])

def build(n=4):
    elts=list(permutations(range(1,n+1)))
    idx={p:i for i,p in enumerate(elts)}
    rank={p:inv(p) for p in elts}
    edges=[]  # (lo, hi, span) span=j-i of swapped positions
    for p in elts:
        for i in range(n):
            for j in range(i+1,n):
                q=list(p); q[i],q[j]=q[j],q[i]; q=tuple(q)
                if rank[q]==rank[p]+1:
                    edges.append((idx[p],idx[q],j-i))
    return elts,idx,rank,edges

def render(S=1500):
    t0=time.time()
    elts,idx,rank,edges=build(4)
    R=max(rank.values())
    ranksizes=[sum(1 for p in elts if rank[p]==r) for r in range(R+1)]
    assert ranksizes==[1,3,5,6,5,3,1], ranksizes
    # layout: y by rank, x by barycentric sweeps
    byrank=[[i for i,p in enumerate(elts) if rank[elts[i]]==r] for r in range(R+1)]
    xpos=np.zeros(len(elts))
    for r,row in enumerate(byrank):
        for k,i in enumerate(row): xpos[i]=(k+0.5)/len(row)
    adj=[[] for _ in elts]
    for a,b,s in edges: adj[a].append(b); adj[b].append(a)
    for _ in range(60):
        for r,row in enumerate(byrank):
            for i in row:
                if adj[i]: xpos[i]=0.5*xpos[i]+0.5*np.mean([xpos[j] for j in adj[i]])
        for r,row in enumerate(byrank):
            order=sorted(row,key=lambda i:xpos[i])
            for k,i in enumerate(order): xpos[i]=(k+0.5)/len(row)*0.86+0.07
    W=S; H=int(S*1.02)
    field=np.zeros((H,W,3))
    def XY(i):
        return (0.06*W+xpos[i]*0.88*W, H-0.10*H - rank[elts[i]]/R*0.80*H)
    def seg(p0,p1,col,wt):
        L=int(max(2,abs(p1[0]-p0[0])+abs(p1[1]-p0[1])))
        t=np.linspace(0,1,L); x=p0[0]+(p1[0]-p0[0])*t; y=p0[1]+(p1[1]-p0[1])*t
        ix=np.clip(x.astype(int),0,W-2); iy=np.clip(y.astype(int),0,H-2)
        for ox in (0,1):
          for oy in (0,1): np.add.at(field.reshape(-1,3),(iy+oy)*W+(ix+ox),col*wt)
    # extra strong edges (span>1) dim violet, weak-order edges (span==1) bright gold
    for a,b,s in edges:
        if s>1: seg(XY(a),XY(b),np.array([0.5,0.35,0.8]),0.32)
    for a,b,s in edges:
        if s==1: seg(XY(a),XY(b),np.array([1.0,0.78,0.35]),0.5)
    field/=np.percentile(field[field>0],99.5); field=np.clip(field,0,1)
    img=field.copy()
    for c in range(3): img[...,c]+=0.6*gaussian_filter(field[...,c],1.5)
    img=np.clip(img,0,1)
    out=Image.fromarray((img*255).astype(np.uint8)); dr=ImageDraw.Draw(out)
    try: fnt=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",int(S*0.0145))
    except: fnt=ImageFont.load_default()
    for i,p in enumerate(elts):
        x,y=XY(i); s="".join(map(str,p))
        w=dr.textlength(s,font=fnt)
        dr.rectangle([x-w/2-5,y-int(S*0.012),x+w/2+5,y+int(S*0.012)],fill=(12,12,18))
        dr.text((x-w/2,y-int(S*0.011)),s,font=fnt,fill=(235,235,245))
    # rank-size labels
    for r in range(R+1):
        yy=H-0.10*H - r/R*0.80*H
        dr.text((int(0.012*W),yy-int(S*0.011)),f"{ranksizes[r]}",font=fnt,fill=(150,150,170))
    body=("The STRONG Bruhat order on S4: 24 permutations stacked by their number of inversions (0 at the identity 1234, "
          "6 at the reversal 4321). One permutation covers another when they differ by a single transposition of two "
          "values - ANY two, not just neighbours - that raises the inversion count by exactly one. The gold edges are "
          "neighbour-swaps (these alone give the weak order = the permutohedron of Figure 2); the violet edges are the "
          "extra long-range relations that the strong order adds. Each rank holds a Mahonian number of permutations "
          "(1,3,5,6,5,3,1, verified) and the poset is self-dual. This order indexes how Schubert cells fit inside one "
          "another - the combinatorial skeleton of a flag variety.")
    fig=annotate(out,"FIGURE 11 - STRONG BRUHAT ORDER","The Other Order on the Symmetric Group",body,accent=(180,150,235))
    fig.save("11_bruhat.png"); print("saved",fig.size,"ranksizes",ranksizes,"edges",len(edges),"t=%.1f"%(time.time()-t0))

if __name__=="__main__": render()
