"""rational6.py -- is the s=6 subtree sum F(1,3) a rational number of moderate height?
A rational p/q with q < 10^13 shows up in the continued fraction of a 31-digit value as a huge partial quotient."""
from mpmath import mp, mpf, floor
P = 10**45; mp.dps = 45
def F(s, a, b, L):
    t = 0; st = [(a, b)]
    while st:
        x, y = st.pop()
        if x * y > L: continue
        t += P // (x * y)**s; st.append((x + y, y)); st.append((x, x + y))
    return mpf(t) / P
def cf(x, eps):
    out = []; q0, q1 = 0, 1
    while True:
        a = int(floor(x)); out.append(a); q0, q1 = q1, a * q1 + q0; x -= a
        if q1 * q1 > 1 / eps or x == 0: break
        x = 1 / x
    return out
for s, L, eps in ((4, 3 * 10**6, mpf(10)**-19), (6, 3 * 10**6, mpf(10)**-30)):
    for a, b in ((1, 2), (1, 3), (3, 2), (1, 4)):
        v = F(s, a, b, L); c = cf(v, eps)
        print('s=%d' % s, (a, b), mp.nstr(v, 31), 'max partial quotient', max(c[1:]), 'at position', c.index(max(c[1:])), 'of', len(c))
