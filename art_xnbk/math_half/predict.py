"""Compare counterexamples found by fastscan with the base-p digit criterion.
For n = A p^k (p largest prime, p not dividing A) with p > sigma(A):
R(n) = sum_j p^j R(A) and every element has a unique base-p expansion with digits in [0,sigma(A)].
T=(n+1)/2 has digits a_0=(p+1)/2, a_1..a_{k-1}=(p-1)/2, a_k=(A-1)/2.  So T in R(n) iff all digits in R(A).
In particular p >= 2 sigma(A) + 1  =>  counterexample.
Usage: python3 predict.py N fast_out.txt
"""
import sys, numpy as np
from scan import odd_sigma, spf_sieve, divisors
from util import subset_bits
N = int(sys.argv[1])
found = set(int(l.split()[0]) for l in open(sys.argv[2]) if 'ok=0' in l)
s = odd_sigma(N); spf = spf_sieve(N)
odd = np.arange(1, N+1, 2); ab = odd[s[odd] > 2*odd]
pred = set(); undecided_bad = []; cache = {}
fam = {}
for n in ab:
    n = int(n); m = n; p = int(spf[m]); fac = {}
    while m > 1:
        q = int(spf[m]); fac[q] = fac.get(q, 0)+1; m //= q
    p = max(fac); k = fac[p]; A = n // p**k; sA = int(s[A]) if A % 2 else None
    if sA is None or p <= sA: continue
    if A not in cache: cache[A] = subset_bits(divisors(A, spf))
    R = cache[A]
    digits = [(p+1)//2] + [(p-1)//2]*(k-1) + [(A-1)//2]
    if not all(d <= sA and (R >> d) & 1 for d in digits):
        pred.add(n); fam.setdefault((A, sA, k), []).append(p)
print('found', len(found), 'predicted by digit criterion', len(pred), 'equal sets:', found == pred)
print('found-not-predicted', sorted(found - pred)[:20], 'predicted-not-found', sorted(pred - found)[:20])
for (A, sA, k), ps in sorted(fam.items()):
    print(f'  A={A} sigma(A)={sA} k={k}: {len(ps)} primes p in [{min(ps)},{max(ps)}]; 2sigma+1={2*sA+1}; window primes (p<2sigma(A)): {[q for q in ps if q < 2*sA]}')
