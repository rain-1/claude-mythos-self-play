"""heuristic32_tail.py — the same refined heuristic with a LARGE modulus, estimated by sampling classes (a, b) mod M
uniformly instead of enumerating them.  M = 720720 = 2^4·3^2·5·7·11·13 adds the moduli 7, 11, 13 to the exact runs.
usage: python3 heuristic32_tail.py PMAX NSAMPLES"""
import sys, time, json
import numpy as np
from math import gcd
from sympy import primerange, primitive_root, discrete_log
PMAX = int(sys.argv[1]); NSAMP = int(sys.argv[2]); t0 = time.time()
Ms = [6, 720, 720720, 720720 * 17 * 19 * 23]
primes = list(primerange(5, PMAX + 1))
L = {q: (lambda g: (discrete_log(q, 2, g), discrete_log(q, 3, g)))(primitive_root(q)) for q in primes}
rng = np.random.default_rng(7)
out = {}
for M in Ms:
    a = rng.integers(0, M, NSAMP).astype(np.int64); b = rng.integers(0, M, NSAMP).astype(np.int64)
    prod = np.ones(NSAMP); rows = {}
    for q in primes:
        L2, L3 = L[q]; h = gcd(gcd(L2, L3), q - 1); G = gcd(M * h, q - 1)
        c = (a * L3 - b * L2) % (q - 1)
        prod *= np.where(c % G == 0, 1 - G / (q - 1), 1.0)
        for cp in (1000, 10000, 100000):
            if q <= cp: rows[cp] = float(prod.mean())
    out[M] = rows
    print('M', M, {cp: round(v, 5) for cp, v in rows.items()}, '[%.0fs]' % (time.time() - t0), flush=True)
json.dump(out, open('heuristic32_tail.json', 'w'), indent=1)
