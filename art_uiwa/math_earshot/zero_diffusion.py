"""D -> 0 limit: replicator dynamics m' = m (1 - phi*m) on a torus, top-hat disc radius 1.
Stationary + uninvadable  <=>  phi*m = 1 on supp m, >= 1 elsewhere.  Record mean density (units of carrying capacity).
Bounds: 1 <= density <= 4 (elementary); hexagonal villages at spacing 1+ give 2 pi/sqrt 3 = 3.6276."""
import numpy as np, scipy.fft as sf, sys
from scipy.special import j1
def run(L,N,seed,T=4000,dt=0.25,init="rand",ret=False):
    dx=L/N; k=2*np.pi*sf.fftfreq(N,dx); kx,ky=np.meshgrid(k,k,indexing='ij')
    # exact discrete top hat (closed disc) on the grid, normalised to sum 1
    x=np.minimum(np.arange(N),N-np.arange(N))*dx; X,Y=np.meshgrid(x,x,indexing='ij')
    K=(X**2+Y**2<=1+1e-9).astype(float); K/=K.sum(); Kh=sf.rfft2(K)
    rng=np.random.default_rng(seed)
    if init=='rand': u=rng.random((N,N))**8
    else:
        u=np.zeros((N,N)); a=init; 
        for i in range(-40,40):
            for j in range(-40,40):
                px=(i+0.5*j)*a; py=j*a*np.sqrt(3)/2
                if 0<=px<L-1e-9 and 0<=py<L-1e-9: u[int(round(px/dx))%N,int(round(py/dx))%N]+=1
        u=u+1e-6*rng.random((N,N))
    for n in range(int(T/dt)):
        c=sf.irfft2(sf.rfft2(u,workers=4)*Kh,s=(N,N),workers=4)
        u*=np.exp(dt*(1-c)); 
        if n%400==399: u[u<1e-12]=0
    c=sf.irfft2(sf.rfft2(u)*Kh,s=(N,N))
    sup=u>1e-3*u.max()
    if ret: return u
    return u.mean(), c.min(), np.abs(c[sup]-1).max(), sup.sum()
if __name__=='__main__':
    out=[]
    for L,N in [(8.0,256),(9.3,256),(11.1,320)]:
        for seed in range(1,9):
            r=run(L,N,seed); out.append(r[0]); print('rand',L,seed,*['%.4f'%v for v in r],flush=True)
    print('random starts: min %.4f mean %.4f max %.4f'%(min(out),np.mean(out),max(out)))
    print('2pi/sqrt3 = %.4f'%(2*np.pi/np.sqrt(3)))
