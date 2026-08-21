import sympy as sp
from sympy import Rational as R, sqrt

r = sp.symbols('r')
Q = 35534992*r**4 + 3306770731944*r**3 + 15172317493269316128*r**2 + 1093490321304049798772416*r + 18958669594580211381729967107
P = -Q
r1 = R(-48044056139, 1242748)
D1sq = P.subs(r, r1)
q = sp.sqrt(D1sq)
assert q.is_rational or sp.simplify(q**2 - D1sq)==0
q = sp.nsimplify(sp.sqrt(sp.Rational(D1sq)))
assert q**2 == D1sq
print("q =", q)

# substitute r = r1 + 1/w, z = D*w^2  => z^2 = w^4 * P(r1+1/w) = quartic in w
w = sp.symbols('w')
quart = sp.expand(w**4 * P.subs(r, r1 + 1/w))
qp = sp.Poly(quart, w)
a4,a3,a2,a1,a0 = qp.all_coeffs()   # a4 w^4 + ... + a0
assert a4 == q**2
print("quartic in w coeffs (lead, ..., const):")
for cf in [a4,a3,a2,a1,a0]: print("  ", cf)

# z = q w^2 + (a3/(2q)) w + t  =>  quadratic in w:
# [2q t - (a2 - a3^2/(4q^2))] w^2 + [a3 t / q - a1] w + (t^2 - a0) = 0
t = sp.symbols('t')
c2 = 2*q*t - (a2 - a3**2/(4*q**2))
c1 = a3*t/q - a1
c0 = t**2 - a0
Delta = sp.expand(c1**2 - 4*c2*c0)   # cubic in t; Y^2 = Delta(t) needed
print("Delta cubic in t:")
dp = sp.Poly(Delta, t)
for cf in dp.all_coeffs(): print("  ", cf)

# verify: for the seed point w -> infinity corresponds to r=r1... use another test:
# pick any rational w0, solve nothing—instead verify identity: z^2 - quart == 0 with z from t
# Round-trip check: choose the second known representation: at u=0 (r=r1) both branches degenerate.
# Instead verify: for generic t with Delta=Y^2, w = (-c1 + Y)/(2 c2) satisfies quart(w)=z^2.
Y = sp.symbols('Y')
wsol = (-c1 + Y)/(2*c2)
zsol = q*wsol**2 + a3/(2*q)*wsol + t
chk = sp.expand(zsol**2 - quart.subs(w, wsol))
chk = sp.simplify(chk.subs(Y**2, Delta))
print("roundtrip identity check (should be 0):", chk)

# Weierstrass integral model: Delta = A3 t^3 + A2 t^2 + A1 t + A0
A3,A2,A1,A0 = dp.all_coeffs()
# scale: Y^2 = A3 t^3 + ... ; X = A3 t, YY = A3 Y => YY^2 = X^3 + A2 X^2 + A1 A3 X + A0 A3^2
e_a2 = A2; e_a4 = sp.nsimplify(A1*A3); e_a6 = sp.nsimplify(A0*A3**2)
# clear denominators of (e_a2, e_a4, e_a6) by scaling X -> X/l^2? coefficients may be rational
den = sp.lcm([sp.fraction(sp.Rational(v))[1] for v in [sp.Rational(e_a2), sp.Rational(e_a4), sp.Rational(e_a6)]])
print("denominator lcm of model:", den)
# scale X = X'/s^2? For y^2=x^3+a2 x^2+a4 x+a6, scaling x->x/l^2,y->y/l^3 gives coeffs a2 l^2, a4 l^4, a6 l^6
import math
l = 1
d2 = sp.Rational(e_a2); d4 = sp.Rational(e_a4); d6 = sp.Rational(e_a6)
# find minimal l s.t. all integral
ll = 1
while True:
    if (d2*ll**2).is_integer and (d4*ll**4).is_integer and (d6*ll**6).is_integer: break
    ll += 1
print("scale l =", ll)
E = [sp.Integer(d2*ll**2), sp.Integer(d4*ll**4), sp.Integer(d6*ll**6)]
print("E: y^2 = x^3 + %d x^2 + %d x + %d" % tuple(E))
with open('curve_model.txt','w') as f:
    f.write(repr({'q':q, 'r1':r1, 'quart':[a4,a3,a2,a1,a0], 'Delta':[A3,A2,A1,A0], 'E':E, 'l':ll}))
print("saved curve_model.txt")
