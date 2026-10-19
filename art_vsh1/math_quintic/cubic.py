from sympy import *
a,b,d,w,z=symbols('a b d w z')
F=lambda a,b: a*b*(a+b)*(a**2+a*b+b**2)
def red(e): return rem(expand(e),w**2+w+1,w)
c=a-w*(b-d)
G=red(F(a,b)-F(c,d))
# divide by (b-d) and (a-w b) over Q(w)
K=QQ.algebraic_field(sqrt(-3))
ws=(-1+sqrt(-3))/2
Gs=expand(G.subs(w,ws))
P=Poly(Gs,a,b,d,domain=K)
fac=factor_list(P)
print([ (f.as_expr(),m) for f,m in fac[1]])
C=[f for f,m in fac[1] if f.total_degree()==3][0].as_expr()
Cc=expand(C.subs(sqrt(3)*I, 2*w+1)); Cc=red(Cc)
gs=[red(diff(Cc,v)) for v in (a,b,d)]
for chart in [(d,1),(b,1),(a,1)]:
  eq=[e.subs(*chart) for e in gs]+[w**2+w+1]
  vs=[v for v in (a,b,d) if v!=chart[0]]+[w]
  G=groebner(eq,*vs,order='lex')
  print(chart, list(G)[:3] if list(G)!=[1] else 'no singular point')
