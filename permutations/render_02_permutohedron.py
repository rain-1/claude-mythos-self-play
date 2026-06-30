import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
from figkit import annotate
from itertools import permutations
import time

def build(nn=4):
    perms=list(permutations(range(1,nn+1)))
    idx={p:i for i,p in enumerate(perms)}
    V=np.array(perms,dtype=float)
    edges=[]; egen=[]
    for p in perms:
        for i in range(nn-1):                 # adjacent transposition of positions i,i+1
            q=list(p); q[i],q[i+1]=q[i+1],q[i]; q=tuple(q)
            a,b=idx[p],idx[q]
            if a<b: edges.append((a,b)); egen.append(i)
    return V,edges,egen,perms

def project(V):
    # center, basis of hyperplane sum=const (orthonormal, orthogonal to all-ones)
    Vc=V-V.mean(0)
    n=V.shape[1]
    # Helmert-like orthonormal basis of the (n-1)-dim subspace
    B=[]
    for k in range(1,n):
        v=np.zeros(n); v[:k]=1; v[k]=-k; v/=np.linalg.norm(v); B.append(v)
    B=np.array(B)            # (n-1, n)
    P=Vc@B.T                 # (24, n-1) ; for n=4 -> 3D
    return P

def render(S=1500, ss=2):
    t0=time.time()
    V,edges,egen,perms=build(4)
    assert len(perms)==24 and len(edges)==36, (len(perms),len(edges))
    P=project(V)             # (24,3)
    # rotate for a pleasing view
    def rot(a,axis):
        c,s=np.cos(a),np.sin(a); R=np.eye(3)
        i,j=[(1,2),(0,2),(0,1)][axis]; R[i,i]=c;R[i,j]=-s;R[j,i]=s;R[j,j]=c; return R
    R=rot(0.6,0)@rot(0.5,1)@rot(0.2,2)
    Q=P@R.T
    Q/=np.abs(Q).max()
    z=Q[:,2]; zr=(z-z.min())/(z.max()-z.min()+1e-9)
    W=S*ss; acc=np.zeros((W,W,3))
    def to_px(pt): return ((pt[0]*0.42+0.5)*(W-1),(0.5-pt[1]*0.42)*(W-1))
    gcol=[np.array([0.95,0.55,0.25]),np.array([0.30,0.80,0.85]),np.array([0.70,0.45,0.95])]
    def line(p0,p1,col,zr0,zr1):
        L=np.hypot((p0[0]-p1[0])*0.42*W,(p0[1]-p1[1])*0.42*W)
        npts=max(80,int(L*2))
        tt=np.linspace(0,1,npts)
        pts=p0[None]*(1-tt[:,None])+p1[None]*tt[:,None]
        zz=zr0*(1-tt)+zr1*tt
        xs=(pts[:,0]*0.42+0.5)*(W-1); ys=(0.5-pts[:,1]*0.42)*(W-1)
        ix=np.clip(xs.astype(int),0,W-2); iy=np.clip(ys.astype(int),0,W-2)
        bright=(0.35+0.65*zz)[:,None]
        for ox in (0,1):
          for oy in (0,1):
            np.add.at(acc.reshape(-1,3),(iy+oy)*W+(ix+ox),bright*col*(1.4/npts*120))
    for (a,b),g in zip(edges,egen):
        line(Q[a],Q[b],gcol[g],zr[a],zr[b])
    acc/=np.percentile(acc[acc>0],99.5); acc=np.clip(acc,0,1)
    for i in range(24):
        x,y=to_px(Q[i]); xi,yi=int(x),int(y); rr=int(ss*3)
        acc[max(0,yi-rr):yi+rr,max(0,xi-rr):xi+rr]+=(0.5+0.5*zr[i])*np.array([1,1,1])*0.9
    acc=np.clip(acc,0,1)
    img=acc.copy()
    for k in range(3): img[...,k]+=0.85*gaussian_filter(acc[...,k],ss*1.2)+0.4*gaussian_filter(acc[...,k],ss*5)
    img=np.clip(img*1.3,0,1)**0.82
    out=Image.fromarray((img*255).astype(np.uint8)).resize((S,S),Image.LANCZOS)
    body=("The 24 permutations of (1,2,3,4) placed at their own coordinates in 3-space (on the hyperplane x1+..+x4=10) "
          "form the vertices of a truncated octahedron - the permutohedron. Edges join permutations differing by an "
          "adjacent transposition (swap of neighbouring positions): 36 edges, 3-coloured by which generator s1,s2,s3 is "
          "applied. This is the Cayley graph of the symmetric group S4 and the Hasse diagram of the weak Bruhat order; "
          "its 14 faces are 6 squares and 8 hexagons. Identity and its reverse sit at opposite poles.")
    fig=annotate(out,"FIGURE 2 - WEAK ORDER","The Permutohedron",body,accent=(120,200,210))
    fig.save("02_permutohedron.png"); print("saved",fig.size,"V",len(perms),"E",len(edges),"t=%.1f"%(time.time()-t0))

if __name__=="__main__": render()
