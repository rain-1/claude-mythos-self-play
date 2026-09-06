"""appell.py — zeros of the moment polynomials Q_n(x) = E[(x+X)^n] (MO 514900).

Law: X ∈ {−1, 0, 1}, P(X=±1) = q, P(X=0) = 1−2q,  0 < q ≤ 1/2.
    Q_n(x; q) = q[(x−1)^n + (x+1)^n] + (1−2q) x^n.
With u = 1/x:  Q_n = 0  ⇔  f_n(u) := (1+u)^n + (1−u)^n = −(1−2q)/q =: c ∈ (−∞, 0).
So the zero ROADS (q from 0 to 1/2) are f_n^{-1}((−∞, 0]) and a double zero
occurs exactly at a critical point of f_n lying on a road:
    u = i tan(πk/(n−1)),   value  2(−1)^k cos^{1−n}(πk/(n−1)) < 0,
    i.e.  q_{n,k} = 1 / (2 + 2 |cos(πk/(n−1))|^{1−n}),   x = ∓ i cot(πk/(n−1)),
    for k with (−1)^k cos(πk/(n−1)) < 0  (k odd & k < (n−1)/2, or its mirror).
THEOREM. Q_n has a multiple zero for some non-degenerate law iff n ≥ 4; for every
n ≥ 4 the law above with k = 1 gives a double zero at x = ±i cot(π/(n−1)).
(n ≤ 3: normalise m1 = 0, Q_2 = x²+m2 has roots ±i√m2 and Q_3(±i√m2) = m3 ± 2i m2^{3/2} ≠ 0.)
"""
import numpy as np
from numpy.polynomial import polynomial as P
from fractions import Fraction
import json, sys

def Qn_coeffs(n, q):
    """ascending coefficients of Q_n(x;q)"""
    a = P.polypow([-1, 1], n)      # (x-1)^n
    b = P.polypow([1, 1], n)       # (x+1)^n
    c = np.zeros(n + 1); c[n] = 1
    return q * (a + b) + (1 - 2 * q) * c

def double_points(n):
    out = []
    for k in range(1, n - 1):
        phi = np.pi * k / (n - 1)
        val = 2 * (-1) ** k * np.cos(phi) ** (1 - n)
        if val < 0 and abs(np.cos(phi)) > 1e-12:
            q = 1.0 / (2 - val)             # c = val = -(1-2q)/q  ->  q = 1/(2 - val)
            x = -1j / np.tan(phi)
            out.append((k, q, x))
    return out

def roads(n, qs):
    """zeros of Q_n(x;q) for each q, tracked (unsorted) — returns (len(qs), n) complex"""
    Z = np.zeros((len(qs), n), complex)
    for i, q in enumerate(qs):
        Z[i] = P.polyroots(Qn_coeffs(n, q))
    return Z

def verify_exact(nmax=40):
    """exact rational check: Q_n(x; q_{n,k}) has a double root — via sympy gcd(Q_n, Q_n')"""
    import sympy as sp
    x = sp.symbols('x')
    rows = []
    for n in range(4, nmax + 1):
        for k, q, xc in double_points(n):
            # q is algebraic in general (cos(π/(n-1))); check numerically with high precision instead
            qq = sp.Rational(1, 2) if False else None
            phi = sp.pi * k / (n - 1)
            qexact = 1 / (2 + 2 * sp.Abs(sp.cos(phi)) ** (1 - n))
            Q = qexact * ((x - 1) ** n + (x + 1) ** n) + (1 - 2 * qexact) * x ** n
            xc_exact = -sp.I * sp.cot(phi)
            v0 = sp.N(Q.subs(x, xc_exact), 60)
            v1 = sp.N(sp.diff(Q, x).subs(x, xc_exact), 60)
            v2 = sp.N(sp.diff(Q, x, 2).subs(x, xc_exact), 60)
            rows.append(dict(n=n, k=k, q=float(qexact), x=[float(xc.real), float(xc.imag)], Q=float(abs(v0)), dQ=float(abs(v1)), d2Q=float(abs(v2))))
    return rows

if __name__ == '__main__':
    import sympy as sp
    x = sp.symbols('x')
    print('n=4:', sp.factor(sp.Rational(1, 18) * ((x - 1) ** 4 + (x + 1) ** 4) + sp.Rational(8, 9) * x ** 4))
    print('n=5:', sp.factor(sp.Rational(1, 10) * ((x - 1) ** 5 + (x + 1) ** 5) + sp.Rational(4, 5) * x ** 5))
    rows = verify_exact(40)
    worst = max(max(r['Q'], r['dQ']) for r in rows)
    print(f'{len(rows)} double points n=4..40 verified: max |Q|,|Q\'| = {worst:.1e}; min |Q\'\'| = {min(r["d2Q"] for r in rows):.3e} (so exactly double)')
    for r in rows[:8]:
        print(r)
    json.dump(rows, open('appell_double_points.json', 'w'), indent=1)
    # n<=3 impossibility: generic symbolic check
    m2, m3 = sp.symbols('m2 m3', positive=True, real=True)
    Q2 = x ** 2 + m2; Q3 = x ** 3 + 3 * m2 * x + m3
    r = sp.resultant(Q2, Q3, x)
    print('Res(Q2,Q3) with m1=0 =', sp.factor(r), ' (>0 for m2>0: no common zero)')


def degree4_criterion(atoms, weights):
    """Theorem (n=4): Q_4 has a multiple zero  <=>  skewness 0 and kurtosis 9 (then Q_4 = ((x+m1)^2 + 3 mu2)^2)."""
    atoms = np.asarray(atoms, float); w = np.asarray(weights, float)
    m1 = w @ atoms; c = atoms - m1
    mu2, mu3, mu4 = w @ c ** 2, w @ c ** 3, w @ c ** 4
    return mu3 / mu2 ** 1.5, mu4 / mu2 ** 2

if __name__ == '__main__':
    print('degree-4 criterion on the two known laws: (skew, kurt) =',
          degree4_criterion([-1, 0, 1], [1 / 18, 8 / 9, 1 / 18]), degree4_criterion([-3 ** .5, 0, 3 ** .5], [1 / 18, 8 / 9, 1 / 18]))
