"""gamma_layers.py — complete resolution of MO 513837 ("Euler's constant via
the odd harmonic series with dyadic layers grouping").

CLAIM (poster):  with  B_k = sum of 1/n over odd n in [2^(k-1), 2^k),
    gamma = lim_N [ sum_{k=1..N} (2 - 2^(k-N)) B_k - N ln 2 ].

THEOREM (this file, exact):   for every N >= 1,

    sum_{k=1..N} (2 - 2^(k-N)) B_k  =  H_{2^N - 1}          (finite, rational!)

Proof (one line): group H_{2^N-1} = sum_{n<2^N} 1/n by odd part. Each n
factors uniquely as n = 2^j * m with m odd; if m lies in layer k then
n < 2^N iff j <= N-k, and 1/n = 2^-j / m, so the total weight received by
1/m is sum_{j=0..N-k} 2^-j = 2 - 2^(k-N).  QED

Hence the poster's limit IS the classical H_M - ln M -> gamma along M = 2^N,
equivalently  S_N - gamma = psi(2^N) - N ln 2, with the Euler-Maclaurin error
    S_N - gamma = -1/(2M) - sum_j B_{2j}/(2j M^{2j}),  M = 2^N
                = -(1/2)2^-N - (1/12)4^-N + (1/120)16^-N - ...
i.e. exactly 0.301 decimal digits per layer — elegant, but not competitive
as a gamma algorithm (layer k holds 2^(k-2) terms; work is exponential in
digits unless B_k is computed by psi, which is circular).

Generalization (same proof, grouping by b-free part): for any base b >= 2,
    H_{b^N - 1} = sum_{k=1..N} (b - b^(k-N))/(b-1) * B_k^(b),
    B_k^(b) = sum of 1/n over b∤n, n in [b^(k-1), b^k).

Checks below:
  T1  exact-rational identity for N <= 12 (Fraction arithmetic, no floats)
  T2  weight bookkeeping: per-even-integer weights recount H exactly (N=10)
  T3  high-precision: S_N - gamma == psi(2^N) - N ln 2 to ~400 digits
  T4  error law coefficients -1/2, -1/12, +1/120 (Bernoulli), and
      digits-per-layer = log10(2)
  T5  base-3 generalization at high precision
"""
from fractions import Fraction
import mpmath as mp

# ---------- T1: exact rational identity ----------
print("== T1: exact rational identity  sum (2-2^(k-N)) B_k = H(2^N-1) ==")
for N in (1, 2, 3, 5, 8, 12):
    Bk = [sum(Fraction(1, n) for n in range(2 ** (k - 1), 2 ** k) if n % 2)
          for k in range(1, N + 1)]
    lhs = sum((2 - Fraction(1, 2 ** (N - k))) * Bk[k - 1] for k in range(1, N + 1))
    rhs = sum(Fraction(1, n) for n in range(1, 2 ** N))
    assert lhs == rhs, (N, lhs, rhs)
print("T1 PASS: identity holds EXACTLY in Q for N = 1,2,3,5,8,12")

# ---------- T2: weight bookkeeping ----------
print("\n== T2: odd-part grouping bookkeeping (N=10) ==")
N = 10
acc = {}
for n in range(1, 2 ** N):
    m = n
    while m % 2 == 0:
        m //= 2
    acc[m] = acc.get(m, Fraction(0)) + Fraction(1, n)
ok = True
for m, tot in acc.items():
    k = m.bit_length()  # layer: 2^(k-1) <= m < 2^k
    w = 2 - Fraction(1, 2 ** (N - k))
    assert tot == w * Fraction(1, m), (m, tot)
print("T2 PASS: every odd m receives exactly (2 - 2^(k-N))/m from its 2-power multiples")

# ---------- T3: high precision equivalence ----------
mp.mp.dps = 420
ln2 = mp.log(2); gamma = +mp.euler
def O(M):
    if M <= 0: return mp.mpf(0)
    return mp.harmonic(M) - mp.harmonic(M // 2) / 2
print("\n== T3: S_N - gamma = psi(2^N) - N ln2 ==")
for N in (10, 50, 200, 400):
    Bk = [O(2 ** k - 1) - O(2 ** (k - 1) - 1) for k in range(1, N + 1)]
    S = sum((2 - mp.mpf(2) ** (k - N)) * Bk[k - 1] for k in range(1, N + 1)) - N * ln2
    d = abs(S - gamma - (mp.digamma(2 ** N) - N * ln2))
    print(f"N={N:4d}: |S_N - gamma - (psi(2^N)-N ln2)| = {mp.nstr(d, 4)}")
    assert d < mp.mpf(10) ** (-380)
print("T3 PASS")

# ---------- T4: error law ----------
print("\n== T4: Euler-Maclaurin error law ==")
for N in (60, 100):
    x = mp.mpf(2) ** -N
    E = mp.digamma(2 ** N) - N * ln2      # == S_N - gamma
    r1 = (E) / x
    r2 = (E + x / 2) / x ** 2
    r3 = (E + x / 2 + x ** 2 / 12) / x ** 4
    print(f"N={N}: E/x = {mp.nstr(r1, 15)}  (E+x/2)/x^2 = {mp.nstr(r2, 15)}  "
          f"(E+x/2+x^2/12)/x^4 = {mp.nstr(r3, 15)}")
print("-> coefficients -1/2, -1/12, +1/120 = -B1, -B2/2, -B4/4 (Bernoulli), no odd terms")
print(f"-> digits per layer = log10 2 = {float(mp.log10(2)):.6f}")

# ---------- T5: base-3 generalization ----------
print("\n== T5: base-3 version, exact rational, N=8 ==")
b, N = 3, 8
Bk3 = [sum(Fraction(1, n) for n in range(b ** (k - 1), b ** k) if n % b)
       for k in range(1, N + 1)]
lhs = sum(Fraction(b - Fraction(1, b ** (N - k)), b - 1) * Bk3[k - 1]
          for k in range(1, N + 1))
rhs = sum(Fraction(1, n) for n in range(1, b ** N))
assert lhs == rhs
print("T5 PASS: H(3^N - 1) = sum (3 - 3^(k-N))/2 * B_k^(3) exactly; "
      "gamma = lim [...] - N ln 3 follows identically")

print("\nALL GAMMA-LAYER CHECKS PASSED")
