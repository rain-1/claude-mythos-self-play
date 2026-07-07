"""
Semidiscrete OPTIMAL TRANSPORT — the Brenier map (HERO engine).
Solve dual weights on a coarse grid, then ASSIGN + cache at target res, then
recolour cheaply.  Colour = transport work, not raw HSV.
"""
import numpy as np, time, sys
from PIL import Image

# ---------- source measures (rotation-invariant) ----------
def radial_density(S, kind='disk'):
    y, x = np.mgrid[0:S, 0:S].astype(np.float64)
    cx = cy = (S-1)/2
    r = np.hypot(x-cx, y-cy) / (S/2)
    if kind == 'disk':
        d = 1.0/(1.0+np.exp((r-0.94)/0.02))          # smooth-edged disk
    elif kind == 'gauss':
        d = np.exp(-(r**2)/(2*0.46**2))
    elif kind == 'ring':
        d = np.exp(-((r-0.55)**2)/(2*0.22**2))
    d = d.astype(np.float64); d /= d.sum()
    return d

# ---------- target sites ----------
def spiral_sites(N, seed=7, arms=2, twist=3.2, sharp=1.6):
    rng = np.random.default_rng(seed)
    M = N*60
    theta = rng.uniform(0, 2*np.pi, M)
    rr = rng.uniform(0,1,M)**0.5
    dens = (0.5+0.5*np.cos(arms*(theta - twist*rr)))**sharp
    dens *= (0.25+0.75*rr)                      # thin the crowded center
    keep = rng.uniform(0,1,M) < dens
    xs = 0.5+0.47*rr*np.cos(theta)
    ys = 0.5+0.47*rr*np.sin(theta)
    return np.c_[xs[keep], ys[keep]][:N]

def spiral_density_at(x, y, arms=2, twist=6.0, sharp=2.2):
    """Target density (rotation-BROKEN spiral galaxy) at normalized coords."""
    dx=x-0.5; dy=y-0.5
    r=np.hypot(dx,dy)/0.47
    th=np.arctan2(dy,dx)
    arm=(0.5+0.5*np.cos(arms*th - twist*np.log(r+0.06)))**sharp
    core=np.exp(-(r**2)/(2*0.16**2))            # gentle bulge
    disk=np.exp(-(r/0.85)**3)                   # outer cutoff
    d=(0.16 + 0.84*arm)*disk + 0.55*core
    d=np.where(r<1.02, d, 0.0)
    return d

def grid_sites(N, seed=11, mask_r=0.985):
    """Jittered hex-ish grid of ~N sites inside the unit disk (space-filling)."""
    rng=np.random.default_rng(seed)
    n=int(np.sqrt(N/(np.pi/4)))+2
    xs=[]; ys=[]
    for j in range(n):
        for i in range(n):
            x=(i+0.5+0.5*(j%2))/n; y=(j+0.5)/n
            xs.append(x); ys.append(y)
    P=np.c_[xs,ys]
    P += (rng.uniform(-0.5,0.5,P.shape))*(0.9/n)
    # map [0,1]^2 -> disk-centered coords, keep inside disk
    d=np.hypot(P[:,0]-0.5,P[:,1]-0.5)
    P=P[d<0.5*mask_r]
    return P

# ---------- power-diagram assignment (KD-tree candidate restriction) ----------
# The power cell owning a pixel is (for mild weights) among its k Euclidean-
# nearest sites. Query k neighbours, then argmin |x-p|^2 - w over just those k.
from scipy.spatial import cKDTree
def power_assign(px, py, w, S, k=14, row_chunk=None):
    N = len(px)
    k = min(k, N)
    tree = cKDTree(np.c_[px, py])
    idx = np.empty(S*S, np.int32)
    if row_chunk is None:
        row_chunk = max(1, 12_000_000 // S)      # ~ bounded query size
    xs = np.arange(S, dtype=np.float64)
    for r0 in range(0, S, row_chunk):
        r1 = min(r0+row_chunk, S)
        gy, gx = np.mgrid[r0:r1, 0:S]
        Q = np.c_[gx.ravel().astype(np.float64), gy.ravel().astype(np.float64)]
        dd, ii = tree.query(Q, k=k, workers=-1)          # (P,k)
        pw = dd*dd - w[ii]                                # power distance
        sel = ii[np.arange(len(Q)), np.argmin(pw, axis=1)]
        idx[r0*S:r1*S] = sel
    return idx

import scipy.sparse as sp
import scipy.sparse.linalg as spla

def solve_weights(px, py, nu, mu, S, iters=300, damp=0.9):
    """Stable log-domain damped ascent on the Kantorovich dual."""
    muf=mu.ravel(); N=len(px); w=np.zeros(N)
    base=S*S/N; mfloor=0.25/N
    bestw=w.copy(); beste=1e9
    for it in range(iters):
        idx=power_assign(px,py,w,S)
        m=np.bincount(idx,weights=muf,minlength=N).astype(float)
        e=np.abs(m-nu).sum()
        if e<beste: beste=e; bestw=w.copy()
        mm=np.maximum(m,mfloor)
        step=base*damp*(np.log(nu)-np.log(mm))
        step=np.clip(step,-2.5*base,2.5*base)
        w+=step; w-=w.mean()
        if it%40==0 or it==iters-1:
            r=m/np.maximum(nu,1e-9)
            print(f"   it{it:3d} L1 {e:.3e} ratio[{r.min():.2f},{r.max():.2f}] med {np.median(r):.2f}",flush=True)
    print(f"   best L1 {beste:.3e}",flush=True)
    return bestw

def hessian(idx, muf, px, py, N, S):
    """Approx dual Hessian entries H_ij = sum_{shared boundary} rho/|pi-pj|."""
    I = idx.reshape(S,S)
    mu2 = muf.reshape(S,S)
    rows=[]; cols=[]; vals=[]
    # horizontal neighbours
    a=I[:,:-1].ravel(); b=I[:,1:].ravel()
    diff=a!=b
    rho=0.5*(mu2[:,:-1].ravel()+mu2[:,1:].ravel())
    ra,rb,rr=a[diff],b[diff],rho[diff]
    rows.append(ra); cols.append(rb); vals.append(rr)
    # vertical neighbours
    a=I[:-1,:].ravel(); b=I[1:,:].ravel()
    diff=a!=b
    rho=0.5*(mu2[:-1,:].ravel()+mu2[1:,:].ravel())
    va,vb,vr=a[diff],b[diff],rho[diff]
    rows.append(va); cols.append(vb); vals.append(vr)
    r=np.concatenate(rows); c=np.concatenate(cols); v=np.concatenate(vals)
    dist=np.hypot(px[r]-px[c], py[r]-py[c])
    v=v/np.maximum(dist,1e-6)
    # symmetric off-diagonals
    H=sp.coo_matrix((np.concatenate([v,v]),
                     (np.concatenate([r,c]),np.concatenate([c,r]))),shape=(N,N)).tocsr()
    deg=np.asarray(H.sum(1)).ravel()
    M=sp.diags(deg)-H          # graph Laplacian (PSD, nullspace=const)
    return M

def solve_weights_newton(px, py, nu, mu, S, iters=45, reg=1e-9):
    muf=mu.ravel(); N=len(px); w=np.zeros(N)
    for it in range(iters):
        idx=power_assign(px,py,w,S)
        m=np.bincount(idx,weights=muf,minlength=N).astype(float)
        g=nu-m
        M=hessian(idx,muf,px,py,N,S)
        M=M+sp.eye(N)*(reg+1e-12)
        try:
            dw=spla.spsolve(M,g)
        except Exception:
            dw=spla.cg(M,g,maxiter=400)[0]
        dw-=dw.mean()
        # damped line search on mass error
        best=None
        for al in (1.0,0.6,0.35,0.18,0.08):
            wt=w+al*dw
            it2=power_assign(px,py,wt,S)
            mt=np.bincount(it2,weights=muf,minlength=N).astype(float)
            e=np.abs(mt-nu).sum()
            if best is None or e<best[0]: best=(e,al,wt)
        w=best[2]; w-=w.mean()
        if it%5==0 or it==iters-1:
            r=m/np.maximum(nu,1e-9)
            print(f"   it{it:3d} L1 {best[0]:.3e} al {best[1]:.2f} ratio[{r.min():.2f},{r.max():.2f}]",flush=True)
        if best[0]<2e-3:
            print("   converged"); break
    return w

def main():
    S_solve = 512
    Nreq = 1900
    t0=time.time()
    mu = radial_density(S_solve, 'disk')
    sites = grid_sites(Nreq, seed=11)
    N = len(sites)
    px = sites[:,0]*S_solve; py = sites[:,1]*S_solve
    # target mass = spiral density at each site (floor prevents cell collapse)
    dens = spiral_density_at(sites[:,0], sites[:,1])
    nu = dens + 0.22*dens.mean()
    nu = nu/nu.sum()
    print(f"N={N}  solving weights (log-ascent) on {S_solve}^2 ...", flush=True)
    w = solve_weights(px, py, nu, mu, S_solve, iters=300)
    # centroids under mu (in normalized [0,1] coords)
    muf = mu.ravel()
    yy,xx = np.mgrid[0:S_solve,0:S_solve].astype(np.float64)
    idx = power_assign(px,py,w,S_solve)
    mm = np.bincount(idx, weights=muf, minlength=N); mm[mm==0]=1
    cx = np.bincount(idx, weights=muf*xx.ravel(), minlength=N)/mm/S_solve
    cy = np.bincount(idx, weights=muf*yy.ravel(), minlength=N)/mm/S_solve
    # cell areas (fraction of pixels) to derive density = mass/area
    ar = np.bincount(idx, minlength=N).astype(float); ar/=ar.sum()
    np.savez('/home/user/claude-mythos-self-play/art_bcm8/ot_state.npz',
             sites=sites, w=w, S_solve=S_solve, cx=cx, cy=cy, nu=nu, area=ar)
    print(f"solved+cached {time.time()-t0:.1f}s", flush=True)

if __name__=='__main__':
    main()
