#!/usr/bin/env python3
"""Cross-check: primes N = 2^(n-1)+3 found by the scan should have n-1 in
OEIS A057732 (2^k+3 prime), and the test-passers must coincide exactly."""
import sys
A057732 = [int(l.split()[1]) for l in open("b057732.txt") if l.strip() and not l.startswith("#")]
fn = sys.argv[1] if len(sys.argv) > 1 else "liars_final.txt"
passers, primes, nmax = [], [], 0
for line in open(fn):
    if line.startswith("#"): continue
    p = line.split()
    n, ps, pr = int(p[0]), int(p[1]), int(p[2])
    nmax = max(nmax, n)
    if ps: passers.append(n)
    if pr: primes.append(n)
assert passers == primes, ("MISMATCH", set(passers) ^ set(primes))
expect = [k + 1 for k in A057732 if k + 1 <= nmax and k + 1 >= 3]
assert primes == expect, ("A057732 MISMATCH", primes, expect)
print(f"scan {fn}: n up to {nmax}; passers == primes == A057732+1 exactly "
      f"({len(primes)} primes: n-1 in {[n-1 for n in primes]})")
