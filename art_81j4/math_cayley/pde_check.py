"""Check the PDE route with sympy (truncated power series, exact rationals).

G(x,y) = sum_{n>=0} x^n/n! (1+y)^C(n,2);  (1+y) G_y = (x^2/2) G_xx   (termwise identity)
C = log G  =>  (1+y) C_y = (x^2/2)(C_xx + C_x^2)
W(u,y) := y*C(u/y, y) = sum_n u^n/n! sum_e c_{n,e} y^{e-n+1}  (power series in y)
=> (1+y)(u W_u - W + y W_y) = (u^2/2)(y W_uu + W_u^2)
y^0:  u T' - T = (u^2/2) T'^2           (T = trees EGF)
y^1:  U' = R^3 / (2u(1-R)^2), R = u T'   (U = unicyclic EGF)
"""
import sympy as sp
u, y, x = sp.symbols('u y x')
N = 11
# exact c_{n,e} via truncated log in x with polynomial coefficients in y
G = sum(x**n / sp.factorial(n) * (1 + y)**sp.binomial(n, 2) for n in range(N + 1))
F = sp.expand(G - 1)
C = 0; P = 1
for k in range(1, N + 1):
    P = sp.expand(sp.series(P * F, x, 0, N + 1).removeO())
    C += sp.Rational((-1)**(k - 1), k) * P
C = sp.expand(C)
# PDE for C (truncate to x^N; the C_x^2 product is fine below degree N)
lhs = sp.expand((1 + y) * sp.diff(C, y))
rhs = sp.expand(x**2 / 2 * (sp.diff(C, x, 2) + sp.diff(C, x)**2))
diff = sp.expand(lhs - rhs)
bad = [d for d in range(N + 1) if sp.expand(diff.coeff(x, d)) != 0]
print("PDE for C holds for x-degrees <=", N, ":", bad == [])
# trees / unicyclic / excess 1 coefficients
def coeff(n, e): return sp.factorial(n) * sp.Poly(C.coeff(x, n), y).coeff_monomial(y**e) if n else 0
T = sum(sp.Integer(n)**(n - 2) * u**n / sp.factorial(n) for n in range(1, N + 1))
print("trees match n^(n-2):", all(coeff(n, n - 1) == sp.Integer(n)**(n - 2) for n in range(1, N + 1)))
ode = sp.expand(u * sp.diff(T, u) - T - u**2 / 2 * sp.diff(T, u)**2)
print("ODE uT'-T=(u^2/2)T'^2 to order", N, ":", all(ode.coeff(u, d) == 0 for d in range(N + 1)))
# Abel-type identity behind the recurrence
print("sum C(n,k) k^(k-1)(n-k)^(n-k-1) = 2(n-1)n^(n-2):",
      all(sum(sp.binomial(n, k) * k**(k - 1) * (n - k)**(n - k - 1) for k in range(1, n)) == 2 * (n - 1) * n**(n - 2) for n in range(2, 30)))
# Wright's W_0 and W_1 in terms of the tree function t = R
R = sum(sp.Integer(n)**(n - 1) * u**n / sp.factorial(n) for n in range(1, N + 2))
ser = lambda e: sp.expand(sp.series(e, u, 0, N + 1).removeO())
U = ser(sp.Rational(1, 2) * sp.log(1 / (1 - R)) - R / 2 - R**2 / 4)
V = ser(R**4 * (6 - R) / (24 * (1 - R)**3))
print("unicyclic (1/2)log(1/(1-R)) - R/2 - R^2/4:",
      all(sp.factorial(n) * U.coeff(u, n) == coeff(n, n) for n in range(1, N + 1)))
print("excess 1 = R^4(6-R)/(24(1-R)^3):",
      all(sp.factorial(n) * V.coeff(u, n) == coeff(n, n + 1) for n in range(1, N + 1)))
