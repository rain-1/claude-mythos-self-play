#!/usr/bin/env python3
"""THE SELF THAT SURVIVES THE SHUFFLE — permutable-prime census (MO 514708).

A permutable (absolute) prime stays prime under EVERY permutation of its
decimal digits.  Census in two exhaustive phases:

Phase 1 (lengths 1..7, EXHAUSTIVE by sieve): every n-digit number is binned
by its digit multiset; per orbit we count members T (permutations without
leading zero) and prime members P.  Perfect orbits (P == T, all members
prime) are the permutable primes' orbits.

Phase 2 (lengths 8..25, over digits {1,3,7,9} only — any other digit gives
a permutation ending in an even digit or 5, hence composite; digit sums
divisible by 3 die wholesale): for each multiset we hunt ONE composite
permutation (a certificate of non-permutability).  A multiset whose every
distinct permutation is prime would be a new permutable prime — none is
expected except the repunits R19 and R23.  Repunits are single-member
orbits, tested directly.

Output: perm_census.json
"""
import numpy as np, json, time, random, sys
from sympy import isprime

t0 = time.time()
LIMIT = 10 ** 7

# ---------------------------------------------------------------- sieve
sieve = np.ones(LIMIT, dtype=bool)
sieve[:2] = False
for p in range(2, int(LIMIT ** 0.5) + 1):
    if sieve[p]:
        sieve[p * p::p] = False
print(f"[census] sieve to 1e7: {int(sieve.sum())} primes  {time.time()-t0:.0f}s")
assert int(sieve.sum()) == 664579          # pi(10^7), known — engine tripwire

# ---------------------------------------------------------------- phase 1
phase1 = {}          # key string (sorted digits) -> [T, P]
for n in range(1, 8):
    lo = 10 ** (n - 1) if n > 1 else 1
    hi = 10 ** n
    nums = np.arange(lo, hi, dtype=np.int64)
    digs = np.empty((len(nums), n), dtype=np.int8)
    x = nums.copy()
    for j in range(n):
        digs[:, n - 1 - j] = x % 10
        x //= 10
    digs.sort(axis=1)
    key = np.zeros(len(nums), dtype=np.int64)
    for j in range(n):
        key = key * 10 + digs[:, j]
    pr = sieve[nums]
    uk, inv = np.unique(key, return_inverse=True)
    T = np.bincount(inv)
    P = np.bincount(inv, weights=pr.astype(np.float64)).astype(np.int64)
    for k, t, p in zip(uk.tolist(), T.tolist(), P.tolist()):
        phase1[f"{n}:{k:0{n}d}"] = [t, p]
    nperf = int(((T == P) & (P > 0)).sum())
    print(f"[census] n={n}: {len(uk)} orbits, {nperf} perfect  {time.time()-t0:.0f}s")

# perfect orbits, phase 1
perfect1 = sorted(k for k, (t, p) in phase1.items() if t == p and p > 0)
print("[census] perfect orbits (n<=7):", perfect1)
# known permutable primes below 10^7: digits of each orbit
KNOWN = {"1:2", "1:3", "1:5", "1:7", "2:11", "2:13", "2:17", "2:37", "2:79",
         "3:113", "3:199", "3:337"}
assert set(perfect1) == KNOWN, f"census disagrees with known list: {set(perfect1) ^ KNOWN}"
print("[census] phase-1 verdict: perfect orbits are EXACTLY the 12 known ones")

# ---------------------------------------------------------------- phase 2
def multisets(n):
    """counts (a,b,c,d) of digits (1,3,7,9), a+b+c+d = n."""
    for a in range(n + 1):
        for b in range(n - a + 1):
            for c in range(n - a - b + 1):
                yield (a, b, c, n - a - b - c)

def distinct_perm_count(cnt):
    from math import factorial
    n = sum(cnt)
    r = factorial(n)
    for c in cnt:
        r //= factorial(c)
    return r

rng = random.Random(20260830)
phase2 = {}          # "n:1a3b7c9d" -> ["killed", tries, witness] or ["SURVIVOR", T]
MAXN = 25
survivors2 = []
for n in range(8, MAXN + 1):
    col = []
    for cnt in multisets(n):
        digits = [1] * cnt[0] + [3] * cnt[1] + [7] * cnt[2] + [9] * cnt[3]
        key = f"{n}:{cnt[0]}.{cnt[1]}.{cnt[2]}.{cnt[3]}"
        dsum = sum(digits)
        T = distinct_perm_count(cnt)
        if dsum % 3 == 0:
            phase2[key] = ["mod3", 0, T]        # entire orbit divisible by 3
            continue
        if T == 1:
            # repunit-like (single distinct digit) — direct test
            v = int("".join(map(str, digits)))
            if isprime(v):
                phase2[key] = ["SURVIVOR", T, v]
                survivors2.append(key)
            else:
                phase2[key] = ["composite-orbit1", 0, T]
            continue
        found = None
        tries = 0
        # deterministic first tries: sorted, reversed, then random shuffles
        cands = [digits[:], digits[::-1]]
        while found is None and tries < 6000:
            if tries < 2:
                d = cands[tries]
            else:
                d = digits[:]
                rng.shuffle(d)
            v = int("".join(map(str, d)))
            tries += 1
            if not isprime(v):
                found = v
        if found is None:
            # exhaustive check before declaring a miracle
            from itertools import permutations
            allprime = True
            for pm in set(permutations(digits)):
                v = int("".join(map(str, pm)))
                if not isprime(v):
                    found = v; allprime = False; break
            if allprime:
                phase2[key] = ["SURVIVOR", T, int("".join(map(str, digits)))]
                survivors2.append(key)
                continue
        phase2[key] = ["killed", tries, T]
        col.append(tries)
    mx = max(col) if col else 0
    print(f"[census] n={n}: {len(col)} orbits killed, max tries {mx}, "
          f"survivors so far {survivors2}  {time.time()-t0:.0f}s", flush=True)

print("[census] phase-2 survivors:", survivors2)
# expected: exactly the repunits R19 and R23
assert survivors2 == ["19:19.0.0.0", "23:23.0.0.0"], survivors2
print("[census] VERDICT: the only permutable primes with 8..25 digits are R19 and R23")

# ---------------------------------------------------------------- ledger
# heuristic expectation of a perfect non-repunit orbit at length n:
# P(random {1,3,7,9}-digit n-digit number prime) ~ (10/4)*(1/ln(10^n)) * (15/4)/(10/4)...
# measure it empirically instead at n=8..12 by sampling, then extrapolate 1/(n ln 10) scaling
emp = {}
for n in (8, 10, 12):
    cnt = 0; tot = 4000
    for _ in range(tot):
        v = int("".join(str(rng.choice((1, 3, 7, 9))) for _ in range(n)))
        cnt += isprime(v)
    emp[n] = cnt / tot
print("[census] empirical prime density {1379}^n:", emp)
# density model p_n = c / n  (c fitted)
c_fit = float(np.mean([emp[n] * n for n in emp]))
ledger = {}
for n in range(4, MAXN + 1):
    pn = c_fit / n
    E = 0.0
    for cnt in multisets(n):
        if sum(cnt) != n: continue
        if (cnt[0] + 3 * cnt[1] + 7 * cnt[2] + 9 * cnt[3]) % 3 == 0: continue
        T = distinct_perm_count(cnt)
        if T == 1: continue
        E += pn ** T
    ledger[n] = E
print("[census] expectation ledger E[perfect non-repunit orbits]:",
      {n: f"{v:.2e}" for n, v in list(ledger.items())[:8]})

json.dump({"phase1": phase1, "phase2": phase2, "perfect1": perfect1,
           "survivors2": survivors2, "ledger": ledger, "c_fit": c_fit,
           "emp_density": emp},
          open("perm_census.json", "w"))
print(f"[census] wrote perm_census.json  {time.time()-t0:.0f}s")
