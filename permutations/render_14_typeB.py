import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
from figkit import annotate
from itertools import permutations, product
import time

def signed_perm_matrices():
    mats=[]
    for perm in permutations(range(3)):
        Pm=np.zeros((3,3))
        for i,pi in enumerate(perm): Pm[i,pi]=1
        for signs in product([1,-1],repeat=3):
            mats.append(Pm@np.diag(signs))
    return mats

def build():
    base=np.array([1.0, 1+np.sqrt(2), 1+2*np.sqrt(2)])   # great rhombicuboctahedron
    mats=signed_perm_matrices()
    verts=[M@base for M in mats]
    key=lambda v: tuple(np.round(v,6))
    idx={key(v):i for i,v in enumerate(verts)}
    S0=np.diag([-1.0,1,1])
    S1=np.array([[0,1,0],[1,0,0],[0,0,1.0]]); S2=np.array([[1,0,0],[0,0,1],[0,1,0.0]])
    gens=[S0,S1,S2]
    edges=set()
    for i,M in enumerate(mats):
        for g,S in enumerate(gens):
            j=idx[key((M@S)@base)]
            if i!=j: edges.add((min(i,j),max(i,j),g))
    # dedupe (i,j) keep one gen
    seen={}; E=[]
    for i,j,g in edges:
        if (i,j) not in seen: seen[(i,j)]=g; E.append((i,j,g))
    return np.array(verts), E

def render(S=1600):
    t0=time.time()
    V,E=build()
    nv=len(V); ne=len(E)
    F=2-nv+ne   # Euler -> faces
    assert nv==48 and ne==72, (nv,ne)
    Vc=V-V.mean(0); Vc/=np.abs(Vc).max()
    def rotm(ax,ay,az):
        cx,sx=np.cos(ax),np.sin(ax); cy,sy=np.cos(ay),np.sin(ay); cz,sz=np.cos(az),np.sin(az)
        Rx=np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]]); Ry=np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]])
        Rz=np.array([[cz,-sz,0],[sz,cz,0],[0,0,1.0]])
        return Rz@Ry@Rx
    R=rotm(0.55,0.45,0.45); Q=Vc@R.T   # corner-on view
    z=Q[:,2]; zr=(z-z.min())/(z.max()-z.min()+1e-9)
    # ---- crisp PIL drawing at 2x supersample, depth-sorted (robust; no accumulation artifacts) ----
    from PIL import ImageDraw
    ss=2; Wf=S*ss
    base=Image.new("RGB",(Wf,Wf),(6,7,12)); dr=ImageDraw.Draw(base)
    def px(p): return ((p[0]*0.44+0.5)*(Wf-1),(0.5-p[1]*0.44)*(Wf-1))
    gcol=[(238,100,140),(240,178,80),(90,205,230)]  # s0 sign-flip, s1, s2
    order=sorted(range(len(E)), key=lambda e:(zr[E[e][0]]+zr[E[e][1]])/2)  # far first
    for e in order:
        i,j,g=E[e]; d=(zr[i]+zr[j])/2; f=0.30+0.70*d
        col=tuple(int(c*f) for c in gcol[g])
        dr.line([px(Q[i]),px(Q[j])], fill=col, width=max(2,int(ss*1.6)))
    for i in sorted(range(nv), key=lambda i:zr[i]):
        x,y=px(Q[i]); rr=ss*4; f=0.55+0.45*zr[i]
        c=int(235*f)
        dr.ellipse([x-rr,y-rr,x+rr,y+rr], fill=(c,c,min(255,c+12)))
    arr=np.asarray(base).astype(np.float32)/255
    g=arr.copy()
    for k in range(3): g[...,k]+=0.30*gaussian_filter(arr[...,k],ss*1.4)
    arr=np.clip(g,0,1)
    out=Image.fromarray((arr*255).astype(np.uint8)).resize((S,S),Image.LANCZOS)
    body=("Permutation theory is the n=A case of a much larger story. Allow each value to carry a SIGN and you get the "
          "hyperoctahedral group B_n - the signed permutations, the symmetries of the n-cube. Here B_3: its 48 elements, "
          "placed at a generic point in 3-space, are the vertices of the great rhombicuboctahedron (the type-B "
          "permutohedron), with 72 edges 3-coloured by the three Coxeter generators - two adjacent transpositions (gold, "
          "teal) and one sign-flip (rose). V-E+F = 48-72+26 = 2: 12 squares, 8 hexagons, 6 octagons. It is to Figure 2's "
          "truncated octahedron (the S_4 permutohedron) exactly what B_3 is to S_4 - the same construction, one Coxeter "
          "rank further out, where the whole theory of orders, lengths and descents carries over.")
    fig=annotate(out,"FIGURE 14 - THE HYPEROCTAHEDRAL GROUP","Signed Permutations: One Coxeter Step Further",body,accent=(235,150,170))
    fig.save("14_typeB.png"); print("saved",fig.size,"V",nv,"E",ne,"F",F,"t=%.1f"%(time.time()-t0))

if __name__=="__main__": render()
