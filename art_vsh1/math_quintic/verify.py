from sympy import *
u,v,t,a,b,c,d,x=symbols('u v t a b c d x')
F=lambda a,b: a*b*(a+b)*(a**2+a*b+b**2)
f=lambda a,b: a**5+b**5+(-a-b)**5
print("f = -5F:", expand(f(a,b)+5*F(a,b))==0)
A=u/v; B=2*u*v**4*(3*u**10+v**10)/((u**5+v**5)*(u**10-4*u**5*v**5-v**10))
C=(u**10+4*u**5*v**5-v**10)/(u**10-4*u**5*v**5-v**10); D=(u**5-v**5)/(u**5+v**5)
print("CW verified:", simplify(together(F(A,B)-F(C,D)))==0)
den=v*(u**5+v**5)*(u**10-4*u**5*v**5-v**10)
H=[factor(cancel(e*den)) for e in (A,B,C,D)]
print("homogeneous CW (deg 16):"); [print("  ",h) for h in H]
g=gcd(gcd(Poly(H[0],u,v),Poly(H[1],u,v)),gcd(Poly(H[2],u,v),Poly(H[3],u,v))); print("  gcd of coords:",g.as_expr())
# base curve in P1xP1: [a:b]=[1:s(t)], [c:d], with t=u^5/v^5
s=cancel(B/A).subs(u**5,t*v**5); s=simplify(s.subs(u, (t)**Rational(1,5)*v))
s=cancel(2*(3*t**2+1)/((t+1)*(t**2-4*t-1)))
cc=(t**2+4*t-1)*(t+1); dd=(t**2-4*t-1)*(t-1)
aa=(t+1)*(t**2-4*t-1); bb=2*(3*t**2+1)
print("base curve: [a:b]=[%s : %s], [c:d]=[%s : %s]"%(factor(aa),factor(bb),factor(cc),factor(dd)))
print("F(aa,bb) =",factor(F(aa,bb)))
print("F(cc,dd) =",factor(F(cc,dd)))
print("ratio F(c,d)/F(a,b) =",factor(cancel(F(cc,dd)/F(aa,bb))))
# symmetry group of F over Q / C
m=symbols('m0:4')
M=Matrix(2,2,m)
eqs=Poly(expand(F(M[0,0]*a+M[0,1]*b,M[1,0]*a+M[1,1]*b)-F(a,b)),a,b).coeffs()
sol=solve(eqs,m,dict=True)
print("number of M in GL2(C) with F(M x)=F(x):",len(sol))
rat=[s_ for s_ in sol if all(val.is_rational for val in s_.values())]
print("rational ones:",[Matrix(2,2,[s_[mm] for mm in m]).tolist() for s_ in rat])
