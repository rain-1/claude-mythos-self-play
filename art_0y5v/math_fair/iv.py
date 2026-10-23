# Minimal vectorised interval arithmetic (numpy), outward rounding by nextafter (+ padding for libm sin/cos/sqrt).
import numpy as np
INF=np.inf
def dn(x,k=1):
    for _ in range(k): x=np.nextafter(x,-INF)
    return x
def up(x,k=1):
    for _ in range(k): x=np.nextafter(x,INF)
    return x
class I:
    __array_priority__=1000
    def __init__(s,lo,hi=None):
        s.lo=np.asarray(lo,float); s.hi=np.asarray(lo if hi is None else hi,float)
    @staticmethod
    def c(x): return x if isinstance(x,I) else I(x,x)
    def __add__(s,o): o=I.c(o); return I(dn(s.lo+o.lo),up(s.hi+o.hi))
    __radd__=__add__
    def __neg__(s): return I(-s.hi,-s.lo)
    def __sub__(s,o): o=I.c(o); return I(dn(s.lo-o.hi),up(s.hi-o.lo))
    def __rsub__(s,o): return I.c(o)-s
    def __mul__(s,o):
        o=I.c(o); p=np.stack([s.lo*o.lo,s.lo*o.hi,s.hi*o.lo,s.hi*o.hi])
        return I(dn(p.min(0)),up(p.max(0)))
    __rmul__=__mul__
    def recip(s):
        assert np.all((s.lo>0)|(s.hi<0)), 'division by interval containing 0'
        return I(dn(1/s.hi),up(1/s.lo))
    def __truediv__(s,o): return s*I.c(o).recip()
    def __rtruediv__(s,o): return I.c(o)*s.recip()
    def contains0(s): return (s.lo<=0)&(s.hi>=0)
    def mid(s): return 0.5*(s.lo+s.hi)
    def w(s): return s.hi-s.lo
def isqrt(x): return I(dn(np.sqrt(np.maximum(x.lo,0)),2),up(np.sqrt(np.maximum(x.hi,0)),2))
def _trig(x,f,peak_shift):
    # f = sin or cos; peaks of f at peak_shift+2k pi (max), +pi (min)
    a=f(x.lo); b=f(x.hi); lo=np.minimum(a,b); hi=np.maximum(a,b)
    kmax=np.ceil((x.lo-peak_shift)/(2*np.pi)); hasmax=peak_shift+2*np.pi*kmax<=x.hi
    kmin=np.ceil((x.lo-peak_shift-np.pi)/(2*np.pi)); hasmin=peak_shift+np.pi+2*np.pi*kmin<=x.hi
    big=(x.hi-x.lo)>=2*np.pi
    hi=np.where(hasmax|big,1.0,hi); lo=np.where(hasmin|big,-1.0,lo)
    return I(np.maximum(dn(lo,2)-1e-16,-1),np.minimum(up(hi,2)+1e-16,1))
def isin(x): return _trig(x,np.sin,np.pi/2)
def icos(x): return _trig(x,np.cos,0.0)
