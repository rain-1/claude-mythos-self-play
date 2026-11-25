"""1-D nonlocal Fisher-KPP, top hat on [-1,1]; space-time record.  usage: sim1d.py s L T tag"""
import sys, numpy as np, scipy.fft as sf
s=float(sys.argv[1]); L=float(sys.argv[2]); T=float(sys.argv[3]); tag=sys.argv[4]
N=int(L/0.005); D=1/s; dx=L/N; dt=0.05
k=2*np.pi*sf.rfftfreq(N,dx); ph=np.sinc(k/np.pi); den=1+dt*D*k*k
x=(np.arange(N)+.5)*dx; u=1e-2*np.exp(-(x-L/2)**2/(2*0.1**2))
rows=[]; nst=int(T/dt); ev=max(1,nst//1600)
for n in range(nst+1):
    uh=sf.rfft(u); c=sf.irfft(uh*ph,n=N)
    if n%ev==0: rows.append(u.astype(np.float32).copy())
    f=np.where(u>1e-7,u*(1-c),0.0)
    u=np.maximum(sf.irfft((uh+dt*sf.rfft(f))/den,n=N),0)
rows=np.array(rows); m=slice(int(N*0.35),int(N*0.65))
print('s',s,'final mean density (middle 30%)',rows[-1][m].mean(),'max',rows[-1].max())
# spacing of peaks in the middle
r=rows[-1]; pk=np.where((r[1:-1]>r[:-2])&(r[1:-1]>=r[2:])&(r[1:-1]>0.2*r.max()))[0]+1
mid=pk[len(pk)//2]; sp=np.diff(x[pk]).mean(); w=int(sp/dx/2); print('mass of a middle village',r[mid-w:mid+w].sum()*dx,'density',r[pk[2]:pk[-3]].sum()*dx/(x[pk[-3]]-x[pk[2]]))
print('peaks',len(pk),'mean spacing',np.diff(x[pk]).mean(),'spacings',np.round(np.diff(x[pk])[len(pk)//2-4:len(pk)//2+4],3))
np.savez_compressed(f'data/st_{tag}.npz',rows=rows[:, ::4],s=s,L=L,T=T)
