"""Brute force: sin^2(pi r1) + sin^2(pi r2) = sin^2(pi r3), r_i in (0,1/2], denominators <= D.
Single core numpy. Hits verified exactly in Q(zeta_N) by reduction mod the cyclotomic polynomial.
Usage: python brute.py D  -> writes hits_D.json
"""
import os, sys, json, time
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np
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
def exact_zero(a, b, c):
    """2(cos2pi a + cos2pi b - cos2pi c - 1) == 0 in Q(zeta_N)?  (exact: remainder mod Phi_N over Z)"""
    N = 1
    for f in (a, b, c):
        N = N * f.denominator // gcd(N, f.denominator)
    if N not in _cyc:
        _cyc[N] = np.array([int(v) for v in Poly(cyclotomic_poly(N, x), x).all_coeffs()[::-1]], dtype=object)  # low->high, monic
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
for i, j, k, d in cand:
    a, b, c = fr[i], fr[j], fr[k]
    if exact_zero(a, b, c):
        hits.append([str(a), str(b), str(c)])
    else:
        print("near miss (not exact):", a, b, c, d)
print("exact hits:", len(hits))
json.dump(hits, open(f"hits_{D}.json", "w"))
