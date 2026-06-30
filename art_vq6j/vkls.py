import numpy as np
from bisect import bisect_right

def rsk_shape(perm):
    """Return Young diagram row lengths (insertion-tableau shape) for a permutation."""
    rows=[]   # each row is a sorted list (insertion tableau values)
    for x in perm:
        for r in rows:
            pos=bisect_right(r,x)
            if pos==len(r):
                r.append(x); x=None; break
            else:
                x, r[pos] = r[pos], x   # bump
        if x is not None:
            rows.append([x])
    return [len(r) for r in rows]

def plancherel_shape(n, seed=0):
    rng=np.random.default_rng(seed)
    perm=rng.permutation(n)
    return rsk_shape(perm.tolist())

def profile(lam):
    """Russian-convention boundary: returns (u, phi) integer breakpoints, |phi'|=1."""
    r=len(lam); l1=lam[0]
    D=set(lam[i]-(i+1) for i in range(r))   # 0-indexed i -> row i+1; content positions of down-steps
    us=list(range(-r, l1+1))
    phi=[r]  # phi(-r)=r
    cur=r
    for m in range(-r, l1):
        slope = -1 if m in D else +1
        cur+=slope; phi.append(cur)
    return np.array(us,dtype=float), np.array(phi,dtype=float)

def Omega(u):
    u=np.asarray(u,dtype=float); out=np.abs(u)
    msk=np.abs(u)<=2
    uu=u[msk]
    out[msk]=(2/np.pi)*(uu*np.arcsin(uu/2)+np.sqrt(np.maximum(4-uu*uu,0)))
    return out

if __name__=="__main__":
    for n in [2000, 20000, 100000]:
        lam=plancherel_shape(n, seed=1)
        u,phi=profile(lam)
        assert phi[0]==len(lam) and phi[-1]==lam[0]
        # rescale
        us=u/np.sqrt(n); ph=phi/np.sqrt(n)
        # compare to Omega on a grid
        grid=np.linspace(-1.8,1.8,37)  # bulk; corner region |u|~2 has finite-n edge fluctuations
        ph_i=np.interp(grid, us, ph, left=None, right=None)
        om=Omega(grid)
        err=np.nanmax(np.abs(ph_i-om))
        print(f"n={n}: rows={len(lam)} l1={lam[0]} (2*sqrt n={2*np.sqrt(n):.1f}) max|phi-Omega|={err:.4f}")
