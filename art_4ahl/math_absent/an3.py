# lambda just above a_n (narrow window) vs log mean gap vs kappa*L
import numpy as np, math
a=np.array([int(l.split()[1]) for l in open('b005282.txt') if l.strip() and l[0]!='#'],dtype=np.int64)
I=7.1907333; kap=I/54
def lam_at(n,Wg=3.0):
    A=a[:n]; an=int(A[-1]); h=max(10,n//20)
    gbar=(int(a[min(n+h,len(a)-1)])-int(a[n-h]))/(min(n+h,len(a)-1)-(n-h))
    W=int(Wg*gbar); lo=an+1; tot=0; distinct=None
    xs=[]
    for i in range(n):
        s=A[i]+A[i:]
        l=np.searchsorted(A,s-lo-W+1,'left'); r=np.searchsorted(A,s-lo,'right')
        tot+=int((r-l).sum())
        m=np.nonzero(r>l)[0]
        for jj in m:
            xs.extend((s[jj]-A[l[jj]:r[jj]]-lo).tolist())
    xs=np.array(xs); cnt=np.bincount(xs,minlength=W)
    return tot/W,gbar,(cnt==0).mean(),cnt.var()/cnt.mean()
print(' n      L    kapL   lam_emp  log(gbar)  free    exp(-lam)  1/gbar  var/mean')
for n in [100,200,400,800,1600,3200,6400,9500]:
    lam,gbar,free,vm=lam_at(n); L=n**3/int(a[n-1])
    print('%5d %6.2f %6.3f %7.3f %8.3f  %.2e %.2e %.2e %.2f'%(n,L,kap*L,lam,math.log(gbar),free,math.exp(-lam),1/gbar,vm),flush=True)
