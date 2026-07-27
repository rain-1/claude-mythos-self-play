import mpmath as mp
mp.mp.dps = 45
M = 300; K = 50
a = []
for k in range(1, K+1):
    B = mp.bernoulli(2*k)
    a.append(mp.mpf(2)**(2*k-1)*(mp.mpf(2)**(2*k)-1)*abs(B)/(k*mp.factorial(2*k)))
hz = [mp.zeta(2*k, M+1) for k in range(1, K+1)]
def phi(t):
    if t == 0: return mp.mpf(1)
    p = mp.mpf(1)
    for n in range(1, M+1):
        p *= mp.cos(t/n)
        if p == 0: return mp.mpf(0)
    s = mp.mpf(0); t2 = t*t; tp = mp.mpf(1)
    for k in range(K):
        tp *= t2
        term = a[k]*tp*hz[k]
        s += term
        if abs(term) < mp.mpf(10)**(-50): break
    return p*mp.exp(-s)
def rho(x, T=110):
    tot = mp.mpf(0); t0 = mp.mpf(0)
    while t0 < T:
        t1 = min(t0+1, T)
        tot += mp.quad(lambda t: mp.cos(x*t)*phi(t), [t0, t1])
        t0 = t1
    return tot/mp.pi
for x in ('1.5','1.8','1.9','1.95','2.05','2.1','2.2','2.5','3.0'):
    r = rho(mp.mpf(x))
    print(x, mp.nstr(r, 30), mp.nstr(r - mp.mpf(1)/8, 8))
