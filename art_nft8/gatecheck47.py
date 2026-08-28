#!/usr/bin/env python3
"""Certificate for the l=4 g=25 product gate (Atlas 47).

Membership set S = {n : x^2-2y^2 = +-n representable} = {n whose primes
p ≡ 3,5 (mod 8) all appear to even exponent}. 2-adically: the odd part of
n must be ≡ ±1 (mod 8) — v2(n) itself is free (2 is ramified/good).
3-adically: 3 ≡ 3 (mod 8) is bad, so v3(n) must be even.

A 4-term run with gap 25 starting at s needs s, s+25, s+50, s+75 ∈ S.
This script decides, for every 2-adic class and every 3-adic class of s,
whether the four points can all avoid the LOCAL exclusions:
  - 2-adic: odd part ≡ 3,5 (mod 8)  [needs v2 determined + 3 more bits]
  - 3-adic: v3 odd                   [needs v3 determined]
by recursive class-splitting to caps 2^A / 3^B. Classes surviving only
via undetermined deep-valuation threads are split until resolved or cap,
and reported separately (conservative).

Output: the surviving 2-adic classes projected mod 16, the surviving
3-adic classes projected mod 9, and their product mod 144.
"""
A_CAP = 2**26
B_CAP = 3**14

def survive2(s, mod):
    """does class s (mod mod=2^a) allow all four points 2-adically?
       returns 'yes'/'no'/'split'"""
    for i in range(4):
        n = (s + 25*i) % mod
        m = mod; v = 0; x = n
        # v2 of the class: trailing zeros of x modulo m
        if x == 0:
            return 'split'          # v2 undetermined at this depth
        while x % 2 == 0:
            x //= 2; v += 1
        # odd part known modulo m/2^v; need 3 bits
        if (mod >> v) < 8:
            return 'split'
        if x % 8 in (3, 5):
            return 'no'
    return 'yes'

def survive3(s, mod):
    for i in range(4):
        n = (s + 25*i) % mod
        if n == 0:
            return 'split'
        v = 0; x = n
        while x % 3 == 0:
            x //= 3; v += 1
        if (mod // (3**v)) < 3:
            return 'split'
        if v % 2 == 1:
            return 'no'
    return 'yes'

def analyse(base, cap, fn):
    """BFS split; returns (survivor classes as (s, mod) list, unresolved)"""
    from collections import deque
    q = deque((s, base) for s in range(base))
    ok, unres = [], []
    while q:
        s, mod = q.popleft()
        r = fn(s, mod)
        if r == 'yes':
            ok.append((s, mod))
        elif r == 'split':
            if mod*[2,3][fn is survive3] > cap:
                unres.append((s, mod))
            else:
                b = 2 if fn is survive2 else 3
                for t in range(b):
                    q.append((s + t*mod, mod*b))
    return ok, unres

ok2, un2 = analyse(64, A_CAP, survive2)
ok3, un3 = analyse(27, B_CAP, survive3)
p16 = sorted({s % 16 for s, m in ok2})
p9  = sorted({s % 9 for s, m in ok3})
print("2-adic survivors project to mod 16:", p16)
print("   unresolved 2-adic threads:", len(un2),
      [(s, m) for s, m in un2[:4]])
print("3-adic survivors project to mod 9:", p9)
print("   unresolved 3-adic threads:", len(un3),
      [(s, m) for s, m in un3[:4]])
un2_16 = sorted({s % 16 for s, m in un2})
un3_9  = sorted({s % 9 for s, m in un3})
print("unresolved threads' projections: mod16", un2_16, " mod9", un3_9)
prod = sorted({(a_ % 16) * 0 + ( ( (a_ % 16) * 9 * 9 + (b_ % 9) * 16 * 4 ) % 144 )
               for a_ in p16 for b_ in p9})
# proper CRT mod 144: find x ≡ a mod 16, x ≡ b mod 9
def crt(a, b):
    for x in range(144):
        if x % 16 == a and x % 9 == b:
            return x
prod = sorted({crt(a_, b_) for a_ in p16 for b_ in p9})
print("PRODUCT GATE mod 144:", prod)
print("expected {94,103,110,119}:", prod == [94, 103, 110, 119])
