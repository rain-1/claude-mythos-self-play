"""
HERO :: WHAT THE COST CHOOSES  (semidiscrete optimal transport / quantization)
The optimal N-point quantization of a measure mu is the CENTROIDAL Voronoi
tessellation: sites where mu is dense get small cells, so that every cell carries
equal transport cost.  It is the fixed point of Lloyd's algorithm and the
semidiscrete OT map from mu to its best N-point approximation.
Here mu is a symmetry-broken spiral density on a disk; the tessellation crowds
into the arms.  Cell size = the map's local magnification.  Cells small & bright
in the arms, wide & dark in the voids: the transport plan made visible.
"""
import numpy as np, time, sys
from PIL import Image
from scipy.spatial import cKDTree
from scipy.ndimage import gaussian_filter
from ot import spiral_density_at

def build_mu(S):
    y,x=np.mgrid[0:S,0:S].astype(np.float64)
    xn=x/S; yn=y/S
    d=spiral_density_at(xn,yn)
    return d  # (S,S)

def sample_from_mu(N, S, mu, seed=4):
    rng=np.random.default_rng(seed)
    p=mu.ravel()/mu.sum()
    idx=rng.choice(len(p), size=N, p=p)
    ys,xs=np.divmod(idx,S)
    jit=rng.uniform(-0.5,0.5,(N,2))
    return (np.c_[xs,ys]+jit)/S   # normalized [0,1]

def lloyd(sites, S, mu, iters=28):
    """Centroidal Voronoi tessellation under density mu (Lloyd)."""
    yy,xx=np.mgrid[0:S,0:S].astype(np.float64)
    px=xx.ravel(); py=yy.ravel(); wgt=mu.ravel()
    N=len(sites)
    for it in range(iters):
        tree=cKDTree(sites*S)
        _,idx=tree.query(np.c_[px,py], workers=-1)
        wsum=np.bincount(idx,weights=wgt,minlength=N)
        cx=np.bincount(idx,weights=wgt*px,minlength=N)
        cy=np.bincount(idx,weights=wgt*py,minlength=N)
        good=wsum>1e-9
        new=sites.copy()
        new[good,0]=cx[good]/wsum[good]/S
        new[good,1]=cy[good]/wsum[good]/S
        shift=np.abs(new-sites).mean()
        sites=new
        if it%6==0 or it==iters-1:
            print(f"   lloyd it{it:2d} shift {shift:.2e}",flush=True)
    return sites

def ramp(t,anchors):
    cols=np.array([c for _,c in anchors]); pos=np.array([p for p,_ in anchors])
    return np.stack([np.interp(t,pos,cols[:,k]) for k in range(3)],-1)

PALS={
 'aurora':[(0.0,(0.015,0.02,0.06)),(0.28,(0.05,0.13,0.34)),(0.52,(0.06,0.44,0.58)),
           (0.72,(0.28,0.80,0.60)),(0.88,(0.97,0.85,0.45)),(1.0,(1.0,0.99,0.9))],
 'ember':[(0.0,(0.02,0.012,0.03)),(0.30,(0.16,0.03,0.18)),(0.54,(0.55,0.10,0.27)),
          (0.74,(0.92,0.38,0.17)),(0.90,(0.99,0.76,0.40)),(1.0,(1.0,0.95,0.80))],
 'gold':[(0.0,(0.02,0.02,0.05)),(0.3,(0.12,0.07,0.2)),(0.53,(0.42,0.18,0.3)),
         (0.73,(0.8,0.42,0.22)),(0.9,(0.98,0.78,0.32)),(1.0,(1.0,0.98,0.86))],
 'nebula':[(0.0,(0.02,0.015,0.05)),(0.28,(0.10,0.06,0.28)),(0.5,(0.32,0.10,0.45)),
           (0.70,(0.72,0.20,0.48)),(0.86,(0.98,0.55,0.42)),(1.0,(1.0,0.93,0.72))],
}

def assign(sites,S):
    tree=cKDTree(sites*S)
    yy,xx=np.mgrid[0:S,0:S]
    _,idx=tree.query(np.c_[xx.ravel(),yy.ravel()],workers=-1)
    return idx.reshape(S,S)

def render(sites, S, pal='aurora', save=None, glow=0.42, wallk=0.10):
    N=len(sites)
    idx=assign(sites,S)
    area=np.bincount(idx.ravel(),minlength=N).astype(float)
    area[area==0]=1
    dens=1.0/area                       # local magnification (small cell = bright)
    # hist-eq across cells
    order=np.argsort(np.argsort(dens)); v=order/(N-1)
    v=v**0.85
    field=v[idx]
    rgb=ramp(field,PALS[pal])
    gx=np.zeros((S,S),bool); gy=np.zeros((S,S),bool)
    gx[:,1:]=idx[:,1:]!=idx[:,:-1]; gy[1:,:]=idx[1:,:]!=idx[:-1,:]
    wall=gx|gy
    rgb[wall]*=wallk
    yy,xx=np.mgrid[0:S,0:S]
    rr=np.hypot(xx-(S-1)/2,yy-(S-1)/2)/((S/2))
    m=1.0/(1.0+np.exp((rr-0.985)/0.006))
    rgb*=m[...,None]
    if glow>0:
        b=gaussian_filter((field*(1-wall))**2,S/360)
        top=np.array(PALS[pal][-1][1])
        rgb+=glow*b[...,None]*top[None,None,:]*m[...,None]
    rgb=np.clip(rgb,0,1)
    img=(rgb*255).astype(np.uint8)
    if save: Image.fromarray(img).save(save); print("  ->",save,flush=True)
    return img

def get_sites(N=2200, S_lloyd=600, seed=4):
    mu=build_mu(S_lloyd)
    s=sample_from_mu(N,S_lloyd,mu,seed)
    s=lloyd(s,S_lloyd,mu,iters=30)
    return s

if __name__=='__main__':
    t0=time.time()
    sites=get_sites()
    np.save('/home/user/claude-mythos-self-play/art_bcm8/cvt_sites.npy',sites)
    print(f"sites built {time.time()-t0:.1f}s",flush=True)
    for pal in ['aurora','ember','gold','nebula']:
        render(sites,900,pal=pal,save=f'/home/user/claude-mythos-self-play/art_bcm8/prev_cvt_{pal}.png')
