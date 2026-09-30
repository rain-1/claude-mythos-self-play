import numpy as np, math
from sympy import divisors, mobius, totient
_Rc = {}
def Rvec(k):
    if k not in _Rc:
        _Rc[k] = np.array([int(mobius(k // math.gcd(m, k))) / int(totient(k // math.gcd(m, k))) for m in range(k)])
    return _Rc[k]
def all_trace_ok(n, d=None):
    """necessary: for every centre r, 0 lies in n*R(-r) + [min,max] over arrangements of the rest."""
    d = np.array(sorted(d or divisors(n)), float); k = len(d); Rv = Rvec(k)
    rest = np.sort(d[:-1])
    for r in range(k):
        co = Rv[(np.arange(1, k) - r) % k]
        cs = np.sort(co)
        mx = np.dot(cs, rest); mn = np.dot(cs[::-1], rest)
        c0 = n * Rv[(-r) % k]
        if c0 + mx < -1e-9 or c0 + mn > 1e-9:
            return False, r
    return True, None
