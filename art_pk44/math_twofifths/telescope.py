"""telescope.py -- for which s is there a homogeneous f(m,n) = sum_j c_j / (m^j n^(2s-j)), 1<=j<=2s-1, with
     f(m,n) - f(m+n,n) - f(m,m+n) = 1/(m n)^s   identically?
If it exists, summing over the Calkin-Wilf forest (every off-diagonal lattice point is (m+n,n) or (m,m+n)
of exactly one point) gives  sum_{m,n} 1/(mn)^s = sum_k f(k,k) = (sum_j c_j) zeta(2s),
and f(a,b) is the total weight of all descendants of (a,b)."""
import sympy as sp, sys
m, n = sp.symbols('m n', positive=True)
for s in range(2, int(sys.argv[1]) + 1):
    k = 2 * s
    c = sp.symbols('c1:%d' % k)
    f = lambda a, b: sum(c[j - 1] / (a**j * b**(k - j)) for j in range(1, k))
    expr = f(m, n) - f(m + n, n) - f(m, m + n) - 1 / (m * n)**s
    num = sp.numer(sp.together(expr))
    eqs = sp.Poly(sp.expand(num), m, n).coeffs()
    sol = sp.solve(eqs, c, dict=True)
    if not sol: print(s, 'NO homogeneous f'); continue
    sol = sol[0]; free = [x for x in c if x not in sol]
    vals = [sol.get(x, x) for x in c]
    print(s, 'coeffs c_1..c_%d =' % (k - 1), vals, ' free:', free, ' sum =', sp.simplify(sum(vals)),
          ' zeta(s)^2/zeta(2s) =', sp.nsimplify(sp.zeta(s)**2 / sp.zeta(2 * s)) if s % 2 == 0 else sp.N(sp.zeta(s)**2 / sp.zeta(2 * s), 12))
