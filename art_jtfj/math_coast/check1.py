import sys; sys.path.insert(0,'..')
import numpy as np
from core import *
def newton(f,s0,it=60):
    s=complex(s0)
    for _ in range(it):
        h=1e-6; d=(f(s+h)-f(s-h))/(2*h); 
        if d==0: break
        s2=s-f(s)/d
        if abs(s2-s)<1e-13: s=s2; break
        s=s2
    return s
def zeros_in(f,box,n=400):
    x0,x1,y0,y1=box; xs=np.linspace(x0,x1,int(n*(x1-x0)/(y1-y0))+40); ys=np.linspace(y0,y1,n*8)
    X,Y=np.meshgrid(xs,ys); Z=f(X+1j*Y); 
    # candidates: sign changes of re and im in a cell
    re=np.sign(Z.real); im=np.sign(Z.imag)
    c=((re[:-1,:-1]!=re[1:,1:])|(re[:-1,1:]!=re[1:,:-1]))&((im[:-1,:-1]!=im[1:,1:])|(im[:-1,1:]!=im[1:,:-1]))
    out=[]
    for i,j in zip(*np.nonzero(c)):
        z=newton(f,X[i,j]+1j*Y[i,j])
        if x0<=z.real<=x1 and y0<=z.imag<=y1 and abs(f(z))<1e-8 and all(abs(z-w)>1e-6 for w in out): out.append(z)
    return sorted(out,key=lambda z:z.imag)

if __name__=='__main__':
    # 1. inequality |F|>1 for Re s>1/2 (divisor case), random sample, several m
    rng=np.random.default_rng(1)
    for m in [2,6,12,30,360,5040,2**7*3**2,9973]:
        ds,a,M=setup(m)
        s=rng.uniform(0.5001,6,20000)+1j*rng.uniform(0,200,20000)
        lf,_=logF(s,ds,a,M); lf0,_=logF(s,ds,a,float(m))
        print(m,'M=',M,'min log|F| (M=m rad m):%.4g'%lf.min(),' (M=m): %.4g'%lf0.min())
    # 2. Epstein, m=5040: zeros of A in Re>1/2, zeros of D off the line
    ds,a,M=setup(5040,'ep'); print('epstein coeffs nonzero',len(ds),'M',M, 'a:',dict(zip(ds.astype(int)[:14],a[:14])))
    fA=lambda s:A(s,ds,a); fD=lambda s:np.exp((np.asarray(s,complex)-1)*np.log(M))*A(s,ds,a)+np.exp(-np.asarray(s,complex)*np.log(M))*A(1-np.asarray(s,complex),ds,a)
    zA=zeros_in(fA,(0.5005,3,0,32)); zD=zeros_in(fD,(0.5005,3,0,32))
    print('zeros of A, Re>1/2, 0<t<32:',len(zA)); print(np.round(zA,3))
    print('zeros of D, Re>1/2:',len(zD)); print(np.round(zD,3))
    np.save('ep_zA.npy',np.array(zA)); np.save('ep_zD.npy',np.array(zD))
    # tide: count sign changes on the line vs T log M/pi
    for kind in ['div','ep']:
        ds,a,M=setup(5040,kind); t=np.linspace(0,32,2000001); y=tide(t,ds,a,M)
        sc=np.sum(np.sign(y[1:])!=np.sign(y[:-1])); 
        # extrema of wrong sign
        dy=np.diff(y); ext=np.nonzero(np.sign(dy[1:])!=np.sign(dy[:-1]))[0]+1
        bad=[(round(t[i],3),round(y[i],4)) for i in ext if (dy[i-1]>0 and y[i]<0) or (dy[i-1]<0 and y[i]>0)]
        print(kind,'crossings',sc,'T logM/pi=%.2f'%(32*np.log(M)/np.pi),'extrema',len(ext),'wrong-sign extrema',len(bad),bad[:20])

