"""hero_final.py — streaming, memory-safe amoeba builder for the 4096^2 hero.
Row-by-row: solve w-roots for a strip of z, embed to symmetric UV, apply the 6 D3
group elements, accumulate into a fixed 2D histogram.  Bounded RAM regardless of Nx,Nth.
"""
import numpy as np
from tropical import poly_w_coeffs, roots_batch
from hero import curve, tropical_field, d3_group, A
from PIL import Image

def coarse_frame(C, d, lam, Nx=500, Nth=800):
    zr=(-lam*d*3-2, lam*d*3+2)
    xs=np.linspace(zr[0],zr[1],Nx); th=np.linspace(0,2*np.pi,Nth,endpoint=False)
    Us=[]; Vs=[]
    for x in xs:
        z=np.exp(x+1j*th); R=roots_batch(poly_w_coeffs(C,z))
        X=np.full(R.shape,x); Y=np.log(np.abs(R)+1e-300)
        P=A@np.vstack([X.ravel(),Y.ravel()]); Us.append(P[0]); Vs.append(P[1])
    U=np.concatenate(Us); V=np.concatenate(Vs)
    Hc,ue,ve=np.histogram2d(U,V,bins=240)
    uc=0.5*(ue[:-1]+ue[1:]); vc=0.5*(ve[:-1]+ve[1:])
    body=Hc>0.18*Hc.max()
    UU,VV=np.meshgrid(uc,vc,indexing='ij')
    cu=UU[body].mean(); cv=VV[body].mean()
    ui=np.where(body.any(1))[0]; vi=np.where(body.any(0))[0]
    s=max(ue[ui[-1]+1]-ue[ui[0]], ve[vi[-1]+1]-ve[vi[0]])
    return cu,cv,s*(0.5+0.16)

def build(d,lam,S=4096,Nx=5200,Nth=7000,tag='HERO'):
    C,val=curve(d,lam)
    cu,cv,half=coarse_frame(C,d,lam)
    print('frame',round(cu,2),round(cv,2),round(half,2),flush=True)
    zr=(-lam*d*3-2, lam*d*3+2)
    xs=np.linspace(zr[0],zr[1],Nx); th=np.linspace(0,2*np.pi,Nth,endpoint=False)
    rng=np.random.default_rng(7); dx=(zr[1]-zr[0])/Nx; dth=2*np.pi/Nth
    G=d3_group()
    u0e,v0e=cu-half,cv-half; inv=S/(2*half)
    Hflat=np.zeros(S*S,np.float64)
    batch=[]; BN=150
    def flush(batch):
        if batch:
            Hflat[:]+=np.bincount(np.concatenate(batch),minlength=S*S)
    for a,x0 in enumerate(xs):
        x=x0+rng.uniform(-0.5,0.5)*dx     # jitter x only (theta stays uniform: clean tentacles)
        z=np.exp(x+1j*th); R=roots_batch(poly_w_coeffs(C,z))
        X=np.full(R.shape,x).ravel(); Y=np.log(np.abs(R)+1e-300).ravel()
        P=A@np.vstack([X,Y]); U0,V0=P[0]-cu,P[1]-cv
        for g in G:
            u=cu+g[0,0]*U0+g[0,1]*V0; v=cv+g[1,0]*U0+g[1,1]*V0
            iu=((u-u0e)*inv).astype(np.intp); iv=((v-v0e)*inv).astype(np.intp)
            ok=(iu>=0)&(iu<S)&(iv>=0)&(iv<S)
            batch.append(iu[ok]*S+iv[ok])
        if len(batch)>=BN*6:
            flush(batch); batch=[]
        if a% max(1,Nx//20)==0: print('row',a,'/',Nx,flush=True)
    flush(batch)
    H=Hflat.reshape(S,S)          # H[iu,iv]
    H=H.T[::-1]
    dens=np.log1p(H); dens/=dens.max()+1e-9
    np.save(f'{tag}_dens.npy',dens.astype(np.float32))
    # tropical spine at full res
    gap,_=tropical_field(val,d,cu,cv,half,S); gap=gap[::-1]
    np.save(f'{tag}_gap.npy',gap.astype(np.float32))
    np.savez(f'{tag}_meta.npz',cu=cu,cv=cv,half=half,S=S,d=d,lam=lam)
    print(tag,'DONE',dens.shape,flush=True)

if __name__=='__main__':
    import sys
    d=int(sys.argv[1]); lam=float(sys.argv[2]); S=int(sys.argv[3])
    Nx=int(sys.argv[4]); Nth=int(sys.argv[5]); tag=sys.argv[6]
    build(d,lam,S=S,Nx=Nx,Nth=Nth,tag=tag)
