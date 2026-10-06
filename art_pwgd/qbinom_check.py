"""MO 330620: is  q^{k c d C(j,2)} [kc+kd, kc]_q^j  >=  q^{j c d C(k,2)} [jc+jd, jc]_q^k  coefficientwise (k >= j)?
Exact integer polynomial arithmetic (python ints via numpy object arrays)."""
import sys, numpy as np
from functools import lru_cache

@lru_cache(None)
def qbin(n, m):
    # Gaussian binomial coefficients as integer coefficient lists, by q-Pascal
    if m < 0 or m > n: return (0,)
    if m == 0 or m == n: return (1,)
    a = qbin(n - 1, m - 1); b = qbin(n - 1, m)   # [n,m] = [n-1,m-1] + q^m [n-1,m]
    L = max(len(a), len(b) + m)
    r = [0] * L
    for i, x in enumerate(a): r[i] += x
    for i, x in enumerate(b): r[i + m] += x
    return tuple(r)

def pw(p, e):
    r = np.array([1], dtype=object); p = np.array(p, dtype=object)
    for _ in range(e): r = np.convolve(r, p)
    return r

def check(c, d, j, k):
    L = pw(qbin(k*c + k*d, k*c), j); L = np.concatenate([np.zeros(k*c*d*j*(j-1)//2, dtype=object), L])
    R = pw(qbin(j*c + j*d, j*c), k); R = np.concatenate([np.zeros(j*c*d*k*(k-1)//2, dtype=object), R])
    n = max(len(L), len(R))
    L = np.concatenate([L, np.zeros(n - len(L), dtype=object)]); R = np.concatenate([R, np.zeros(n - len(R), dtype=object)])
    diff = L - R
    bad = [i for i in range(n) if diff[i] < 0]
    return bad, L, R

if __name__ == '__main__':
    B = int(sys.argv[1]) if len(sys.argv) > 1 else 8   # range for c+d (=b) and k
    nbad = 0; tested = 0
    for b in range(1, B + 1):
        for a in range(0, b + 1):
            c, d = a, b - a
            if c == 0 or d == 0: continue
            if c > d: continue          # symmetric
            for k in range(2, B + 1):
                for j in range(1, k):
                    if k % j == 0: continue   # trivially true
                    bad, L, R = check(c, d, j, k); tested += 1
                    if bad:
                        nbad += 1; print('FAIL', dict(c=c, d=d, j=j, k=k), bad[:5], flush=True)
    print('tested', tested, 'nontrivial cases; failures', nbad)
