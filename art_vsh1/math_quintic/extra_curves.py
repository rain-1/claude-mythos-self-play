from sympy import *
a,b,c,d,s,x,y=symbols('a b c d s x y')
w=Rational(-1,2)+sqrt(3)*I/2
F=lambda a,b: a*b*(a+b)*(a**2+a*b+b**2)
# (1) conic in plane c=a
print("F(a,b)-F(a,d) =",factor(F(a,b)-F(a,d)))
Q=a**2+a*b+b**2+a*d+d**2
p0=Matrix([w,1,0]); q=Matrix([s,0,1])
lam=symbols('lam')
expr=expand(Q.subs({a:p0[0]+lam*q[0],b:p0[1]+lam*q[1],d:p0[2]+lam*q[2]}))
lm=[r for r in solve(expr,lam) if r!=0][0]
P=[simplify((p0[i]+lm*q[i])*(s**2+s+1)) for i in range(3)]
P=[factor(expand(e)) for e in P]
print("conic param (a,b,c,d) =",(P[0],P[1],P[0],P[2]))
print("  check F(a,b)-F(c,d):",simplify(expand(F(P[0],P[1])-F(P[0],P[2]))))
# (2) degree-6 curve from Mobius g: 0->w, inf->w^2, w->0, w^2->inf, -1->1
M=Matrix([[w**2,-1],[1,-w**2]])
X=M*Matrix([a,b])
ratio=factor(simplify(expand(F(X[0],X[1]))/F(a,b)))
print("F(M(a,b))/F(a,b) =",ratio)
r,sg=symbols('rho sigma')
A=(r**5+sg**5)/2; B=(r**5-sg**5)/2
th=3**Rational(1,5)*w
X=M*Matrix([A,B])
pt=[sg*A, sg*B, r/th*X[0], r/th*X[1]]
print("sextic curve:",[simplify(e) for e in pt])
print("  check:", simplify(expand(F(pt[0],pt[1])-F(pt[2],pt[3]))))
