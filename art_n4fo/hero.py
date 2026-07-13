"""HERO — 'The Certain Cage': Gershgorin discs + the 2nd (capture) theorem.

Eigenvalues of A (roots of a degree-n char poly, no closed form for n>=5) are caged
by discs centred at a_ii, radius = off-diagonal row sum. The 2nd theorem: a connected
component built from k discs contains EXACTLY k eigenvalues. Isolated discs (capture 1)
= resolved gold jewels; the overlapping central bath = the contested spectrum.
"""
import numpy as np
from kit import Canvas, disc_field, ring_field, tonemap, bloom
from PIL import Image

def build_matrix(seed=11):
    rng=np.random.default_rng(seed)
    centers=[]; radii=[]; roles=[]   # role: 'jewel' or 'bath'
    # --- outer ring of resolved jewels: well separated, small radius ---
    NJ=9
    for k in range(NJ):
        ang=2*np.pi*k/NJ + 0.13*rng.standard_normal()
        Rout=6.2+0.5*rng.standard_normal()
        centers.append(Rout*np.exp(1j*ang))
        radii.append(0.28+0.10*rng.random())
        roles.append('jewel')
    # --- a few coupled PAIRS: two discs overlapping only each other -> capture exactly 2 ---
    pair_angles=[np.pi*0.32, np.pi*1.16, np.pi*1.74]
    for pa in pair_angles:
        Rp=5.25
        base=Rp*np.exp(1j*pa)
        off=(0.52)*np.exp(1j*(pa+np.pi/2))   # separation < sum of radii
        for s in (+1,-1):
            centers.append(base+s*off)
            radii.append(0.66+0.10*rng.random())
            roles.append('pair')
    # --- central contested bath: compact central mass, larger radii, strong coupling ---
    NB=22
    bath=[]
    for k in range(NB):
        bath.append((rng.standard_normal()+1j*rng.standard_normal())*1.15)
    bath=np.array(bath,complex); bath-=bath.mean()   # centre the bath at the origin
    for c in bath:
        centers.append(c); radii.append(0.85+0.85*rng.random()); roles.append('bath')
    centers=np.array(centers,complex); radii=np.array(radii,float)
    n=len(centers)
    A=np.zeros((n,n),complex)
    A[np.diag_indices(n)]=centers
    # distribute off-diagonal mass so row i sums (in |.|) to radii[i], with directed phases
    for i in range(n):
        js=[j for j in range(n) if j!=i]
        # jewels couple mainly to other bath rows weakly; bath couples strongly within bath
        w=rng.random(len(js))
        if roles[i]=='jewel':
            # keep isolated: only couple to a couple of nearby rows, tiny total already small
            w=w**3
        w=w/ w.sum()
        phases=np.exp(1j*2*np.pi*rng.random(len(js)))
        for jj,j in enumerate(js):
            A[i,j]=radii[i]*w[jj]*phases[jj]
    return A, centers, radii, np.array(roles)

def components(centers, radii):
    n=len(centers); parent=list(range(n))
    def find(x):
        while parent[x]!=x: parent[x]=parent[parent[x]]; x=parent[x]
        return x
    for i in range(n):
        for j in range(i+1,n):
            if abs(centers[i]-centers[j])<=radii[i]+radii[j]:
                parent[find(i)]=find(j)
    comp={}
    for i in range(n): comp.setdefault(find(i),[]).append(i)
    return list(comp.values())

def render(S, out, seed=5, k_tone=1.3, gamma=0.82):
    A,centers,radii,roles=build_matrix(seed)
    lam=np.linalg.eigvals(A)
    comps=components(centers,radii)
    # verify capture
    caps=[]
    for m in comps:
        cnt=sum(1 for l in lam if np.any(np.abs(l-centers[m])<=radii[m]+1e-9))
        caps.append((len(m),cnt))
    inside=all(np.any(np.abs(l-centers)<=radii+1e-9) for l in lam)
    print(f"[hero] n={len(centers)}  eigs_inside={inside}  components={len(comps)}  capture(size,count)={caps}")

    C=Canvas(S, zc=0+0j, half=8.0)
    Z=C.grid_Z()
    # component size per disc -> k=1 resolved (gold), k=2 coupled pair (teal), k>=3 bath (steel)
    csize=np.zeros(len(centers),int)
    for m in comps:
        for i in m: csize[i]=len(m)

    gold=np.array([1.0,0.72,0.30])
    teal=np.array([0.30,0.82,0.72])
    steel=np.array([0.40,0.58,0.82])
    warm_ring=np.array([1.0,0.82,0.48])
    teal_ring=np.array([0.45,1.0,0.88])
    cool_ring=np.array([0.55,0.80,1.0])
    hot=np.array([1.0,0.95,0.85])          # eigenvalue = the real, white-hot

    def tone_of(k):
        return gold if k==1 else (teal if k==2 else steel)
    def ring_of(k):
        return warm_ring if k==1 else (teal_ring if k==2 else cool_ring)

    # overlap-depth nebula = your UNCERTAINTY (translucent haze, never white)
    depth={1:np.zeros((S,S)),2:np.zeros((S,S)),3:np.zeros((S,S))}
    edge=2*C.half/S*2.5
    for i,(c,r) in enumerate(zip(centers,radii)):
        key=min(csize[i],3)
        depth[key]+=disc_field(Z,c,r,edge=edge)
    C.add_field(np.tanh(depth[1]*0.9)*0.34, gold*0.85)
    C.add_field(np.tanh(depth[2]*0.8)*0.32, teal*0.9)
    C.add_field(np.tanh(depth[3]*0.55)*0.30, steel)

    # bright disc boundary rings — the drawn edge of the cage
    wr=2*C.half/S*1.05
    for i,(c,r) in enumerate(zip(centers,radii)):
        k=csize[i]
        amp=0.95 if k==1 else (0.80 if k==2 else 0.50)
        C.add_field(ring_field(Z,c,r,wr)*amp, ring_of(k))

    # eigenvalue stars: THE TRUTH — blaze brightest.
    star_scale=S/900.0
    sig=0.052   # plane units, resolution independent
    for i,l in enumerate(lam):
        di=np.argmin(np.abs(l-centers))
        k=csize[di]
        col=(hot*0.55+gold*0.45) if k==1 else ((hot*0.6+teal*0.4) if k==2 else hot)
        blob=np.exp(-(np.abs(Z-l)/sig)**2)
        C.add_field(blob*3.2, col)

    buf=bloom(C.buf, [(1.4*star_scale,0.85),(4.5*star_scale,0.5),(13.0*star_scale,0.30)])
    img=tonemap(buf,k=k_tone,gamma=gamma)
    Image.fromarray(img).save(out)
    print(f"[hero] wrote {out}  {S}x{S}")

if __name__=="__main__":
    import sys
    S=int(sys.argv[1]) if len(sys.argv)>1 else 900
    out=sys.argv[2] if len(sys.argv)>2 else "variants/hero_proto.png"
    render(S,out)
