"""Bounded-modulus gate checker for l=5 equal-gap runs in S (Z[sqrt2] members:
every prime p ≡ 3,5 mod 8 to even order). A residue class n mod M is KILLED if
some member m = n+k*g provably has odd valuation at 3 or 5 (both ≡ 3,5 mod 8)
with unit part determined, or has determined odd part ≡ 3,5 (mod 8).
If ALL classes die at modulus M = 2^A * 3^B * 5^C, the channel is closed for
l=5 (a rigorous finite certificate). Survivor classes are the gate."""
import sys
import numpy as np

A, B, C = 8, 5, 4
M2, M3, M5 = 2**A, 3**B, 5**C

def killed_member(m_mod2, m_mod3, m_mod5):
    # valuation at 3: determined if v3 < B-1
    m = m_mod3; v = 0
    while m % 3 == 0 and v < B - 1:
        m //= 3; v += 1
    if v < B - 1 and v % 2 == 1 and m % 3 != 0:
        return True
    v3_undet = not (v < B - 1)
    m = m_mod5; v = 0
    while m % 5 == 0 and v < C - 1:
        m //= 5; v += 1
    if v < C - 1 and v % 2 == 1 and m % 5 != 0:
        return True
    m = m_mod2; v = 0
    while m % 2 == 0 and v < A - 3:
        m //= 2; v += 1
    if v < A - 3:
        # odd part determined mod 8
        if m % 8 in (3, 5):
            return True
    return False

def gate(g, l=5):
    survivors = []
    # work mod lcm componentwise (CRT): enumerate mod 2^A,3^B,5^C jointly is
    # 2^8*3^5*5^4 = 38.9M -- do componentwise kills first, then CRT-combine
    ok2 = [n for n in range(M2)
           if not any(killed_member((n + k*g) % M2, 1, 1) for k in range(l))]
    ok3 = [n for n in range(M3)
           if not any(killed_member(1, (n + k*g) % M3, 1) for k in range(l))]
    ok5 = [n for n in range(M5)
           if not any(killed_member(1, 1, (n + k*g) % M5) for k in range(l))]
    return ok2, ok3, ok5

for g in [14, 17, 18, 19, 20, 21, 22, 23, 24, 25]:
    ok2, ok3, ok5 = gate(g)
    closed = (not ok2) or (not ok3) or (not ok5)
    print(f'g={g}: |ok mod {M2}|={len(ok2)} |ok mod {M3}|={len(ok3)} '
          f'|ok mod {M5}|={len(ok5)}  => {"CLOSED (certified)" if closed else "open gate"}')
    if g == 25 and not closed:
        print('   g=25 gate mod 16:', sorted(set(n % 16 for n in ok2)),
              ' mod 9:', sorted(set(n % 9 for n in ok3)),
              ' mod 25:', sorted(set(n % 25 for n in ok5))[:12], '...')
        print('   density: 2-part %.4f  3-part %.4f  5-part %.4f  total %.6f'
              % (len(ok2)/M2, len(ok3)/M3, len(ok5)/M5,
                 len(ok2)/M2 * len(ok3)/M3 * len(ok5)/M5))
