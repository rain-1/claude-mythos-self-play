"""Exact class numbers h(-D) for ALL discriminants -D, D <= X, by direct census
of reduced binary quadratic forms — vectorized numpy, no libraries.

Reduced: |b| <= a <= c, with b >= 0 when |b| == a or a == c.  D = 4ac - b² > 0.
H[D] counts ALL reduced forms; primitive h[D] recovered by Mobius over squares:
    H[D] = sum_{g² | D-compatible} h[D/g²]   =>   h[D] = sum_g mu(g) H[D/g²].

Self-checks: 30 random D vs pure-python brute force; the nine h=1 fundamental
discriminants; genus theory 2^(omega-1) | h for fundamental D.
"""
import numpy as np, math, time

X = 3_000_000
t0 = time.time()

H = np.zeros(X + 1, np.int32)
amax = int(math.isqrt(X // 3)) + 1
for a in range(1, amax + 1):
    fa = 4 * a
    cmax_all = (X + a * a) // fa
    if cmax_all < a:
        continue
    for b in range(0, a + 1):
        b2 = b * b
        cmax = (X + b2) // fa
        if cmax < a:
            continue
        # +b branch: c from a to cmax, weight 1
        D0 = fa * a - b2
        H[D0: fa * cmax - b2 + 1: fa] += 1
        # -b branch: 0 < b < a, requires a < c strictly
        if 0 < b < a and cmax >= a + 1:
            D1 = fa * (a + 1) - b2
            H[D1: fa * cmax - b2 + 1: fa] += 1
print(f"census raw counts done  {time.time()-t0:.1f}s   total forms = {H.sum():,}")

# Mobius over square divisors
def mobius_upto(n):
    mu = np.ones(n + 1, np.int8)
    primes = []
    spf = np.zeros(n + 1, np.int32)
    for i in range(2, n + 1):
        if spf[i] == 0:
            spf[i::i] = np.where(spf[i::i] == 0, i, spf[i::i])
    mu[0] = 0
    for D in range(2, n + 1):
        d, m, sq = D, 1, False
        while d > 1:
            p = spf[d]
            d //= p
            if d % p == 0:
                sq = True
                break
            m = -m
        mu[D] = 0 if sq else m
    return mu

gmax = int(math.isqrt(X // 3))
mu = mobius_upto(gmax)
h = H.astype(np.int64).copy()
for g in range(2, gmax + 1):
    if mu[g] == 0:
        continue
    g2 = g * g
    n = X // g2
    idx = np.arange(1, n + 1)
    h[idx * g2] += int(mu[g]) * H[idx].astype(np.int64)
print(f"primitivity correction done  {time.time()-t0:.1f}s")

# valid discriminants and fundamentality
D = np.arange(X + 1)
valid = (D % 4 == 0) | (D % 4 == 3)
h[~valid] = 0

# fundamental: -D is a fundamental discriminant.
# D≡3 mod 4: fundamental iff squarefree; D≡0 mod4: m=D/4 must be ≡1,2 mod 4 and squarefree
sqfree = np.ones(X + 1, bool)
for p in range(2, int(math.isqrt(X)) + 1):
    sqfree[p * p:: p * p] = False
fund = np.zeros(X + 1, bool)
m3 = (D % 4 == 3)
fund[m3] = sqfree[m3]
d4 = D[(D % 4 == 0)]
m = d4 // 4
ok = ((m % 4 == 1) | (m % 4 == 2)) & sqfree[m]
fund[d4] = ok
fund[:3] = False

# omega(D) for genus coloring (number of distinct primes)
omega = np.zeros(X + 1, np.int8)
is_comp = np.zeros(X + 1, bool)
for p in range(2, X + 1):
    if not is_comp[p]:
        omega[p::p] += 1
        is_comp[p * p:: p] = True
print(f"omega sieve done  {time.time()-t0:.1f}s")

# ---------------- verification ----------------
def h_brute(Dv):
    hh = 0
    b = Dv % 2
    while 3 * b * b <= Dv:
        mm = Dv + b * b
        if mm % 4 == 0:
            mm //= 4
            a = max(b, 1)
            while a * a <= mm:
                if mm % a == 0:
                    cc = mm // a
                    if math.gcd(math.gcd(a, b), cc) == 1 and cc >= a >= b:
                        hh += 1 if (b in (0, a) or a == cc) else 2
                a += 1
        b += 2
    return hh

rng = np.random.default_rng(163)
test = list(rng.integers(3, 200000, 30)) + [3, 4, 163, 427, 907, 5460, 999999]
bad = 0
for Dv in test:
    Dv = int(Dv)
    if Dv % 4 not in (0, 3):
        continue
    hb = h_brute(Dv)
    if h[Dv] != hb:
        print("MISMATCH", Dv, h[Dv], hb); bad += 1
assert bad == 0
print("spot checks vs brute force: all pass")

nine = D[fund & (h == 1)]
print("h=1 fundamental:", nine.tolist())
assert nine.tolist() == [3, 4, 7, 8, 11, 19, 43, 67, 163]

# genus theory: 2^(omega(D)-1) divides h for fundamental D
sel = fund.copy()
g2t = np.where(sel)[0]
viol = np.sum(h[g2t] % (2 ** np.maximum(omega[g2t].astype(np.int64) - 1, 0)) != 0)
print("genus-theory divisibility violations:", int(viol))
assert viol == 0

# gates: last fundamental D with h = n
gates = {}
hf = h[fund]
Df = D[fund]
for n in range(1, 101):
    m = Df[hf == n]
    if len(m):
        gates[n] = int(m.max())
print("gates (last fundamental D with h=n), n=1..16:", [gates.get(n) for n in range(1, 17)])

np.savez_compressed("census.npz", h=h.astype(np.uint16), fund=fund,
                    omega=omega, gates_n=np.array(list(gates.keys())),
                    gates_d=np.array(list(gates.values())))
print(f"saved census.npz  {time.time()-t0:.1f}s")
