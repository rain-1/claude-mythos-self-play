import numpy as np

def next_level(roots):
    """Given sorted real roots r_1<...<r_m of a hyperbolic poly P, return the m-1 roots of P'
       = unique zeros of f(x)=sum 1/(x-r_i) in each gap (r_j,r_{j+1}), via bisection.
       (Exact: reality preserved under differentiation; Rolle interlacing.)"""
    r=np.sort(roots); m=len(r)
    out=np.empty(m-1)
    for j in range(m-1):
        lo=r[j]; hi=r[j+1]
        # f decreasing +inf->-inf on (lo,hi); bisect
        a=lo+1e-12*(hi-lo); b=hi-1e-12*(hi-lo)
        for _ in range(80):
            mid=0.5*(a+b)
            fm=np.sum(1.0/(mid-r))
            if fm>0: a=mid
            else: b=mid
        out[j]=0.5*(a+b)
    return out

def cascade(base_roots):
    """Return list levels[0..N-1]; levels[0]=base (N roots), levels[k]=roots of k-th derivative."""
    levels=[np.sort(np.asarray(base_roots,dtype=np.float64))]
    while len(levels[-1])>1:
        levels.append(next_level(levels[-1]))
    return levels

def verify_interlacing(levels):
    ok=True
    for k in range(len(levels)-1):
        a=levels[k]; b=levels[k+1]
        for j in range(len(b)):
            if not (a[j] < b[j] < a[j+1]): ok=False
    return ok

if __name__=="__main__":
    z=np.load("zeta_zeros.npy")
    lev=cascade(z)
    print("levels:",len(lev),"base roots:",len(lev[0]))
    print("interlacing holds:", verify_interlacing(lev))
    print("apex (root of (N-1)th deriv) =", lev[-1][0], " vs mean of roots =", z.mean())
