"""Dominant-pole asymptotics of d(n) from A(x) = N(x)/g(x), g(x)=Phi(x^6;x^4)."""
import json, mpmath as mp
mp.mp.dps = 30
def Phi(z, q):
    s, t, j = mp.mpf(0), mp.mpf(1), 0   # t = (-1)^j q^{j(j-1)} z^j/(q;q)_j
    while abs(t) > mp.mpf(10) ** (-40) or j < 5:
        s += t
        j += 1
        t *= -q ** (2 * (j - 1)) * z / (1 - q ** j)
    return s
g = lambda x: Phi(x ** 6, x ** 4)
Nx = lambda x: mp.fsum(x ** (m * m) * Phi(x ** (4 * m + 6), x ** 4) for m in range(1, 80))
rho = mp.findroot(g, (0.85, 0.95), solver='anderson')
gp = mp.diff(g, rho)
C = -1 / (rho * gp)
a, b = C * Nx(rho), C * Nx(-rho)
print("rho =", rho, " 1/rho =", 1 / rho)
print("a =", a, " b =", b)
d = json.load(open("d_upto_6000.json"))
for n in [100, 101, 500, 501, 1000, 1001, 3000, 3001, 6000]:
    print(n, mp.nstr(d[n] / ((a + (-1) ** n * b) * rho ** (-n)), 25))
# decay rate of relative error -> modulus of next singularity
e = lambda n: abs(d[n] / ((a + (-1) ** n * b) * rho ** (-n)) - 1)
for n1, n2 in [(100, 300), (200, 400), (300, 500)]:
    ratio = (e(n2) / e(n1)) ** (mp.mpf(1) / (n2 - n1))
    print(n1, n2, "error ratio/step", mp.nstr(ratio, 8), " -> next |pole| ~", mp.nstr(rho / ratio, 8))
