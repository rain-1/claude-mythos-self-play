"""High-precision density of the random harmonic series X = sum eps_n / n.

rho(x) = (1/pi) * int_0^inf cos(x t) * phi(t) dt,  phi(t) = prod_{n>=1} cos(t/n).

Exact product to n<=M, tail sum_{n>M} ln cos(t/n) via Bernoulli series + Hurwitz zeta.
Certificates: rho(0), rho(1), rho(2) to ~50 digits; the star: rho(2) vs 1/8.
"""
import mpmath as mp
import time

mp.mp.dps = 75
M = 300
K = 70

# a_k for ln cos x = -sum a_k x^{2k}
a = []
for k in range(1, K+1):
    B = mp.bernoulli(2*k)
    a.append(mp.mpf(2)**(2*k-1) * (mp.mpf(2)**(2*k) - 1) * abs(B) / (k * mp.factorial(2*k)))
# Hurwitz zeta(2k, M+1)
hz = [mp.zeta(2*k, M+1) for k in range(1, K+1)]

def phi(t):
    if t == 0: return mp.mpf(1)
    p = mp.mpf(1)
    for n in range(1, M+1):
        p *= mp.cos(t/n)
        if p == 0: return mp.mpf(0)
    # tail
    s = mp.mpf(0)
    t2 = t*t
    tp = mp.mpf(1)
    for k in range(K):
        tp *= t2
        term = a[k] * tp * hz[k]
        s += term
        if abs(term) < mp.mpf(10)**(-80): break
    return p * mp.exp(-s)

def rho(x, T=150, panel=1):
    total = mp.mpf(0)
    t0 = mp.mpf(0)
    while t0 < T:
        t1 = min(t0 + panel, T)
        total += mp.quad(lambda t: mp.cos(x*t) * phi(t), [t0, t1])
        t0 = t1
    return total / mp.pi

t_start = time.time()
for x in (0, 1, 2):
    r = rho(mp.mpf(x))
    print("rho(%d) = %s" % (x, mp.nstr(r, 55)))
    if x == 2:
        print("rho(2) - 1/8 = %s" % mp.nstr(r - mp.mpf(1)/8, 12))
    if x == 0:
        print("rho(0) - 1/4 = %s" % mp.nstr(r - mp.mpf(1)/4, 12))
    print("  elapsed", time.time() - t_start)
