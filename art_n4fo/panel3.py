"""PANEL 3 — 'The Ghost': pseudospectra of a strongly NON-normal matrix.

Gershgorin/Brauer say where the spectrum MUST be. Pseudospectra say where it could
GO: sigma_eps(A) = {z : sigma_min(zI-A) <= eps} = eigenvalues of some A+E, ||E||<=eps.
For a non-normal matrix (here the Grcar Toeplitz) the eigenvalues sit on a tight curve
but the pseudospectra bulge enormously — the spectrum is a ghost, fragile to a whisper
of perturbation. Density = resolvent norm 1/sigma_min(zI-A). Verified: sigma_min=0 at
each true eigenvalue.
"""
import numpy as np
from scipy.linalg import schur
from PIL import Image
from kit import tonemap, bloom
from scipy.ndimage import gaussian_filter, zoom as ndzoom

def grcar(n, k=3):
    A=np.zeros((n,n))
    for i in range(n):
        A[i,i]=1.0
        if i+1<n: A[i+1,i]=-1.0          # subdiagonal
        for j in range(1,k+1):
            if i+j<n: A[i,i+j]=1.0        # k superdiagonals
    return A

def resolvent_field(A, xs, ys):
    """sigma_min(zI-A) on the grid via batched SVD (Schur-reduced for a small speedup)."""
    T,_=schur(A, output='complex')
    n=A.shape[0]
    X,Y=np.meshgrid(xs,ys)
    Z=(X+1j*Y).ravel()
    smin=np.empty(Z.shape[0])
    I=np.eye(n)
    chunk=4000
    for s in range(0,Z.shape[0],chunk):
        zc=Z[s:s+chunk]
        M=zc[:,None,None]*I[None]-T[None]      # (chunk,n,n)
        sv=np.linalg.svd(M, compute_uv=False)  # (chunk,n)
        smin[s:s+chunk]=sv[:,-1]
    return smin.reshape(X.shape)

def render(S, out, n=48, half=4.2, zc=0.9+0j, grid=None, k_tone=1.0, gamma=0.9):
    A=grcar(n)
    lam=np.linalg.eigvals(A)
    if grid is None: grid=min(S,760)
    xs=np.linspace(zc.real-half, zc.real+half, grid)
    ys=np.linspace(zc.imag+half, zc.imag-half, grid)   # y down
    smin=resolvent_field(A, xs, ys)
    # verify: min over grid near an eigenvalue is tiny
    print(f"[panel3] n={n}  min sigma_min on grid={smin.min():.2e}  (eig spread Re[{lam.real.min():.2f},{lam.real.max():.2f}])")

    # resolvent norm, log-compressed -> the ghost density
    res=1.0/np.maximum(smin,1e-12)
    L=np.log10(res)                         # log resolvent norm
    L=np.clip(L,0,None)
    if grid!=S:
        L=ndzoom(L, S/grid, order=3)
    L=np.clip(L,0,None)                      # cubic upsample can overshoot negative
    # normalize the log field
    L=L/np.percentile(L, 99.7)
    # a cool spectral ramp: deep indigo bulk -> cyan mid -> warm-white crest at the spectrum
    def ramp(t):
        t=np.clip(t,0,1)
        # piecewise: indigo(0) -> teal(0.5) -> gold-white(1)
        c0=np.array([0.05,0.06,0.18]); c1=np.array([0.10,0.55,0.75])
        c2=np.array([0.85,0.95,1.0]); c3=np.array([1.0,0.92,0.72])
        out=np.empty(t.shape+(3,))
        for ch in range(3):
            out[...,ch]=np.interp(t,[0,0.45,0.8,1.0],[c0[ch],c1[ch],c2[ch],c3[ch]])
        return out
    field=ramp(L)*(L[...,None]**0.9)
    buf=field*2.3

    # nested contour glow at eps decades (the classic pseudospectra curves)
    Lc=L*np.percentile(np.log10(res),99.7)   # back to raw log scale for contour placement
    Sf=Lc if grid==S else ndzoom(np.log10(res),S/grid,order=3)
    for lev in np.arange(0.5, Sf.max(), 0.5):
        band=np.exp(-((Sf-lev)/0.10)**2)
        buf+=band[...,None]*np.array([0.55,0.85,1.0])*0.35

    # true eigenvalues: white-hot points on the ghost
    Xs=(lam.real-(zc.real-half))/(2*half)*S
    Ys=((zc.imag+half)-lam.imag)/(2*half)*S
    star=np.zeros((S,S))
    for x,y in zip(Xs,Ys):
        xi,yi=int(round(x)),int(round(y))
        if 0<=xi<S and 0<=yi<S: star[yi,xi]+=1
    # beaded gold truth-thread; carve a soft trough in the ghost so gold reads on top
    star=gaussian_filter(star, sigma=S/700*1.5)
    star/= (star.max()+1e-12)
    thread=np.clip(star*1.6,0,1)
    buf*= (1.0-0.60*thread[...,None])                    # trough for the thread
    buf+=star[...,None]*np.array([1.0,0.72,0.24])*3.6    # pure gold = the truth (stays gold, not white)

    buf=bloom(buf,[(S/700*2.5,0.4),(S/700*8,0.25)])
    img=tonemap(buf,k=k_tone,gamma=gamma)
    Image.fromarray(img).save(out)
    print(f"[panel3] wrote {out} {S}x{S}")

if __name__=="__main__":
    import sys
    S=int(sys.argv[1]) if len(sys.argv)>1 else 760
    out=sys.argv[2] if len(sys.argv)>2 else "variants/panel3_proto.png"
    g=int(sys.argv[3]) if len(sys.argv)>3 else 760
    render(S,out,grid=g)
