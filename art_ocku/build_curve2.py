import sympy as sp
from sympy import Rational as R
import json

r,w,t = sp.symbols('r w t')
Q = 35534992*r**4 + 3306770731944*r**3 + 15172317493269316128*r**2 + 1093490321304049798772416*r + 18958669594580211381729967107
P = -Q
r1 = R(-48044056139, 1242748)
D1sq = P.subs(r, r1)
q = sp.sqrt(R(D1sq))
assert q**2 == D1sq and q.is_rational
quart = sp.expand(w**4 * P.subs(r, r1 + 1/w))
a4,a3,a2,a1,a0 = sp.Poly(quart, w).all_coeffs()
assert a4 == q**2

c2 = 2*q*t - (a2 - a3**2/(4*q**2)); c1 = a3*t/q - a1; c0 = t**2 - a0
Delta = sp.expand(c1**2 - 4*c2*c0)
A3,A2,A1,A0 = sp.Poly(Delta, t).all_coeffs()

# roundtrip identity check
Y = sp.symbols('Y')
wsol = (-c1 + Y)/(2*c2)
zsol = q*wsol**2 + a3/(2*q)*wsol + t
chk = sp.simplify(sp.expand(zsol**2 - quart.subs(w, wsol)).subs(Y**2, Delta))
assert chk == 0, chk
print("roundtrip OK")

# integral Weierstrass: X0=A3 t, Y0=A3 Y: Y0^2 = X0^3 + A2 X0^2 + A1*A3 X0 + A0*A3^2
e2, e4, e6 = A2, A1*A3, A0*A3**2
ll = 1
while not ((e2*ll**2).is_integer and (e4*ll**4).is_integer and (e6*ll**6).is_integer):
    ll += 1
E = [sp.Integer(e2*ll**2), sp.Integer(e4*ll**4), sp.Integer(e6*ll**6)]
print("scale l =", ll)

# seed point: t_inf where c2=0
tinf = (a2 - a3**2/(4*q**2))/(2*q)
assert sp.expand(Delta.subs(t,tinf) - (a3*tinf/q - a1)**2) == 0
xE = e_x = A3*tinf*ll**2
yE = A3*(a3*tinf/q - a1)*ll**3
assert sp.expand(yE**2 - (xE**3 + E[0]*xE**2 + E[1]*xE + E[2])) == 0
print("seed point lies on integral model: OK")
print("xE =", xE, " yE =", yE)

def ser(x):
    x = R(x); return [str(x.p), str(x.q)]
data = {'r1':ser(r1), 'q':ser(q), 'quart':[ser(v) for v in [a4,a3,a2,a1,a0]],
        'Delta':[ser(v) for v in [A3,A2,A1,A0]], 'E':[str(v) for v in E],
        'l':str(ll), 'seed':[ser(xE), ser(yE)]}
json.dump(data, open('curve_model.json','w'))
print("saved curve_model.json")
if xE.is_integer and yE.is_integer:
    open('seedpt.txt','w').write(f"[{xE},{yE}]")
else:
    open('seedpt.txt','w').write(f"[{sp.nsimplify(xE)},{sp.nsimplify(yE)}]")
