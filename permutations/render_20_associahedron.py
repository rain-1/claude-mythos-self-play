import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter
from associ import build
from figkit import annotate
import colorsys, time

def render(S=1600):
    t0=time.time()
    T,idx,V,edges,covers=build(4)
    nv=len(T); ne=len(edges); F=2-nv+ne
    Vc=V-V.mean(0)
    # Helmert orthonormal basis of hyperplane sum=const in R^4
    B=[]
    for k in range(1,4):
        v=np.zeros(4); v[:k]=1; v[k]=-k; v/=np.linalg.norm(v); B.append(v)
    P=Vc@np.array(B).T   # 14 x 3
    P/=np.abs(P).max()
    def rotm(ax,ay,az):
        cx,sx=np.cos(ax),np.sin(ax); cy,sy=np.cos(ay),np.sin(ay); cz,sz=np.cos(az),np.sin(az)
        Rx=np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]]); Ry=np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]]); Rz=np.array([[cz,-sz,0],[sz,cz,0],[0,0,1.0]])
        return Rz@Ry@Rx
    Q=P@rotm(0.5,0.7,0.3).T
    Q=Q-Q.mean(0); Q=Q/(np.abs(Q[:,:2]).max()*1.08)   # center+fit to the 2D frame
    zr=(Q[:,2]-Q[:,2].min())/(np.ptp(Q[:,2])+1e-9)
    # Tamari height (longest chain from a source) for colour
    import collections
    up=collections.defaultdict(list)
    for a,b in covers: up[a].append(b)
    # min element = left comb; compute height by longest path in cover DAG
    height={}
    order=list(range(nv))
    def h(i):
        if i in height: return height[i]
        height[i]=0 if not up[i] else 1+max(h(j) for j in up[i])
        return height[i]
    # height from top; invert to get rank from bottom
    ht=[h(i) for i in range(nv)]; maxh=max(ht); rank=[maxh-x for x in ht]
    SS=2; Wf=S*SS
    base=Image.new("RGB",(Wf,Wf),(7,8,13)); dr=ImageDraw.Draw(base)
    def px(p): return ((p[0]*0.45+0.5)*(Wf-1),(0.5-p[1]*0.45)*(Wf-1))
    def rcol(r):
        h_=0.08+0.62*r/maxh; return colorsys.hls_to_rgb(h_,0.6,0.95)
    order=sorted(range(ne),key=lambda e:(zr[edges[e][0]]+zr[edges[e][1]])/2)
    for e in order:
        a,b=edges[e]; d=(zr[a]+zr[b])/2; f=0.45+0.65*d
        r,g,bl=rcol((rank[a]+rank[b])/2); col=tuple(int(c*255*f) for c in (r,g,bl))
        dr.line([px(Q[a]),px(Q[b])],fill=col,width=max(2,int(SS*2.1)))
    for i in sorted(range(nv),key=lambda i:zr[i]):
        x,y=px(Q[i]); rr=SS*5; f=0.55+0.45*zr[i]; c=int(240*f)
        dr.ellipse([x-rr,y-rr,x+rr,y+rr],fill=(c,c,min(255,c+15)))
    arr=np.asarray(base).astype(np.float32)/255
    g=arr.copy()
    for k in range(3): g[...,k]+=0.45*gaussian_filter(arr[...,k],SS*1.4)
    out=Image.fromarray((np.clip(g,0,1)*255).astype(np.uint8)).resize((S,S),Image.LANCZOS)
    body=("The ASSOCIAHEDRON - the Catalan cousin of the permutohedron. Its %d vertices (Catalan number C_4) are the "
          "%d ways to bracket five factors, equivalently the triangulations of a hexagon or the binary trees on 4 nodes; "
          "each is placed by Loday's rule (coordinate = leaves-left times leaves-right at each node). Its %d edges are "
          "single re-bracketings (rotations / diagonal flips), and V-E+F = %d-%d+%d = 2 (6 pentagons + 3 squares). "
          "Orienting every edge in the direction that rotates rightward turns this polytope into the TAMARI LATTICE "
          "(vertices tinted by Tamari height) - the order in which associativity lets you re-parenthesise. The "
          "231-avoiding permutations of Figure 7 are its vertices in disguise."%(nv,nv,ne,nv,ne,F))
    fig=annotate(out,"FIGURE 20 - ASSOCIAHEDRON & TAMARI","The Shape of Associativity",body,accent=(180,150,235))
    fig.save("20_associahedron.png"); print("saved",fig.size,"V",nv,"E",ne,"F",F,"t=%.1f"%(time.time()-t0))

if __name__=="__main__": render()
