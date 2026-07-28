"""T_2A q-series from scratch (exact integer arithmetic), evaluation at CM points,
Baby Monster decompositions, class number h(-232), rung ladder."""
from math import isqrt, factorial
from fractions import Fraction

# ---------- exact integer q-series ----------
N = 40   # series precision (powers of q)
def mul(a, b):
    c = [0]*(N+1)
    for i, ai in enumerate(a):
        if ai:
            for j, bj in enumerate(b):
                if i+j <= N and bj: c[i+j] += ai*bj
    return c
def power(a, k):
    r = [1]+[0]*N
    while k:
        if k & 1: r = mul(r, a)
        a = mul(a, a); k >>= 1
    return r
def inv(a):
    assert a[0] == 1
    b = [1]+[0]*N
    for n in range(1, N+1):
        b[n] = -sum(a[i]*b[n-i] for i in range(1, n+1))
    return b

# f0 = prod_{m odd} (1 - q^m)^24  (this is q * (eta(tau)/eta(2tau))^24)
f0 = [1]+[0]*N
for m in range(1, N+1, 2):
    t = [0]*(N+1); t[0] = 1
    if m <= N: t[m] = -1
    f0 = mul(f0, power(t, 24)[:N+1])
# f = q^{-1} f0 ;  T = f + 4096/f + const  -> compute series of f0inv = 1/f0
f0i = inv(f0)
# T(q) = q^{-1} f0 + 4096 q * f0i + 24?  check coefficient of q^1
# q^{-1}f0: coefficient of q^k is f0[k+1]; 4096 q f0i: coeff of q^k is 4096*f0i[k-1]
T = {}
for k in range(-1, N-1):
    c = (f0[k+1] if 0 <= k+1 <= N else 0) + (4096*f0i[k-1] if 0 <= k-1 <= N else 0)
    T[k] = c
print("T_2A series (f + 4096/f):", {k: T[k] for k in range(-1, 6)})
# known: T_2A = q^-1 + 4372 q + 96256 q^2 + 1240002 q^3 + ... constant conventionally 0 (here f0[0..]=?)

# ---------- high-precision evaluation at CM points ----------
DPS = 170; S = 10**DPS
def iarctan_inv(x, S):
    total = 0; num = S // x; n = 0; x2 = x*x
    while True:
        t = num // (2*n+1)
        if t == 0: break
        total += t if n % 2 == 0 else -t
        num //= x2; n += 1
    return total
PI = 16*iarctan_inv(5,S) - 4*iarctan_inv(239,S)
def isqrt_scaled(n): return isqrt(n*S*S)
def iexp(x):
    k = 0
    while x > S//4: x //= 2; k += 1
    total = S; term = S; n = 1
    while term:
        term = term*x//(n*S); total += term; n += 1
    for _ in range(k): total = total*total//S
    return total

def T2A_at(s2m_scaled):
    """T_2A(i*sqrt(2m)/2) where q = e^{-pi sqrt(2m)}; input: sqrt(2m) scaled."""
    x = PI*s2m_scaled//S
    qinv = iexp(x)                 # e^{pi sqrt(2m)} scaled  (= 1/q)
    q = S*S//qinv                  # q scaled
    # f = q^{-1} * prod_{m odd}(1-q^m)^24 ; evaluate product with enough factors
    prod = S
    qm = q  # q^1
    m = 1
    while qm and m < 60:
        if m % 2 == 1:
            term = S - qm
            # (1-q^m)^24
            p24 = term
            for _ in range(23):
                p24 = p24*term//S
            prod = prod*p24//S
        qm = qm*q//S; m += 1
    f = qinv*prod//S
    T = f + 4096*S*S//f + 24*S
    return T, q, qinv

SQ58 = isqrt_scaled(58)
T, q, qinv = T2A_at(SQ58)
print("T_2A(i sqrt58/2) =", str(T)[:DPS-155], ".", str(T)[11:11+50])
tgt = (396**4-104)
print("  integer?  T - (396^4-104) =", (T - tgt*S)/S)
# the identity: e^{pi sqrt58} = (396^4-104) - (T - q^{-1})  i.e. miss = tail
tail = tgt*S - qinv          # 396^4-104 - e^{pi sqrt58}
series_tail = (4372*q + 96256*(q*q//S) + 1240002*(q*q//S*q//S)) // 1
d = abs(tail - series_tail)
print("  miss vs 4372q+96256q^2+1240002q^3 : agree to", DPS - len(str(d)) - 11, "digits after the point")

# ---------- the rung ladder: T_2A at i sqrt(2m)/2 for m=1..40 ----------
print("\nrung ladder  m : e^{pi sqrt(2m)}  T_2A value  nearest-int miss")
rungs = []
for m in range(1, 41):
    s = isqrt_scaled(2*m)
    T, q, qinv = T2A_at(s)
    nearest = (T + S//2)//S
    miss = (T - nearest*S)/S
    rungs.append((m, nearest, miss))
    if abs(miss) < 1e-3:
        print(f"  m={m:3d}  disc=-{8*m:4d}  T_2A = {nearest}  miss = {miss:+.3e}")

# ---------- class number h(-232) by brute force reduced forms ----------
def class_number(D):
    h = 0; forms = []
    b = D % 2
    while b*b <= -D//3:
        rem = (b*b - D)
        if rem % 4 == 0:
            ac = rem//4
            a = max(b, 1)
            while a*a <= ac:
                if a and ac % a == 0:
                    c = ac//a
                    if a <= c and (0 <= b <= a):
                        # count (a,b,c) and (a,-b,c) appropriately
                        if b == 0 or b == a or a == c:
                            h += 1; forms.append((a,b,c))
                        else:
                            h += 2; forms.append((a,b,c)); forms.append((a,-b,c))
                a += 1
        b += 2 if D%2==0 else 2
    return h, forms
# D=-232: b even
h, forms = class_number(-232)
print("\nh(-232) =", h, " forms:", forms, " genus bound 2^(omega-1) = 2  [232 = 8*29]")

# ---------- Baby Monster decompositions ----------
# smallest irreducible character degrees of the Baby Monster B (ATLAS):
Bdims = [1, 4371, 96255, 1139374, 9458750, 9550635, 63532485, 347643114, 356054375, 1407126890]
def decomps(n, dims, maxparts=8):
    out = []
    def rec(i, rem, cur):
        if rem == 0: out.append(tuple(cur)); return
        if i < 0 or len(cur) >= maxparts: return
        d = dims[i]
        k = 0
        while k*d <= rem:
            rec(i-1, rem-k*d, cur + [d]*k) if k else None
            k += 1
        rec(i-1, rem, cur)
        # include k copies
    # simpler: bounded DP
    def rec2(i, rem, cur):
        if rem == 0: out.append(tuple(sorted(cur, reverse=True))); return
        if i < 0: return
        d = dims[i]
        kmax = rem//d
        for k in range(kmax, -1, -1):
            if len(cur)+k <= maxparts:
                rec2(i-1, rem-k*d, cur+[d]*k)
    rec2(len(dims)-1, n, [])
    return sorted(set(out))
for lvl, c in [(1, 4372), (2, 96256), (3, 1240002)]:
    ds = decomps(c, Bdims, maxparts=6)
    print(f"level {lvl}: {c} = decompositions into <=6 B-irrep dims: {len(ds)}")
    for d in ds[:4]: print("   ", " + ".join(map(str,d)))
