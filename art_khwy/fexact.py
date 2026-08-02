"""Exact far-shore representation test:
   F(x) =? SUM_{k>=0} binom(1/2,k)/(1-4^k/6) x^(1/2-k)
          + x^(-log_4 3) * Phi(log_4 x),
   Phi(u) = sum_j phi_j e^(2 pi i j u),
   phi_j = -Gamma(s_j)Gamma(-1/2-s_j) / (Gamma(-1/2) ln 4),
   s_j = log_4 3 + 2 pi i j/ln 4.
Checks: (a) corrected ladder makes Phi periodic & e-independent,
(b) numeric Fourier of Phi matches the Gamma formula,
(c) the EXACT identity at moderate x (2, 10, 100) to ~25 digits."""
import mpmath as mp
mp.mp.dps = 90

def F(x, terms=450):
    return mp.fsum(mp.power(3, -n) * mp.sqrt(1 + x * mp.power(4, -n))
                   for n in range(terms))

lg3 = mp.log(3) / mp.log(4)
ln4 = mp.log(4)

def a(k):
    return mp.binomial(mp.mpf(1)/2, k) / (1 - mp.power(4, k)/mp.mpf(6))

def ladder(x, K):
    return mp.fsum(a(k) * mp.power(x, mp.mpf(1)/2 - k) for k in range(K))

def phi(j):
    s = lg3 + 2 * j_unit * mp.pi * j / ln4
    return -mp.gamma(s) * mp.gamma(-mp.mpf(1)/2 - s) / (mp.gamma(-mp.mpf(1)/2) * ln4)
j_unit = mp.mpc(0, 1)

def Phi_gamma(u, J=6):
    """phi_j = -Gamma(s_{-j})Gamma(-1/2-s_{-j})/(Gamma(-1/2) ln4),
    s_{-j} = lg3 - 2 pi i j/ln4  (contour orientation fixed by numerics)."""
    s = mp.mpf(0)
    for j in range(-J, J+1):
        sj = lg3 - 2 * mp.pi * j_unit * j / ln4
        pj = mp.gamma(sj) * mp.gamma(-mp.mpf(1)/2 - sj) / (mp.gamma(-mp.mpf(1)/2) * ln4)
        s += pj * mp.exp(2 * mp.pi * j_unit * j * u)
    return s.real

# (a) periodicity with corrected ladder
def Phi_num(u, e=24, K=12):
    x = mp.power(4, e + u)
    return (F(x) - ladder(x, K)) * mp.power(x, lg3)

print("(a) corrected-ladder Phi:")
p03, p13, p03b = Phi_num(mp.mpf('0.3')), Phi_num(mp.mpf('1.3')), Phi_num(mp.mpf('0.3'), e=28)
print("  Phi(0.3) =", mp.nstr(p03, 20))
print("  |Phi(0.3)-Phi(1.3)| =", mp.nstr(abs(p03 - p13), 4))
print("  |Phi(0.3)e24-e28|   =", mp.nstr(abs(p03 - p03b), 4))

# (b) Fourier match
print("(b) Fourier coefficients:")
N = 32
samples = [Phi_num(mp.mpf(t)/N) for t in range(N)]
for j in [0, 1, 2, 3]:
    num = mp.fsum(samples[t] * mp.exp(-2*mp.pi*j_unit*j*mp.mpf(t)/N)
                  for t in range(N)) / N
    sj = lg3 + 2 * mp.pi * j_unit * j / ln4
    pred = -mp.gamma(sj) * mp.gamma(-mp.mpf(1)/2 - sj) / (mp.gamma(-mp.mpf(1)/2) * ln4)
    print(f"  j={j}: numeric {mp.nstr(num, 12)}")
    print(f"        gamma   {mp.nstr(pred, 12)}   |diff| = {mp.nstr(abs(num-pred), 3)}")

# (c) exact identity at moderate x
print("(c) exact identity F = ladder + x^-lg3 Phi(log_4 x):")
for xv in ['2', '10', '100', '0.51']:
    x = mp.mpf(xv)
    lhs = F(x)
    rhs = ladder(x, 200) + mp.power(x, -lg3) * Phi_gamma(mp.log(x)/ln4, J=8)
    print(f"  x={xv}: |F - rep| = {mp.nstr(abs(lhs - rhs), 4)}")
