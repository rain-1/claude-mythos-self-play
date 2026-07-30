"""
tower.py -- the frozen tower  t_a = a^^inf  as a profinite integer.

For every modulus n the sequence a^^k mod n is eventually constant
(k large enough), so t_a = lim_k a^^k is a well-defined element of
Zhat = prod_p Z_p.  This module computes:

    T(a, n)      = t_a mod n            (the frozen residue)
    traj(a,n,K)  = [a^^1, ..., a^^K] mod n  (exact trajectory, incl. pre-freeze)
    freeze(a, n) = smallest k0 with a^^k = a^^k0 mod n for all k >= k0

Method for T: CRT split n = n_bad * m with m coprime to a and n_bad the
a-sharing prime-power part; t_a = 0 mod n_bad (v_q(a^^k) -> infinity),
and t_a = a^(t_a mod lambda(m)) mod m (pure congruence, gcd(a,m)=1,
ord_m(a) | lambda(m)).  Independent cross-check: hzy's totient algorithm
(the MO 479419 poster's), and OEIS A245970.
"""
from sympy import factorint, totient, isprime
from math import gcd, lcm
from functools import lru_cache

# ---------- Carmichael lambda ----------
@lru_cache(maxsize=None)
def carm(n: int) -> int:
    if n == 1:
        return 1
    out = 1
    for q, e in factorint(n).items():
        if q == 2:
            lam = 1 if e == 1 else (2 if e == 2 else 2 ** (e - 2))
        else:
            lam = q ** (e - 1) * (q - 1)
        out = lcm(out, lam)
    return out

# ---------- T(a, n): the frozen residue ----------
@lru_cache(maxsize=None)
def T(a: int, n: int) -> int:
    """a^^inf mod n, via CRT + lambda recursion."""
    if n == 1:
        return 0
    # split n = bad * m, bad = prime powers sharing a factor with a
    bad, m = 1, n
    for q in factorint(gcd(a, n)):
        while m % q == 0:
            bad *= q
            m //= q
    # t = 0 mod bad;  t = a^(T(a, carm(m))) mod m
    rm = 0 if m == 1 else pow(a, T(a, carm(m)), m)
    if bad == 1:
        return rm
    if m == 1:
        return 0
    # CRT: x = 0 mod bad, x = rm mod m
    inv = pow(bad, -1, m)
    return (bad * ((rm * inv) % m)) % n

# ---------- hzy's algorithm (MO 479419), independent implementation ----------
def towermod_hzy(a: int, m: int) -> int:
    if m == 1:
        return 0
    tm = int(totient(m))
    return pow(a, tm + towermod_hzy(a, tm), m)

# ---------- exact trajectory a^^k mod n  (pre-freeze honest values) ----------
def _lam_chain(n):
    ch = [n]
    while ch[-1] != 1:
        ch.append(carm(ch[-1]))
    return ch

@lru_cache(maxsize=None)
def traj_val(a: int, k: int, n: int) -> int:
    """a^^k mod n, exact for every k >= 1 (a >= 2)."""
    if n == 1:
        return 0
    if k == 1:
        return a % n
    # exact small towers: a^^(k-1) as an actual integer when feasible
    if a == 2 and k <= 5:            # 2^^4 = 65536, 2^^5 = 2^65536 (20k digits ok)
        e = 2 ** 65536 if k == 5 else [None, 2, 4, 16, 65536][k - 1]
        return pow(2, e, n)
    if a == 3 and k <= 3:            # 3^^2 = 27, 3^^3 = 3^27
        e = [None, 3, 27][k - 1]
        return pow(3, e, n)
    if a == 4 and k <= 3:
        e = [None, 4, 256][k - 1]
        return pow(4, e, n)
    # general step: exponent E = a^^(k-1) is astronomically large; use
    # a^E = a^E' mod n for any E' = E mod lam(n) with E' >= log2(n).
    # (add enough multiples of lam so the lifted exponent clears log2 n)
    lam = carm(n)
    e_red = traj_val(a, k - 1, lam)
    m = max(1, (70 - e_red + lam - 1) // lam)
    return pow(a, e_red + lam * m, n)

def freeze_height(a: int, n: int, pad: int = 3):
    """(k0, frozen_value): smallest k0 with a^^k constant mod n for k>=k0.
    Checked out to chain-depth + pad, and frozen value cross-checked vs T."""
    depth = len(_lam_chain(n)) + pad
    vals = [traj_val(a, k, n) for k in range(1, depth + 1)]
    tv = T(a, n)
    assert vals[-1] == tv and vals[-2] == tv, (a, n, vals, tv)
    k0 = depth
    while k0 > 1 and vals[k0 - 2] == tv:
        k0 -= 1
    # confirm all values from k0 on equal tv
    assert all(v == tv for v in vals[k0 - 1:]), (a, n, k0, vals)
    return k0, tv

if __name__ == "__main__":
    import random, sys
    random.seed(1)

    # 1) vs OEIS A245970 (2^^inf mod n), full b-file
    bfile = "/tmp/claude-0/-home-user-claude-mythos-self-play/df482f23-d1ae-562a-8002-f98face66e54/scratchpad/b245970.txt"
    bad = 0
    with open(bfile) as f:
        for line in f:
            parts = line.split()
            if len(parts) != 2 or parts[0].startswith('#'):
                continue
            n, v = int(parts[0]), int(parts[1])
            if T(2, n) != v:
                bad += 1
                print("MISMATCH A245970 at n =", n, T(2, n), v)
    print("A245970 check (n<=10000): mismatches =", bad)

    # 2) vs hzy's totient algorithm, random n, bases 2 and 3
    for a in (2, 3):
        for _ in range(300):
            n = random.randint(2, 10 ** 6)
            assert T(a, n) == towermod_hzy(a, n), (a, n)
    print("hzy cross-check: 600 random n <= 1e6 agree (bases 2,3)")

    # 3) literal towers: 2^^4 and 2^^5 computed as actual integers
    for n in random.sample(range(2, 10 ** 5), 200):
        e4 = 2 ** 65536
        lit5 = pow(2, e4, n)                      # literal 2^^5 mod n
        assert lit5 == traj_val(2, 5, n)
        k0, tv = freeze_height(2, n)
        if k0 <= 5:
            assert tv == lit5, (n, k0)
    print("literal 2^^5 (20k-digit exponent) agrees; freeze<=5 values literal-checked")

    # 4) known facts from MO 479419
    assert T(2, 3) == 1                       # 3 | t-1
    assert (T(2, 13) - 3) % 13 == 0           # 13 | t-3
    assert (T(2, 71) - 3) % 71 == 0           # 71 | t-3
    p = 61094071
    assert isprime(p) and (T(3, p) + 4) % p == 0   # 3^^inf+4: hzy's giant key
    assert (T(4, 7) + 3) % 7 == 0             # base 4: door +3 opens at p=7
    print("known facts verified: 3|t-1, 13,71|t-3, 61094071|t3+4, 7|t4+3")

    # 5) the +1 theorem: v2(t mod (p-1)) >= v2(p-1) >= v2(ord) makes
    #    2^x = -1 impossible; empirically no small p divides t+1
    for p in [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 1009, 65537]:
        assert (T(2, p) + 1) % p != 0
    print("+1 door: no small prime divides t+1 (theorem holds empirically)")
    print("ALL CORE CHECKS PASS")
