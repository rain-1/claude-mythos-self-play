import sympy as sp
u,v,a,b,c,d,q = sp.symbols('u v a b c d q')
quart = a*u**4 + b*u**3 + c*u**2 + d*u + q**2
# general ansatz: X=(2q(v+q)+d u + x2 u^2)/u^2 ; Y=(4q^2(v+q)+ y1 u + y2 u^2 + y3 u^3 + y1v u*v + y2v u^2*v)/u^3
x2,y1,y2,y3,y1v,y2v,A,B,C = sp.symbols('x2 y1 y2 y3 y1v y2v A B C')
X = (2*q*(v+q) + d*u + x2*u**2)/u**2
Y = (4*q**2*(v+q) + y1*u + y2*u**2 + y3*u**3 + y1v*u*v + y2v*u**2*v)/u**3
expr = sp.expand(Y**2 - (X**3 + A*X**2 + B*X + C)).subs(v**2, quart)
expr = sp.expand(expr).subs(v**2, quart)
num, den = sp.fraction(sp.cancel(sp.together(sp.expand(expr))))
poly = sp.Poly(sp.expand(num), u, v)
eqs = poly.coeffs()
sol = sp.solve(eqs, [x2,y1,y2,y3,y1v,y2v,A,B,C], dict=True)
for s in sol: print(s)
