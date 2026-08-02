"""C5 revised: F(x) = (6/5)x^(1/2) + sum_{k>=1} a_k x^(1/2-k)
                        + x^(-log_4 3) * Phi(log_4 x) + ...
   conjecture a_k = binom(1/2,k)/(1 - 4^k/3)  (mirror of the Taylor law
   c_m = binom(1/2,m)/(1 - 4^-m/3)); Phi periodic period 1."""
import mpmath as mp
mp.mp.dps = 80

def F(x, terms=400):
    return mp.fsum(mp.power(3, -n) * mp.sqrt(1 + x * mp.power(4, -n))
                   for n in range(terms))

lg3 = mp.log(3) / mp.log(4)
def a(k):
    return mp.binomial(mp.mpf(1)/2, k) / (1 - mp.power(4, k)/3)

# test the ladder coefficients: (F - (6/5)sqrt(x)) * sqrt(x) -> a_1?
for e in [16, 20, 24]:
    x = mp.power(4, e)
    r = (F(x) - mp.mpf(6)/5 * mp.sqrt(x)) * mp.sqrt(x)
    print(f"x=4^{e}:  (F-(6/5)sqrt x)*sqrt x = {mp.nstr(r, 10)}   a1={mp.nstr(a(1),10)}")

# subtract k=1..6 ladder, look at Phi
def Phi(u, e=24, K=8):
    x = mp.power(4, e + u)
    s = F(x) - mp.mpf(6)/5 * mp.sqrt(x)
    for k in range(1, K+1):
        s -= a(k) * mp.power(x, mp.mpf(1)/2 - k)
    return s * mp.power(x, lg3)

print("\nPhi samples (should now be periodic):")
vals = {}
for u8 in range(0, 9):
    u = mp.mpf(u8) / 8
    vals[u8] = Phi(u)
    print(f"  u={mp.nstr(u,4):6} Phi={mp.nstr(vals[u8], 15)}")
p1 = Phi(mp.mpf('0.3')); p2 = Phi(mp.mpf('1.3')); p3 = Phi(mp.mpf('0.3'), e=26)
print("periodicity |Phi(0.3)-Phi(1.3)| =", mp.nstr(abs(p1 - p2), 4))
print("e-independence |Phi(0.3)@e24 - @e26| =", mp.nstr(abs(p1 - p3), 4))
print("Phi mean ~", mp.nstr((vals[0]+vals[4])/2, 8), " amplitude ~",
      mp.nstr(abs(vals[0]-vals[4]), 8))

# Fourier: Phi(u) = sum_k phi_k e^{2pi i k u}; predicted from Mellin poles at
# s = lg3 + 2 pi i k / ln 4:  phi_k = -Gamma(s_k)Gamma(-1/2-s_k)/(Gamma(-1/2) ln 4)
print("\nMellin-predicted Fourier coefficients vs numerics:")
ln4 = mp.log(4)
for k in [0, 1, 2]:
    sk = lg3 + 2j * mp.pi * k / ln4
    pred = -mp.gamma(sk) * mp.gamma(-mp.mpf(1)/2 - sk) / (mp.gamma(-mp.mpf(1)/2) * ln4)
    # numeric Fourier coefficient of Phi
    N = 16
    num = mp.fsum(Phi(mp.mpf(j)/N) * mp.expjpi(-2 * mp.mpf(k * j)/N)
                  for j in range(N)) / N
    print(f"  k={k}: predicted {mp.nstr(pred, 10)}  numeric {mp.nstr(num, 10)}")
