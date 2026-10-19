# Complex Gauss-Newton search for  F(C,D) = t^j F(A,B)  (deg A,B<=kx, deg C,D<=ky), see RESULTS.md
import numpy as np, sys, time, json
from numpy.polynomial import polynomial as Pn
mul=Pn.polymul; add=Pn.polyadd
def parts(a,b):
    s=add(a,b); q=add(add(mul(a,a),mul(a,b)),mul(b,b)); ab=mul(a,b)
    F=mul(mul(ab,s),q)
    Fa=add(add(mul(mul(b,s),q),mul(ab,q)),mul(mul(ab,s),add(2*a,b)))
    Fb=add(add(mul(mul(a,s),q),mul(ab,q)),mul(mul(ab,s),add(a,2*b)))
    return F,Fa,Fb
def put(v,L,off=0):
    o=np.zeros(L,complex); o[off:off+len(v)]=v; return o
def run(kx,ky,j,nstart,seed,tlim,real=False):
    rng=np.random.default_rng(seed); nx=kx+1; ny=ky+1; n=2*nx+2*ny
    L=max(5*ky,5*kx+j)+1
    r1=rng.normal(size=n)+(0 if real else 1j)*rng.normal(size=n); r2=rng.normal(size=5*kx+1)+(0 if real else 1j)*rng.normal(size=5*kx+1)
    sols=[]; t0=time.time(); k=0
    while k<nstart and time.time()-t0<tlim:
        k+=1
        z=(rng.normal(size=n)+(0 if real else 1j)*rng.normal(size=n)).astype(complex); z/= (r1@z)
        for it in range(200):
            A,B,C,D=z[:nx],z[nx:2*nx],z[2*nx:2*nx+ny],z[2*nx+ny:]
            Fc,Fca,Fcb=parts(C,D); Fab,Faa,Fab_b=parts(A,B)
            R=put(Fc,L)-put(Fab,L,j)
            Lf=5*kx+1
            R=np.r_[R,r1@z-1,(r2@put(Fab,Lf))-1]
            J=np.zeros((L+2,n),complex)
            for i in range(nx):
                J[:,i][:L]=-put(Faa,L,j+i); J[:,nx+i][:L]=-put(Fab_b,L,j+i)
            for i in range(ny):
                J[:,2*nx+i][:L]=put(Fca,L,i); J[:,2*nx+ny+i][:L]=put(Fcb,L,i)
            J[L,:]=r1
            for i in range(nx):
                J[L+1,i]=r2@put(Faa,Lf,i); J[L+1,nx+i]=r2@put(Fab_b,Lf,i)
            nr=np.linalg.norm(R)
            if nr<1e-13 or not np.isfinite(nr): break
            dz=np.linalg.lstsq(J,R,rcond=None)[0]
            # damping
            lam=1.0
            z=z-lam*dz
        if np.isfinite(nr) and nr<1e-11:
            A,B,C,D=z[:nx],z[nx:2*nx],z[2*nx:2*nx+ny],z[2*nx+ny:]
            Fab=parts(A,B)[0]
            if np.linalg.norm(Fab)<1e-4*(np.linalg.norm(A)+np.linalg.norm(B))**5: continue
            sv=np.linalg.svd(J,compute_uv=False); smin=sv[-1]/sv[0]
            if smin<1e-6: continue
            sols.append((A,B,C,D))
    return sols,k
if __name__=="__main__":
    t=time.time(); s,k=run(3,3,1,100000,1,float(sys.argv[1])); print(len(s),k,time.time()-t)
