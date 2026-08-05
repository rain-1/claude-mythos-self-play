#!/usr/bin/env python3
"""MO 513606 sufficiency scan: does any COMPOSITE N = 2^(n-1)+3 pass the
parity-dependent Lucas-Lehmer test  s(n-2) === 14 (n odd) / -4 (n even)  mod N?
s(0)=4, s(k)=s(k-1)^2-2.  Necessity (prime => pass) is proven on MO; we assert it
as a live tripwire.  Output: one line per n."""
import sys, os, time
import gmpy2
from gmpy2 import mpz
from multiprocessing import Pool

def scan_one(n):
    N = (mpz(1) << (n - 1)) + 3
    s = mpz(4)
    for _ in range(n - 2):
        s = (s * s - 2) % N
    target = mpz(14) % N if (n & 1) else (N - 4)
    passes = (s == target)
    isprime = gmpy2.is_prime(N)  # BPSW + extra MR
    # distance of final residue from target, as float in [0, 0.5]
    d = abs(s - target)
    dist = float(min(d, N - d) / N)
    pos = float(s / N)
    return (n, int(passes), int(isprime), pos, dist)

def main(lo, hi, out, procs=4):
    t0 = time.time()
    with Pool(procs) as pool, open(out, 'w', buffering=1) as f:
        for (n, p, q, pos, dist) in pool.imap(scan_one, range(lo, hi + 1), chunksize=1):
            f.write(f"{n} {p} {q} {pos:.9f} {dist:.9e}\n")
            if q and not p:
                f.write(f"# TRIPWIRE: prime {n} FAILS test (necessity broken?!)\n")
                print(f"TRIPWIRE n={n}", flush=True)
            if p and not q:
                f.write(f"# LIAR FOUND: composite n={n} passes!\n")
                print(f"LIAR n={n}", flush=True)
            if n % 500 == 0:
                print(f"n={n} elapsed={time.time()-t0:.0f}s", flush=True)
    print(f"done {lo}..{hi} in {time.time()-t0:.0f}s", flush=True)

if __name__ == '__main__':
    lo, hi = int(sys.argv[1]), int(sys.argv[2])
    out = sys.argv[3]
    main(lo, hi, out)
