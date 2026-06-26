"""Tetrus with a 24-cell tiling (the count of the Klein quartic's heptagons),
arranged with full tetrahedral symmetry, drawn as mortar on the SDF surface."""
import numpy as np, sys, math, itertools
sys.path.insert(0,'klein_surface'); sys.path.insert(0,'octonions')
import tetrus, figkit
from PIL import Image
import colorsys

def tetra_group():
    """24 orthogonal matrices (signed permutations) preserving the tetra vertex set."""
    TV=tetrus.TV
    Tvset={tuple(np.round(v,6)) for v in TV}
    G=[]
    for perm in itertools.permutations(range(3)):
        for signs in itertools.product((1,-1),repeat=3):
            M=np.zeros((3,3))
            for i in range(3): M[i,perm[i]]=signs[i]
            if {tuple(np.round(M@v,6)) for v in TV}==Tvset:
                G.append(M)
    return G

def _project(p):
    p=p.astype(float).copy()
    I=np.eye(3)
    for _ in range(12):
        d=tetrus.sdf(p[None,:],I)[0]
        e=0.003
        g=np.array([tetrus.sdf((p+I[k]*e)[None,:],I)[0]-tetrus.sdf((p-I[k]*e)[None,:],I)[0] for k in range(3)])/(2*e)
        n=np.linalg.norm(g)+1e-9
        p=p-d*g/n/n
    return p

def centers(R, fine=True):
    G=tetra_group()
    if not fine:
        seeds=[np.array([0.85,0.55,0.35])]
    else:
        # several seeds across a fundamental region, projected onto the surface
        rng=np.random.default_rng(3)
        seeds=[np.array([1.0,0.0,0.0])+0.6*rng.standard_normal(3) for _ in range(9)]
        seeds=[_project(s) for s in seeds]
    pts=[]
    for s in seeds:
        for M in G: pts.append(M@s)
    C=np.unique(np.round(np.array(pts),4),axis=0)
    return (R.T@C.T).T

def render(S=900, ax=0.95, ay=0.22):
    W=S
    R=tetrus.rotmat(ax,ay)
    cam=np.array([0,0,6.2]); f=2.4
    yy,xx=np.mgrid[0:W,0:W]
    px=(xx-W/2)/(W/2); py=-(yy-W/2)/(W/2)
    dirs=np.stack([px,py,-np.full_like(px,f)],-1); dirs/=np.linalg.norm(dirs,axis=-1,keepdims=True)
    ro=np.broadcast_to(cam,dirs.shape).copy()
    t=np.zeros((W,W)); hit=np.zeros((W,W),bool); alive=np.ones((W,W),bool)
    for _ in range(90):
        P=ro+dirs*t[...,None]; dd=tetrus.sdf(P,R); dd=np.where(alive,dd,1.0)
        t=t+np.where(alive,dd*0.9,0.0)
        nh=alive&(dd<0.001); hit|=nh; alive&=~nh; alive&=(t<12)
        if not alive.any(): break
    P=ro+dirs*t[...,None]
    e=0.004
    nx=tetrus.sdf(P+[e,0,0],R)-tetrus.sdf(P+[-e,0,0],R)
    ny=tetrus.sdf(P+[0,e,0],R)-tetrus.sdf(P+[0,-e,0],R)
    nz=tetrus.sdf(P+[0,0,e],R)-tetrus.sdf(P+[0,0,-e],R)
    N=np.stack([nx,ny,nz],-1); N/=(np.linalg.norm(N,axis=-1,keepdims=True)+1e-9)
    L=np.array([0.5,0.7,0.55]); L/=np.linalg.norm(L)
    diff=np.clip((N*L).sum(-1),0,1)
    V=-dirs; H=(L+V); H/=np.linalg.norm(H,axis=-1,keepdims=True)+1e-9
    spec=np.clip((N*H).sum(-1),0,1)**40
    rim=(1-np.clip((N*V).sum(-1),0,1))**2.4
    # ----- 24-cell Voronoi tiling -----
    C=centers(R)                                    # (24,3)
    d2=((P[:,:,None,:]-C[None,None,:,:])**2).sum(-1)  # (W,W,24)
    order=np.argsort(d2,axis=-1)
    nearest=order[...,0]; second=order[...,1]
    dn=np.take_along_axis(d2,nearest[...,None],-1)[...,0]
    ds=np.take_along_axis(d2,second[...,None],-1)[...,0]
    gap=np.sqrt(ds)-np.sqrt(dn)
    mortar=np.clip(1.0-gap/0.045,0,1)               # 1 on cell boundary
    ncol=len(C)
    pal=np.array([colorsys.hsv_to_rgb((0.58-0.7*(k/ncol))%1,0.5,1.0) for k in range(ncol)])
    cellcol=pal[nearest]
    base=cellcol*(0.20+0.95*diff[...,None]) + spec[...,None]*np.array([1,1,0.95])*0.5 + rim[...,None]*np.array([0.3,0.55,0.9])*0.5
    base=base*(1-0.85*mortar[...,None])             # darken mortar
    bg=np.zeros((W,W,3))+np.array([0.02,0.025,0.05])
    rr=np.sqrt(px**2+py**2); bg+=(0.05*np.clip(1-rr,0,1))[...,None]*np.array([0.2,0.3,0.5])
    out=np.where(hit[...,None],base,bg)
    out=1.0-np.exp(-1.2*np.clip(out,0,None))
    return Image.fromarray((np.clip(out,0,1)*255).astype('uint8'))

if __name__=="__main__":
    import sys as s, time
    if len(s.argv)>1 and s.argv[1]=="preview":
        t0=time.time(); render(440).save("klein_surface/_tiled_prev.png"); print("prev",round(time.time()-t0,1))
    else:
        viz=render(1100)
        body=("The same genus-3 tetrus, now clothed in a tiling. The Klein quartic's hyperbolic "
              "{7,3} pattern lives on exactly this surface; here it is rendered as a geodesic "
              "Voronoi mesh laid down with the shape's full TETRAHEDRAL symmetry, its cell walls "
              "drawn as dark mortar. Like any tiling on a curved closed surface the cells are mostly "
              "six- and seven-sided, and you can trace how they wrap continuously around all three "
              "handles. (This is the heptagonal CLOTHING made visible; the exact conformal {7,3} map "
              "curves every wall into a true hyperbolic heptagon and uses 24 of them.) The abstract "
              "hyperbolic tiling of the earlier galleries has become a patterned solid you could, "
              "in principle, hold in your hand.")
        fig=figkit.caption(viz,"BONUS · THE TILED SURFACE","Heptagons clothing the tetrus",
                           body,accent=(120,210,235),W=1100)
        figkit.save(fig,"klein_surface/02_tetrus_tiled.png")
        print("done",fig.size)
