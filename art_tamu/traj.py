import numpy as np, math
def T(n):
    n=3*n-1
    while n%2==0: n//=2
    return n
CYC={1:1,5:2,7:2,17:3,25:3,37:3,55:3,41:3,61:3,91:3}
def orbit(n):
    o=[n]
    while n not in CYC:
        n=T(n); o.append(n)
    # continue around the cycle once to close it
    lab=CYC[n]
    return o,lab
def starts(top=31, per=3, spread=0.0, seed=1):
    rng=np.random.default_rng(seed); S=[]
    for j in range(12):
        for k in range(per):
            x=top + j/12 + rng.uniform(-spread,spread)
            n=int(2**x)|1
            S.append(n)
    return S
