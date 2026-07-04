"""Six-vertex DWBC ice-point sampler: mixing & symmetry study."""
import numpy as np, sys, time
from PIL import Image

def init_H(N):
    x=np.arange(N+1)[:,None]; y=np.arange(N+1)[None,:]
    return np.abs(x-y).astype(np.int32)

def sweep(H, rng, parity):
    M=H.shape[0]; c=H[1:-1,1:-1]
    up=H[1:-1,:-2]; dn=H[1:-1,2:]; lf=H[:-2,1:-1]; rt=H[2:,1:-1]
    a0=np.arange(1,M-1); xx,yy=np.meshgrid(a0,a0,indexing='ij')
    pm=((xx+yy)%2)==parity
    ismax=(lf==c-1)&(rt==c-1)&(up==c-1)&(dn==c-1)
    ismin=(lf==c+1)&(rt==c+1)&(up==c+1)&(dn==c+1)
    flip=(ismax|ismin)&pm&(rng.random(c.shape)<0.5)
    H[1:-1,1:-1]=c+np.where(flip, np.where(ismin,2,-2), 0)

def c_field(H):
    # c-vertex (saddle) indicator on NxN vertices
    f00=H[:-1,:-1]; f10=H[1:,:-1]; f11=H[1:,1:]; f01=H[:-1,1:]
    s0=f10-f00; s2=f01-f11
    return (s0*s2>0)   # alternating +-+- => c vertex

def asym(D):
    # relative deviation from D4 symmetrization
    S=(D+D.T+D[::-1,::-1]+D[::-1,::-1].T)/4.0
    return float(np.abs(D-S).mean()/ (D.mean()+1e-9))

def render(H, size=512):
    f00=H[:-1,:-1]; f10=H[1:,:-1]; f11=H[1:,1:]; f01=H[:-1,1:]
    s0=f10-f00; s2=f01-f11
    isc=(s0*s2>0)
    gx=(f10-f00); gy=(f01-f00)
    code=((gx>0).astype(int)+2*(gy>0).astype(int))
    code=np.where(isc, 4+((s0>0).astype(int)), code)
    pal=np.array([[25,35,75],[60,95,170],[150,80,40],[210,150,60],
                  [255,250,240],[130,240,220]],np.uint8)
    img=pal[code]
    im=Image.fromarray(np.transpose(img,(1,0,2))[::-1])
    return im.resize((size,size),Image.NEAREST)

if __name__=="__main__":
    N=int(sys.argv[1]); TOT=int(sys.argv[2])
    rng=np.random.default_rng(7); H=init_H(N); t0=time.time()
    chk=max(1,TOT//12)
    for s in range(TOT+1):
        if s%chk==0:
            D=c_field(H).astype(float)
            # coarse-bin for symmetry metric
            n=D.shape[0]; b=n//32 or 1; nb=n//b
            Dc=D[:nb*b,:nb*b].reshape(nb,b,nb,b).mean((1,3))
            print(f"sweep {s:7d}  t={time.time()-t0:6.1f}s  c_dens={D.mean():.4f}  asym={asym(Dc):.4f}",flush=True)
            if s in (0, chk*3, chk*6, TOT):
                render(H).save(f"art_eygo/mix_{N}_{s}.png")
        if s<TOT: sweep(H,rng,0); sweep(H,rng,1)
    render(H,600).save(f"art_eygo/mix_{N}_final.png")
    print("done")
