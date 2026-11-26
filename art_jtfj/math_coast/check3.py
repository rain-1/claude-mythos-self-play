import sys; sys.path.insert(0,'..')
import numpy as np
from core import *
from check1 import zeros_in
ds,a,M0=setup(5040,'ep'); m=5040; T=60.0
print('Epstein coefficients on divisors of 5040; largest d with a(d)!=0:',int(ds[-1]))
t=np.linspace(1e-9,T,600001)
for M in [np.sqrt(m),2*np.sqrt(m),4*np.sqrt(m),8*np.sqrt(m),16*np.sqrt(m),32*np.sqrt(m),float(m),4.0*m,16.0*m,M0]:
    y=tide(t,ds,a,M); c=int(np.sum(np.sign(y[1:])!=np.sign(y[:-1]))); tot=T*np.log(M)/np.pi
    fD=lambda s:np.exp((np.asarray(s,complex)-1)*np.log(M))*A(s,ds,a)+np.exp(-np.asarray(s,complex)*np.log(M))*A(1-np.asarray(s,complex),ds,a)
    off=[]
    for lo in range(0,60,10): off+=zeros_in(fD,(0.5002,3,lo,lo+10),n=200)
    print('M=%10.1f  on-line %4d  Langer %7.1f  deficit %5.1f  off-line found %2d: %s'%(M,c,tot,tot-c,len(off),np.round(off[:6],3)),flush=True)
