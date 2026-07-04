"""Production six-vertex DWBC ice-point sampler (a=b=c=1, uniform ASM measure).

Config = +-1 integer height function H on (N+1)^2 faces (adjacent differ by +-1
=> ice rule automatic). DWBC saddle boundary: H(x,0)=x, H(0,y)=y, H(N,y)=N-y,
H(x,N)=N-x. Uniform measure sampled by checkerboard heat-bath extremum flips
(flip local max/min by -+2 w.p. 1/2). Caches raw H to .npy for fast re-render.
"""
import numpy as np, sys, time

def init_H(N):
    x=np.arange(N+1)[:,None]; y=np.arange(N+1)[None,:]
    return np.abs(x-y).astype(np.int16)

def make_parity(M):
    a=np.arange(1,M-1)
    xx,yy=np.meshgrid(a,a,indexing='ij')
    p=(xx+yy)&1
    return (p==0), (p==1)

def sweep(H, rng, pmask):
    c=H[1:-1,1:-1]
    up=H[1:-1,:-2]; dn=H[1:-1,2:]; lf=H[:-2,1:-1]; rt=H[2:,1:-1]
    ismax=(lf==c-1)&(rt==c-1)&(up==c-1)&(dn==c-1)
    ismin=(lf==c+1)&(rt==c+1)&(up==c+1)&(dn==c+1)
    flip=(ismax|ismin)&pmask&(rng.random(c.shape)<0.5)
    c += (flip*np.where(ismin,2,-2)).astype(np.int16)

def valid(H):
    return (np.abs(np.diff(H,axis=0))==1).all() and (np.abs(np.diff(H,axis=1))==1).all()

def flip_density(H):
    c=H[1:-1,1:-1]; up=H[1:-1,:-2]; dn=H[1:-1,2:]; lf=H[:-2,1:-1]; rt=H[2:,1:-1]
    mx=(lf==c-1)&(rt==c-1)&(up==c-1)&(dn==c-1)
    mn=(lf==c+1)&(rt==c+1)&(up==c+1)&(dn==c+1)
    return float((mx|mn).mean())

if __name__=="__main__":
    N=int(sys.argv[1]); factor=float(sys.argv[2]) if len(sys.argv)>2 else 2.5
    tag=sys.argv[3] if len(sys.argv)>3 else str(N)
    TOT=int(factor*N*N)
    rng=np.random.default_rng(20260704)
    H=init_H(N); pe,po=make_parity(N+1)
    assert valid(H)
    t0=time.time(); chk=max(1,TOT//20)
    for s in range(TOT+1):
        if s%chk==0:
            el=time.time()-t0
            print(f"sweep {s:8d}/{TOT} ({s/(N*N):.2f}N^2) t={el:6.1f}s fd={flip_density(H):.4f}",flush=True)
            np.save(f"art_eygo/H_{tag}.npy", H)
        if s<TOT: sweep(H,rng,pe); sweep(H,rng,po)
    assert valid(H), "final invalid!"
    np.save(f"art_eygo/H_{tag}.npy", H)
    print(f"DONE N={N} sweeps={TOT} time={time.time()-t0:.1f}s valid={valid(H)} fd={flip_density(H):.4f}")
