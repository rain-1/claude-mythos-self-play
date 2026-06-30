import numpy as np

def Q_vec(x, N=32, eps=1e-15):
    """Vectorised Minkowski ? on array x in [0,1]."""
    x=np.asarray(x,dtype=np.float64)
    y=np.clip(x.copy(),0,1)
    s=np.zeros_like(y); cum=np.zeros_like(y); sign=1.0
    active=(y>eps)&(y<1-1e-16)
    # handle x==1 -> 1, x==0 -> 0 at end
    yy=np.where(active,y,0.5)
    for k in range(N):
        inv=1.0/np.where(yy>eps,yy,1.0)
        a=np.floor(inv)
        cum_new=cum+a
        term=sign*np.exp2(-np.clip(cum_new,0,1000))
        s=np.where(active, s+term, s)
        cum=np.where(active, cum_new, cum)
        yy=inv-a
        active=active&(yy>eps)
        yy=np.where(active,yy,0.5)
        sign=-sign
    Q=2.0*s
    Q=np.where(x<=0,0.0,Q); Q=np.where(x>=1,1.0,Q)
    return Q

if __name__=="__main__":
    from mink import Q_cf
    import math
    xs=np.array([0,0.25,1/3,0.4,0.5,(math.sqrt(5)-1)/2,math.sqrt(2)-1,0.75,1.0])
    qv=Q_vec(xs)
    for x,q in zip(xs,qv):
        print(f"x={x:.5f}  Qvec={q:.6f}  Qcf={Q_cf(float(x)):.6f}")
    # random check
    rng=np.random.default_rng(0); r=rng.random(5000)
    qv=Q_vec(r); qc=np.array([Q_cf(float(v)) for v in r])
    print("max err vs Q_cf:", np.max(np.abs(qv-qc)))
