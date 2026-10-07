"""Zeros of zeta on the critical line up to height T by Riemann-Siegel Z(t) with two correction terms."""
import numpy as np, sys
def theta(t): return t/2*np.log(t/(2*np.pi))-t/2-np.pi/8+1/(48*t)+7/(5760*t**3)
def Z(t):
    t=np.asarray(t,float); th=theta(t); a=np.sqrt(t/(2*np.pi)); N=np.floor(a).astype(int); p=a-N
    out=np.zeros_like(t)
    for n in range(1,N.max()+1):
        m=n<=N; out[m]+=2*np.cos(th[m]-t[m]*np.log(n))/np.sqrt(n)
    c0=np.cos(2*np.pi*(p*p-p-1/16))/np.cos(2*np.pi*p)
    # first correction term C1 via derivatives of psi(p) (standard R-S), good enough for sign changes
    def psi(p): return np.cos(2*np.pi*(p*p-p-1/16))/np.cos(2*np.pi*p)
    h=1e-4
    psi3=(psi(p+2*h)-2*psi(p+h)+2*psi(p-h)-psi(p-2*h))/(2*h**3)
    c1=-psi3/(96*np.pi**2)
    R=(-1)**(N-1)*a**(-0.5)*(c0+c1*a**(-1))
    return out+R
def zeros(T,step=0.01):
    t=np.arange(14.0,T,step); z=Z(t); s=np.sign(z); idx=np.nonzero(s[:-1]*s[1:]<0)[0]
    # refine by secant
    t0,t1=t[idx],t[idx+1]; z0,z1=z[idx],z[idx+1]
    return t0-z0*(t1-t0)/(z1-z0)
if __name__=="__main__":
    T=float(sys.argv[1]); zs=zeros(T); print(len(zs), zs[:5], zs[-3:])
    np.save('proto/zeros_%d.npy'%int(T),zs)
    import mpmath
    for k in (1,2,10,100,min(len(zs),1000)):
        print(k, zs[k-1], float(mpmath.zetazero(k).imag))
