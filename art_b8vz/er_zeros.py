"""zeros of E_r(z) = sum z^m/(m!)^r near the origin, from a long truncation (mpmath polyroots)."""
import mpmath as mp, sys
mp.mp.dps = 120
for r in [0.6, 0.8, 0.9, 1.2, 1.5, 1.7, 2.5]:
    N = 90
    c = [1 / mp.factorial(m) ** r for m in range(N + 1)]
    roots = mp.polyroots(c[::-1], maxsteps=400, extraprec=600)
    roots = sorted(roots, key=lambda z: abs(z))[:8]
    print('r=%.2f' % r, '  '.join(mp.nstr(z, 6) for z in roots))
