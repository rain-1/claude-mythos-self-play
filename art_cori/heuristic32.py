"""heuristic32.py — MO 515202: why does the naive independence heuristic fail for primes 3^n - 2^k?

Claim tested here.  The events  q | 3^n - 2^k  for different primes q are NOT independent, because each one is a
congruence condition on (n, k):  3^n ≡ 2^k (mod q)  ⇔  n·L3 ≡ k·L2 (mod q-1)  with L2, L3 the discrete logs.
Two such conditions share the residues of (n, k) modulo the common factors of q-1 and q'-1 (parity first: if
2 and 3 are both non-residues mod q, then n ≡ k mod 2 is forced; if only one of them is, one of n, k has a
forced parity — and these forcings are shared by every q with the same Legendre pattern).

Refined heuristic: condition on the class (n, k) mod M.  For a class (a, b),
    ρ_q(a,b) = G/(q-1)  if  G | (a·L3 - b·L2)  else 0,      G = gcd(M·h, q-1),  h = gcd(L2, L3, q-1)
(derivation in notes_taken.md), and
    D_ref(M; p) = mean over (a,b) mod M of  Π_{q ≤ p} (1 - ρ_q(a,b)).
M = 1 is the poster's D_ind.  As M runs through multiples of more and more small prime powers, D_ref(M) should
rise toward the empirical D_emp; the table below tests this.

usage: python3 heuristic32.py PMAX
"""
import sys, time, json
import numpy as np
from math import gcd
from sympy import primerange, primitive_root, discrete_log, n_order

PMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 10000
t0 = time.time()
primes = [q for q in primerange(5, PMAX + 1)]
L2 = {}; L3 = {}
for q in primes:
    g = primitive_root(q)
    L2[q] = discrete_log(q, 2, g); L3[q] = discrete_log(q, 3, g)
print('discrete logs for', len(primes), 'primes [%.0fs]' % (time.time() - t0), flush=True)

# --- empirical D_emp by Monte Carlo over (n, k), 1 <= k < n log2 3 ---
rng = np.random.default_rng(1)
NS = 300000; NMAX = 10_000_000
n = rng.integers(1, NMAX, NS); k = np.maximum((rng.random(NS) * (n * np.log2(3.0))).astype(np.int64), 1)  # 1 <= k, 2^k < 3^n
alive = np.ones(NS, bool)
checkpoints = [500, 1000, 2000, 5000, 10000, 20000, 50000, 100000]
emp = {}
for q in primes:
    d3 = n_order(3, q); d2 = n_order(2, q)
    t3 = np.array([pow(3, i, q) for i in range(d3)]); t2 = np.array([pow(2, i, q) for i in range(d2)])
    alive &= (t3[n % d3] != t2[k % d2])
    for cp in checkpoints:
        if q <= cp and cp not in emp:
            pass
    # record at the largest checkpoint <= q boundary crossing
    emp[q] = alive.mean()
def D_emp(p):
    qs = [q for q in primes if q <= p]
    return emp[qs[-1]]
print('D_emp done [%.0fs]' % (time.time() - t0), flush=True)

# --- refined heuristic ---
def D_ref(M, p):
    qs = [q for q in primes if q <= p]
    a, b = np.meshgrid(np.arange(M), np.arange(M), indexing='ij'); a = a.ravel(); b = b.ravel()
    prod = np.ones(M * M)
    for q in qs:
        h = gcd(gcd(L2[q], L3[q]), q - 1)
        G = gcd(M * h, q - 1)
        c = (a * L3[q] - b * L2[q]) % (q - 1)
        rho = np.where(c % G == 0, G / (q - 1), 0.0)
        prod *= (1 - rho)
    return prod.mean(), prod

rows = []
Ms = [1, 2, 4, 8, 3, 6, 12, 24, 48, 72, 120, 240, 360, 720]
for p in [c for c in checkpoints if c <= PMAX]:
    de = D_emp(p)
    row = dict(p=p, D_emp=float(de), D_emp_lnp=float(de * np.log(p)))
    for M in Ms:
        dr, _ = D_ref(M, p)
        row[f'M{M}'] = float(dr)
    rows.append(row)
    print(f"p={p:>6}  D_emp={de:.5f} ({de*np.log(p):.3f}/ln p)  " + '  '.join(f"M{M}={row[f'M{M}']:.5f}" for M in [1, 2, 8, 24, 120, 720]), flush=True)
    print('        ratio D_emp/D_ref:', '  '.join(f"M{M}: {de / row[f'M{M}']:.3f}" for M in Ms), flush=True)
json.dump(dict(rows=rows, NS=NS, NMAX=NMAX, seconds=time.time() - t0), open('heuristic32.json', 'w'), indent=1)
print('done [%.0fs]' % (time.time() - t0))
