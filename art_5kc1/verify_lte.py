#!/usr/bin/env python3
"""MO 513938 verification.  q_j(a) = (a^j - 1)/2^v2(a-1), odd a, odd j.
OP's claim (two cases, alpha=v2(a-1), beta=v2(a+1)):
    v2(q_x - q_y) = v2(x-y)            if alpha > beta
                  = v2(x-y) + beta - 1 if beta > alpha
Unified single formula (ours):  v2(q_x - q_y) = v2(x-y) + (beta - 1)   ALWAYS
(both cases: exactly one of alpha,beta equals 1 for odd a).
Proof: q_x - q_y = a^y (a^{x-y} - 1)/2^alpha ; x-y even; LTE(even case):
v2(a^m - 1) = alpha + beta + v2(m) - 1.  QED.
Also: for odd prime p | a-1, normalizing by p^{v_p(a-1)} gives an ISOMETRY
(v_p(Q_x - Q_y) = v_p(x-y)) — the only prime that can shift is 2.
Plus residue-count law mod 2^R."""
import random, sys
from sympy import factorint

def v2(n):
    n = abs(n); assert n != 0
    v = 0
    while n % 2 == 0: n //= 2; v += 1
    return v

def vp(n, p):
    n = abs(n); assert n != 0
    v = 0
    while n % p == 0: n //= p; v += 1
    return v

random.seed(20260805)
checks = 0; fails = 0
# exhaustive small + random large
As = [a for a in range(3, 200, 2)] + [random.randrange(3, 10**12) | 1 for _ in range(60)]
for a in As:
    al = v2(a - 1); be = v2(a + 1)
    assert (al == 1) != (be == 1) or (al == 1 and be == 1) == False
    assert min(al, be) == 1 and al != be
    sh = be - 1
    pairs = [(x, y) for x in range(1, 40, 2) for y in range(1, x, 2)]
    pairs += [(random.randrange(1, 10**6) | 1, random.randrange(1, 10**6) | 1) for _ in range(15)]
    for (x, y) in pairs:
        if x == y: continue
        qx = (pow(a, x) - 1) >> al if x < 2000 else None
        if qx is None:
            # work mod 2^BIG to keep it fast for huge exponents
            BIG = v2(x - y) + sh + 64
            M = 1 << (BIG + al)
            qx = (pow(a, x, M) - 1) >> al
            qy = (pow(a, y, M) - 1) >> al
            lhs = v2((qx - qy) % (1 << BIG) or 1 << BIG)
            got = lhs if lhs < BIG else None
        else:
            qy = (pow(a, y) - 1) >> al
            got = v2(qx - qy)
        want = v2(x - y) + sh
        # OP two-case form for cross-check
        op = v2(x - y) if al > be else v2(x - y) + be - 1
        assert op == want
        if got != want:
            fails += 1; print("FAIL", a, x, y, got, want)
        checks += 1
print(f"2-adic similarity law: {checks} checks, {fails} fails")

# odd-prime isometry claim
checks2 = 0
for _ in range(400):
    p = random.choice([3, 5, 7, 11, 13, 31, 97])
    k = random.randrange(1, 3)
    a = 1 + p**k * random.randrange(1, 10**5)
    if a % 2 == 0: a += p**k
    e = vp(a - 1, p)
    x = random.randrange(1, 10**4) | 1; y = random.randrange(1, 10**4) | 1
    if x == y: continue
    Qx = (pow(a, x) - 1) // p**e; Qy = (pow(a, y) - 1) // p**e
    assert vp(Qx - Qy, p) == vp(x - y, p), (p, a, x, y)
    checks2 += 1
print(f"odd-prime isometry: {checks2} checks, 0 fails")

# residue-count law mod 2^R: image size of {q_j mod 2^R : j odd} should be
# 2^(R - sh) exactly (similarity with ratio 2^-sh collapses sh levels), each
# attained residue hit equally often as j runs over odd classes mod 2^(R-sh+?).
print("\nresidue counts mod 2^R  (a, beta-1, R, #distinct, predicted 2^(R-sh), equidistributed?)")
for a in [3, 5, 7, 9, 11, 13, 15, 17, 23, 31, 33, 63, 65]:
    al = v2(a - 1); be = v2(a + 1); sh = be - 1
    for R in [6, 10]:
        T = R + 6  # j over odd residues mod 2^T
        from collections import Counter
        cnt = Counter()
        M = 1 << (R + al)
        for j in range(1, 1 << T, 2):
            q = (pow(a, j, M) - 1) >> al
            cnt[q & ((1 << R) - 1)] += 1
        distinct = len(cnt)
        # domain {odd j} is a ball of radius 1/2; similarity ratio 2^-sh maps it
        # onto a ball of radius 2^-(sh+1): the coset q_1 + 2^(sh+1) Z_2.
        pred = 1 << max(R - sh - 1, 0)
        eq = (len(set(cnt.values())) == 1)
        q1 = (a - 1) >> al
        ball_ok = all((r - q1) % (1 << min(sh + 1, R)) == 0 for r in cnt)
        status = "OK" if distinct == pred and eq and ball_ok else "MISMATCH"
        print(f"  a={a:3d} sh={sh}  R={R:2d}  distinct={distinct:5d} pred={pred:5d} "
              f"equidist={eq} ball(q1+2^{sh+1}Z2)={ball_ok}  {status}")
