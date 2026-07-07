import numpy as np
import itertools

def dos_LxL(L):
    """Exact density of states g(E) for the LxL periodic Ising lattice by brute enumeration.
    Returns dict E-> count. Feasible for L<=4 (2^16). E in units of J (sum of s_i s_j over bonds)."""
    n=L*L
    # bond list (torus)
    bonds=[]
    for r in range(L):
        for c in range(L):
            i=r*L+c
            bonds.append((i, r*L+(c+1)%L))      # right
            bonds.append((i, ((r+1)%L)*L+c))     # down
    bonds=np.array(bonds)
    from collections import Counter
    cnt=Counter()
    # vectorised over all 2^n configs in chunks
    idx=np.arange(2**n, dtype=np.uint32)
    CH=1<<20
    for s in range(0,2**n,CH):
        block=idx[s:s+CH]
        bits=((block[:,None]>>np.arange(n)[None,:])&1).astype(np.int8)
        spins=1-2*bits                       # +-1
        E=(spins[:,bonds[:,0]]*spins[:,bonds[:,1]]).sum(1)
        u,c=np.unique(E,return_counts=True)
        for uu,cc in zip(u.tolist(),c.tolist()):
            cnt[uu]+=cc
    return cnt

def zeros_in_v(cnt):
    """Z(K)=sum g(E) e^{K E}. Set t=e^{K}; Z*t^{Emax} is a polynomial in t.
    Root it, map K=log t, v=sinh(2K)=(t^2 - t^-2)/2. Return v roots."""
    Es=np.array(sorted(cnt))
    Emax=int(Es.max())
    deg=2*Emax
    coeff=np.zeros(deg+1, dtype=np.float64)   # index p = power of t = E+Emax
    for E in Es:
        coeff[int(E)+Emax]=cnt[E]
    # numpy roots wants highest-power first
    r=np.roots(coeff[::-1])
    r=r[np.abs(r)>1e-9]
    v=(r**2 - r**-2)/2.0
    return v

if __name__=="__main__":
    for L in [3,4]:
        cnt=dos_LxL(L)
        # sanity: total configs
        tot=sum(cnt.values());
        v=zeros_in_v(cnt)
        av=np.abs(v)
        print(f"L={L}: configs={tot} (2^{L*L}={2**(L*L)}), #vroots={len(v)}, "
              f"|v| median={np.median(av):.4f} mean={av.mean():.4f} "
              f"frac within 8% of circle={np.mean(np.abs(av-1)<0.08):.2f}")
        np.save(f"zeros_v_L{L}.npy", v)
