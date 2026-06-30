import numpy as np

def Q_cf(x, N=40):
    """Minkowski ? via continued fraction, x in [0,1]."""
    if x<=0: return 0.0
    if x>=1: return 1.0
    a=[]; y=x
    for _ in range(N):
        y=1.0/y
        ai=int(np.floor(y))
        a.append(ai)
        y=y-ai
        if y<1e-15: break
    # ?([0;a1,a2,...]) = 2 * sum_{k>=1} (-1)^{k+1} 2^{-(a1+...+ak)}
    s=0.0; cum=0; sign=1.0
    for ai in a:
        cum+=ai
        s+=sign*2.0**(-cum)
        sign=-sign
    return 2.0*s

# IFS maps whose attractor is the graph of ?
def L(p): x,y=p; return (x/(1.0+x), y/2.0)
def R(p): x,y=p; return (1.0/(2.0-x), (1.0+y)/2.0)

if __name__=="__main__":
    # verify IFS lands on the graph: apply random words, check y == Q(x)
    rng=np.random.default_rng(0)
    maxerr=0
    for _ in range(2000):
        p=(rng.random(), rng.random())
        for _ in range(40):
            p=L(p) if rng.random()<0.5 else R(p)
        err=abs(p[1]-Q_cf(p[0]))
        maxerr=max(maxerr,err)
    print("IFS-on-graph max error:",maxerr)
    # verify known values
    import math
    g=(math.sqrt(5)-1)/2  # 1/phi, CF [0;1,1,1,...] -> ?=2/3
    print("?(1/phi)=",Q_cf(g),"expected 2/3")
    print("?(1/2)=",Q_cf(0.5),"?(1/3)=",Q_cf(1/3),"expected .25")
    print("?(2/5)=",Q_cf(0.4),"  ?(sqrt2-1)=",Q_cf(math.sqrt(2)-1))
