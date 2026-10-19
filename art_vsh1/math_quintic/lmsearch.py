# Search for rational curves on S of "CW type": polynomials A,B (deg<=kx), C,D (deg<=ky) over C with
#   F(C(t),D(t)) = t^j F(A(t),B(t)),  j in 1..4,
# which give the rational curve tau -> (tau^j A(tau^5), tau^j B(tau^5), C(tau^5), D(tau^5)) on S.
import numpy as np, sys, time, itertools, json
from numpy.polynomial import polynomial as Pn
from scipy.optimize import least_squares
def Fp(a,b):
    ab=Pn.polymul(a,b); s=Pn.polyadd(a,b); q=Pn.polyadd(Pn.polyadd(Pn.polymul(a,a),Pn.polymul(a,b)),Pn.polymul(b,b))
    return Pn.polymul(Pn.polymul(ab,s),q)
def run(kx,ky,j,nstart,seed,tlim):
    rng=np.random.default_rng(seed)
    nx=kx+1; ny=ky+1; n=2*nx+2*ny
    L=max(5*ky,5*kx+j)+1
    r1=rng.normal(size=n)+1j*rng.normal(size=n)
    def unpack(z):
        return z[:nx],z[nx:2*nx],z[2*nx:2*nx+ny],z[2*nx+ny:]
    def res(x):
        z=x[:n]+1j*x[n:]
        A,B,C,D=unpack(z)
        lhs=np.zeros(L,complex); r=Fp(C,D); lhs[:len(r)]+=r
        r=Fp(A,B); lhs[j:j+len(r)]-=r
        nrm=np.dot(r1,z)-1   # fixes overall scale
        # fix t-scaling: sum |A|^2+|B|^2 = sum |C|^2+|D|^2 balance? use: coefficient-norm of (A,B) = 1
        nab=np.sum(abs(z[:2*nx])**2)-1
        out=np.r_[lhs.real,lhs.imag,nrm.real,nrm.imag,nab]
        return out
    sols=[]; t0=time.time(); k=0
    while k<nstart and time.time()-t0<tlim:
        k+=1
        x0=rng.normal(size=2*n)
        r=least_squares(res,x0,method='lm',xtol=1e-15,ftol=1e-15,gtol=1e-15,max_nfev=4000)
        if np.linalg.norm(r.fun)<1e-10:
            z=r.x[:n]+1j*r.x[n:]; A,B,C,D=unpack(z)
            fab=Fp(A,B)
            if np.linalg.norm(fab)<1e-6: continue
            sols.append([list(map(complex,p)) for p in (A,B,C,D)])
    return sols,k
if __name__=="__main__":
    out={}
    tl=float(sys.argv[1]) if len(sys.argv)>1 else 20
    for kx in range(0,5):
      for ky in range(0,5):
        if kx+ky==0: continue
        for j in range(1,5):
          sols,k=run(kx,ky,j,100000,kx*100+ky*10+j,tl)
          print(kx,ky,j,'starts',k,'solutions',len(sols),flush=True)
          out['%d,%d,%d'%(kx,ky,j)]=[[[ [c.real,c.imag] for c in p] for p in s] for s in sols]
    json.dump(out,open('lm_solutions.json','w'))
