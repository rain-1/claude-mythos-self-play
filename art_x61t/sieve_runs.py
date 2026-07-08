"""Sieve primes to 1e9 and find all maximal symmetric runs of consecutive primes.

A run of consecutive primes p_a..p_b is symmetric iff p_a + p_b = p_{a+1} + p_{b-1} = ...
(equivalently the gap sequence inside the run is a palindrome).

Seeded by the live MathOverflow front-page question
"Are there symmetric runs of consecutive primes of arbitrary length?" (2026-07-08).

Outputs (in art_x61t/data/):
  primes.npy      uint32 primes < N
  runs_even.npz   idx (center-left prime index i), m (half-length; run = p[i-m+1..i+m])
  runs_odd.npz    idx (center prime index i), m (run = p[i-m..i+m], length 2m+1)
Only MAXIMAL runs kept, with run length >= 4 (even) / >= 3 (odd).
"""
import numpy as np, time, os

N = 1_000_000_000
os.makedirs("art_x61t/data", exist_ok=True)
t0 = time.time()

# ---- odd-only sieve ----
half = N // 2                       # index i represents odd number 2i+1
sieve = np.ones(half, dtype=bool)
sieve[0] = False                    # 1 is not prime
limit = int(N ** 0.5)
for p in range(3, limit + 1, 2):
    if sieve[(p - 1) // 2]:
        start = (p * p - 1) // 2
        sieve[start::p] = False
print(f"sieve done {time.time()-t0:.1f}s", flush=True)

primes = 2 * np.flatnonzero(sieve).astype(np.int64) + 1
primes[0] = 2                       # replace 1-slot? no: index0 was 1, removed. fix:
# flatnonzero skips index0 since sieve[0]=False; prepend 2
primes = np.concatenate(([2], primes)).astype(np.uint32)
print(f"{len(primes)} primes < {N}, last={primes[-1]}, {time.time()-t0:.1f}s", flush=True)
np.save("art_x61t/data/primes.npy", primes)

g = np.diff(primes.astype(np.int64)).astype(np.int32)   # gaps, len M-1
M = len(g)

# ---- even-centered runs: center between p_i and p_{i+1} ----
# condition for half-length m: g[i-j] == g[i+j] for j=1..m-1 (m=1 trivial)
# even_h[i] = maximal m
even_h = np.ones(M, dtype=np.int32)     # every adjacent pair is a (trivial) length-2 run
alive = np.ones(M, dtype=bool)
alive[0] = alive[-1] = False
j = 1
while alive.any():
    idx = np.flatnonzero(alive)
    ok = g[idx - j] == g[idx + j]
    even_h[idx[ok]] = j + 1
    alive[:] = False
    alive[idx[ok]] = True
    j += 1
    # kill borders
    alive[:j] = False
    alive[M - j:] = False
print(f"even scan done maxm={even_h.max()} {time.time()-t0:.1f}s", flush=True)

# ---- odd-centered runs at p_i: condition g[i-j] == g[i+j-1] for j=1..m ----
L = len(primes)
odd_h = np.zeros(L, dtype=np.int32)
alive = np.ones(L, dtype=bool)
alive[0] = alive[-1] = False
j = 1
while alive.any():
    idx = np.flatnonzero(alive)
    lo = idx - j
    hi = idx + j - 1
    valid = (lo >= 0) & (hi < M)
    idx = idx[valid]
    ok = g[idx - j] == g[idx + j - 1]
    odd_h[idx[ok]] = j
    alive[:] = False
    alive[idx[ok]] = True
    j += 1
print(f"odd scan done maxm={odd_h.max()} {time.time()-t0:.1f}s", flush=True)

# ---- keep maximal, interesting runs ----
# even run at i with half m: primes p[i-m+1 .. i+m], length 2m  (keep m>=2 -> length>=4)
em = even_h
keep_e = em >= 2
ei = np.flatnonzero(keep_e).astype(np.int64)
emv = em[keep_e]
# odd run at i half m: length 2m+1 (keep m>=1 -> length>=3)
keep_o = odd_h >= 1
oi = np.flatnonzero(keep_o).astype(np.int64)
omv = odd_h[keep_o]

# maximality: an even run of half m contains odd runs etc. — we keep all and let the
# renderer filter; but drop even runs strictly inside a longer even run at same center
# (already maximal by construction: even_h IS the maximal m at that center).
np.savez_compressed("art_x61t/data/runs_even.npz", idx=ei, m=emv)
np.savez_compressed("art_x61t/data/runs_odd.npz", idx=oi, m=omv)

for name, mv in (("even", emv), ("odd", omv)):
    print(name, "count by run length:")
    if name == "even":
        lens = 2 * mv
    else:
        lens = 2 * mv + 1
    u, c = np.unique(lens, return_counts=True)
    for uu, cc in zip(u[-12:], c[-12:]):
        print(f"  len {uu}: {cc}")
print(f"TOTAL {time.time()-t0:.1f}s", flush=True)
