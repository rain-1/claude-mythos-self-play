"""subtree6.py s L -- Calkin-Wilf subtree sums F_s(a,b) = sum over descendants (m,n) of (a,b) of 1/(mn)^s,
to ~30 digits by fixed-point integer arithmetic (all nodes with mn <= L), then tests for rationality (continued
fraction) and for a relation with zeta(odd) products (PSLQ)."""
import sys
from mpmath import mp, mpf, zeta, pslq, identify, pi
s = int(sys.argv[1]); L = int(sys.argv[2]); P = 10**45; mp.dps = 45
def F(a, b):
    t = 0; st = [(a, b)]
    while st:
        x, y = st.pop()
        if x * y > L: continue
        t += P // (x * y)**s; st.append((x + y, y)); st.append((x, x + y))
    return mpf(t) / P
def cf(x, n=14):
    out = []
    for _ in range(n):
        a = int(mp.floor(x)); out.append(a); x -= a
        if abs(x) < mpf(10)**-25: break
        x = 1 / x
    return out
z2s = zeta(2 * s)
print('s =', s, ' zeta(s)^2/zeta(2s) =', zeta(s)**2 / z2s)
for a, b in [(1, 1), (1, 2), (1, 3), (3, 2), (2, 3), (1, 4), (3, 5)]:
    v = F(a, b)
    basis = [v, mpf(1)] + [zeta(j) * zeta(2 * s - j) / z2s for j in range(3, s + 1, 2)]
    print((a, b), mp.nstr(v, 28), ' cf of v*a^s*b^s:', cf(v * (a * b)**s), ' pslq[v,1,z(odd)z(odd)/z(2s)]:', pslq(basis, maxcoeff=10**7, maxsteps=10**5, tol=mpf(10)**-24))
