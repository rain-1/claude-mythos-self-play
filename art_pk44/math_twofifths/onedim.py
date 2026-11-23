"""onedim.py -- at s=6 the subtree sums F(a,b) are not rational.  Is ONE new constant enough?
Test integer relations  x*F(a,b) + y*F(1,3) + z = 0  for several (a,b) (F(1,2)=F(1,3)+F(3,2)+1/64 is the trivial one)."""
from mpmath import mp, mpf, pslq, zeta
s = 6; L = 3 * 10**6; P = 10**45; mp.dps = 45
def F(a, b):
    t = 0; st = [(a, b)]
    while st:
        x, y = st.pop()
        if x * y > L: continue
        t += P // (x * y)**s; st.append((x + y, y)); st.append((x, x + y))
    return mpf(t) / P
ref = F(1, 3); print('F(1,3) =', mp.nstr(ref, 30))
vals = {}
for a, b in [(3, 2), (1, 4), (4, 1), (2, 5), (5, 2), (3, 5), (4, 3), (1, 5), (5, 3), (2, 7)]:
    v = F(a, b); vals[(a, b)] = v
    print((a, b), mp.nstr(v, 30), pslq([v, ref, mpf(1)], maxcoeff=10**14, maxsteps=10**6, tol=mpf(10)**-26))
# the constant itself: kappa = F(1,3) - (rational part)?  try against periods of Delta: L(Delta,k) ratios are unknown here,
# so only record kappa-candidates: F(1,3) - F(3,2)
print('F(1,3)-F(3,2) =', mp.nstr(ref - vals[(3, 2)], 30))
