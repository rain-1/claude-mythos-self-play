"""BONUS — 'The Capture Dance': animating Gershgorin's 2nd theorem.

Cages breathe. When two discs are disjoint each holds exactly one eigenvalue (gold,
resolved). As a coupling grows the discs merge into one component that now holds two
(teal) or three (steel) eigenvalues — and you watch the eigenstars get CAUGHT together,
then freed as the cage shrinks. The colour is recomputed live from the component
structure every frame, so the 2nd theorem literally choreographs the animation.
"""
import numpy as np
from kit import Canvas, disc_field, ring_field, tonemap, bloom
from PIL import Image

def scene(t):
    """Return centers, radii for parameter t in [0,2pi). Discs stay put; cages breathe."""
    centers=[]; radii=[]
    # three core nodes; gentle vertical sway breaks the rigid row
    core=[(-2.15+0.25j)-0.18j*np.cos(t),
          (0.05-0.10j)+0.16j*np.cos(t+1.0),
          (2.2+0.15j)-0.18j*np.cos(t+2.0)]
    base=0.58
    # phase so L-C merge peaks at t=pi/2, R-C at t=3pi/2 (sharpened for a clear separated rest)
    gL=(0.5+0.5*np.cos(t-np.pi/2))**1.6
    gR=(0.5+0.5*np.cos(t-3*np.pi/2))**1.6
    radL=base+0.98*gL
    radR=base+0.98*gR
    radC=base+0.60*max(gL,gR)
    for c,r in zip(core,[radL,radC,radR]):
        centers.append(c); radii.append(r)
    # six gold jewel witnesses on an outer ring (static, each caging one)
    for k in range(6):
        a=2*np.pi*k/6+0.3
        centers.append(5.2*np.exp(1j*a)); radii.append(0.34)
    return np.array(centers,complex), np.array(radii,float), (gL,gR)

def build_A(centers, radii, seed=0):
    n=len(centers); rng=np.random.default_rng(seed)
    A=np.zeros((n,n),complex); A[np.diag_indices(n)]=centers
    # fixed random directions so the eigenvalue motion is smooth in t
    for i in range(n):
        js=[j for j in range(n) if j!=i]
        w=rng.random(len(js)); w/=w.sum()
        ph=np.exp(1j*2*np.pi*rng.random(len(js)))
        for jj,j in enumerate(js):
            A[i,j]=radii[i]*w[jj]*ph[jj]
    return A

def components(centers,radii):
    n=len(centers); parent=list(range(n))
    def find(x):
        while parent[x]!=x: parent[x]=parent[parent[x]]; x=parent[x]
        return x
    for i in range(n):
        for j in range(i+1,n):
            if abs(centers[i]-centers[j])<=radii[i]+radii[j]: parent[find(i)]=find(j)
    comp={}
    for i in range(n): comp.setdefault(find(i),[]).append(i)
    csize=np.zeros(n,int)
    for m in comp.values():
        for i in m: csize[i]=len(m)
    return csize

def frame(t, S):
    centers,radii,_=scene(t)
    A=build_A(centers,radii)
    lam=np.linalg.eigvals(A)
    csize=components(centers,radii)
    C=Canvas(S, zc=0.0+0j, half=6.6); Z=C.grid_Z()
    gold=np.array([1.0,0.72,0.30]); teal=np.array([0.30,0.82,0.72]); steel=np.array([0.42,0.60,0.84])
    warm_ring=np.array([1.0,0.82,0.48]); teal_ring=np.array([0.45,1.0,0.88]); cool_ring=np.array([0.6,0.82,1.0])
    hot=np.array([1.0,0.95,0.85])
    edge=2*C.half/S*2.5
    dep={1:np.zeros((S,S)),2:np.zeros((S,S)),3:np.zeros((S,S))}
    for i,(c,r) in enumerate(zip(centers,radii)):
        dep[min(csize[i],3)]+=disc_field(Z,c,r,edge=edge)
    C.add_field(np.tanh(dep[1]*0.9)*0.34, gold*0.85)
    C.add_field(np.tanh(dep[2]*0.8)*0.32, teal*0.9)
    C.add_field(np.tanh(dep[3]*0.6)*0.30, steel)
    wr=2*C.half/S*1.05
    for i,(c,r) in enumerate(zip(centers,radii)):
        k=csize[i]; amp=0.95 if k==1 else (0.82 if k==2 else 0.55)
        C.add_field(ring_field(Z,c,r,wr)*amp, warm_ring if k==1 else (teal_ring if k==2 else cool_ring))
    sig=0.058
    for l in lam:
        di=np.argmin(np.abs(l-centers)); k=csize[di]
        col=(hot*0.55+gold*0.45) if k==1 else ((hot*0.6+teal*0.4) if k==2 else hot)
        C.add_field(np.exp(-(np.abs(Z-l)/sig)**2)*3.0, col)
    ss=S/720.0
    buf=bloom(C.buf,[(1.4*ss,0.85),(4.5*ss,0.5),(13*ss,0.3)])
    return tonemap(buf,k=1.3,gamma=0.82)

if __name__=="__main__":
    import sys
    S=int(sys.argv[1]) if len(sys.argv)>1 else 720
    NF=int(sys.argv[2]) if len(sys.argv)>2 else 60
    out=sys.argv[3] if len(sys.argv)>3 else "capture_dance.gif"
    frames=[]
    for f in range(NF):
        t=2*np.pi*f/NF
        frames.append(Image.fromarray(frame(t,S)))
        if f%10==0: print(f"frame {f}/{NF}")
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=70, loop=0, optimize=True)
    print(f"wrote {out} {S}x{S} {NF}f")
