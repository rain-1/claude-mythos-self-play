import numpy as np
from scipy.optimize import brentq
from eta_koopman import eta, support
rows=[]
for al in np.round(np.arange(0,1.0,0.01),2):
    if al==0: rows.append((0.0, np.log((1+5**.5)/2), 0.0)); continue
    e1=eta(al,200)[0]; e2=eta(al,400)[0]
    rows.append((al, e2, abs(e1-e2)))
np.savetxt("eta.csv", np.array(rows)[:,:2], delimiter=",", header="alpha,eta", comments="", fmt=["%.2f","%.15f"])
print("max N-discrepancy", max(r[2] for r in rows))
for r in rows:
    if round(r[0]*100)%5==0: print(f"{r[0]:.2f} {r[1]:.14f}")
# derived thresholds
a0 = brentq(lambda x: eta(x,400)[0], 0.99, 0.999, xtol=1e-15); print("eta=0 at alpha0 =", repr(a0))
chi = lambda x: 2*eta(x,300)[0] - 0.5*np.log(1-x*x)
ast = brentq(lambda x: chi(x)-np.log(4), 0.5, 0.999, xtol=1e-14); print("h/chi=1 at alpha* =", repr(ast))
# support is always the whole interval: image of (u,v)=(1-al,1+al) is [a', b'] covering almost all of [a,b]
for al in (0.3,0.6,0.9,0.99):
    a,b=support(al); I=sorted([(u+v/b,u+v/a) for u in (1-al,1+al) for v in (1-al,1+al)])
    print(al, "images cover [a,b] without gaps:", all(I[i+1][0] <= max(J[1] for J in I[:i+1]) for i in range(3)))
# alpha -> 1: eta - log(1-alpha)/9 -> C
eps=[10.0**-j for j in range(3,9)]
d=[eta(1-e,400,maxit=20000)[0]-np.log(e)/9 for e in eps]
for e,x in zip(eps,d): print("1-alpha=%.0e  eta-log(1-alpha)/9 = %.12f"%(e,x))
print("Richardson C =", d[-1]-(d[-2]-d[-1])/9)
g=np.loadtxt("eta.csv",delimiter=",",skiprows=1); print("eta strictly decreasing on grid:", np.all(np.diff(g[:,1])<0))
