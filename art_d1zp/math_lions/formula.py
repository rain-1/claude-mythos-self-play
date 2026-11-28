"""Closed form for the nested construction, general n.
mu = law of eps^G (1 - eps^U), G ~ Geometric(p on 'go deeper'), U ~ U(0,1), eps -> 0.
k = number of the n draws on the top level. Lions (X_i > S/(n-1)):
  k <= n-2 : all k top draws;  k = n-1 : all but the smallest (n-2);  k = n : none.
T_n(p) = E[lions]/n."""
import sympy as sp
p=sp.symbols('p')
def T(n):
    q=1-p
    num=sum(sp.binomial(n,k)*q**k*p**(n-k)*k for k in range(1,n-1))+n*q**(n-1)*p*(n-2)
    return sp.cancel(num/(n*(1-p**n)))
for n in range(3,13):
    t=T(n); d=sp.numer(sp.together(sp.diff(t,p)))
    roots=[r for r in sp.Poly(d,p).nroots(n=30) if abs(sp.im(r))<1e-20 and 0<sp.re(r)<1]
    best=max(((t.subs(p,sp.re(r)),sp.re(r)) for r in roots),default=None)
    # endpoints
    lim0=sp.limit(t,p,0); 
    print(n,'p*=',sp.N(best[1],20) if best else None,'T=',sp.N(best[0],20) if best else None,'T(0+)=',lim0)
    if n==4:
        print('  T_4(p)=',sp.factor(t)); print('  dT/dp numerator:',sp.factor(d))
        P=sp.Poly(sp.factor_list(d)[1][-1][0],p); print('  min poly of p*:',P)
        x=sp.symbols('x'); 
        res=sp.resultant(sp.numer(sp.together(t-x)),P.as_expr(),p); print('  min poly of T*:',sp.factor(res))
