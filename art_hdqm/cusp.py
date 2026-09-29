"""Envelope of unit-perimeter ellipses near the cusp (1/4, 0), high precision with mpmath."""
import mpmath as mp
mp.mp.dps = 40
def P(a, b):  # 4 a E(m), m = 1 - b^2/a^2
    return 4 * a * mp.ellipe(1 - (b / a) ** 2)
def env(k):   # k = b/a
    p = P(1, k); a, b = 1 / p, k / p
    Pa = mp.diff(lambda s: P(s, b), a); Pb = mp.diff(lambda s: P(a, s), b)
    return a * mp.sqrt(a * Pa), b * mp.sqrt(b * Pb)
print(" k            1/4 - x            y        y/(1/4-x)^(3/2)   y^2/((1/4-x)^3 * log(1/k))")
for e in range(2, 13):
    k = mp.mpf(10) ** (-e)
    x, y = env(k); d = mp.mpf(1) / 4 - x
    print(f"1e-{e:<3d} {mp.nstr(d,10):>18} {mp.nstr(y,10):>18} {mp.nstr(y/d**1.5,10):>14} {mp.nstr(y**2/(d**3*mp.log(1/k)),10):>14}")
