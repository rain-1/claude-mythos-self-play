"""Nonlocal Fisher-KPP in 2-D:  u_t = D lap u + u (1 - phi_R * u),  phi_R = top hat on the disc of radius R=1.
usage: sim2d.py s N L T tag [seed]     (s = R^2/D)"""
import sys, numpy as np, scipy.fft as sf
from scipy.special import j1
s=float(sys.argv[1]); N=int(sys.argv[2]); L=float(sys.argv[3]); T=float(sys.argv[4]); tag=sys.argv[5]
seed=int(sys.argv[6]) if len(sys.argv)>6 else 0
D=1.0/s; dx=L/N; dt=0.05
k=2*np.pi*sf.fftfreq(N,dx); kx,ky=np.meshgrid(k,k,indexing='ij'); kk=np.sqrt(kx**2+ky**2)
ph=np.where(kk>0,2*j1(kk)/np.where(kk>0,kk,1),1.0)       # FT of the normalised unit disc
ph=ph[:, :N//2+1]; den=1+dt*D*(kk**2)[:, :N//2+1]
x=(np.arange(N)+.5)*dx; X,Y=np.meshgrid(x,x,indexing='ij')
rng=np.random.default_rng(seed)
if seed==0: cx,cy=L*0.5,L*0.5; u=1e-2*np.exp(-((X-cx)**2+(Y-cy)**2)/(2*0.15**2))
else: u=1e-3*rng.random((N,N))
snaps=[]; times=[]; nst=int(T/dt)
for n in range(nst+1):
    uh=sf.rfft2(u,workers=4)
    if n%max(1,nst//40)==0:
        c=sf.irfft2(uh*ph,s=(N,N),workers=4)
        print(n*dt, u.mean(), u.max(), c.min(), flush=True)
        snaps.append(u.astype(np.float32)); times.append(n*dt)
    c=sf.irfft2(uh*ph,s=(N,N),workers=4)
    f=np.where(u>1e-7,u*(1-c),0.0)
    u=sf.irfft2((uh+dt*sf.rfft2(f,workers=4))/den,s=(N,N),workers=4)
    np.maximum(u,0,out=u)
np.savez_compressed(f'data/sim_{tag}.npz',snaps=np.array(snaps),times=np.array(times),s=s,L=L)
