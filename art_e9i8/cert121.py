import sys; sys.set_int_max_str_digits(200000)
import sympy as sp, math, json
from math import isqrt
t=sp.symbols('t')
def qpoly(m):
    c0,c1=sp.Integer(1),t-1
    for k in range(2,m+1):
        a=t-1 if k==m else t-2
        c0,c1=c1,sp.expand(a*c1-c0)
    return sp.div(c1,t)[0]
def fpoly(n):
    e0,e1=sp.Integer(1),t+1
    for k in range(2,n):
        e0,e1=e1,sp.expand((t+2)*e1-e0)
    return sp.expand((t+1)*e1-e0)
for n in (98,121,128):
    T=abs(sp.resultant(qpoly(n),fpoly(n),t))//n
    s=isqrt(T); assert s*s==T, ("NOT SQUARE",n)
    print(f"n={n}: T(n,n) is a perfect square, sqrt has {len(str(s))} digits, T has {len(str(T))} digits", flush=True)
print("CERT121 DONE")
