"""Certificates for THE SECOND SHEET (e^{pi sqrt 58} / Ramanujan 1/pi / T_2A).
Everything from scratch in bare Python ints (scaled-integer arithmetic)."""
from math import isqrt

DPS = 170                     # working digits
S = 10**DPS                   # scale

def iarctan_inv(x, S):
    """arctan(1/x) * S, x integer >= 2."""
    total = 0; num = S // x; n = 0; x2 = x*x
    while True:
        t = num // (2*n + 1)
        if t == 0: break
        total += t if n % 2 == 0 else -t
        num //= x2; n += 1
    return total

def compute_pi(S):
    # Machin: pi = 16 arctan(1/5) - 4 arctan(1/239)
    return 16*iarctan_inv(5, S) - 4*iarctan_inv(239, S)

def compute_pi2(S):
    # Stormer: pi = 24 atan(1/8) + 8 atan(1/57) + 4 atan(1/239)
    return 24*iarctan_inv(8,S) + 8*iarctan_inv(57,S) + 4*iarctan_inv(239,S)

def isqrt_scaled(n, S):
    """sqrt(n) * S for integer n."""
    return isqrt(n * S * S)

def iexp(x, S):
    """e^(x/S) * S for x>=0, via halving + series."""
    k = 0
    while x > S // 4:
        x //= 2; k += 1
    total = S; term = S; n = 1
    while term:
        term = term * x // (n * S)
        total += term; n += 1
    for _ in range(k):
        total = total * total // S
    return total

PI = compute_pi(S)
PI2 = compute_pi2(S)
assert abs(PI - PI2) < 10**6, (PI - PI2)   # two formulas agree to ~163 digits
print("pi =", str(PI)[:1]+"."+str(PI)[1:60], "... (two Machin-type formulas agree to", DPS - len(str(abs(PI-PI2))), "digits)")

SQ58 = isqrt_scaled(58, S)
X = PI * SQ58 // S
E58 = iexp(X, S)             # e^{pi sqrt 58}, scaled
target = (396**4 - 104) * S
miss = target - E58
print("e^{pi sqrt58} = %s.%s..." % (str(E58)[:11], str(E58)[11:11+30]))
print("396^4-104 - e^{pi sqrt58} = %.15e" % (miss / S))

# --- Ramanujan's series: 1/pi = (2 sqrt2 / 9801) * sum (4k)! (1103+26390k) / ((k!)^4 396^(4k))
from math import factorial
SQ2 = isqrt_scaled(2, S)
def ram_partial(K, S):
    # returns scaled 1/pi approximation using K+1 terms, exact big-rational -> scaled
    num_acc = 0; den = 1
    # sum as exact rational: sum_k (4k)! (1103+26390k) / ((k!)^4 396^(4k))
    from fractions import Fraction
    tot = Fraction(0)
    for k in range(K+1):
        tot += Fraction(factorial(4*k) * (1103 + 26390*k), factorial(k)**4 * 396**(4*k))
    # 1/pi = 2 sqrt2 /9801 * tot  -> scaled: SQ2 * 2 * tot / 9801
    inv_pi = SQ2 * 2 * tot.numerator // (9801 * tot.denominator)
    return inv_pi

INV_PI = S * S // PI
for K in (0, 1, 2, 5, 10, 19):
    ap = ram_partial(K, S)
    err = abs(ap - INV_PI)
    digs = DPS - len(str(err)) if err else DPS
    print(f"Ramanujan series, {K+1:2d} term(s): 1/pi correct to {digs} digits")

# 26390 = 5*7*13*58 ; 9801 = 99^2 ; 396 = 4*99 ; level 58 = 2*29
assert 26390 == 5*7*13*58 and 9801 == 99**2 and 396 == 4*99
print("factors: 26390 = 5*7*13*58 ; 9801 = 99^2 ; 396 = 4*99 ; 58 = 2*29  [level-58 signature]")
