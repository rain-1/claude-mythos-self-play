"""turn.py X -- the prime shell.  theta_p = 2*arctan(1/p), so cos(theta_p) = (p^2-1)/(p^2+1): a right triangle
similar to (p^2-1, 2p, p^2+1).  Projecting a unit segment onto a line turned by theta_2, then theta_3, theta_5 ...
leaves prod (p^2-1)/(p^2+1) -> 2/5.  At which prime has the shell turned once (sum of theta_p >= 2*pi)?"""
import sys, numpy as np
X = int(float(sys.argv[1])); seg = 10**7
base = np.ones(int(X**0.5) + 2, bool); base[:2] = False
for i in range(2, int(len(base)**0.5) + 1):
    if base[i]: base[i * i::i] = False
bp = np.nonzero(base)[0]
tot = np.longdouble(0); logr = np.longdouble(0); count = 0; target = np.longdouble(np.pi); done = False
marks = [1, 2, 3]; mi = 0
for lo in range(0, X, seg):
    hi = min(lo + seg, X); s = np.ones(hi - lo, bool)
    if lo == 0: s[:2] = False
    for p in bp:
        if p * p >= hi: break
        st = max(p * p, (lo + p - 1) // p * p); s[st - lo::p] = False
    ps = (np.nonzero(s)[0] + lo).astype(np.longdouble)
    a = np.arctan(1 / ps); c = tot + np.cumsum(a)
    lr = logr + np.cumsum(np.log1p(-2 / (ps * ps + 1)))
    for q in (0.25, 0.5, 0.75, 1.0):
        j = np.searchsorted(c, q * target)
        if j < len(c) and (j > 0 or tot < q * target):
            print('turn %.2f reached at prime %d (the %d-th), remaining length %.15f' % (q, int(ps[j]), count + j + 1, float(np.exp(lr[j]))), flush=True)
    tot = c[-1]; logr = lr[-1]; count += len(ps)
    if tot >= target: break
print('primes used', count, 'up to', hi, ' angle/2pi =', float(tot / target), ' length', float(np.exp(logr)))
