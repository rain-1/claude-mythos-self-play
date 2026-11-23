"""check.py -- numerical checks of every number used in the pictures."""
from fractions import Fraction as Fr
from math import gcd, pi
import numpy as np
from sympy import factorint
N = 6000
inv2 = 1.0 / np.arange(1, N + 1, dtype=np.float64)**2
z2 = pi**2 / 6
tot = z2**2
print('diagonal share  ', (pi**4 / 90) / tot, ' = 2/5')
# shares by parity of Omega(ab) over coprime rays, exact tail-free: use Euler products numerically
lam = lambda x: (-1)**sum(factorint(x).values()) if x > 1 else 1
L = 400; even = odd = 0.0
for a in range(1, L):
    for b in range(1, L):
        if gcd(a, b) == 1:
            w = 1.0 / (a * b)**2
            if lam(a) * lam(b) > 0: even += w
            else: odd += w
print('even rays %.6f (29/20 = 1.45)   odd rays %.6f (21/20 = 1.05)   [truncated at %d]' % (even, odd, L))
# Calkin-Wilf subtree sums against f
def f(a, b): return Fr(1, a * b**3) + Fr(1, 2 * a * a * b * b) + Fr(1, a**3 * b)
def subtree(a, b, lim):
    s = 0.0; st = [(a, b)]
    while st:
        x, y = st.pop()
        if x * y > lim: continue
        s += 1.0 / (x * y)**2; st.append((x + y, y)); st.append((x, x + y))
    return s
for a, b in [(1, 1), (1, 2), (2, 3), (3, 2), (1, 3), (3, 5), (5, 2), (7, 4)]:
    print('subtree', (a, b), '%.7f' % subtree(a, b, 3 * 10**6), ' f =', f(a, b), '= %.7f' % float(f(a, b)), ' visit prob =', Fr(2, 5) * f(a, b) * 1)
# three equal / two equal / none, zeta(2)-random triple
z = lambda k: {2: pi**2 / 6, 4: pi**4 / 90, 6: pi**6 / 945, 8: pi**8 / 9450}[k]
p3 = z(6) / z(2)**3; p2 = z(4) / z(2)**2
print('cubes %.9f = 8/35 = %.9f ; exactly two equal %.9f = 18/35 ; all different %.9f = 9/35' % (p3, 8 / 35, 3 * (p2 - p3), 1 - p3 - 3 * (p2 - p3)))
print('s=4 squares', z(8) / z(4)**2, 6 / 7)
