"""pinchuk.py — Pinchuk's map: a polynomial F: R^2 -> R^2 whose Jacobian
determinant is strictly positive EVERYWHERE and which is still not injective.

    t = xy - 1
    h = t(xt + 1)
    f = (t^2 + y)(xt + 1)^2          [ = ((h+1)/x)(xt+1)^2 , a polynomial ]
    P = f + h                                              deg 10
    Q = -t^2 - 6th(h+1) - 170fh - 91h^2 - 195fh^2 - 69h^3 - 75fh^3 - (75/4)h^4   deg 25

S. Pinchuk, "A counterexample to the strong real Jacobian conjecture",
Math. Z. 217 (1994).  Only (0,0) and (-1,-163/4) are missed; the asymptotic
variety has one preimage per point; every other point of R^2 has exactly TWO.
"""
import numpy as np


def aux(x, y):
    t = x * y - 1.0
    xt1 = x * t + 1.0
    h = t * xt1
    f = (t * t + y) * xt1 * xt1
    return t, h, f


def F(x, y):
    t, h, f = aux(x, y)
    P = f + h
    Q = (-t * t - 6.0 * t * h * (h + 1.0) - 170.0 * f * h - 91.0 * h * h
         - 195.0 * f * h * h - 69.0 * h ** 3 - 75.0 * f * h ** 3 - 18.75 * h ** 4)
    return P, Q


def asymptotic_variety(hh):
    """the curve the two sheets join along, parameterised by h"""
    u = hh * hh + 2.0 * hh
    v = -0.25 * (1736.0 * hh ** 3 + 1044.0 * hh ** 2 + 1155.0 * hh ** 4 + 300.0 * hh ** 5)
    return u, v


MISSED = [(0.0, 0.0), (-1.0, -163.0 / 4.0)]

if __name__ == '__main__':
    import sympy as sp
    x, y = sp.symbols('x y', real=True)
    t = x * y - 1
    h = sp.expand(t * (x * t + 1))
    f = sp.expand((t**2 + y) * (x * t + 1)**2)
    Pp = sp.expand(f + h)
    Qq = sp.expand(-t**2 - 6*t*h*(h+1) - 170*f*h - 91*h**2 - 195*f*h**2
                   - 69*h**3 - 75*f*h**3 - sp.Rational(75, 4) * h**4)
    print('deg P =', sp.total_degree(Pp), '   deg Q =', sp.total_degree(Qq))
    J = sp.expand(sp.diff(Pp, x) * sp.diff(Qq, y) - sp.diff(Pp, y) * sp.diff(Qq, x))
    print('deg det J =', sp.total_degree(J), '  terms:', len(J.args))
    # Pinchuk: det J = t^2 + (t + f(15h^2 + 20h ... ))^2 -- test positivity structure
    Jt = sp.factor(J)
    print('factored head:', str(Jt)[:300])
    # numeric floor of det J on a big box (it must never be <= 0)
    import numpy as np
    Jf = sp.lambdify((x, y), J, 'numpy')
    rng = np.random.default_rng(0)
    for scale in (0.5, 2.0, 8.0, 40.0):
        xs = rng.uniform(-scale, scale, 400000); ys = rng.uniform(-scale, scale, 400000)
        v = Jf(xs, ys)
        print(f'  |x|,|y| < {scale:5.1f}:  min det J = {v.min():.6g}   (all > 0: {bool((v>0).all())})')
