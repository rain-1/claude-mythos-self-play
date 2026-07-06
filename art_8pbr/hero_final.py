"""FINAL HERO: 'The Astroid of Return' — conjugate locus (Jacobi 4-cusp astroid)
of a point on a triaxial ellipsoid, with its cut-locus segment.

Layers, composited over a dark shaded ellipsoid body:
  - geodesic fold-density caustic  (gold -> white-hot cusps)  = conjugate locus
  - cut-locus seam                 (electric cyan)            = where 2 shortest tie
"""
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
from cutlocus_ell import cut_locus_field

def rot_matrix(view_dir, up=np.array([0,0,1.0])):
    f=view_dir/np.linalg.norm(view_dir)
    if abs(np.dot(f,up))>0.95: up=np.array([0,1.0,0])
    r=np.cross(up,f); r/=np.linalg.norm(r)
    u=np.cross(f,r)
    return np.stack([r,u,f],0)

def ellipsoid_body(Rc, ext, S, A, light_dir):
    """analytic orthographic ray-cast of x^T A x = 1; returns mask, normal_cam_z, shade."""
    r,u,f=Rc
    xs=np.linspace(-ext,ext,S); ys=np.linspace(ext,-ext,S)
    X,Y=np.meshgrid(xs,ys)
    # world point w = X r + Y u + t f ; solve (w)^T A (w)=1 for t
    # coefficients: At2 t^2 + Bt t + Ct =0
    Ar=A*r; Au=A*u; Af=A*f
    a2=f@Af
    b1=2*(X*(r@Af)+Y*(u@Af))
    c1=(X*X)*(r@Ar)+(Y*Y)*(u@Au)+2*X*Y*(r@Au)-1.0
    disc=b1*b1-4*a2*c1
    mask=disc>0
    sq=np.sqrt(np.clip(disc,0,None))
    t1=(-b1-sq)/(2*a2); t2=(-b1+sq)/(2*a2)
    tfront=np.maximum(t1,t2)  # +f points to camera? choose the hit with larger w·f (closer)
    # world hit
    W=(X[...,None]*r+Y[...,None]*u+tfront[...,None]*f)
    n=W*A; nn=np.linalg.norm(n,axis=2,keepdims=True)+1e-12; n=n/nn
    ncam=n@Rc.T
    facing=ncam[...,2]>0
    mask=mask&facing
    L=light_dir/np.linalg.norm(light_dir)
    diff=np.clip((n*L).sum(2),0,1)
    rim=np.clip(1-ncam[...,2],0,1)**2.2
    shade=0.06+0.34*diff+0.28*rim
    depth=W@f  # closeness
    return mask, shade, depth, W, n

def accumulate_caustic(pos, spread, s_of_t, Rc, ext, S, A, fold_pow=1.3,
                       sfrac_min=0.15, cull=-0.03, sconj=None, edge_boost=0.0,
                       edge_sigma=0.18):
    """Bilinear-splat the geodesic fan, weighted by fold density (1/spreading).
    Chunked over the time axis to bound RAM at high resolution."""
    T,N,_=pos.shape
    sp_med=np.median(spread[spread>0])
    acc=np.zeros((S,S))
    accf=acc.reshape(-1)
    sfrac_t=np.linspace(0,1,T)
    for t0 in range(0,T,64):
        t1=min(T,t0+64)
        P=pos[t0:t1].reshape(-1,3)@Rc.T
        nrm=(pos[t0:t1].reshape(-1,3)*A)
        nrm/=np.linalg.norm(nrm,axis=1)[:,None]
        facing=(nrm@Rc.T)[:,2]>cull
        sx=((P[:,0]/ext)*0.5+0.5)*(S-1); sy=((-P[:,1]/ext)*0.5+0.5)*(S-1)
        sp=spread[t0:t1].reshape(-1)
        foldw=np.clip((sp_med/(sp+1e-9))**fold_pow,0,600.0)
        if edge_boost>0 and sconj is not None:
            sarr=np.repeat(s_of_t[t0:t1,None],N,axis=1).reshape(-1)
            scj=np.tile(sconj,t1-t0)
            foldw=foldw*(1.0+edge_boost*np.exp(-((sarr-scj)/edge_sigma)**2))
        sfr=np.repeat(sfrac_t[t0:t1,None],N,axis=1).reshape(-1)
        m=facing&(sfr>sfrac_min)&(sx>=0)&(sx<S-1)&(sy>=0)&(sy<S-1)
        sx=sx[m]; sy=sy[m]; w=foldw[m]
        x0=sx.astype(np.int64); y0=sy.astype(np.int64)
        fx=sx-x0; fy=sy-y0
        base=y0*S+x0
        np.add.at(accf,base,       w*(1-fx)*(1-fy))
        np.add.at(accf,base+1,     w*fx*(1-fy))
        np.add.at(accf,base+S,     w*(1-fx)*fy)
        np.add.at(accf,base+S+1,   w*fx*fy)
    return acc

def render(cache, S=1000, out="hero_final.png", fold_pow=1.35, ss=1):
    d=np.load(cache)
    pos=d['pos']; spread=d['spread']; A=d['A']; p=d['p']; abc=d['abc']; s_of_t=d['s_of_t']
    a,b,c=abc; ext=max(a,b,c)*1.16
    view=-p
    Rc=rot_matrix(view)
    Sr=S*ss
    # light from upper-left, slightly toward camera
    light=Rc[0]*(-0.5)+Rc[1]*0.7+Rc[2]*0.5
    mask,shade,depth,W,n=ellipsoid_body(Rc,ext,Sr,A,light)
    acc=accumulate_caustic(pos,spread,s_of_t,Rc,ext,Sr,A,fold_pow=fold_pow,
                           sconj=d['sconj'],edge_boost=2.2,edge_sigma=0.16)
    # only keep caustic on the body
    acc=acc*mask
    # tone caustic
    v=np.log1p(acc); pos97=np.percentile(v[v>0],99.4); v=np.clip(v/pos97,0,1)
    # cut locus: compute at a FIXED moderate res (clean thin seam), then upsample.
    from scipy.ndimage import label
    Sc=700
    cut,mins,dirf=cut_locus_field(pos,s_of_t,Rc,ext,Sc,A)
    lab,ncomp=label(cut)
    if ncomp>0:
        sizes=np.bincount(lab.ravel()); sizes[0]=0
        cut=lab==sizes.argmax()
    cutf=np.array(Image.fromarray((cut*255).astype(np.uint8)).resize((Sr,Sr),Image.BILINEAR),float)/255.0
    cutf=gaussian_filter(cutf,0.9*ss)*(mask>0)
    if cutf.max()>0: cutf/=cutf.max()
    # ---- compose ----
    rgb=np.zeros((Sr,Sr,3))
    # body: deep indigo->teal, darker at the terminator, faint warm limb
    rim=np.clip(1-(n@Rc.T)[...,2],0,1)**2.2
    rgb[...,0]=(shade*0.11+0.05*rim)*mask
    rgb[...,1]=(shade*0.15+0.05*rim)*mask
    rgb[...,2]=(shade*0.30+0.04*rim)*mask
    # caustic via curated ramp: near-black -> dim violet -> amber -> gold -> white-hot
    ve=v**1.20
    anchor=np.array([0.0,0.18,0.42,0.72,1.0])
    cr=np.array([0.00,0.22,0.95,1.25,1.55])
    cg=np.array([0.00,0.10,0.48,0.98,1.42])
    cb=np.array([0.00,0.34,0.16,0.42,1.15])
    rgb[...,0]+=np.interp(ve,anchor,cr)
    rgb[...,1]+=np.interp(ve,anchor,cg)
    rgb[...,2]+=np.interp(ve,anchor,cb)
    # bloom on the brightest caustic (cusps)
    hot=np.clip(v-0.6,0,1)
    bl=gaussian_filter(hot,3*ss)
    rgb[...,0]+=1.4*bl; rgb[...,1]+=1.1*bl; rgb[...,2]+=0.6*bl
    # cut locus electric cyan (the fork line)
    rgb[...,0]+=0.22*cutf
    rgb[...,1]+=1.05*cutf
    rgb[...,2]+=1.25*cutf
    clb=gaussian_filter(cutf,2.2*ss)
    rgb[...,1]+=0.55*clb; rgb[...,2]+=0.70*clb
    # filmic tone + gamma
    rgb=1-np.exp(-1.25*np.clip(rgb,0,None))
    rgb=np.clip(rgb,0,1)**0.90
    if ss>1:
        img=Image.fromarray((255*rgb).astype(np.uint8)).resize((S,S),Image.LANCZOS)
    else:
        img=Image.fromarray((255*rgb).astype(np.uint8))
    img.save(out); print("saved",out)

if __name__=="__main__":
    import os
    CACHE="hero_hi.npz"
    if not os.path.exists(CACHE):
        from hero_build import compute
        # source at the +x vertex of the ellipsoid -> a symmetric antipodal astroid
        compute((1.6,1.35,0.8),(np.pi/2,0.0),N=18000,L=5.0,nsteps=3200,cache=CACHE)
    render(CACHE,S=4096,out="01_astroid_of_return.png")
