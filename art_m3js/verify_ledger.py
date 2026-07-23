"""Verify: A_n[i,j] = [i+j is a power of 2] (1-indexed).
MO 513368: accepted answer proves perm=1 (unique permutation), det=+-1.
NEW claim to verify: det A_n = (-1)^((n - r(n))/2), r(n)=#maximal runs of equal
bits in binary(n).  Also verify the unique permutation construction."""
import numpy as np
from fractions import Fraction

def is_pow2(x): return x >= 1 and (x & (x-1)) == 0

def build(n):
    i = np.arange(1, n+1)
    S = i[:,None] + i[None,:]
    return (S & (S-1) == 0).astype(np.int64)

def det_exact_mod(n, p):
    """det mod prime p via elimination (int64 safe: p < 2^31)."""
    A = build(n) % p
    A = A.astype(np.int64)
    sign = 1; det = 1
    for c in range(n):
        piv = np.nonzero(A[c:, c])[0]
        if len(piv) == 0: return 0
        r = c + piv[0]
        if r != c:
            A[[c, r]] = A[[r, c]]; sign = -sign
        det = det * A[c, c] % p
        inv = pow(int(A[c, c]), p-2, p)
        rows = A[c+1:, c] != 0
        if rows.any():
            f = (A[c+1:, c][rows] * inv) % p
            A[c+1:, :][rows] = (A[c+1:, :][rows] - f[:,None]*A[c, :]) % p
    return det * sign % p

def unique_perm(n):
    """The nested-reversal permutation: pi[i] = 2^{k+1}-i on [2^{k+1}-n, n], recurse."""
    pi = np.zeros(n+1, dtype=np.int64)  # 1-indexed
    m = n; stages = []
    while m > 0:
        k = m.bit_length() - 1          # 2^k <= m < 2^{k+1}
        s = 1 << (k+1)                  # pairs sum to s
        lo, hi = s - m, m
        idx = np.arange(lo, hi+1)
        pi[idx] = s - idx
        stages.append((m, lo, hi, s))
        m = s - m - 1                   # bitwise complement of m
    return pi[1:], stages

def runs(n):
    b = bin(n)[2:]; r = 1
    for a, c in zip(b, b[1:]):
        if a != c: r += 1
    return r

P1, P2 = 2**31 - 1, 2**31 - 19
bad = 0
for n in range(1, 401):
    pi, stages = unique_perm(n)
    # verify permutation and powers-of-2 sums
    assert sorted(pi) == list(range(1, n+1)), n
    assert all(is_pow2(i+1 + int(pi[i])) for i in range(n)), n
    # sign of pi
    seen = np.zeros(n, bool); c2 = 0
    for i in range(n):
        if not seen[i]:
            j = i; l = 0
            while not seen[j]:
                seen[j] = True; j = int(pi[j]) - 1; l += 1
            c2 += l - 1
    sign_pi = -1 if c2 % 2 else 1
    # formula
    r = runs(n)
    assert len(stages) == r, (n, len(stages), r)
    formula = -1 if ((n - r) // 2) % 2 else 1
    d1 = det_exact_mod(n, P1); d2 = det_exact_mod(n, P2)
    det = 1 if (d1 == 1 and d2 == 1) else (-1 if (d1 == P1-1 and d2 == P2-1) else None)
    if det is None or det != formula or det != sign_pi:
        bad += 1; print("MISMATCH", n, det, formula, sign_pi)
print("n<=400: all match" if bad == 0 else f"{bad} mismatches")

# spot-check large n mod primes
for n in [1000, 2048, 2730, 3000, 4095, 4096]:
    d1 = det_exact_mod(n, P1)
    det = 1 if d1 == 1 else (-1 if d1 == P1-1 else 0)
    r = runs(n); formula = -1 if ((n - r) // 2) % 2 else 1
    print(f"n={n}: det={det:+d} formula={formula:+d} runs={r} match={det==formula}")

# exact Fraction determinant for a few n as belt-and-braces (no mod tricks)
import sys
def det_exact_frac(n):
    A = [[Fraction(x) for x in row] for row in build(n).tolist()]
    sign = 1
    for c in range(n):
        r = next((r for r in range(c, n) if A[r][c] != 0), None)
        if r is None: return Fraction(0)
        if r != c: A[c], A[r] = A[r], A[c]; sign = -sign
        for rr in range(c+1, n):
            if A[rr][c]:
                f = A[rr][c] / A[c][c]
                A[rr] = [a - f*b for a, b in zip(A[rr], A[c])]
    d = Fraction(sign)
    for c in range(n): d *= A[c][c]
    return d
for n in [37, 100, 173, 256]:
    d = det_exact_frac(n); r = runs(n)
    formula = -1 if ((n - r) // 2) % 2 else 1
    print(f"exact n={n}: det={d} formula={formula:+d} match={d==formula}")
