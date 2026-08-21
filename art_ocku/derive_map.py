# Derive birational map quartic->Weierstrass based at known rational point.
# Classical: v^2 = a u^4 + b u^3 + c u^2 + d u + q^2  (constant term a square)
# Ansatz (Connell/Cohen): X = (2q(v+q)+d u)/u^2, Y = (4q^2(v+q)+2q(c u^2 + d u) - (d^2 u^2)/(2q))/u^3
# Find A,B,C with Y^2 = X^3 + A X^2 + B X + C identically mod v^2-quartic.
import sympy as sp
u,v,a,b,c,d,q = sp.symbols('u v a b c d q')
quart = a*u**4 + b*u**3 + c*u**2 + d*u + q**2
X = (2*q*(v+q) + d*u)/u**2
Y = (4*q**2*(v+q) + 2*q*(c*u**2 + d*u) - d**2*u**2/(2*q))/u**3
A,B,C = sp.symbols('A B C')
expr = (Y**2 - (X**3 + A*X**2 + B*X + C))
# reduce v^2 -> quart
expr = sp.expand(expr)
expr = expr.subs(v**2, quart)
expr = sp.expand(sp.together(expr))
num, den = sp.fraction(sp.cancel(expr))
poly = sp.Poly(num, u, v)
eqs = poly.coeffs()
sol = sp.solve(eqs, [A,B,C], dict=True)
print(sol)
