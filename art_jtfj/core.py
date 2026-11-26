"""Shared maths for the Straight Coast (MO 518177).
E(s)=M^(s-1) * sum_{d|m} a(d) d^-s,  D=E(s)+E(1-s),  F(s)=E(s)/E(1-s).  |F|=1 is the coast."""
import numpy as np
from sympy import factorint, divisors, jacobi_symbol
def chi_m4(n): n%=4; return {1:1,3:-1}.get(n,0)
def chi_5(n): n%=5; return {1:1,4:1,2:-1,3:-1}.get(n,0)
def chi_m20(n): return chi_m4(n)*chi_5(n)
def a_epstein(n):
    return sum(chi_m20(d)+chi_m4(d)*chi_5(n//d) for d in divisors(n))
def setup(m,kind='div',M=None):
    ds=np.array(divisors(m),float)
    if kind=='div': a=np.ones_like(ds)
    else: a=np.array([a_epstein(int(d)) for d in ds],float)
    if M is None:
        M=m*np.prod([p for p in factorint(m)])
    keep=a!=0
    return ds[keep],a[keep],float(M)
def A(s,ds,a):           # Dirichlet polynomial sum a(d) d^-s, s any complex array
    s=np.asarray(s,complex); out=np.zeros(s.shape,complex)
    for d,c in zip(ds,a): out+=c*np.exp(-s*np.log(d))
    return out
def logF(s,ds,a,M):      # log|F| and arg F
    s=np.asarray(s,complex)
    num=A(s,ds,a); den=A(1-s,ds,a)
    with np.errstate(divide='ignore',invalid='ignore'):
        lf=(2*s.real-1)*np.log(M)+np.log(np.abs(num))-np.log(np.abs(den))
    ph=np.angle(num/den)+2*s.imag*np.log(M)
    return lf,ph
def tide(t,ds,a,M):      # sqrt(M) D(1/2+it) = 2 Re( M^{it} A(1/2+it) ), real
    s=0.5+1j*np.asarray(t,float)
    return 2*np.real(np.exp(1j*np.asarray(t,float)*np.log(M))*A(s,ds,a))

def Aprod(s,m):
    """sigma_{-s}(m) as a product over primes (fast), s complex array"""
    s=np.asarray(s,np.complex128); out=np.ones(s.shape,np.complex128)
    for p,e in factorint(m).items():
        u=np.exp(-s*np.log(p)); q=np.ones(s.shape,np.complex128)
        for _ in range(e): q=q*u+1
        out*=q
    return out
def logF_fast(s,m,M):
    s=np.asarray(s,np.complex128); n=Aprod(s,m); d=Aprod(1-s,m)
    with np.errstate(divide='ignore',invalid='ignore'):
        lf=(2*s.real-1)*np.log(M)+np.log(np.abs(n))-np.log(np.abs(d))
        ph=np.angle(n/d*np.exp(2j*s.imag*np.log(M)))
    return lf,ph
def pits(m,t0,t1):
    """zeros of sigma_{-s}(m): s=i t, t=2 pi k/((e+1) log p), (e+1) not dividing k"""
    out=[]
    for p,e in factorint(m).items():
        per=2*np.pi/((e+1)*np.log(p)); k=np.arange(int(np.floor(t0/per)),int(np.ceil(t1/per))+1)
        k=k[(k%(e+1)!=0)]; t=k*per; out+=[(float(x),int(p)) for x in t if t0<=x<=t1]
    return sorted(out)
def lights(m,M,t0,t1,n=400001,kind='div',dsa=None):
    t=np.linspace(t0,t1,n)
    if dsa is None: y=2*np.real(np.exp(1j*t*np.log(M))*Aprod(0.5+1j*t,m))
    else: y=tide(t,dsa[0],dsa[1],M)
    i=np.nonzero(np.sign(y[1:])!=np.sign(y[:-1]))[0]
    return t[i]-y[i]*(t[i+1]-t[i])/(y[i+1]-y[i]), (t,y)
