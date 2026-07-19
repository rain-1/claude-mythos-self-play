"""Verification certificates for 'Where the Slope Must Fall'.
Every theorem the triptych rests on, checked numerically. Run: python3 verify.py
"""
import numpy as np
rng = np.random.default_rng(7)

print("== Sendov (metric lens) : all zeros in |z|<=1 => every zero within 1 of a critical pt")
worst = 0.0
for _ in range(20000):
    r = np.sqrt(rng.random(8)); th = rng.uniform(0, 2*np.pi, 8)
    roots = r*np.exp(1j*th)
    crit = np.roots(np.polyder(np.poly(roots)))
    worst = max(worst, np.abs(roots[:, None]-crit[None, :]).min(axis=1).max())
print(f"   max leash over 20000 random configs = {worst:.4f}  (must be <= 1)")
for n in (3, 6, 13):
    c = np.zeros(n+1); c[0] = 1; c[-1] = -1          # p = z^n - 1
    crit = np.roots(np.polyder(c))
    print(f"   extremal z^{n}-1: max|crit|={np.abs(crit).max():.2e} (crit pile at origin) -> every leash = 1")

print("== Marden / Siebeck (geometric lens) : crit pts of a cubic = foci of Steiner inellipse")
for _ in range(4):
    A, B, C = rng.normal(size=3) + 1j*rng.normal(size=3)
    f = np.roots(np.polyder(np.poly([A, B, C]))); g = (A+B+C)/3
    a = (abs((A+B)/2-f[0]) + abs((A+B)/2-f[1]))/2
    mids = [(A+B)/2, (B+C)/2, (C+A)/2]
    onE = max(abs(abs(M-f[0])+abs(M-f[1]) - 2*a) for M in mids)
    print(f"   f1+f2-2centroid={abs(f.sum()-2*g):.1e}  f1*f2-(ab+bc+ca)/3={abs(f.prod()-(A*B+B*C+C*A)/3):.1e}"
          f"  midpoints-on-ellipse={onE:.1e}")

print("== Bocher / Gauss-Lucas (physical lens) : crit pts are equilibria of the root charges")
for _ in range(4):
    roots = rng.normal(size=7) + 1j*rng.normal(size=7)
    crit = np.roots(np.polyder(np.poly(roots)))
    field = np.array([np.sum(1.0/(z-roots)) for z in crit])
    print(f"   max|sum 1/(z-root)| at crit pts = {np.abs(field).max():.1e}  (should be ~0)")
