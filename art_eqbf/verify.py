"""Independent verification of the July 19, 2026 counterexample to the
Jacobian conjecture (map credited to Levent Alpoge), plus the cubic-model
claims from the live MO question, checked from scratch with sympy."""
import sympy as sp

x, y, z = sp.symbols('x y z')
T = sp.symbols('T')

a = (1+x*y)**3*z + y**2*(1+x*y)*(4+3*x*y)
b = y + 3*x*(1+x*y)**2*z + 3*x*y**2*(4+3*x*y)
c = 2*x - 3*x**2*y - x**3*z
F = sp.Matrix([a, b, c])

# 1. Jacobian determinant
J = F.jacobian([x, y, z])
detJ = sp.expand(J.det())
print("det DF =", detJ)
assert detJ == -2

# 2. the collision
P0 = (0, 0, sp.Rational(-1,4))
P1 = (1, sp.Rational(-3,2), sp.Rational(13,2))
P2 = (-1, sp.Rational(3,2), sp.Rational(13,2))
for P in (P0, P1, P2):
    img = tuple(sp.simplify(f.subs({x:P[0], y:P[1], z:P[2]})) for f in (a,b,c))
    print("F", P, "=", img)
    assert img == (sp.Rational(-1,4), 0, 0)
print("COLLISION VERIFIED: three distinct points -> (-1/4, 0, 0); Jacobian constant -2")
print("=> the Jacobian conjecture is FALSE in dimension 3 (and all n>=3).")

# 3. Cubic model claims (MO question)
t = y + 1/x
claim1a = sp.simplify(b - (4*t + 2/x - 3*c*t**2))
claim1b = sp.simplify(2*a - (c*t**3 - 2*t**2 + b*t))
print("Claim1: b - (4t+2/x-3ct^2) =", claim1a, " ; 2a - (ct^3-2t^2+bt) =", claim1b)
assert claim1a == 0 and claim1b == 0

Pprime = sp.simplify(3*c*t**2 - 4*t + b)   # P'(t)
print("P'(t) =", Pprime)
assert sp.simplify(Pprime - 2/x) == 0

# Claim 2: rational inversion
r = 2/x
cx = sp.simplify(2/r - x)
cy = sp.simplify((t - r/2) - y)
cz = sp.simplify((sp.Rational(5,4)*r**2 - sp.Rational(3,2)*t*r - c/8*r**3) - z)
print("inversion residuals:", cx, cy, cz)
assert cx == 0 and cy == 0 and cz == 0
print("CLAIMS 1-2 VERIFIED: t = y+1/x satisfies P(T)=cT^3-2T^2+bT-2a, P'(t)=2/x,")
print("and (x,y,z) are rational in (t, r=P'(t), a,b,c) => generic fiber = roots of a cubic.")

# 4. fiber over q* = (-1/4,0,0): solve exactly
sols = sp.solve([a + sp.Rational(1,4), b, c], [x, y, z], dict=True)
print("affine fiber over (-1/4,0,0):", sols)
