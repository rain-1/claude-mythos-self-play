"""MO 513995: verify the trigonometric/hyperbolic parametrization of the roots
of the Bring-Jerrard quintic x^5 - x + d = 0 (d real), derive it in two lines,
generalize to x^n - x + d, and certify numerically at high precision.

Claimed (poster):
  complex roots x = R e^{i psi}:  R^4 = sin(psi)/sin(5 psi),
                                  d   = sin(4 psi) sin^{1/4}(psi) / sin^{5/4}(5 psi)
  real root     x = -sinh(theta): d = (sinh 5t - 5 sinh 3t - 6 sinh t)/16

Derivation (ours, one line each):
  d = x - x^5 must be real; with x = R e^{i psi},
  Im: R sin(psi) - R^5 sin(5 psi) = 0        =>  R^4 = sin(psi)/sin(5 psi)
  Re: d = R cos(psi) - R^5 cos(5 psi)
        = R [cos(psi) sin(5 psi) - sin(psi) cos(5 psi)] / sin(5 psi)
        = R sin(4 psi)/sin(5 psi)            => poster's d-formula.  QED
  Real root: sinh^5 t = (sinh 5t - 5 sinh 3t + 10 sinh t)/16 (exact identity),
  so d = x - x^5 at x = -sinh t gives  d = (sinh 5t - 5 sinh 3t - 6 sinh t)/16. QED

Generalization (same proof verbatim):  for x^n - x + d = 0, d real,
  R^{n-1} = sin(psi)/sin(n psi),   d = sin((n-1) psi) sin^{1/(n-1)}(psi) / sin^{n/(n-1)}(n psi).
The non-real roots for ALL real d live on the fixed curve Im(x - x^n) = 0."""
import sympy as sp
import mpmath as mp

R, psi, th, t = sp.symbols('R psi theta t', positive=True)
n = sp.Symbol('n', integer=True, positive=True)

print("== symbolic identities ==")
# 1. d-formula from the R^4 relation (n=5)
Rq = (sp.sin(psi)/sp.sin(5*psi))**sp.Rational(1, 4)
d_re = Rq*sp.cos(psi) - Rq**5*sp.cos(5*psi)
d_claim = sp.sin(4*psi)*sp.sin(psi)**sp.Rational(1, 4)/sp.sin(5*psi)**sp.Rational(5, 4)
print("d(Re part) - d(claimed) simplifies to:",
      sp.simplify(sp.trigsimp(sp.together(d_re - d_claim))))
# 2. sinh^5 identity and the real-root formula
lhs = sp.sinh(t)**5
rhs = (sp.sinh(5*t) - 5*sp.sinh(3*t) + 10*sp.sinh(t))/16
print("sinh^5 identity residual:", sp.simplify(sp.expand_trig(rhs) - lhs))
d_real = -sp.sinh(t) + sp.sinh(t)**5          # d = x - x^5 at x = -sinh t
d_real_claim = (sp.sinh(5*t) - 5*sp.sinh(3*t) - 6*sp.sinh(t))/16
print("real-root d residual:", sp.simplify(sp.expand_trig(d_real_claim) - d_real))

print("\n== 60-digit numeric certificates (n=5, poster's test values) ==")
mp.mp.dps = 60
for dval in [mp.sqrt(3), mp.mpf(2), mp.mpf(10), mp.mpf('0.1'), mp.mpf('0.53')]:
    roots = mp.polyroots([1, 0, 0, 0, -1, dval], maxsteps=200, extraprec=200)
    worst = mp.mpf(0)
    for x in roots:
        if abs(mp.im(x)) > 1e-40:                       # complex root
            Rv, ps = abs(x), mp.arg(x)
            res1 = Rv**4 - mp.sin(ps)/mp.sin(5*ps)
            res2 = (mp.sin(4*ps)*mp.sin(ps)**mp.mpf('0.25') /
                    mp.sin(5*ps)**mp.mpf('1.25')) - dval
            # sign conventions: sin(psi)/sin(5psi) must be > 0; d-formula holds
            # up to the branch of the quarter power -> compare |.| and signed
            worst = max(worst, abs(res1), min(abs(res2), abs(res2 + 2*dval)))
        else:                                            # real root
            x = mp.re(x)
            tv = mp.asinh(-x)
            res = (mp.sinh(5*tv) - 5*mp.sinh(3*tv) - 6*mp.sinh(tv))/16 - dval
            worst = max(worst, abs(res))
    print(f"d={mp.nstr(dval,8):12s} max residual over all 5 roots: {mp.nstr(worst, 3)}")

print("\n== generalization x^n - x + d, n = 3..12, random d ==")
for nn in range(3, 13):
    worst = mp.mpf(0)
    for dval in [mp.mpf('0.37'), mp.mpf('1.9'), mp.mpf('7.3')]:
        coeffs = [1] + [0]*(nn-2) + [-1, dval]
        roots = mp.polyroots(coeffs, maxsteps=200, extraprec=200)
        for x in roots:
            if abs(mp.im(x)) > 1e-40:
                Rv, ps = abs(x), mp.arg(x)
                res = Rv**(nn-1) - mp.sin(ps)/mp.sin(nn*ps)
                worst = max(worst, abs(res))
    print(f"n={nn:2d}  max |R^(n-1) - sin(psi)/sin(n psi)| = {mp.nstr(worst, 3)}")

print("\n== collision points (double roots), n=5: d* = ±(4/5)·5^(-1/4) ==")
dstar = mp.mpf(4)/5 * mp.power(5, mp.mpf('-0.25'))
print("d* =", mp.nstr(dstar, 30))
# discriminant of x^5 - x + d is 5^5 d^4 - 4^4 = 3125 d^4 - 256; zero at:
print("disc root:", mp.nstr(mp.power(mp.mpf(256)/3125, mp.mpf('0.25')), 30))
