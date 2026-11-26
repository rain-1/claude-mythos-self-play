import sys; sys.path.insert(0,'..')
import numpy as np
from core import *
from check1 import zeros_in
def crossings(ds,a,M,T,n=400000):
    t=np.linspace(1e-9,T,int(n*T/100)+1); y=tide(t,ds,a,M); return int(np.sum(np.sign(y[1:])!=np.sign(y[:-1])))
print('--- threshold sweep: on-line crossings in (0,T] vs Langer total T*max(logM,log(m/M))/pi ; T=300')
T=300.0
for m in [6,12,30,360,5040]:
    ds,a,_=setup(m)
    for r in [8.0,2.0,1.0,0.99,0.95,0.8,0.5,0.2]:
        M=r*np.sqrt(m); c=crossings(ds,a,M,T); tot=T*max(abs(np.log(M)),np.log(m/M))/np.pi
        print('m=%5d M=%.3f*sqrt(m)=%9.3f  on-line %5d   total %8.1f   off-line pairs ~ %6.1f'%(m,r,M,c,tot,(tot-c)/2),flush=True)
print('--- pits and lights at the critical M: zeros of sigma_{-s}(m) with 0<t<T  vs zeros of D on the line')
from sympy import factorint
for m in [12,5040,720720]:
    ds,a,_=setup(m); M=np.sqrt(m); T=300.0
    pits=0
    for p,e in factorint(m).items():
        per=2*np.pi/((e+1)*np.log(p)); k=np.arange(1,int(T/per)+1); pits+=int(np.sum(k%(e+1)!=0))
    print('m=%d  pits %d  lights %d   T log(sqrt m)/pi = %.2f'%(m,pits,crossings(ds,a,M,T),T*np.log(M)/np.pi),flush=True)
print('--- Epstein m=5040, M=m rad m, 0<t<60')
import core
ds,a,M=setup(5040,'ep')
fA=lambda s:A(s,ds,a); fD=lambda s:np.exp((np.asarray(s,complex)-1)*np.log(M))*A(s,ds,a)+np.exp(-np.asarray(s,complex)*np.log(M))*A(1-np.asarray(s,complex),ds,a)
zA=[]; zD=[]
for lo in range(0,60,10):
    zA+=zeros_in(fA,(0.5002,3,lo,lo+10),n=200); zD+=zeros_in(fD,(0.5002,3,lo,lo+10),n=200)
print(len(zA),'zeros of A:',np.round(zA,3)); print(len(zD),'zeros of D:',np.round(zD,3))
print('pair distances |zD-zA| vs M^-(2 sigma-1):')
for z in zD:
    w=min(zA,key=lambda q:abs(q-z)); print('  %.4f%+.4fi  dist %.2e   M^-(2s-1)=%.2e'%(z.real,z.imag,abs(z-w),M**(-(2*w.real-1))))
c=crossings(ds,a,M,60.0); print('on-line crossings in (0,60]:',c,' Langer total %.1f'%(60*np.log(M)/np.pi),' deficit',60*np.log(M)/np.pi-c,' 2*offline',2*len(zD))
