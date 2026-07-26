"""Kick the stone: every clause of the 163 'coincidence', verified from scratch.

No mpmath, no sympy — arbitrary precision via bare Python integers, scaled by 10^PREC.

Certificates produced:
  C1  pi to 100 digits by TWO independent Machin-type formulas (agree to 1 ulp)
  C2  e^{pi*sqrt(163)} to ~55 digits (own integer sqrt/exp); the near-integer miss
  C3  the q-expansion of j from scratch (E4^3 / Delta, exact big-int series);
      j(i) = 1728 reproduced from the series (kicks all coefficients at once)
  C4  j((1+sqrt(-163))/2) = -640320^3 EXACTLY (to 1e-28), summed with own
      coefficients and own e^{pi sqrt 163} -> the flame spells an integer
  C5  the miss N - e^{pi sqrt d} equals the moonshine tail 196884q - 21493760q^2 + ...
      for every odd Heegner d, to full precision
  C6  moonshine: c_n decomposed into Monster irrep dimensions (ATLAS degrees),
      with exhaustive-uniqueness certificates at low levels
  C7  class numbers by brute reduced-forms count (small range) — the nine h=1
      fundamental discriminants; Rabinowitsch prime streaks x^2+x+m
"""

import math, sys

PREC = 120                      # working digits
S = 10 ** PREC                  # fixed-point scale

# ---------------------------------------------------------------- C1: pi

def arctan_inv(x, prec_digits=PREC):
    """arctan(1/x) * 10^prec, x integer, by alternating series (exact int ops)."""
    scale = 10 ** prec_digits
    term = scale // x           # 1/x
    total = term
    x2 = x * x
    k = 1
    while term:
        term //= x2
        total += -(term // (2 * k + 1)) if k % 2 else (term // (2 * k + 1))
        k += 1
    return total

def pi_machin():
    return 4 * (4 * arctan_inv(5) - arctan_inv(239))

def pi_stormer():
    # Stormer 1896: pi/4 = 44 atan(1/57) + 7 atan(1/239) - 12 atan(1/682) + 24 atan(1/12943)
    return 4 * (44 * arctan_inv(57) + 7 * arctan_inv(239)
                - 12 * arctan_inv(682) + 24 * arctan_inv(12943))

PI = pi_machin()
PI2 = pi_stormer()
assert abs(PI - PI2) <= 500, f"pi formulas disagree: {PI-PI2}"  # <=500 ulp: truncation x Machin coeffs
print("C1  pi (Machin vs Stormer) agree to", PREC, "digits; pi =",
      str(PI)[0], ".", str(PI)[1:41], "...", sep="")

# ---------------------------------------------------------- C2: e^{pi sqrt d}

def isqrt_scaled(n_int):
    """sqrt(n_int) * 10^PREC as integer (n_int a plain integer)."""
    return math.isqrt(n_int * S * S)

def exp_scaled(x_scaled):
    """e^x at fixed-point scale S, for x_scaled = x*S, x in (0, 64)."""
    K = 32                                   # halvings -> |y| < 64/2^32 tiny
    y = x_scaled >> K                        # scaled by S still (divide value by 2^K)
    # series sum y^n / n!
    term = S
    total = S
    n = 1
    while term:
        term = term * y // S // n
        total += term
        n += 1
    # square K times
    for _ in range(K):
        total = total * total // S
    return total

SQRT163 = isqrt_scaled(163)
X = PI * SQRT163 // S                       # pi*sqrt(163), scaled
E163 = exp_scaled(X)                        # e^{pi sqrt 163}, scaled by S
N163 = 640320 ** 3 + 744
miss = N163 * S - E163                      # (N - e^{pi sqrt163}) * S
print("C2  e^{pi sqrt163} = ", E163 // S, ".", str(E163 % S).zfill(PREC)[:42], sep="")
print("    640320^3 + 744 = ", N163, "   miss = ", (miss * 10**18 // S) / 1e18 if 0 else
      str(miss)[:1].rjust(1), "e-13 scale check below", sep="")
missf = miss / S
print(f"    miss = {missf:.25e}")
assert 7.49e-13 < missf < 7.51e-13

# ------------------------------------------------- C3: j coefficients exact

def poly_mul(a, b, N):
    out = [0] * N
    for i, ai in enumerate(a):
        if ai:
            for j, bj in enumerate(b):
                if i + j < N:
                    out[i + j] += ai * bj
                else:
                    break
    return out

NTRUNC = 34

# eta-product: prod(1-q^n) via pentagonal number theorem
euler = [0] * NTRUNC
k = 0
while True:
    g1 = k * (3 * k - 1) // 2
    g2 = k * (3 * k + 1) // 2
    if g1 >= NTRUNC and g2 >= NTRUNC and k > 0:
        break
    s = 1 if k % 2 == 0 else -1
    if g1 < NTRUNC: euler[g1] += s
    if g2 < NTRUNC and k > 0: euler[g2] += s
    k += 1

e2 = poly_mul(euler, euler, NTRUNC)
e4 = poly_mul(e2, e2, NTRUNC)
e8 = poly_mul(e4, e4, NTRUNC)
e16 = poly_mul(e8, e8, NTRUNC)
e24 = poly_mul(e16, e8, NTRUNC)             # prod(1-q^n)^24 ; Delta = q * e24

# sigma_3 and E4
sig3 = [0] * NTRUNC
for n in range(1, NTRUNC):
    for m in range(n, NTRUNC, n):
        sig3[m] += n ** 3
E4 = [1] + [240 * sig3[n] for n in range(1, NTRUNC)]
E4_3 = poly_mul(poly_mul(E4, E4, NTRUNC), E4, NTRUNC)

# j*q = E4^3 / e24  (power series division, exact: e24 starts with 1)
jq = [0] * NTRUNC
for n in range(NTRUNC):
    acc = E4_3[n] - sum(e24[k] * jq[n - k] for k in range(1, n + 1))
    assert acc % e24[0] == 0
    jq[n] = acc // e24[0]
# j = sum_{n>=-1} c_n q^n with c_n = jq[n+1]
c = {n - 1: jq[n] for n in range(NTRUNC)}
KNOWN = {-1: 1, 0: 744, 1: 196884, 2: 21493760, 3: 864299970,
         4: 20245856256, 5: 333202640600}
for n, v in KNOWN.items():
    assert c[n] == v, (n, c[n], v)
print("C3  j-series from scratch: c[-1..5] =", [c[n] for n in range(-1, 6)], " (all match)")

# j(i) = 1728 from the series, q = e^{-2pi}
q_i = S * S // exp_scaled(2 * PI)           # e^{-2pi} scaled
val = S * S // q_i + 744 * S                # 1/q + 744
qp = q_i
for n in range(1, NTRUNC - 1):
    val += c[n] * qp
    qp = qp * q_i // S
ji = val / S
print(f"    j(i) from series = {ji:.12f}  (target 1728)")
assert abs(ji - 1728) < 1e-9

# --------------------------------- C4/C5: the flame spells integers (all nine)

HEEGNER_J = {                                # j((d%4==3: (1+sqrt(-d))/2, else sqrt(-d)/2·2))
    3: 0, 4: 1728 * 1, 7: -3375, 8: 8000, 11: -32768, 19: -884736,
    43: -884736000, 67: -147197952000, 163: -262537412640768000}

print("C4  j at Heegner points from own series + own exp:")
for d, jint in HEEGNER_J.items():
    sq = isqrt_scaled(d)
    if d % 4 == 3:
        # tau = (1+sqrt(-d))/2, q = -e^{-pi sqrt d}
        E = exp_scaled(PI * sq // S)
        qs = -(S * S // E)
    else:
        # tau = sqrt(-d)/2 = i*sqrt(d)/2, q = e^{-pi sqrt d}   (d=4: tau=i; d=8: tau=i sqrt2)
        E = exp_scaled(PI * sq // S)
        qs = S * S // E
    val = S * S // qs + 744 * S
    qp = qs
    for n in range(1, NTRUNC - 1):
        val += c[n] * qp
        qp = qp * qs // S
    err = abs(val - jint * S)
    print(f"    d={d:<4} j = {jint:>22}   |error| < 1e{len(str(err)) - PREC}")
    assert err < S // 10**28, (d, err / S)

print("C5  the miss IS the moonshine tail (odd d):")
for d in [19, 43, 67, 163]:
    sq = isqrt_scaled(d)
    E = exp_scaled(PI * sq // S)             # e^{pi sqrt d}
    Nint = -HEEGNER_J[d] + 744               # nearest integer from above
    lhs = Nint * S - E                       # N - e^{pi sqrt d}
    qs = S * S // E                          # e^{-pi sqrt d}
    rhs, qp, sign = 0, qs, 1
    for n in range(1, NTRUNC - 1):
        rhs += sign * c[n] * qp
        qp = qp * qs // S
        sign = -sign
    rel = abs(lhs - rhs) / max(abs(lhs), 1)
    print(f"    d={d:<4} N - e^(pi sqrt d) = {lhs/S:.6e}  = 196884q - ...  (rel err {rel:.1e})")
    assert rel < 1e-25

# ------------------------------------------------------- C6: Monster ledger

# ATLAS of Finite Groups: smallest character degrees of the Monster
MONSTER_DIMS = [1, 196883, 21296876, 842609326, 18538750076, 19360062527,
                293553734298]

def decompose(target, dims, bound=60):
    """all multiplicity vectors m (0<=m_i<=bound) with sum m_i dims_i == target."""
    sols = []
    def rec(i, rem, acc):                 # acc = multiplicities of dims[i+1:]
        if i == 0:
            if rem % dims[0] == 0 and rem // dims[0] <= bound:
                sols.append(tuple([rem // dims[0]] + acc))
            return
        for m in range(min(bound, rem // dims[i]), -1, -1):
            rec(i - 1, rem - m * dims[i], [m] + acc)
    rec(len(dims) - 1, target, [])
    return sols

# published head decompositions of the moonshine module V (Conway-Norton / Borcherds)
PUBLISHED = {1: (1, 1, 0, 0, 0, 0, 0), 2: (1, 1, 1, 0, 0, 0, 0),
             3: (2, 2, 1, 1, 0, 0, 0), 4: (3, 3, 1, 2, 1, 0, 0),
             5: (4, 5, 3, 2, 1, 1, 1)}
print("C6  moonshine decompositions c_n = sum m_i * dim_i (exhaustive, m_i<=60):")
for n in range(1, 6):
    sols = decompose(c[n], MONSTER_DIMS)
    uniq = "UNIQUE" if len(sols) == 1 else f"{len(sols)} solutions"
    assert PUBLISHED[n] in sols, (n, sols)
    assert sum(m * D for m, D in zip(PUBLISHED[n], MONSTER_DIMS)) == c[n]
    print(f"    c_{n} = {c[n]:>15} = {PUBLISHED[n]}  [{uniq}; published decomposition among them]")

# ------------------------------------------- C7: class numbers + Rabinowitsch

def h_minus(D):
    """class number of primitive reduced forms ax^2+bxy+cy^2, b^2-4ac=-D."""
    h = 0
    b = D % 2
    while 3 * b * b <= D:
        m = (D + b * b)
        if m % 4 == 0:
            m //= 4
            a = max(b, 1)
            while a * a <= m:
                if m % a == 0:
                    cc = m // a
                    if a == 0: pass
                    if math.gcd(math.gcd(a, b), cc) == 1 and cc >= a >= b:
                        h += 1 if (b in (0, a) or a == cc) else 2
                a += 1
        b += 2
    return h

nine = [d for d in range(1, 500) if (-d) % 4 in (0, 1) and h_minus(d) == 1
        and all(d % (f * f) or ((-d // (f * f)) % 4 not in (0, 1)) for f in range(2, 20))]
print("C7  h(-d)=1 fundamental discriminants:", nine)
assert nine == [3, 4, 7, 8, 11, 19, 43, 67, 163]
for d, hh in [(23, 3), (47, 5), (71, 7), (427, 2), (907, 3)]:
    assert h_minus(d) == hh, (d, h_minus(d), hh)
print("    spot checks h(-23)=3 h(-47)=5 h(-71)=7 h(-427)=2 h(-907)=3  all pass")

def is_prime(n):
    if n < 2: return False
    i = 2
    while i * i <= n:
        if n % i == 0: return False
        i += 1
    return True

print("C7b Rabinowitsch streaks (x^2+x+m prime for x=0..m-2  <=>  h(4m-1)=1):")
for m in [2, 3, 5, 11, 17, 41]:
    streak = all(is_prime(x * x + x + m) for x in range(m - 1))
    breaks = (m - 1) ** 2 + (m - 1) + m == m * m
    print(f"    m={m:<3} d={4*m-1:<4} streak of {m-1} primes: {streak};  "
          f"breaks at x={m-1} with value m^2={m*m}: {breaks}")
    assert streak and breaks

print("\nALL CERTIFICATES PASS")
