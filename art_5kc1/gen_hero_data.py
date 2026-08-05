#!/usr/bin/env python3
"""Hero data: full LL orbits s(0..n-2) mod N=2^(n-1)+3 as positions s/N in [0,1),
for n = 3..NMAX.  Saved ragged: concatenated positions + offsets.  Endpoint data
(pass/isprime/dist) recomputed here as an independent cross-check of scan_liars."""
import numpy as np, gmpy2
from gmpy2 import mpz

NMAX = 1027
pos_all, offs, meta = [], [0], []
for n in range(3, NMAX + 1):
    N = (mpz(1) << (n - 1)) + 3
    s = mpz(4)
    orbit = [float(s / N)]
    for _ in range(n - 2):
        s = (s * s - 2) % N
        orbit.append(float(s / N))
    target = mpz(14) % N if (n & 1) else (N - 4)
    passes = int(s == target)
    isprime = int(gmpy2.is_prime(N))
    d = abs(s - target); d = min(d, N - d)
    dist = float(d / N)
    pos_all.extend(orbit)
    offs.append(len(pos_all))
    meta.append((n, passes, isprime, dist))
    assert passes == isprime or not isprime, n   # necessity tripwire
meta = np.array(meta, np.float64)
np.savez_compressed("hero_orbits.npz",
                    pos=np.array(pos_all, np.float32),
                    offs=np.array(offs, np.int64),
                    meta=meta)
pr = meta[meta[:, 2] == 1][:, 0].astype(int)
print("primes n:", list(pr))
print("total orbit points:", len(pos_all))
