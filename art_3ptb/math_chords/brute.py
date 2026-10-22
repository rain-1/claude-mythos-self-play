"""Brute force: sin^2(pi r1) + sin^2(pi r2) = sin^2(pi r3), r_i in (0,1/2], denominators <= D.
Single core numpy. Hits verified exactly in Q(zeta_N) by reduction mod the cyclotomic polynomial.
Usage: python brute.py D  -> writes hits_D.json
"""
import os, sys, json, time
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np
import mpmath as mp
mp.mp.dps = 60
from fractions import Fraction
from math import gcd
from sympy import Poly, cyclotomic_poly, symbols

D = int(sys.argv[1]) if len(sys.argv) > 1 else 420
TOL = 1e-12

fr = sorted({Fraction(k, n) for n in range(2, D + 1) for k in range(1, n // 2 + 1) if gcd(k, n) == 1})
r = np.array([float(f) for f in fr])
s2 = np.sin(np.pi * r) ** 2          # strictly increasing on (0,1/2]
M = len(fr)
print("rationals:", M, flush=True)

t0 = time.time()
cand = []
for i in range(M):
    s = s2[i] + s2[i:]                # r2 >= r1
    ok = s <= 1 + 1e-9
    if not ok.any():
        break
    s = s[ok]
    j = np.searchsorted(s2, s)
    best = np.full(s.shape, np.inf); idx = np.zeros(s.shape, dtype=np.int64)
    for jj in (j - 1, j):
        jc = np.clip(jj, 0, M - 1)
        d = np.abs(s2[jc] - s)
        better = d < best
        best[better] = d[better]; idx[better] = jc[better]
    hit = np.nonzero(best < TOL)[0]
    for h in hit:
        cand.append((i, i + int(h), int(idx[h]), float(best[h])))
    if i % 2000 == 0:
        print(i, len(cand), round(time.time() - t0, 1), flush=True)
print("candidates:", len(cand), "time", round(time.time() - t0, 1), flush=True)

x = symbols("x")
_cyc = {}
from sympy import mobius, divisors

def cyclo(N):
    """Phi_N as integer coefficient array (low->high) via prod_{d|N} (x^d-1)^mu(N/d)."""
    num = [d for d in divisors(N) if mobius(N // d) == 1]
    den = [d for d in divisors(N) if mobius(N // d) == -1]
    L = sum(num) + 1
    p = np.zeros(L, dtype=object); p[0] = 1; deg = 0
    for d in num:                       # multiply by (x^d - 1)
        q = np.zeros(L, dtype=object)
        q[d:deg + d + 1] += p[:deg + 1]; q[:deg + 1] -= p[:deg + 1]; p = q; deg += d
    for d in den:                       # exact division by (x^d - 1): p = (x^d-1) q
        q = np.zeros(L, dtype=object)
        for i in range(deg - d, -1, -1):
            q[i] = p[i + d] + (q[i + d] if i + d <= deg - d else 0)
        p = q; deg -= d
    return p[:deg + 1]

assert all(list(cyclo(n)) == [int(v) for v in Poly(cyclotomic_poly(n, x), x).all_coeffs()[::-1]] for n in range(1, 200))
def exact_zero(a, b, c):
    """2(cos2pi a + cos2pi b - cos2pi c - 1) == 0 in Q(zeta_N)?  (exact: remainder mod Phi_N over Z)"""
    N = 1
    for f in (a, b, c):
        N = N * f.denominator // gcd(N, f.denominator)
    if N not in _cyc:
        _cyc[N] = cyclo(N)
    phi = _cyc[N]; d = len(phi) - 1
    coeff = np.zeros(N, dtype=object)
    for f, sg in ((a, 1), (b, 1), (c, -1)):
        e = int(f * N) % N
        coeff[e] += sg; coeff[(-e) % N] += sg
    coeff[0] -= 2
    for deg in range(N - 1, d - 1, -1):   # long division by monic Phi_N
        q = coeff[deg]
        if q:
            coeff[deg - d:deg + 1] -= q * phi   # exact Python-int arithmetic (object dtype)
    return not any(coeff[:d])

hits = []
for ii, (i, j, k, d) in enumerate(cand):
    if ii % 500 == 0:
        print("verified", ii, round(time.time() - t0, 1), flush=True)
    a, b, c = fr[i], fr[j], fr[k]
    res = mp.sin(mp.pi * mp.mpf(a.numerator) / a.denominator) ** 2 + mp.sin(mp.pi * mp.mpf(b.numerator) / b.denominator) ** 2 \
        - mp.sin(mp.pi * mp.mpf(c.numerator) / c.denominator) ** 2
    # |res| > 1e-40 at 60 digits proves nonzero; otherwise confirm exactly in Q(zeta_N)
    if abs(res) < mp.mpf(10) ** -40 and exact_zero(a, b, c):
        hits.append([str(a), str(b), str(c)])
    else:
        print("near miss (not exact):", a, b, c, "float diff", d, "60-digit residual", mp.nstr(res, 5))
print("exact hits:", len(hits))
json.dump(hits, open(f"hits_{D}.json", "w"))
