import json
from fractions import Fraction as F
from math import comb
D={int(n):{int(x):c for x,c in v.items()} for n,v in json.load(open('dist.json')).items()}
mom={}
for n,d in D.items():
    T=2**(n-1)
    m1=F(sum(x*c for x,c in d.items()),T); m2=F(sum(x*x*c for x,c in d.items()),T)
    mom[n]=(m1,m2-m1*m1)
    assert m1==F(comb(n,3),4)
for n in range(3,13): print(n, mom[n][1], mom[n][1]*2880)
# fit Var as polynomial in n of degree 4 using exact rational interpolation, check on all n
def lagrange_fit(pts,deg):
    import itertools
    xs=pts[:deg+1]
    def P(z):
        s=F(0)
        for i,(xi,yi) in enumerate(xs):
            t=F(yi)
            for j,(xj,_) in enumerate(xs):
                if j!=i: t*=F(z-xj,xi-xj)
            s+=t
        return s
    return P
for deg in range(3,8):
    P=lagrange_fit([(n,mom[n][1]) for n in range(3,60)],deg)
    if all(P(n)==mom[n][1] for n in D): 
        print("deg",deg,"fits all; coefficients via values:");
        # coefficients
        import numpy as np
        break
