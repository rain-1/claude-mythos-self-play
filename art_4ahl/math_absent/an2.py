# Poisson test: triple sums a_i+a_j-a_k in a window above a_n
import numpy as np, math
from scipy import integrate
a=np.array([int(l.split()[1]) for l in open('b005282.txt') if l.strip() and l[0]!='#'],dtype=np.int64)
# the constant I
f=lambda v,u:(u*v*(u+v-1))**(-2/3)
# substitute to tame singularities: do a Monte-Carlo-free quadrature via tanh-sinh style change
def Iint():
    # u=1-p, v=1-q, w=1-p-q>=0 ; integrate over simplex p,q>=0,p+q<=1 : ((1-p)(1-q)(1-p-q))^(-2/3)
    # let p=s*t, q=s*(1-t), s in[0,1], jac s ; w=1-s -> substitute 1-s=z^3 (ds=3z^2dz), w^(-2/3)=z^-2
    g=lambda t,z:3*(1-z**3)*((1-(1-z**3)*t)*(1-(1-z**3)*(1-t)))**(-2/3)
    # singular at z=0,t=0/1 mildly: (1-s(1-t))^(-2/3) at t=0,s=1 -> integrable
    val,err=integrate.dblquad(g,0,1,0,1,epsabs=1e-10,epsrel=1e-10); return val,err
I,err=Iint(); print('I=',I,err,'kappa=I/54=',I/54,'c=I/108=',I/108)
def test(n,Wg=400):
    A=a[:n]; an=int(A[-1]); gbar=(int(a[min(n+50,len(a)-1)])-int(a[max(n-50,0)]))/ (min(n+50,len(a)-1)-max(n-50,0))
    W=int(Wg*gbar); cnt=np.zeros(W,dtype=np.int32)
    lo=an+1
    for i in range(n):
        s=A[i]+A[i:]            # j>=i
        # need a_k in [s-lo-W+1, s-lo]  (x = s-a_k in [lo, lo+W))
        l=np.searchsorted(A,s-lo-W+1,'left'); r=np.searchsorted(A,s-lo,'right')
        m=r>l
        if not m.any(): continue
        js=np.nonzero(m)[0]
        for jj in js:
            ks=np.arange(l[jj],r[jj]); j=i+jj
            ks=ks[(ks!=i)&(ks!=j)]
            np.add.at(cnt,(s[jj]-A[ks]-lo),1)
    lam=cnt.mean(); free=(cnt==0).mean()
    L=n**3/an
    print('n=%d a=%d gbar=%.0f W=%d lam_emp=%.3f free=%.3e exp(-lam)=%.3e 1/gbar=%.3e | L=%.2f lam/L=%.4f log(gbar)=%.3f'%(n,an,gbar,W,lam,free,math.exp(-lam),1/gbar,L,lam/L,math.log(gbar)),flush=True)
    return cnt
for n in [200,500,1000,2000]:
    c=test(n)
    v=c.var(); print('   var/mean=%.3f  max=%d'%(v/c.mean(),c.max()))
