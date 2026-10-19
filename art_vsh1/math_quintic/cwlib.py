from fractions import Fraction as Fr
from math import gcd
from functools import reduce
import itertools
S3=[((1,0),(0,1)),((0,1),(1,0)),((0,1),(-1,-1)),((-1,-1),(1,0)),((1,0),(-1,-1)),((-1,-1),(0,1))]
def ap(M,x,y): return (M[0][0]*x+M[0][1]*y, M[1][0]*x+M[1][1]*y)
def F(a,b): return a*b*(a+b)*(a*a+a*b+b*b)
def prim(P):
    g=reduce(gcd,P); P=[p//g for p in P]
    # sign normalize: make F(a,b)>0
    if F(P[0],P[1])<0: P=[-p for p in P]
    return tuple(P)
def cw(u,v):
    a=u*(u+v)*(u**10-4*u**5*v**5-v**10)*(u**4-u**3*v+u**2*v**2-u*v**3+v**4)
    b=2*u*v**5*(3*u**10+v**10)
    c=v*(u+v)*(u**10+4*u**5*v**5-v**10)*(u**4-u**3*v+u**2*v**2-u*v**3+v**4)
    d=v*(u-v)*(u**10-4*u**5*v**5-v**10)*(u**4+u**3*v+u**2*v**2+u*v**3+v**4)
    return (a,b,c,d)
def images(P):
    a,b,c,d=P; out=[]
    for M in S3:
        for N in S3:
            x=ap(M,a,b); y=ap(N,c,d)
            out.append(x+y); out.append(y+x)
    return out
def height(P): return max(abs(p) for p in P)
def on_cw(P):
    """P on the CW curve itself (projectively)? solve for t rational."""
    a,b,c,d=P
    if 0 in (a,b,c,d): return None
    import sympy
    t=sympy.symbols('t')
    p1=sympy.Poly((t**2+4*t-1)*(t+1)*d-(t**2-4*t-1)*(t-1)*c,t)
    p2=sympy.Poly(2*(3*t**2+1)*a-b*(t+1)*(t**2-4*t-1),t)
    g=sympy.gcd(p1,p2)
    for r in sympy.roots(g,filter='Q'):
        r=sympy.Rational(r)
        # tau = a/d * d(t) ; check tau^5 = t  (CW: a=tau, d=(t-1)/(t+1))
        tau=sympy.Rational(a,d)*(r-1)/(r+1)
        if tau**5==r: return tau
    return None
def on_cw_orbit(P):
    for Q in images(P):
        tau=on_cw(Q)
        if tau is not None: return (Q,tau)
    return None
